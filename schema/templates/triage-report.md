---
title: "Triage run — YYYY-MM-DD HH:MM"
type: report
status: resolved
description: "On-demand inbox triage: <n> drops read, <n> pages changed, <n> reminders proposed"
updated: YYYY-MM-DD
---

# Triage run — YYYY-MM-DD HH:MM

<!-- One report per on-demand run, in runs/triage/YYYY-MM-DD-HHMM-triage.md.
     Summarize; do not copy sensitive drop content into the report. -->

## Gates

- `runs/PAUSE`: <absent / present → stopped>
- `git status --short`: <clean / dirty → aborted>
- `git pull --rebase`: <up to date / pulled n commits / no remote>
- Diff cap: planned <n> files, <n> lines (caps `DIFF_CAP_FILES` / `DIFF_CAP_LINES`)

## Drops read (<n>)

| Drop | Routed to | Action |
|---|---|---|
| `inbox/<name>.md` | [[<page>]] | <updated §..., created page, reminder proposed> |

## Pages changed

- [[<page>]] — <what changed>

## Reminders

- Proposed-only: <n> (see [[reminders/YYYY]])
- Needs clarification: <n>

## Drops removed

- `inbox/<name>.md` (content now in [[<page>]])

## Questions for you (max `NEEDS_OWNER_MAX_QUESTIONS`)

1. <...>

## Skipped

- `inbox/<name>.md` — <reason>

## Checks

- kb-lint, wikilink-check, reminder-ledger-check: <results>
- Commit: `triage: process inbox batch YYYY-MM-DD`
