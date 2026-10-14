# school/

Everything about being enrolled: courses, semesters, degree requirements, advising, and school admin.

- Durable profile and admin pages sit at the top level: `academic-profile.md` (`type: profile`: major, minors, expected graduation, advisor, degree audit), `degree-requirements.md` if the audit needs its own page.
- One page per term under `semesters/` and one page per class under `courses/` (see their READMEs).
- Exam prep and lecture notes for a course sit next to its course page (`type: exam-prep`, `type: course-notes`), named `<course-slug>-<topic>.md`.
- In-flight planning (a study-abroad idea, a possible course swap, a project idea for a course) gets its own silo page (`type: plan`), never folded into the course, semester or profile page (AGENTS.md §Write). Those pages link to the silo; they never state the plan as fact.
- Promote a course to its own folder (`courses/<course-slug>/`) only when one page stops being enough.

## Identifiers and grades

Student ID, GPA and grades may live in the body of `academic-profile.md`, with a source. They never go in a `description:` line, because descriptions are copied into `INDEX.md`, which every agent reads first.

## Course workspace convention

Keep bulky working files (downloaded lecture slides, past exams, your own problem-set drafts, project code) in a **course workspace** folder outside the KB, for example `~/School/<course-slug>/`. Record the workspace root once in your gitignored `CLAUDE.local.md`, and on course pages refer to files relative to it (`<workspace>/demo-101/past-exams/`), never by absolute path. Originals you cite as evidence (a syllabus PDF, the textbook, a transcript) go in `raw/school/` with a `manifest.jsonl` entry instead.

## Templates and DEMO pages

Templates: `schema/templates/course.md`, `semester.md`, `exam-prep.md`, `course-notes.md`, `academic-profile.md`, `plan.md`. DEMO pages for the fictional student Alex Example: `academic-profile.md`, `2100-spring-study-abroad-exploration.md`, `semesters/2099-fall.md`, `courses/demo-101*.md`, `courses/math-2xx-example.md`. Delete them once you add real pages.

Allowed types: `course`, `semester`, `exam-prep`, `course-notes`, `profile`, `plan`, `note` (see `scripts/kb-schema.json`). Commit scope: `school`.
