# reminders/

Ledger of proposed and scheduled reminders, one file per year (`YYYY.md`, `type: reminder`), for dedupe and explainability. This is not a task manager and nothing reads it on a schedule: agents update it on demand, during triage or when a dated item comes up in a session.

Every bullet carries `status:` and `scheduler_ref:` (validated by `scripts/reminder-ledger-check.py`):

- `status: proposed-only` · `scheduler_ref: none` — the default: recorded, not scheduled anywhere.
- `status: needs-clarification` · `scheduler_ref: none` · `reason: ...` — ambiguous recurrence or relative dates.
- `status: scheduled` · `scheduler_ref: <id>` — only when the student asked for a real reminder; record the ID of whatever created it (calendar event, scheduled routine, phone reminder).
- `status: sent | completed | cancelled` — closed out.

Template: `schema/templates/reminder-ledger.md`. DEMO: `2099.md`, with one bullet for each status.

Times use `REMINDER_*` defaults from `THRESHOLDS.md`. Commit scope: `reminders`.
