---
name: kb-triage
description: Use when the student asks to triage, process, file, or empty the inbox ("process my drops", "clean up the inbox"); on demand only, never scheduled. Batch-absorbs inbox/ drops into pages, lists, and reminder ledgers behind safety gates.
---

# kb-triage

`AGENTS.md` is canonical; this is only a thin task pointer. The full procedure, with every safety gate, is `runs/prompts/triage.md`. Read it and follow it exactly; it wins over this summary.

1. Gates first, before reading any drop: `CLAUDE.local.md` hostname match; `runs/PAUSE` absent; `git status --short` clean; `git pull --rebase` (when a remote exists) succeeds; planned changes within `DIFF_CAP_FILES` / `DIFF_CAP_LINES` from `THRESHOLDS.md`.
2. Read the drops as one batch (oldest first, at most `TRIAGE_MAX_DROPS_PER_RUN`) and cluster related ones before writing anything.
3. A cluster may produce any number of actions: page updates (`kb-write` rules), source or research pages (`kb-ingest-source`), list items, raw artifacts, reminder-ledger bullets, or a question for the student. Do not force one action per drop.
4. Reminders are recorded as `status: proposed-only` · `scheduler_ref: none` unless the student asks for a real one in this session (`reminders/README.md`).
5. Write a run report at `runs/triage/YYYY-MM-DD-HHMM-triage.md` (`type: report`, from `schema/templates/triage-report.md`) every run, even when the inbox is empty.
6. Remove a drop only after its content is committed elsewhere. Leave blocked drops and say why.
7. Run the checks, re-check the diff cap, commit `triage: process inbox batch YYYY-MM-DD`. Push only if asked or `kb.autopush` is on.
8. Reply briefly: drops processed, pages changed, reminders proposed, questions (at most `NEEDS_OWNER_MAX_QUESTIONS`), commit SHA or "no commit".
