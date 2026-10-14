# runs/gardener/

One report per on-demand gardening run (the `kb-garden` skill, following `runs/prompts/gardener.md`), named `YYYY-MM-DD-gardener.md`: gates checked, checks run and their results, mechanical fixes made (with commit subjects), proposals that need the student's judgment (archive, split, merge, supersede) with reasons, and at most `NEEDS_OWNER_MAX_QUESTIONS` questions. Proposals here are never applied by the gardener itself; the student approves them in a later session.

Use `type: report` frontmatter, like triage reports (`schema/templates/triage-report.md` has the shape; swap the sections for the ones above). Commit with the `gardener` scope, e.g. `gardener: record weekly-report 2099-10-05`.
