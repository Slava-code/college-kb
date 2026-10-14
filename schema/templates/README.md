# schema/templates/

Copy-ready page shapes, one or more per `type:` in `scripts/kb-schema.json`. Copy the template, rename it to the folder's naming rule, replace every `<placeholder>`, and delete guidance comments (`<!-- ... -->`) you do not need. Templates are excluded from lint, indexing and link checks, so their placeholder wikilinks never fail a check; the page you make from one is checked like any other.

Each live DEMO page in the content folders is a filled-in example of one of these templates (fictional student Alex Example at Example State University). Read the DEMO page next to a template when the template alone is unclear.

| Template | `type:` | Folder and file name | DEMO example |
|---|---|---|---|
| `course.md` | `course` | `school/courses/<code-slug>.md` | `school/courses/demo-101.md`, dropped: `school/courses/math-2xx-example.md` |
| `semester.md` | `semester` | `school/semesters/YYYY-<term>.md` | `school/semesters/2099-fall.md` |
| `exam-prep.md` | `exam-prep` | `school/courses/<code-slug>-<exam>-prep.md` | `school/courses/demo-101-midterm-1-prep.md` |
| `course-notes.md` | `course-notes` | `school/courses/<code-slug>-notes.md` | `school/courses/demo-101-notes.md` |
| `academic-profile.md` | `profile` | `school/academic-profile.md` | `school/academic-profile.md` |
| `application-profile.md` | `profile` | `career/application-profile.md` | `career/application-profile.md` |
| `application-log.md` | `application-log` | `career/application-log-<cycle>.md` | `career/application-log-2100-summer.md` |
| `resume-pointer.md` | `note` | `career/resume.md` | `career/resume.md` |
| `lab-prospects.md` | `note` | `career/research-lab-prospects.md` | `career/research-lab-prospects.md` |
| `decision.md` | `decision` | `decisions/YYYY-MM-DD-<slug>.md` | `decisions/2099-09-04-drop-math-2xx-example.md` |
| `source.md` | `source` | `sources/YYYY-MM-DD-<slug>.md` | `sources/2099-08-25-demo-101-syllabus.md` |
| `research-memo.md` | `research` | `research/YYYY-MM-DD-<slug>.md`, or one part of a run folder | `research/2099-09-26-summer-research-programs/synthesis.md` |
| `research-run-readme.md` | (freeform README) | `research/YYYY-MM-DD-<slug>/README.md` | `research/2099-09-26-summer-research-programs/README.md` |
| `project.md` | `project` | `projects/<slug>.md` | (see the hackathon DEMO) |
| `hackathon.md` | `project` | `projects/YYYY-<event-slug>.md` | `projects/2099-example-state-hack.md` |
| `person.md` | `person` | `people/<name-slug>.md` | `people/prof-example.md` |
| `brainstorm.md` | `brainstorm` | `brainstorms/YYYY-MM-DD-<slug>.md` | `brainstorms/2099-09-28-notes-swap-club.md` |
| `list.md` | `list` | `lists/YYYY-wNN-<slug>.md` | `lists/2099-w41-midterm-week.md` |
| `plan.md` | `plan` | next to what it plans (`school/`, `career/`, `projects/`), or a `trips/` module folder | `school/2100-spring-study-abroad-exploration.md` |
| `inbox-drop.md` | `drop` | `inbox/YYYY-MM-DD-HHMM-<slug>.md` (made by `scripts/kbdrop.sh`) | `inbox/2099-10-01-1525-prof-example-office-hours-moving.md` |
| `triage-report.md` | `report` | `runs/triage/YYYY-MM-DD-HHMM-triage.md` | `runs/triage/2099-09-29-0800-triage.md` |
| `reminder-ledger.md` | `reminder` | `reminders/YYYY.md` | `reminders/2099.md` |
| `note.md` | `note` | any folder whose README allows `note` | `career/resume.md` |

## Shared conventions

- **Required frontmatter** on every page outside `inbox/` and `runs/`: `title`, `type`, `status`, `description`, `updated` (see `required_frontmatter` in `scripts/kb-schema.json`). `aliases:` is optional but expected on entity pages (courses, people, projects).
- **`status:` values:** `active` (current), `proposed` (idea or plan, not started), `resolved` (finished, dropped or decided, kept as a record), `superseded` (replaced; links to the replacement), `archived` (moved under `archive/`).
- **`description:`** is one line of at most 120 characters. It feeds `INDEX.md`, so write what a future question would search for. Never put IDs, grades, GPA, or secret-adjacent values in it; keep those in the page body with a `[Source: ...]`.
- **Body shape:** `## Compiled Truth` (rewritten as facts change), `## Open Threads`, `## See Also`, then `---` and `## Timeline` (newest first, append-only, never edited). Templates that differ say so.
- **Citations:** facts that can rot carry `[Source: who/context/YYYY-MM-DD]`. Transcript-backed claims cite `[T:NN](<relative path to raw transcript>#LNN)`.
- **Resolution stamp:** `**Resolved YYYY-MM-DD → [[folder/page]]:** one line`, placed on the open thread it settles.
