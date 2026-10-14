# Glossary — entities and vocabulary
<!-- Gardener-owned. In-session agents may APPEND entries; only a gardener run restructures. -->

Aliases let an agent resolve "Prof. E's class" or "the stats course" to the right page.
Entry format: `- **Canonical name** (aliases: a, b, c) — one-line gloss → [[folder/page]]`.
Keep in-flight plans out of this file (AGENTS.md §Write); link to the plan's own page instead.
Rows marked DEMO are fictional examples; delete them once you add real entries.

## People

- **Prof. Example** (aliases: Professor Example, Dr. Example, Prof. E) — DEMO: fictional instructor of DEMO 101 and PI of the Example Systems Lab → [[people/prof-example]]
- **TA Sample** (aliases: Sample, the DEMO 101 TA) — DEMO: fictional teaching assistant for DEMO 101 DIS 312 → [[school/courses/demo-101]]
- **Dr. Demo Advisor** (aliases: my advisor, the advisor) — DEMO: fictional Example Studies academic advisor → [[school/academic-profile]]
- **Dr. Placeholder** (aliases: Placeholder) — DEMO: fictional instructor of the dropped MATH 2XX-EXAMPLE → [[school/courses/math-2xx-example]]

## Courses

- **DEMO 101 — Introduction to Examples** (aliases: DEMO101, Demo 101, SAMPLE 101, intro examples, the demo course, 101) — DEMO: fictional fall 2099 course used to show the course-page pattern → [[school/courses/demo-101]]
- **MATH 2XX-EXAMPLE — Example Linear Structures** (aliases: MATH 2XX, MATH2XX, linear structures, the math course) — DEMO: fictional course dropped 2099-09-04; shows a dropped course kept as `status: resolved` → [[school/courses/math-2xx-example]]

## Things (tools, clubs, projects)

- **Example State University** (aliases: Example State, ESU, example.edu) — DEMO: the fictional school of the DEMO persona Alex Example → [[school/academic-profile]]
- **StudyBuddy-Example** (aliases: StudyBuddy, Example State Hack project, ESH 2099) — DEMO: fictional hackathon project, an office-hours queue app → [[projects/2099-example-state-hack]]
- **Example Systems Lab** (aliases: Prof. Example's lab) — DEMO: fictional research lab Alex might join → [[career/research-lab-prospects]]

## Vocabulary

- **Compiled Truth** — the rewritten, current-state section of a page.
- **Timeline** — the dated, append-only history section of a page; never edited after the fact.
- **Drop** — a verbatim capture file in `inbox/`, absorbed later by triage.
- **Resolution stamp** — `**Resolved YYYY-MM-DD → [[page]]:** one line`, added where an open thread gets settled.
- **Silo page** — a separate page for a plan or exploration, so abandoned plans never leak into entity pages.
- **Record of truth** — the system that actually holds a course's submission state (the LMS, Gradescope, a course git server, a paper sign-off). The semester page records it per course, so a "what's due" sweep checks the right place.
