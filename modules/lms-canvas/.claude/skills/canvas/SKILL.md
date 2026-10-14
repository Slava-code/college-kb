---
name: canvas
description: Use when the student asks about anything on Canvas (their LMS) — what's due, an assignment's details or rubric, grades, submissions, syllabus, modules, announcements, files, quizzes — or pastes a Canvas URL. Reads the Canvas REST API from the shell via scripts/canvas.sh; browser only as a fallback. Read-only; never submits or posts.
---

# canvas — read Canvas through the API

`AGENTS.md` is canonical; this skill only adds the Canvas procedure. Module docs: `modules/lms-canvas/README.md`.

## 0. Preconditions

- If `scripts/canvas.sh` is missing at the repo root, the module is not installed: say so and point to `modules/lms-canvas/README.md`. Stop.
- Run `scripts/canvas.sh whoami` once per session. On 401, tell the student the token is missing, expired, revoked, or still **pending activation** (Canvas → Account → Settings → Approved Integrations; an admin-issued token often needs a click on "activate" first). Do not try to fix the token yourself.
- Never print, echo, `cat`, or `grep` the env file or `$CANVAS_TOKEN`. Do not put the token on any command line.

## 1. Routing: API first, browser last

Use the API for: course lists, syllabi, modules, assignments (description, rubric, due date, points, submission type), the student's own submissions and grades, quiz metadata and their quiz submissions, announcements, discussions, pages, files, calendar events, to-dos.

Use a browser only when (a) the token is unavailable and the student asks you to use their logged-in browser, (b) the content exists only in rendered UI — LTI/external tools (homework platforms, video players, proctoring, clickers), embedded media, iframes from another host — or (c) a UI-only control is needed, or the student asks to see the page. With a logged-in browser, call the same `/api/v1/...` endpoints from the page rather than scraping HTML. Subagents never drive a browser.

## 2. Translate a Canvas URL

Reuse the IDs in the path: `https://<canvas>/courses/123/assignments/456` → `courses/123/assignments/456`. `scripts/canvas.sh url <url>` does this offline and handles the common special cases (course home, announcements, grades).

## 3. Endpoints (relative to `/api/v1/`)

| Endpoint | Gives |
|---|---|
| `users/self` | Who the token belongs to (sanity check) |
| `courses?enrollment_state=active&include[]=term` | Current courses with term names; filter on `term.name` for one semester |
| `courses/{c}?include[]=syllabus_body` | Syllabus HTML (often empty; the real syllabus is frequently a file in modules) |
| `courses/{c}/assignments?include[]=submission&order_by=due_at` | Assignments with due dates, points, and the student's submission state |
| `courses/{c}/assignments/{a}?include[]=submission` | One assignment: description HTML, rubric, submission types, lock dates |
| `courses/{c}/assignment_groups` | Grading categories and their weights |
| `courses/{c}/modules?include[]=items` | Module tree, including file `content_id`s |
| `courses/{c}/discussion_topics?only_announcements=true` | Announcements |
| `courses/{c}/pages/{slug}` | A wiki page's body |
| `courses/{c}/quizzes` / `courses/{c}/quizzes/{q}/submissions` | Quiz metadata / the student's quiz attempts |
| `courses/{c}/enrollments?user_id=self` | Which section the student is in, current score where visible |
| `users/self/todo` / `users/self/upcoming_events` | Canvas's own to-do list and calendar items |
| `files/{f}` → `scripts/canvas.sh download {f} <dest>` | File metadata / download |

If `courses/{c}/files` returns 403, the course hides its Files tab; take file IDs from `modules` or from links in assignment and announcement HTML.

Write large responses to the session scratchpad (`scripts/canvas.sh get <path> -o <scratchpad>/x.json`) and extract what you need; do not dump big JSON into chat.

## 4. What's-due sweep

A general "what's due" question belongs to the core `whats-due` skill: it merges the KB, the reminder ledger and the LMS. This command is its LMS step, and also answers a Canvas-only question directly:

1. `python3 scripts/canvas-due.py --days 14` (add `--term "<term name>"` to limit to one semester, `--undated` for items with no due date, `--json` for merging).
2. It prints one row per assignment with its due time in local time, the submission state, and `OVERDUE` or `missing` flags. Cite Canvas for each row (`[Source: Canvas API, <today>]`).
3. If Canvas and the syllabus or course page disagree on a date, report **both** and do not pick one (AGENTS.md §Write). With the student's OK, record the discrepancy or the new date on the course page Timeline with a `[Source: ...]`.
4. If the student wants reminders, hand off to the reminders skill if it is installed. Do not schedule anything unasked.

## 5. Recording into the KB

- Syllabus files and handouts the student wants kept go to `raw/school/` (date-prefixed name, `raw/manifest.jsonl` entry), cited from the course page.
- Course facts from Canvas (grading weights, exam dates, AI-use policy text) go into the course page Compiled Truth with `[Source: Canvas <what>, YYYY-MM-DD]`.
- Never copy grades of other students, roster data, or classmates' discussion posts into the KB.

## 6. Never

- Never submit assignments, take quizzes, post discussion replies, send Canvas messages, or change settings. `scripts/canvas.sh` is GET-only by design. If the student asks for help with a submission, draft it for them to submit; if they explicitly want an API write, show the exact request and get a yes first.
- Never use Canvas access to do graded work against the course's AI policy (recorded on the course page).
