---
name: exam-prep
description: Use when the student says "help me prep for the DEMO 101 midterm", "make a study plan for exam 2", "what's on the final", or asks for an exam countdown; builds an exam-prep silo page from the course page, notes, and materials.
---

# exam-prep

`AGENTS.md` is canonical; this is the procedure. Write with the `kb-write` rules. The prep page is a silo next to the course page: exam-specific planning never gets folded into the course page beyond one link.

1. **Policy first.** Read the course page's AI-use and collaboration policy and follow it. This skill organizes facts, coverage, and a schedule from the student's own materials. It does not write answers to graded or take-home work, and it does not produce exam content the policy forbids.
2. **Gate and orient.** `CLAUDE.local.md` hostname match; `git pull --rebase` on the first write when a remote exists. Read `school/courses/README.md`, the course page, its `course-notes` pages, linked sources, and `schema/templates/exam-prep.md` (DEMO: `school/courses/demo-101-midterm-1-prep.md`). Check whether `school/courses/<course-slug>-<exam>-prep.md` (e.g. `demo-101-midterm-1-prep`, `demo-101-final-prep`) already exists; update it rather than starting a second one.
3. **Gather (read-only).**
   - Exam facts from the course page: date, time, room, length, format, allowed materials (formula sheet, calculator), coverage, weight.
   - If the LMS module is installed and configured on this machine (`modules/lms-canvas/README.md`; `python3 scripts/canvas-due.py --json` for upcoming items): the exam's assignment entry and recent announcements, to confirm date, room, and coverage.
   - The local course workspace named in `CLAUDE.local.md`, if any: past exams, practice sets, review sheets. Do not copy them into the repo; cite them by name, or file one in `raw/school/` with a manifest entry if the student wants it kept.
   - If you fan out to subagents for anything, they read local files and use web search/fetch only; no browser driving.
4. **Write `school/courses/<course-slug>-<exam>-prep.md`** from the template (`type: exam-prep`, `status: active`):
   - **Exam facts**: each with `[Source: ...]`; conflicts recorded side by side.
   - **Coverage map**: topic → lectures, readings, notes pages (wikilinks), and practice problems.
   - **Past-exam pattern** (if past exams exist): points or question count per topic, recurring question types.
   - **Formula sheet plan** (only if one is allowed): what goes on it, size limit.
   - **Countdown plan**: concrete dated study blocks from today to the exam in `REMINDER_TIMEZONE`, weakest topics first, with a final review day and a buffer.
   - **Questions for office hours**: open items to ask the instructor or TA.
   - **Timeline**: `- YYYY-MM-DD — prep page created` and later dated updates.
5. **Link and remind.** Add one line to the course page's Compiled Truth linking the prep page. Add the exam (and, if the student wants, study blocks) to `reminders/YYYY.md` as `status: proposed-only` · `scheduler_ref: none` unless they ask for real reminders.
6. **Check and commit.** `python3 scripts/kb-lint.py && python3 scripts/wikilink-check.py && python3 scripts/reminder-ledger-check.py`; commit `school: add <course-slug>-<exam>-prep` (and `reminders: schedule ...` or `reminders: record ...` separately). Push only if asked or `kb.autopush` is on.
7. **After the exam** (when the student reports it): add a Timeline line (how it went, score when known, with source), set `status: resolved` (the allowed statuses are in `schema/templates/README.md`), and record lessons for the next exam. The page stays; gardening may propose archiving it at term end.
