#!/usr/bin/env python3
"""Read-only mailbox reader over Thunderbird's local message store.

Thunderbird (IMAP or POP, with offline sync on) keeps a copy of the mailbox on
disk. This script only READS those files; it never writes to the Thunderbird
profile, never sends, moves, flags or deletes mail. Both store formats work:
maildir (one file per message, recommended) and mbox (Thunderbird's default).

Usage (always run as `python3 -I scripts/school-mail.py ...`):
  status                                   is Thunderbird running, message counts, newest file
  accounts                                 list profiles/accounts found on this machine
  folders                                  folders and message counts
  list   [-f FOLDER] [-n N] [--since YYYY-MM-DD]
  search QUERY [-f FOLDER|all] [-n N] [--since D] [--from ADDR] [--to ADDR] [--body]
  show   ID [--html] [--save-attachments DIR]
  cite   ID                                a [Source: ...] line for a KB page

IDs look like "INBOX/1712345678901.eml" (maildir) or "INBOX@123456" (mbox byte offset).

Configuration (all optional; auto-detected when unset):
  --account TEXT / SCHOOL_MAIL_ACCOUNT     substring picking one account from `accounts`
  SCHOOL_MAIL_TB_ROOT                      Thunderbird data dir (holds Profiles/ or profile dirs)
  SCHOOL_MAIL_CACHE                        header-cache dir (outside the repo)
  SCHOOL_MAIL_CONFIG                       JSON config file, default ~/.config/school-mail/config.json
                                           keys: thunderbird_root, account, cache_dir
"""
from __future__ import annotations

import argparse
import email
import email.policy
import hashlib
import html
import json
import os
import re
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from email.parser import BytesHeaderParser
from email.utils import getaddresses, parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path

HOME = Path.home()
HEADER_KEYS = ("From", "To", "Cc", "Subject", "Message-ID")
MOZ_EXPUNGED = 0x0008  # X-Mozilla-Status flag: deleted, not yet compacted


# ---------------------------------------------------------------- configuration

