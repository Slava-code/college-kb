# Module: reminders

Students run on deadlines: problem sets, exams, add/drop dates, scholarship windows, application deadlines, renewal chores. This module turns the core `reminders/` ledger into a working loop. The agent writes every dated item it notices into the ledger, and when you ask, it creates a real reminder in a scheduler you already use and records that scheduler's ID next to the item.

The ledger is **not** a task manager and nothing reads it on a timer. It exists so any agent can answer "did we already schedule that?" and "why is this on my calendar?"

## What the core already has

The core repo ships `reminders/README.md` (the `status:` / `scheduler_ref:` vocabulary), a DEMO ledger `reminders/2099.md` with one bullet per status, the template `schema/templates/reminder-ledger.md`, and `scripts/reminder-ledger-check.py`, which validates every bullet in the pre-commit hook. `THRESHOLDS.md` holds the `REMINDER_*` defaults: time zone, default morning time, lead time, and what "this weekend" means.

## What this module adds

| File (in this module) | Installs to | Purpose |
|---|---|---|
| `.claude/skills/reminders/SKILL.md` | `.claude/skills/reminders/SKILL.md` | Agent procedure: dedupe, resolve dates, ledger first, schedule only on request, record `scheduler_ref` |
| `scripts/reminders-ics.py` | `scripts/reminders-ics.py` | Exports ledger bullets to an `.ics` file that any calendar app can import (standard library only) |

## Install

1. `bash modules/install.sh reminders` (add `--dry-run` to preview).
2. Schema: none needed. `type: reminder` and the `reminders` scope are already in the core schema.
3. Set `REMINDER_TIMEZONE` in `THRESHOLDS.md` to your IANA zone, such as `America/New_York` or `Europe/Berlin`.
4. Check that `python3 scripts/reminder-ledger-check.py` passes, then commit as `schema: add reminders-module`.

## Bullet format

```text
- YYYY-MM-DD [HH:MM [Zone]] · <title> · status: <status> · scheduler_ref: <ref> · source: <page or citation>
```

`Zone` is an IANA name such as `Etc/UTC` or `America/New_York`. Without one, the time is read in `REMINDER_TIMEZONE`. A bullet that has no concrete date yet ("November 2099", "Fridays") must be `needs-clarification`.

| status | scheduler_ref | Meaning |
|---|---|---|
| `proposed-only` | `none` | Recorded, not scheduled anywhere (the default) |
| `needs-clarification` | `none`, plus `reason:` | Ambiguous date or recurrence; the agent asks |
| `scheduled` | a real ref | A reminder exists in some scheduler |
| `sent` / `completed` / `cancelled` | keep the ref | Closed out |

## Scheduler hookups (pick any, or none)

Nothing is wired by default. The `scheduler_ref` prefix records which hookup was used, so a later session knows where to look.

| Hookup | How | `scheduler_ref` |
|---|---|---|
| **None** | The ledger only; you check it, or ask "what's coming up?" | `none` |
| **Calendar file (.ics)** | `python3 scripts/reminders-ics.py -o ~/calendars/kb-reminders.ics` exports every `scheduled` bullet with an `ics:` ref. Open or import the file in Apple Calendar, Google Calendar, Outlook or Thunderbird. Each event has a stable UID, so re-importing updates it. Put the file somewhere your calendar can subscribe to if you want automatic refresh. Keep it out of git. | `ics:<uid>` |
| **Agent scheduled tasks** | If your agent host has scheduled tasks or routines (Claude Code's `/schedule`, for example), the agent creates one and records its ID | `routine:<id>` |
| **Calendar connector** | If your agent has a permitted calendar integration, the agent creates the event and records the event ID | `<calendar>:<event id>` |
| **OS scheduler** | cron or systemd timers (Linux), launchd (macOS), Task Scheduler (Windows), firing a desktop notification | `cron:<label>`, `launchd:<label>`, `task:<name>` |
| **By hand** | You set a phone reminder yourself and tell the agent | `manual:<where>` |

Scheduling always needs your request in the current session. Triage and other maintenance runs only *propose*.

## Caveats

- **Time zones:** `reminders-ics.py` converts to UTC using Python's `zoneinfo`. On systems without a time-zone database (some Windows installs), it falls back to floating local times and prints a warning.
- **Recurring items** need an explicit start, end and interval from you. The agent will not schedule "every week" indefinitely.
- **Exporting to a calendar copies data out of the KB.** Titles land in your calendar provider, so keep them short and leave out sensitive details.
