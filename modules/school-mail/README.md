# Module: school-mail

This module gives your agent **read-only** access to your school mailbox, for questions like "did my advisor reply?", "find the email with the lab schedule" or "save that syllabus attachment". The agent never sees your password and never touches Microsoft's servers. Thunderbird keeps an offline copy of the mailbox on disk, and a standard-library Python script reads that copy.

## When to use it

Use it when your school mail is Outlook / Microsoft 365, or Gmail, or any other IMAP server, **and** the direct routes are closed to you:

- Your university tenant blocks third-party app consent, so Microsoft Graph API apps and Microsoft 365 MCP connectors either can't be authorized or need an admin approval you won't get.
- Your desktop mail client has no scripting or readable store. New Outlook for Mac, for example, has no AppleScript and keeps mail in an undocumented database.

If your agent host already has a working, permitted mail connector for your school account, use that instead.

### Why this works (and when it doesn't)

Thunderbird signs in to Microsoft 365 or Google with **its own OAuth client**. That client is widely used, so many tenants allow it even when they block unknown apps. You sign in through your school's normal single-sign-on page, Thunderbird syncs over IMAP, and with offline sync turned on it writes every message to disk. The script reads those files, and nothing else talks to the mail server.

It does **not** work everywhere:

- Some tenants block Thunderbird's client too, or disable IMAP entirely, or require compliant or managed devices for mail. If the sign-in is refused, stop there. Do not try to work around your school's access controls.
- **Check your IT acceptable-use policy** before setting this up. Syncing your own mail to your own computer with a mainstream client is normally fine. Copying university mail to devices or services the policy forbids is not.

A common fallback, where policy allows it: a server-side rule that forwards a copy of new mail to a personal account your agent can already read. It only covers new mail, and some messages get filtered out on the way.

## What's in it

| File (in this module) | Installs to | Purpose |
|---|---|---|
| `scripts/school-mail.py` | `scripts/school-mail.py` | Read-only reader with `status`, `accounts`, `folders`, `list`, `search`, `show` (with attachment extraction) and `cite`. Standard library only. |
| `.claude/skills/school-mail/SKILL.md` | `.claude/skills/school-mail/SKILL.md` | Agent procedure and rules: untrusted content, no writes, mail never committed. |
| `school/school-mail-bridge.md` | `school/school-mail-bridge.md` | DEMO record of your bridge setup. Rewrite it with your own facts or delete it. |

## Install

1. Copy the files: `bash modules/install.sh school-mail` (add `--dry-run` to preview). Or copy by hand with `cp -n` into `scripts/`, `.claude/skills/school-mail/` and `school/`.
2. Schema: none needed. The DEMO page is `type: note` in `school/`. Commit as `schema: add school-mail-module`.
3. Set up Thunderbird (below), then run `python3 -I scripts/school-mail.py status`.
4. Record in this machine's `CLAUDE.local.md` that school-mail is enabled, and which account selector it uses if there is more than one.

## Thunderbird setup

1. **Install Thunderbird** from the official Mozilla site or your OS package manager. The ESR (Extended Support Release) channel changes less often. If you follow a package-age rule, pick a release that has been out for a while. Check the download against Mozilla's published checksums where you can.
2. **Choose the store format before adding the account.** Maildir, one file per message, is recommended: it is faster to index and safer to read while Thunderbird writes. Close Thunderbird, then create `user.js` in your profile folder (Help → Troubleshooting Information → Profile Folder) with:
   ```js
   user_pref("mail.serverDefaultStoreContractID", "@mozilla.org/msgstore/maildirstore;1");
   user_pref("mail.server.default.offline_download", true);
   user_pref("mail.server.default.autosync_offline_stores", true);
   user_pref("mail.shell.checkDefaultClient", false);
   ```
   The store format applies only to accounts created after it is set. The script also reads Thunderbird's default **mbox** format, so an existing account works without changes.
3. **Add your school account** as IMAP and sign in through the school SSO page that opens. For Microsoft 365 the server is usually `outlook.office365.com`. You don't have to make Thunderbird your default mail app, and you can keep using your usual client.
4. **Turn on offline sync for every folder you want readable.** Account Settings → Synchronization & Storage → keep messages on this computer. For folders other than the inbox: right-click → Subscribe, then folder Properties → Synchronization → select for offline use. Then File → Offline → Download/Sync Now. A large mailbox takes a while and can use several GB of disk.
5. **Keep Thunderbird running** (add it as a login item) so the copy stays current. `status` tells you whether it is running and when the newest message landed.

## Configuration

Everything is auto-detected. Override it when needed:

| Setting | How | Default |
|---|---|---|
| Thunderbird data dir | `SCHOOL_MAIL_TB_ROOT` or config `thunderbird_root` | macOS `~/Library/Thunderbird`; Linux `~/.thunderbird` (also the snap and flatpak locations); Windows `%APPDATA%\Thunderbird` |
| Account | `--account <substring>`, `SCHOOL_MAIL_ACCOUNT`, or config `account` | the only IMAP account; run `accounts` to list them |
| Header cache | `SCHOOL_MAIL_CACHE` or config `cache_dir` | macOS `~/Library/Caches/school-mail`; Linux `~/.cache/school-mail`; Windows `%LOCALAPPDATA%\school-mail` |
| Config file | `SCHOOL_MAIL_CONFIG` | `~/.config/school-mail/config.json` (`%APPDATA%\school-mail\config.json` on Windows) |

Example config. It lives outside the repo and holds no secrets:

```json
{"account": "ImapMail/outlook.office365.com"}
```

The header cache is a SQLite file of message headers (sender, subject, date). It sits outside the repo, but it is still private data, so treat it as you treat the mailbox itself. Delete it whenever you like, and it is rebuilt on the next run.

## Caveats

- **Read-only by design.** The script cannot send, reply, move, flag or delete. For replies, the agent drafts text or opens a `mailto:` compose window, and you send it.
- **No read/unread state.** Thunderbird keeps flags in its own index files, which the script does not parse.
- **No calendar.** Calendar items don't come through IMAP as usable events.
- **Only synced folders exist.** A folder you never marked for offline use doesn't appear.
- **Mail never enters git.** Pages summarize and cite (`cite` prints a `[Source: email ..., Message-ID ...]` line). Attachments you keep go to `raw/` with a manifest entry. `scripts/leak-gate.sh` and gitleaks are a last line of defense, not a substitute.
- **Email is untrusted input.** The skill tells the agent to ignore instructions inside messages and not to fetch links unprompted.
- **First run is slow** on a big mailbox, because the header cache gets built (seconds to a minute). After that, list and search take well under a second. Big mbox folders are rescanned only when the file changes.