def _config() -> dict:
    default = (Path(os.environ["APPDATA"]) / "school-mail" / "config.json"
               if sys.platform == "win32" and os.environ.get("APPDATA")
               else Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config")) / "school-mail" / "config.json")
    p = Path(os.environ.get("SCHOOL_MAIL_CONFIG", default)).expanduser()
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except ValueError as e:
            sys.exit(f"Bad JSON in {p}: {e}")
    return {}


CONFIG = _config()


def tb_roots() -> list[Path]:
    explicit = os.environ.get("SCHOOL_MAIL_TB_ROOT") or CONFIG.get("thunderbird_root")
    if explicit:
        return [Path(explicit).expanduser()]
    if sys.platform == "darwin":
        cands = [HOME / "Library/Thunderbird"]
    elif sys.platform == "win32":
        cands = [Path(os.environ.get("APPDATA", HOME / "AppData/Roaming")) / "Thunderbird"]
    else:
        cands = [HOME / ".thunderbird",
                 HOME / "snap/thunderbird/common/.thunderbird",
                 HOME / ".var/app/org.mozilla.Thunderbird/.thunderbird"]
    return [c for c in cands if c.is_dir()]


def cache_dir() -> Path:
    explicit = os.environ.get("SCHOOL_MAIL_CACHE") or CONFIG.get("cache_dir")
    if explicit:
        return Path(explicit).expanduser()
    if sys.platform == "darwin":
        return HOME / "Library/Caches/school-mail"
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", HOME / "AppData/Local")) / "school-mail"
    return Path(os.environ.get("XDG_CACHE_HOME", HOME / ".cache")) / "school-mail"


def find_accounts() -> list[Path]:
    """Every account store dir: <profile>/ImapMail/<server> and <profile>/Mail/<server>."""
    out = []
    for root in tb_roots():
        profiles = [p for p in (root / "Profiles").glob("*") if p.is_dir()] if (root / "Profiles").is_dir() else []
        profiles += [p for p in root.glob("*") if (p / "prefs.js").is_file()]  # Linux layout
        for prof in sorted(set(profiles)):
            for kind in ("ImapMail", "Mail"):
                for server in sorted((prof / kind).glob("*")):
                    if server.is_dir():
                        out.append(server)
    return out


def account_root(selector: str | None) -> Path:
    accts = find_accounts()
    if not accts:
        roots = ", ".join(str(r) for r in tb_roots()) or "(no Thunderbird data dir found)"
        sys.exit(f"No Thunderbird mail store found under {roots}. Is Thunderbird set up with offline sync? "
                 "Set SCHOOL_MAIL_TB_ROOT if it lives elsewhere.")
    sel = selector or os.environ.get("SCHOOL_MAIL_ACCOUNT") or CONFIG.get("account")
    if sel:
        hits = [a for a in accts if sel.lower() in a.as_posix().lower()]
        if len(hits) == 1:
            return hits[0]
        sys.exit(f"Account selector {sel!r} matched {len(hits)} stores; run `accounts` and pick a longer substring.")
    imap = [a for a in accts if a.parent.name == "ImapMail"]
    if len(imap) == 1:
        return imap[0]
    if not imap and len(accts) == 1:
        return accts[0]
    sys.exit("Several mail stores found; choose one with --account (or SCHOOL_MAIL_ACCOUNT):\n  "
             + "\n  ".join(a.as_posix() for a in accts))


# ---------------------------------------------------------------- folders

def folder_map(root: Path) -> dict[str, tuple[str, Path]]:
    """Display name ("INBOX", "Archive/2099") -> (kind, path); kind is 'maildir' or 'mbox'."""
    out: dict[str, tuple[str, Path]] = {}
    for cur in root.rglob("cur"):
        if cur.is_dir():
            rel = cur.parent.relative_to(root).as_posix().replace(".sbd/", "/")
            out[rel] = ("maildir", cur.parent)
    for msf in root.rglob("*.msf"):
        mbox = msf.with_suffix("")
        if mbox.is_file() and not (mbox / "cur").exists():
            rel = mbox.relative_to(root).as_posix().replace(".sbd/", "/")
            out.setdefault(rel, ("mbox", mbox))
    # Thunderbird sometimes stores a folder on disk as "Archive-1"; show the real name when free.
    for rel in list(out):
        base = re.sub(r"-\d+$", "", rel)
        if base != rel and base not in out:
            out[base] = out.pop(rel)
    return out


def resolve_folder(root: Path, name: str) -> list[tuple[str, str, Path]]:
    fm = folder_map(root)
    if name.lower() == "all":
        return [(k, *v) for k, v in sorted(fm.items())]
    for k, v in fm.items():
        if k.lower() == name.lower():
            return [(k, *v)]
    sys.exit(f"Unknown folder {name!r}. Known: {', '.join(sorted(fm)) or '(none synced yet)'}")


# ---------------------------------------------------------------- mbox helpers

def _is_from_line(line: bytes, prev_blank: bool) -> bool:
    return line.startswith(b"From ") and prev_blank


def mbox_scan(path: Path):
    """Yield (offset, header_bytes) for each message in a Thunderbird mbox file."""
    with open(path, "rb") as fh:
        offset, prev_blank, start, hdr, in_hdr = 0, True, None, [], False
        for line in fh:
            if _is_from_line(line, prev_blank):
                if start is not None:
                    yield start, b"".join(hdr)
                start, hdr, in_hdr = offset, [], True
            elif in_hdr:
                if line in (b"\n", b"\r\n"):
                    in_hdr = False
                else:
                    hdr.append(line)
            prev_blank = line in (b"\n", b"\r\n")
            offset += len(line)
        if start is not None:
            yield start, b"".join(hdr)


def mbox_read(path: Path, offset: int) -> bytes:
    with open(path, "rb") as fh:
        fh.seek(offset)
        first = fh.readline()
        if not first.startswith(b"From "):
            sys.exit("Stale message id (the mbox was compacted); run list/search again.")
        parts, prev_blank = [], False
        for line in fh:
            if _is_from_line(line, prev_blank):
                break
            parts.append(line)
            prev_blank = line in (b"\n", b"\r\n")
        return b"".join(parts)


def expunged(h) -> bool:
    try:
        return bool(int(str(h.get("X-Mozilla-Status", "0")).strip() or "0", 16) & MOZ_EXPUNGED)
    except ValueError:
        return False


# ---------------------------------------------------------------- header cache

def msg_date(h) -> datetime:
    try:
        d = parsedate_to_datetime(str(h.get("Date", "")))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.fromtimestamp(0, timezone.utc)


def open_index(root: Path):
    """Header cache outside the Thunderbird profile, so list/search do not re-parse every file."""
    d = cache_dir()
    d.mkdir(parents=True, exist_ok=True)
    tag = hashlib.sha1(root.as_posix().encode()).hexdigest()[:12]
    db = sqlite3.connect(d / f"index-{tag}.sqlite")
    db.execute("""CREATE TABLE IF NOT EXISTS msgs (key TEXT PRIMARY KEY, folder TEXT, ts REAL,
                  "From" TEXT, "To" TEXT, "Cc" TEXT, "Subject" TEXT, "Message-ID" TEXT)""")
    db.execute("CREATE TABLE IF NOT EXISTS mbox_state (folder TEXT PRIMARY KEY, sig TEXT)")
    return db


def _row(key, folder, h):
    return (key, folder, msg_date(h).timestamp(), *(str(h.get(k, "")) for k in HEADER_KEYS))


def refresh_index(db, folders):
    parser = BytesHeaderParser(policy=email.policy.default)
    for fname, kind, fpath in folders:
        if kind == "maildir":
            on_disk = {str(p) for p in (fpath / "cur").iterdir() if p.is_file()}
            indexed = {r[0] for r in db.execute("SELECT key FROM msgs WHERE folder = ?", (fname,))}
            db.executemany("DELETE FROM msgs WHERE key = ?", [(p,) for p in indexed - on_disk])
            rows = []
            for p in on_disk - indexed:
                try:
                    with open(p, "rb") as fh:
                        h = parser.parse(fh)
                except Exception:
                    continue
                rows.append(_row(p, fname, h))
        else:
            st = fpath.stat()
            sig = f"{st.st_size}:{st.st_mtime_ns}"
            old = db.execute("SELECT sig FROM mbox_state WHERE folder = ?", (fname,)).fetchone()
            if old and old[0] == sig:
                continue
            db.execute("DELETE FROM msgs WHERE folder = ?", (fname,))
            rows = []
            for off, raw in mbox_scan(fpath):
                try:
                    h = parser.parsebytes(raw)
                except Exception:
                    continue
                if not expunged(h):
                    rows.append(_row(f"{fpath}#{off}", fname, h))
            db.execute("INSERT OR REPLACE INTO mbox_state VALUES (?, ?)", (fname, sig))
        db.executemany("INSERT OR REPLACE INTO msgs VALUES (?,?,?,?,?,?,?,?)", rows)
    db.commit()


def iter_messages(root, folders, since=None):
    db = open_index(root)
    refresh_index(db, folders)
    seen = set()  # an interrupted sync can leave the same message on disk twice
    q = "SELECT key, ts, " + ", ".join(f'"{k}"' for k in HEADER_KEYS) + " FROM msgs WHERE folder = ?"
    for fname, kind, _ in folders:
        for key, ts, *vals in db.execute(q, (fname,)):
            h = dict(zip(HEADER_KEYS, vals))
            dedupe = (fname, h["Message-ID"].strip() or key)
            if dedupe in seen:
                continue
            seen.add(dedupe)
            d = datetime.fromtimestamp(ts, timezone.utc)
            if since and d < since:
                continue
            if kind == "maildir":
                mid = f"{fname}/{Path(key).name}"
            else:
                mid = f"{fname}@{key.rpartition('#')[2]}"
            yield mid, h, d


def load_message(root: Path, mid: str):
    if re.search(r"@\d+$", mid):
        folder, _, off = mid.rpartition("@")
        (_, kind, fpath), = resolve_folder(root, folder)
        if kind != "mbox":
            sys.exit(f"{folder} is a maildir folder; ids there look like {folder}/<file>")
        data = mbox_read(fpath, int(off))
    else:
        folder, _, fname = mid.rpartition("/")
        (_, kind, fpath), = resolve_folder(root, folder)
        path = fpath / "cur" / Path(fname).name
        if kind != "maildir" or not path.is_file():
            sys.exit(f"No such message: {mid}")
        data = path.read_bytes()
    return email.message_from_bytes(data, policy=email.policy.default)


# ---------------------------------------------------------------- text helpers

class _Text(HTMLParser):
    BLOCK = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "table", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip, self._href = [], 0, None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "head"):
            self.skip += 1
        elif tag in self.BLOCK:
            self.parts.append("\n")
        elif tag == "a":
            href = dict(attrs).get("href")
            if href and href.startswith("http"):
                self._href = href  # shown after the link text, never fetched

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head"):
            self.skip = max(0, self.skip - 1)
        elif tag == "a" and self._href:
            self.parts.append(f" [{self._href}]")
            self._href = None

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_to_text(s: str) -> str:
    p = _Text()
    p.feed(s)
    text = html.unescape("".join(p.parts))
    text = re.sub(r"[ \t ]+", " ", text)
    return re.sub(r"\n\s*\n\s*\n+", "\n\n", text).strip()


