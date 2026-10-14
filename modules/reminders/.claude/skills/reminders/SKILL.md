---
name: reminders
description: Use when KB content or the conversation implies a dated task, deadline, exam, appointment, or read-later item, or the student asks to be reminded / to schedule something; records it in the reminders/YYYY.md ledger and, only when asked, schedules it (calendar .ics, scheduled routine, OS scheduler) and records the scheduler_ref.
---

# reminders — the ledger first, a scheduler only on request

`AGENTS.md` is canonical. Ledger format: `reminders/README.md`. Module docs: `modules/reminders/README.md`.

1. **Read `reminders/YYYY.md` first** to avoid duplicates. Create the year file from `schema/templates/reminder-ledger.md` if it doesn't exist (`type: reminder`). Keep the section layout the template uses (proposed, needs clarification, scheduled, done/cancelled).
2. **Write one bullet per reminder:**
   `- YYYY-MM-DD [HH:MM [Zone]] · <title> · status: <status> · scheduler_ref: <ref> · source: <page or [Source]>`
   The default is `status: proposed-only · scheduler_ref: none`: recorded, nothing scheduled.
3. **Fill in the time from `THRESHOLDS.md` defaults:**
   - Exact date but no time: use `REMINDER_DEFAULT_MORNING`.
   - Timed event: remind `REMINDER_DEFAULT_BEFORE_MINUTES` before it, unless the student said otherwise.
   - All times are in `REMINDER_TIMEZONE`. If it is still the placeholder `Etc/UTC` and the student is clearly elsewhere, ask once and suggest they set it.
4. **Relative dates** ("tomorrow", "next Tuesday", "this weekend") are allowed only when they anchor unambiguously to the capture or session timestamp (`REMINDER_RELATIVE_ANCHOR`). Use `WEEKEND_REFERENCE_DEFAULT` for "this weekend", and write the concrete date into the bullet.
5. **Ambiguity:** if a phrase could mean more than one date, a default is missing, or a recurrence has no clear start and end ("every two weeks"), record `status: needs-clarification · scheduler_ref: none · reason: <why>` and ask. Never schedule a recurrence forever by inference.
6. **Schedule only when the student asks.** Pick the hookup they use (see `modules/reminders/README.md`), create the reminder there, then set `status: scheduled` and record a real `scheduler_ref`:
   - `.ics` export: get a ref with `python3 scripts/reminders-ics.py --uid "<date> · <title>"`, write the bullet, then run `python3 scripts/reminders-ics.py -o <path outside the repo>` and tell the student to import or open the file. Re-importing updates the events instead of duplicating them.
   - Agent scheduled task or routine: `routine:<id>`. Calendar connector: `<calendar>:<event id>`. OS scheduler: `cron:<label>` / `launchd:<label>` / `task:<name>`. A reminder the student set by hand: `manual:<where>`.
7. **Closing:** when a reminder fires or the task is done, move it to the done/cancelled section with `status: sent | completed | cancelled`. Keep the `scheduler_ref`, and delete the event in the external scheduler if the student asks.
8. **Read-later items:** keep the source or list item first (`lists/` or `sources/`), then add the reminder. Do not claim facts from a source nobody has fetched.
9. **Urgent:** if something is due within 48 hours, say so directly in your reply, not only in the ledger.
10. **Dry runs and triage seeding:** no real scheduling side effects. Bullets stay `proposed-only` or `needs-clarification`.

Run `python3 scripts/reminder-ledger-check.py` (the pre-commit hook does too) and commit with scope `reminders`, e.g. `reminders: schedule demo-101-midterm-review-2099-10-06`.
