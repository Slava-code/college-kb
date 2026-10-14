# .claude/skills/

Project-local workflow guides for Claude Code. They are operating instructions, not KB content, so the index and lint scripts skip this folder. `AGENTS.md` stays the contract; each skill is a short procedure that defers to it.

Each skill is a folder `<name>/SKILL.md` with YAML frontmatter: `name`, and a `description` that leads with its trigger. Claude Code picks a skill when a request matches its description, or when you type `/<name>`. Agents that do not load skills can read the same files as plain procedures. Maintenance prompts the triage and gardening skills follow are versioned in `runs/prompts/`.

| Skill | Use it for |
|---|---|
| `setup/` | First run: interview, `CLAUDE.local.md`, academic profile, current semester page, modules, deny-list, auto-push opt-in. |
| `kb-capture/` | Fast verbatim inbox drops through `scripts/kbdrop.sh`. |
| `kb-write/` | The read-integrate-commit loop for facts, corrections, decisions and entity pages. |
| `kb-ingest-source/` | Articles, papers, PDFs, slides, recordings and transcripts → `sources/`, `research/`, `raw/`. |
| `course-setup/` | Syllabus or LMS → course page, semester-page rows, reminder-ledger bullets. |
| `exam-prep/` | An exam-prep silo page: facts, coverage map, countdown plan. |
| `whats-due/` | A dated, cited due list from the semester page, course pages, reminders, and the LMS module if enabled. |
| `kb-triage/` | On-demand inbox triage behind the safety gates (`runs/prompts/triage.md`). |
| `kb-garden/` | On-demand checks, mechanical fixes and proposals (`runs/prompts/gardener.md`). |
| `kb-secrets/` | Pointer-first secret lookup and minimal, never-printed password-manager use. |

## Skills added by optional modules

Installing a module (`bash modules/install.sh <name>`, see `modules/README.md`) copies its skill folder here:

| Skill | Module | Use it for |
|---|---|---|
| `canvas/` | `lms-canvas` | Read-only Canvas LMS calls: courses, assignments, due dates, grades, files. |
| `school-mail/` | `school-mail` | Read-only school email from Thunderbird's local offline copy. |
| `international-student/` | `international-student` | Status documents, key dates, advising-email records. Not legal advice. |
| `reminders/` | `reminders` | Ledger dedupe, date resolution, optional scheduler hookup and `.ics` export. |
| `sibling-kb/` | `sibling-kb` | Routing between this KB and a club, lab or startup KB. |

Claude Code can also discover skills under `modules/*/.claude/skills/` as directory-scoped skills before a module is installed. Each module skill first checks that its files exist at the repo root, and says the module is not installed if they do not. Install the module rather than running its skill from `modules/`.