def body_text(msg, prefer_html=False) -> str:
    try:
        plain = msg.get_body(preferencelist=("plain",))
        rich = msg.get_body(preferencelist=("html",))
        if prefer_html and rich:
            return rich.get_content()
        if plain:
            return plain.get_content().strip()
        if rich:
            return html_to_text(rich.get_content())
    except Exception as e:  # malformed MIME or unknown charset
        return f"(could not decode body: {e})"
    return "(no text body)"


def short_addr(value: str) -> str:
    addrs = getaddresses([value])
    if not addrs:
        return ""
    name, addr = addrs[0]
    return f"{name} <{addr}>" if name else addr


def fmt_row(mid, h, d):
    subj = str(h.get("Subject") or "(no subject)").replace("\n", " ")
    return f"{d.astimezone().strftime('%Y-%m-%d %H:%M')}  {short_addr(h.get('From', ''))[:40]:<40}  {subj[:90]}\n    id: {mid}"


def parse_since(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").astimezone()
    except ValueError:
        sys.exit("--since must be YYYY-MM-DD")


def safe_name(name: str, i: int) -> str:
    n = re.sub(r"[^A-Za-z0-9._ -]+", "-", Path(name or "").name).strip(" .-")
    return n or f"attachment-{i}"


def thunderbird_running() -> str:
    try:
        if sys.platform == "win32":
            out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq thunderbird.exe"],
                                 capture_output=True, text=True).stdout
            return "yes" if "thunderbird.exe" in out.lower() else "NO (mail is not syncing)"
        r = subprocess.run(["pgrep", "-x", "thunderbird"], capture_output=True, text=True)
        if r.returncode != 0:  # some Linux builds run as thunderbird-bin
            r = subprocess.run(["pgrep", "-f", "thunderbird-bin"], capture_output=True, text=True)
        return "yes" if r.returncode == 0 else "NO (mail is not syncing)"
    except FileNotFoundError:
        return "unknown (no pgrep/tasklist)"


