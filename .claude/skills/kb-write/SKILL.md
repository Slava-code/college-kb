---
name: kb-write
description: Use when the student states a durable fact, correction, or decision ("my advisor is...", "the midterm moved", "I decided to drop DEMO 101"), or asks to create or update a page (course, person, project, decision, career); the read-integrate-commit loop.
---

# kb-write

`AGENTS.md` is canonical (§Write); this is only a thin task pointer.

1. **Gate.** Read `CLAUDE.local.md` and confirm `hostname` matches it; if missing or mismatched, stop and ask. If a remote exists and this is the session's first write, `git pull --rebase`; on conflict, stop.
2. **Orient.** Read `INDEX.md`, `GLOSSARY.md`, and the target folder's `README.md`.
3. **Find before creating.** Search for the entity by name and aliases (`GLOSSARY.md`, `aliases:` frontmatter, `grep -ril`). Update the existing page when there is one.
4. **New page only if earned:** at least `NEW_PAGE_MIN_SENTENCES` (see `THRESHOLDS.md`) meaningful sentences now; otherwise enrich an existing page or capture an inbox drop. Start from the matching template in `schema/templates/` (its `README.md` maps each template to its `type:`, folder and file name, e.g. `course.md`, `decision.md`, `person.md`, `plan.md`); the folder→type map is in `scripts/kb-schema.json`. Read the DEMO page the README names when the template alone is unclear, and never copy DEMO facts.
5. **Re-read the whole target page** before editing.
6. **Integrate.**
   - Rewrite **Compiled Truth** to the new current state; append a dated line to **Timeline** (never edit old Timeline lines).
   - Facts that can rot or be acted on (deadlines, grading weights, office hours, policies, offer terms) get `[Source: who/context/YYYY-MM-DD]`. Conflicting sources: record both, do not pick one silently.
   - Plans and explorations ("thinking about a minor", "might study abroad") go on their own silo page linked by wikilink; never phrase them as settled facts on entity pages, in `GLOSSARY.md`, or in `description:`.
   - Course pages: keep the course's AI-use and collaboration policy current and follow it. Organize the student's notes; do not produce graded work.
   - If this settles an open thread elsewhere, add `**Resolved YYYY-MM-DD → [[this/page]]:** one line` there in the same commit.
   - New recurring names (a TA, a club, a course nickname): append a `GLOSSARY.md` entry.
7. **Frontmatter.** Update `updated:` (today) and `description:` (≤ 120 characters, a rule-like summary) in the same edit. Never edit `INDEX.md` by hand.
8. **No secrets.** Store password-manager pointers only (`kb-secrets`).
9. **Check.** `python3 scripts/kb-lint.py` and `python3 scripts/wikilink-check.py`; fix what they report.
10. **Commit** by explicit path with `<scope>: <verb> <slug>` (scopes and verbs in AGENTS.md §Commit format), e.g. `school: update demo-101`, `decisions: add 2099-09-24-choose-a-minor`. The pre-commit hook rebuilds and stages `INDEX.md`. Push only if the student asks or `kb.autopush` is on.
