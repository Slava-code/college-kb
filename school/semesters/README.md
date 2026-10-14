# school/semesters/

One page per term, `type: semester`, named `YYYY-<term>.md` (e.g. `2099-fall.md`, a DEMO). Template: `schema/templates/semester.md`.

A semester page is the roll-up across courses:

- the **enrolled table** (course, credits, what it counts toward, link to its page) and any drops;
- the **weekly grid** of meeting times;
- the **office-hours roll-up** (each course page stays the authority);
- the **"where the real submission state lives" table**: for each course, whether the LMS, Gradescope, a course git server or something else is the record of truth. A "what's due" sweep reads this first;
- the **exam and deadline calendar** and a **collision check** (same-day or back-to-back exams and deadlines, and how each was resolved);
- the academic calendar (start, add/drop, breaks, finals) and next-term registration dates.

Course detail lives on course pages. Plans for next term live in their own silo page and are only linked from here.

Commit scope: `school`.