# ---------------------------------------------------------------- commands

def cmd_accounts(a):
    accts = find_accounts()
    if not accts:
        print("no Thunderbird mail stores found; roots checked: "
              + (", ".join(str(r) for r in tb_roots()) or "(none exist)"))
    for p in accts:
        fm = folder_map(p)
        kinds = sorted({k for k, _ in fm.values()}) or ["empty"]
        print(f"{p.as_posix()}   [{p.parent.name}, {'/'.join(kinds)}, {len(fm)} folders]")


def cmd_status(a):
    root = account_root(a.account)
    fm = folder_map(root)
    newest, maildir_total, mbox_bytes = None, 0, 0
    for kind, p in fm.values():
        if kind == "maildir":
            for f in (p / "cur").iterdir():
                maildir_total += 1
                m = f.stat().st_mtime
                newest = m if newest is None or m > newest else newest
        else:
            st = p.stat()
            mbox_bytes += st.st_size
            newest = st.st_mtime if newest is None or st.st_mtime > newest else newest
    print(f"store: {root}")
    print(f"thunderbird running: {thunderbird_running()}")
    kinds = sorted({k for k, _ in fm.values()})
    print(f"folders: {len(fm)} ({'/'.join(kinds) or 'none'})")
    if maildir_total:
        print(f"maildir messages on disk: {maildir_total}")
    if mbox_bytes:
        print(f"mbox data on disk: {mbox_bytes / 1e6:.0f} MB (run `folders` for message counts)")
    if newest:
        print(f"newest write: {datetime.fromtimestamp(newest).strftime('%Y-%m-%d %H:%M')}")
    print(f"cache: {cache_dir()}")


