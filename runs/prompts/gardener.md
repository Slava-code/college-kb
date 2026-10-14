---
title: "Gardener prompt"
type: note
status: active
description: "Versioned on-demand prompt for KB gardening: checks, mechanical fixes, and proposals for judgment calls"
updated: 2099-01-01
---

# Gardener prompt

On-demand procedure. Run it when the student asks for maintenance or gardening (the `kb-garden` skill points here), from an agent session whose working directory is this repo's root. A natural moment is the end of a semester; nothing schedules it.

## Prompt

```text
Gardening pass for this college-kb (on demand).

Workdir: this repo root. Machine-local paths come from the gitignored CLAUDE.local.md; never copy them into committed files.

Mandatory gates, in order. Stop at the first one that fails:
1. Read CLAUDE.local.md and confirm `hostname` prints exactly its Host. If missing or mismatched, stop and ask the student.
2. If `runs/PAUSE` exists, change nothing and reply "paused".
3. Run `git status --short`; if dirty, abort and list the dirty paths.
4. If a remote exists, run `git pull --rebase`; on conflict or failure, abort and report it.
5. Read AGENTS.md, THRESHOLDS.md, INDEX.md, GLOSSARY.md, and runs/README.md.
6. Diff cap: estimate planned changes against DIFF_CAP_FILES and DIFF_CAP_LINES before editing, and re-check with `git diff --numstat` plus `git status --short` before each commit. Over either cap: do not commit; report `diff cap hit` and split the work.

Checks (run all, record results):
- python3 scripts/rebuild-indexes.py
- python3 scripts/kb-lint.py
- python3 scripts/wikilink-check.py
- python3 scripts/reminder-ledger-check.py
- bash scripts/gitleaks-smoke-test.sh

Review:
- runs/retrieval-failures.md: unresolved misses; more than RETRIEVAL_FAILURES_PER_MONTH in a month means propose search tooling or new pages.
- `status: active` pages not updated in STALE_ACTIVE_DAYS.
- Semesters that ended more than ARCHIVE_STALE_MONTHS ago, and their exam-prep and silo pages: propose archiving.
- Reminder bullets whose date has passed but are still proposed-only or scheduled: list them for the student to close (completed or cancelled); never guess which.
- Names used on pages but missing from GLOSSARY.md; aliases that collide.
- Pages over OVERSIZED_LINES (propose a split) or under MIN_LINES (propose a merge or enrichment).
- INDEX.md plus GLOSSARY.md over INDEX_GLOSSARY_BUDGET_LINES: propose per-folder indexes.
- Course pages missing an AI-use and collaboration policy line or a syllabus source link.
- DEMO files (first line "> DEMO — fictional example") still present beside real pages: propose removal.
- Plans that leaked into entity pages, GLOSSARY.md, or description: lines: propose moving them to a silo page.

Fix directly (mechanical only): stale or overlong description: lines, glossary appends, obviously broken wikilinks with one clear target, missing resolution stamps where the resolver page is explicit. Every page edit updates `updated:` and `description:`.

Propose, never do: archiving, splitting, merging, superseding, deleting, or rewriting a decision. Write proposals to runs/gardener/YYYY-MM-DD-gardener.md (type: report; see runs/gardener/README.md; checks run and results, fixes made, proposals with reasons, questions for the student; at most NEEDS_OWNER_MAX_QUESTIONS).

Out of scope: processing inbox drops (that is triage), opening raw/ or secrets, unlocking a password manager, fetching the web.

Commit small, by explicit path: `gardener: fix <summary> YYYY-MM-DD` for fixes, and the report in the same or a separate `gardener:` commit. Do not push unless the student asks; the post-commit hook pushes only when `git config kb.autopush true` is set.

Final reply: checks and results, fixes committed (SHAs), proposals written, blockers.
```
