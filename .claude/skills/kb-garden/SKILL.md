---
name: kb-garden
description: Use when the student asks for KB maintenance, gardening, a lint or link cleanup, "tidy up the KB", or an end-of-semester cleanup; on demand only, never scheduled. Runs the checks, makes mechanical fixes, and proposes the rest.
---

# kb-garden

`AGENTS.md` is canonical; this is only a thin task pointer. The full procedure, with every safety gate, is `runs/prompts/gardener.md`. Read it and follow it exactly; it wins over this summary.

1. Gates first: `CLAUDE.local.md` hostname match; `runs/PAUSE` absent; clean `git status --short`; `git pull --rebase` (when a remote exists); diff caps from `THRESHOLDS.md`.
2. Run `scripts/rebuild-indexes.py`, `scripts/kb-lint.py`, `scripts/wikilink-check.py`, `scripts/reminder-ledger-check.py`, and `scripts/gitleaks-smoke-test.sh`.
3. Review: `runs/retrieval-failures.md`, stale `status: active` pages (`STALE_ACTIVE_DAYS`), finished semesters (`ARCHIVE_STALE_MONTHS`), past-date reminder bullets still open, missing glossary aliases, oversized or tiny pages (`OVERSIZED_LINES`, `MIN_LINES`), DEMO files left beside real pages.
4. Fix mechanical things directly (descriptions, glossary appends, obvious broken links), each edit updating `updated:` and `description:`.
5. Judgment calls (archive, split, merge, supersede) go as proposals in `runs/gardener/YYYY-MM-DD-gardener.md` (`type: report`; see `runs/gardener/README.md`). Never delete pages, process the inbox, open `raw/`, or rewrite decisions.
6. Keep commits small: `gardener: fix <summary> YYYY-MM-DD`. Push only if asked or `kb.autopush` is on.