def cmd_folders(a):
    root = account_root(a.account)
    folders = resolve_folder(root, "all")
    counts = {}
    for mid, h, d in iter_messages(root, folders):
        f = re.sub(r"(/[^/]+|@\d+)$", "", mid)
        counts[f] = counts.get(f, 0) + 1
    for name, kind, _ in folders:
        print(f"{counts.get(name, 0):7d}  {name}  [{kind}]")


def cmd_list(a):
    root = account_root(a.account)
    rows = sorted(iter_messages(root, resolve_folder(root, a.folder), parse_since(a.since)),
                  key=lambda r: r[2], reverse=True)
    for mid, h, d in rows[: a.n]:
        print(fmt_row(mid, h, d))
    print(f"-- {min(a.n, len(rows))} of {len(rows)} shown")


def cmd_search(a):
    root = account_root(a.account)
    q = a.query.lower()
    hits = []
    for mid, h, d in iter_messages(root, resolve_folder(root, a.folder), parse_since(a.since)):
        if a.sender and a.sender.lower() not in str(h.get("From", "")).lower():
            continue
        if a.recipient and a.recipient.lower() not in (str(h.get("To", "")) + str(h.get("Cc", ""))).lower():
            continue
        hay = " ".join(str(h.get(k, "")) for k in ("Subject", "From", "To", "Cc")).lower()
        if q and q not in hay and a.body:
            try:
                hay += body_text(load_message(root, mid)).lower()
            except SystemExit:
                pass
        if q in hay:
            hits.append((mid, h, d))
    hits.sort(key=lambda r: r[2], reverse=True)
    for mid, h, d in hits[: a.n]:
        print(fmt_row(mid, h, d))
    print(f"-- {min(a.n, len(hits))} of {len(hits)} matches")


def cmd_show(a):
    root = account_root(a.account)
    m = load_message(root, a.id)
    for k in ("Date", "From", "To", "Cc", "Subject", "Message-ID"):
        if m.get(k):
            print(f"{k}: {m[k]}")
    atts = list(m.iter_attachments())
    if atts:
        print("Attachments: " + ", ".join(f"{x.get_filename() or '(unnamed)'} ({x.get_content_type()})" for x in atts))
    print()
    print(body_text(m, prefer_html=a.html))
    if a.save_attachments and atts:
        out = Path(a.save_attachments).expanduser()
        out.mkdir(parents=True, exist_ok=True)
        for i, x in enumerate(atts):
            target = out / safe_name(x.get_filename(), i)
            stem, suf, n = target.stem, target.suffix, 1
            while target.exists():  # never overwrite
                target = out / f"{stem}-{n}{suf}"
                n += 1
            target.write_bytes(x.get_payload(decode=True) or b"")
            print(f"saved: {target}")


def cmd_cite(a):
    root = account_root(a.account)
    m = load_message(root, a.id)
    d = msg_date(m).astimezone().strftime("%Y-%m-%d")
    subj = str(m.get("Subject") or "(no subject)").replace("\n", " ").replace('"', "'")
    print(f'[Source: email "{subj}" from {short_addr(str(m.get("From", "")))}, {d}, '
          f'Message-ID {str(m.get("Message-ID", "")).strip() or "(none)"}]')


def main():
    ap = argparse.ArgumentParser(description="Read-only mailbox reader over Thunderbird's local store.")
    ap.add_argument("--account", help="substring selecting one store from `accounts`")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    sub.add_parser("accounts").set_defaults(fn=cmd_accounts)
    sub.add_parser("folders").set_defaults(fn=cmd_folders)
    p = sub.add_parser("list")
    p.add_argument("-f", "--folder", default="INBOX")
    p.add_argument("-n", type=int, default=20)
    p.add_argument("--since")
    p.set_defaults(fn=cmd_list)
    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("-f", "--folder", default="all")
    p.add_argument("-n", type=int, default=30)
    p.add_argument("--since")
    p.add_argument("--from", dest="sender")
    p.add_argument("--to", dest="recipient")
    p.add_argument("--body", action="store_true", help="also search message bodies (slower)")
    p.set_defaults(fn=cmd_search)
    p = sub.add_parser("show")
    p.add_argument("id")
    p.add_argument("--html", action="store_true", help="print the raw HTML body instead of text")
    p.add_argument("--save-attachments", metavar="DIR")
    p.set_defaults(fn=cmd_show)
    p = sub.add_parser("cite")
    p.add_argument("id")
    p.set_defaults(fn=cmd_cite)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
