---
name: setup
description: Use when the student runs /setup, says "set up my KB" or "personalize this", or opens a fresh copy of college-kb with no CLAUDE.local.md; first-run interview that writes CLAUDE.local.md, the academic profile, the current semester page, and opt-in modules.
---

# setup

`AGENTS.md` is canonical; this skill is the first-run procedure. Run it once per clone (re-run it on a second machine for steps 1, 3 and 9 only). Ask before every step that writes outside the repo or changes git config.

## 1. Privacy first

- Tell the student up front: **this repo must stay private.** It will hold their courses, people, applications and deadlines.
- If `git remote -v` shows a remote and `gh` is available, run `gh repo view --json visibility -q .visibility`. If it prints `PUBLIC`, stop and ask them to make it private (GitHub → Settings → General → Danger Zone) before anything else is written. A fork of a public repo cannot be made private; the fix is "Use this template" → private, or a fresh private repo.
- Never push during setup.

## 2. Hooks and tools

- `bash scripts/install-hooks.sh`. If it warns that gitleaks is missing, show the install line from `scripts/README.md` and ask before installing anything; commits are refused until it is present.
- `python3 --version` must be 3.8 or newer. Nothing else needs installing.

## 3. Interview (one short batch; every question is skippable)

Ask in a single message, then wait:

1. Name to use in pages (a first name or nickname is fine).
2. School name and its email domain; major, minor, year, expected graduation; advisor (optional).
3. Current term (`YYYY-<term>`, e.g. `2099-fall`) and the course codes they are taking.
4. Learning-management system (Canvas, Moodle, Blackboard, D2L, none) and its base URL.
5. Timezone (IANA name, e.g. `America/New_York`).
6. This machine's role (main laptop, desktop, lab machine) and whether another clone exists.
7. Where raw files should live: local `raw/` folders (default) or a folder their sync client already backs up.
8. Which optional modules to enable: list them with `ls modules/` and read each `modules/<name>/README.md` summary line (for example an LMS module, the school-mail bridge, an international-student module).
9. Auto-push after every commit? Default **no**.

Do not ask for student ID numbers, government ID numbers, passwords or tokens. If they volunteer a secret, do not write it anywhere; point them to `kb-secrets`.

## 4. CLAUDE.local.md (gitignored, this machine only)

- `cp CLAUDE.local.md.example CLAUDE.local.md`, then fill: **Host** = the exact output of `hostname`; this KB = `pwd`; raw store; optional sibling KB path; local quirks; the modules enabled on this machine and where their local config lives (for example an env file path, never its contents).
- Confirm `git check-ignore CLAUDE.local.md` prints the file name. Never copy a path from this file into a committed page.

## 5. Raw store

- Sync folder chosen: `git config kb.rawstore "<folder>"` (per-clone, not committed), then `bash scripts/link-raw.sh school` and `bash scripts/link-raw.sh career`.
- Local: run the same two `link-raw.sh` commands; remind the student that git does not back up `raw/` (see `raw/README.md`).

## 6. Pages (follow `kb-write`)

- `git pull --rebase` first if a remote exists.
- Read `school/README.md`, `school/semesters/README.md`, `schema/templates/README.md`, and the templates `schema/templates/academic-profile.md` and `schema/templates/semester.md`.
- `THRESHOLDS.md`: set `REMINDER_TIMEZONE` to their zone. Commit `schema: update thresholds-timezone`.
- `school/academic-profile.md` (`type: profile`, from `schema/templates/academic-profile.md`; the DEMO file at that path is replaced, not edited around): school, program, major/minor, year, expected graduation, advisor, LMS, each tagged `[Source: student/setup interview/YYYY-MM-DD]`. At least 3 real sentences. Commit `school: add academic-profile`.
- `school/semesters/<term>.md` (`type: semester`, from `schema/templates/semester.md`): the course list (plain course codes for now; `course-setup` turns them into links), plus any calendar dates the student gave, and the "where the real submission state lives" table with one row per course (fill what they know; `course-setup` completes it). Commit `school: add <term>`.
- `GLOSSARY.md`: append the school (with aliases such as its short name) and each course code. Plans the student mentions (a minor they are considering, transferring) get their own silo page or an inbox drop, never a glossary line or profile fact.

## 7. Modules

For each module the student chose, read `modules/<name>/README.md` and follow its install steps exactly. If it adds types, folders or scopes, edit `scripts/kb-schema.json` and the AGENTS.md scope list in the same commit, run `python3 scripts/kb-lint.py`, and commit `schema: add <name>-module`. Module credentials (an LMS token, a mail profile path) are machine-local: record only where they live, in `CLAUDE.local.md`.

## 8. Leak-gate deny-list (outside the repo)

Offer to add the student's own identifiers to `~/.config/college-kb/denylist.txt` (or `$KB_DENYLIST`): their name and nicknames, school name and email domain, their email address, this machine's hostname, other machines' hostnames. One extended regex per line; escape dots (`example\.edu`). Create the folder with `mkdir -p ~/.config/college-kb` only after they agree. Optionally put their public GitHub handle in `allowlist.txt`. These terms never go into the repo, a commit message, or a page. Explain that `scripts/leak-gate.sh` uses the list before any copy is made public.

## 9. Auto-push (only if asked)

If and only if the student said yes: `git config kb.autopush true` (needs an upstream: `git push -u origin main` once, with their go-ahead). Otherwise say it stays off and pushes happen when they ask.

## 10. DEMO content

Offer to remove the fictional examples. Find them with `grep -rl '^> DEMO — fictional example' --include='*.md' .`, plus DEMO rows in `GLOSSARY.md`, `runs/retrieval-failures.md` and `secrets/README.md`. DEMO pages that ship inside an installed module (for example `school/lms-canvas.md`) carry the same banner. Show the list; remove only what they confirm (`git rm` for whole DEMO files, edit out DEMO rows). Commit `schema: update remove-demo-content`.

## 11. Check and hand off

- `python3 scripts/kb-lint.py && python3 scripts/wikilink-check.py && python3 scripts/reminder-ledger-check.py && bash scripts/gitleaks-smoke-test.sh`.
- Reply with: what was written (paths), modules enabled, auto-push state, and next steps: run `course-setup` once per course with its syllabus; add `alias kbdrop="<this repo>/scripts/kbdrop.sh"` to their shell profile; keep the repo private.
