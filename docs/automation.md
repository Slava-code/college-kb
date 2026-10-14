# Automation

college-kb ships with **no scheduled jobs**. Inbox triage, gardening and reminder review run when you ask for them in an agent session:

| You say | Skill | Prompt it follows | Report |
|---|---|---|---|
| "process my inbox", "triage" | `kb-triage` | `runs/prompts/triage.md` | `runs/triage/YYYY-MM-DD-HHMM-triage.md` |
| "tidy up the KB", "garden", "end-of-term cleanup" | `kb-garden` | `runs/prompts/gardener.md` | `runs/gardener/YYYY-MM-DD-gardener.md` |
| "what's due" | `whats-due` | the skill itself (read-only unless you confirm an addition) | none |

## Why on demand

- You see every diff in the session that made it, so a wrong date or a bad merge is caught right away.
- Nothing runs against your notes while your laptop is closed, on battery, or mid-edit.
- Capture is already instant (`kbdrop.sh`), so a daily triage habit costs one sentence: "process my inbox".

A reasonable rhythm: triage once a day or whenever the inbox has a handful of drops; garden at the end of each week and each term.

## The safety gates (always on)

Every maintenance run, however it is started, checks these before reading or writing (AGENTS.md §Growth):

1. `runs/PAUSE` exists → stop and report "paused".
2. `git status --short` is dirty → abort, so a run never commits your half-finished edits.
3. `git pull --rebase` first when a remote exists; abort on conflict.
4. Planned or actual changes exceed `DIFF_CAP_FILES` or `DIFF_CAP_LINES` (`THRESHOLDS.md`) → abort without committing.

## If you want a schedule anyway

That is your call, and you set it up yourself; nothing in this repo installs one. Options, from least to most hands-off:

- **A calendar reminder to yourself** ("process KB inbox", daily). Still on demand, just prompted.
- **Your agent's own scheduling feature**, if it has one, running the same prompt text from `runs/prompts/`.
- **An OS scheduler** (`launchd` on macOS, `cron` or a systemd timer on Linux, Task Scheduler on Windows) that starts your agent non-interactively at the repo root with the prompt from `runs/prompts/triage.md`.

If you schedule anything:

- Start with a dry run that writes only the report, and read a week of reports before allowing writes.
- Keep the gates. Lower `DIFF_CAP_FILES` / `DIFF_CAP_LINES` for unattended runs.
- Leave `kb.autopush` off at first, so a bad run never leaves the machine.
- Point the scheduler at the prompt file in `runs/prompts/` rather than pasting the prompt somewhere else, so changes stay versioned and reviewable. If you change the prompt, commit it (`runs: update triage-prompt`).
- Do not give a scheduled job access to your password manager. Jobs must not depend on an unlocked vault.
- Remember `touch runs/PAUSE` stops it instantly.

## Reminders

The core ledger (`reminders/YYYY.md`) records reminders as `status: proposed-only` · `scheduler_ref: none` unless you ask for a real one. The optional [reminders module](../modules/reminders/README.md) adds an `.ics` export and notes on hooking the ledger to a calendar or scheduler you already use; whatever you connect, its id goes in `scheduler_ref:` so the ledger stays the record.
