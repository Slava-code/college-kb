---
title: "School mail bridge"
type: note
status: active
description: "DEMO: how the agent reads Alex Example's example.edu mailbox read-only via a local Thunderbird sync"
aliases: ["school email", "school mail", "Outlook access", "Thunderbird bridge"]
updated: 2099-08-27
---

> DEMO — fictional example; delete once you add real pages.

# School mail bridge

## Compiled Truth

Example State University mail (`alex@example.edu`) is Microsoft 365. The university tenant does not allow students to consent to third-party mail apps, so the agent reads mail from **Thunderbird's local offline copy** through `scripts/school-mail.py` and the `school-mail` skill. Alex keeps reading and sending in their usual client. Thunderbird only runs in the background to sync. [Source: session, 2099-08-26]

**Setup:** Thunderbird with maildir storage (see the module README), IMAP to `outlook.office365.com` with university single sign-on. INBOX, Sent and Archive are marked for offline use. It runs as a login item. [Source: session, 2099-08-26]

**Acceptable use:** Example State's IT policy allows syncing your own mail to a personally owned device with a standard client. [Source: ESU IT acceptable-use page, read 2099-08-26]

**Limits:** read-only; no read/unread state; no calendar; folders show up only once they are marked for offline sync.

## Open Threads

- Add the "Advising" folder to offline sync so advisor threads become searchable.

## Timeline

### 2099-08-26 — Bridge set up

Connector consent was not available, so Thunderbird was installed and left to finish its first sync. `status` and `list` worked once it had. [Source: session, 2099-08-26]
