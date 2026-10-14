# school/courses/

One page per class, `type: course`, named by a lowercase slug of the course code (`demo-101.md`, `math-2xx-example.md`; DEMO codes are fictional). Template: `schema/templates/course.md`.

## What a course page holds

In Compiled Truth: sections (yours in bold), the instructional team with office hours, grading weights, the course's **AI-use and collaboration policy** (quoted, with source), where submissions really live (LMS, Gradescope, a course git server), materials, an exams table and key dates (including the drop deadline). Each table carries `[Source: ...]`. Dated changes ("midterm moved", "scope widened") go in the Timeline with their source; Compiled Truth is then rewritten to match.

## Alias convention

Put **every way the code gets written** in `aliases:` and in the course's `GLOSSARY.md` row: with and without the space (`DEMO 101`, `DEMO101`), mixed case, hyphenated, cross-listed codes, the bare number (`101`), and nicknames ("the demo course"). Questions arrive in all of those forms; the alias list is how the agent finds the page.

## Dropped courses

Keep the page. Set `status: resolved`, start Compiled Truth with **"Dropped YYYY-MM-DD"** and a link to the decision page, prefix `description:` with `DROPPED YYYY-MM-DD`, and leave the facts as they stood at the drop below as a record. Remove the course from the semester's grid and calendar, not from the KB. Example: `math-2xx-example.md`.

## Siblings for the same course

- `<slug>-<exam>-prep.md` (`exam-prep`, template `exam-prep.md`): study plan for one exam; archive after the exam.
- `<slug>-notes.md` (`course-notes`, template `course-notes.md`): per-lecture digests citing transcript lines as `[T:NN](../../raw/school/<transcript>.md#LNN)`.
- Silo pages (`type: plan`) for in-flight plans about the course.

Commit scope: `school`.
