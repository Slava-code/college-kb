#!/usr/bin/env python3
"""Export reminder-ledger bullets to an iCalendar (.ics) file any calendar app can import.

Reads reminders/*.md (or the files given). A bullet looks like:

  - 2099-10-06 18:00 Etc/UTC · DEMO 101 midterm review · status: scheduled · scheduler_ref: ics:demo101-review · source: `school/courses/demo-101`

The date comes first (`YYYY-MM-DD`, optional `HH:MM`, optional IANA zone), then the
title, then `key: value` fields separated by " · ". Date-only bullets use
REMINDER_DEFAULT_MORNING; times without a zone use REMINDER_TIMEZONE (both from
THRESHOLDS.md). Bullets without a concrete date (needs-clarification) are skipped.

By default only `status: scheduled` bullets whose scheduler_ref starts with `ics:` are
exported: those are the ones this file is the scheduler for. The UID after `ics:` stays
stable, so re-importing the file updates events instead of duplicating them in most
calendar apps.

Usage:
  python3 scripts/reminders-ics.py -o ~/calendars/kb-reminders.ics
  python3 scripts/reminders-ics.py --list                  # show parsed bullets, write nothing
  python3 scripts/reminders-ics.py --uid "2099-10-06 · DEMO 101 midterm review"   # suggest an ics: ref
  python3 scripts/reminders-ics.py --all-open -o /tmp/preview.ics   # also proposed-only (preview)

Standard library only. Uses zoneinfo (Python 3.9+) when the zone database is available;
otherwise it writes floating local times.
"""
from __future__ import annotations
import argparse, hashlib, re, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BULLET_RE = re.compile(r'^- (\d{4}-\d{2}-\d{2})(?:[ T](\d{1,2}:\d{2})(?:\s+([A-Za-z]+(?:/[A-Za-z0-9_+\-]+)*))?)?'
                       r'\s*(?:·|—|-)\s*(.*)$')
OPEN = {'scheduled', 'proposed-only'}


def thresholds() -> dict[str, str]:
    out = {}
    p = ROOT / 'THRESHOLDS.md'
    if p.is_file():
        for line in p.read_text(encoding='utf-8').splitlines():
            m = re.match(r'^([A-Z_]+)\s*=\s*(.*?)\s*(?:#.*)?$', line)
            if m:
                out[m.group(1)] = m.group(2)
    return out


def parse_bullets(paths):
    in_code = False
    for path in paths:
        for lineno, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if line.lstrip().startswith('```'):
                in_code = not in_code
                continue
            m = None if in_code else BULLET_RE.match(line)
            if not m:
                continue
            date, time, zone, rest = m.groups()
            parts = [p.strip() for p in rest.split(' · ')]
            title = parts[0]
            fields = {}
            for p in parts[1:]:
                k, sep, v = p.partition(':')
                if sep and re.fullmatch(r'[a-z_]+', k.strip()):
                    fields[k.strip()] = v.strip()
            yield {'file': path, 'line': lineno, 'date': date, 'time': time, 'zone': zone, 'title': title, **fields}


def suggest_uid(date: str, title: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:40]
    return f'{date}-{slug}-{hashlib.sha1(f"{date}|{title}".encode()).hexdigest()[:6]}'


def esc(s: str) -> str:
    return s.replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')


def fold(line: str) -> str:
    """RFC 5545 line folding at 75 octets."""
    out, cur = [], b''
    for ch in line:
        b = ch.encode('utf-8')
        if len(cur) + len(b) > (75 if not out else 74):
            out.append(cur.decode('utf-8'))
            cur = b''
        cur += b
    out.append(cur.decode('utf-8'))
    return '\r\n '.join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='*', type=Path, help='ledger files (default: reminders/*.md)')
    ap.add_argument('-o', '--output', type=Path, help='write the .ics here (default: stdout)')
    ap.add_argument('--all-open', action='store_true', help='also export proposed-only bullets (preview only)')
    ap.add_argument('--list', action='store_true', help='print parsed bullets and exit')
    ap.add_argument('--uid', metavar='"DATE · TITLE"', help='print a stable ics: scheduler_ref for a new bullet')
    args = ap.parse_args()

    if args.uid:
        date, _, title = args.uid.partition('·')
        print(f'scheduler_ref: ics:{suggest_uid(date.strip(), title.strip())}')
        return 0

    files = args.files or sorted(p for p in (ROOT / 'reminders').glob('*.md') if p.name != 'README.md')
    items = list(parse_bullets(files))
    if args.list:
        for it in items:
            print(f"{it['date']} {it['time'] or '--:--'} {it['zone'] or '':<8} {it.get('status', '?'):<20} "
                  f"{it.get('scheduler_ref', '?'):<28} {it['title']}")
        return 0

    th = thresholds()
    tzname = th.get('REMINDER_TIMEZONE', 'Etc/UTC')
    morning = th.get('REMINDER_DEFAULT_MORNING', '08:00')
    warned = set()

    def zone(name):
        try:
            from zoneinfo import ZoneInfo
            return ZoneInfo(name)
        except Exception:  # Python < 3.9, unknown name, or no tz database (Windows without tzdata)
            if name not in warned:
                warned.add(name)
                print(f'warning: time zone {name!r} unavailable; writing floating local times', file=sys.stderr)
            return None

    def keep(it):
        st, ref = it.get('status'), it.get('scheduler_ref', '')
        if st == 'scheduled' and ref.startswith('ics:'):
            return True
        return args.all_open and st in OPEN

    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//college-kb//reminders-ics//EN', 'CALSCALE:GREGORIAN',
             'X-WR-CALNAME:KB reminders']
    n = 0
    for it in filter(keep, items):
        hh, mm = (it['time'] or morning).split(':')
        start = datetime.strptime(it['date'], '%Y-%m-%d').replace(hour=int(hh), minute=int(mm))
        ref = it.get('scheduler_ref', '')
        uid = ref[4:] if ref.startswith('ics:') else suggest_uid(it['date'], it['title'])
        tz = zone(it.get('zone') or tzname)
        if tz is not None:
            s = start.replace(tzinfo=tz).astimezone(timezone.utc)
            dt = lambda d: d.strftime('%Y%m%dT%H%M%SZ')
        else:
            s = start
            dt = lambda d: d.strftime('%Y%m%dT%H%M%S')
        desc = 'From the KB reminders ledger'
        if it.get('source'):
            desc += f" · source: {it['source']}"
        if it.get('status') != 'scheduled':
            desc += f" · status: {it.get('status')} (preview)"
        lines += ['BEGIN:VEVENT', f'UID:{uid}@college-kb', f'DTSTAMP:{stamp}', f'DTSTART:{dt(s)}',
                  f'DTEND:{dt(s + timedelta(minutes=15))}', f"SUMMARY:{esc(it['title'])}",
                  f'DESCRIPTION:{esc(desc)}', 'BEGIN:VALARM', 'ACTION:DISPLAY',
                  f"DESCRIPTION:{esc(it['title'])}", 'TRIGGER:PT0M', 'END:VALARM', 'END:VEVENT']
        n += 1
    lines.append('END:VCALENDAR')
    data = '\r\n'.join(fold(l) for l in lines) + '\r\n'

    if args.output:
        out = args.output.expanduser().resolve()
        try:
            out.relative_to(ROOT)
            print('warning: writing inside the repo; do not commit the .ics (it is derived data)', file=sys.stderr)
        except ValueError:
            pass
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data.encode('utf-8'))
        print(f'wrote {n} event(s) to {out}', file=sys.stderr)
    else:
        sys.stdout.write(data)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
