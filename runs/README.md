# runs/

Maintenance outputs and controls.

- `PAUSE` — kill switch (gitignored). If this file exists, every maintenance run stops before reading or writing.
- `prompts/` — versioned prompt text for on-demand maintenance runs (triage, gardening).
- `triage/` — one report per triage run (`YYYY-MM-DD-HHMM-triage.md`, `type: report`).
- `gardener/` — one report per gardening run (`YYYY-MM-DD-gardener.md`, `type: report`): checks run, fixes made, proposals, questions.
- `retrieval-failures.md` — one line per question the KB should have answered but did not.

Maintenance runs only when the student asks (nothing is scheduled), and always honors the gates in AGENTS.md §Growth: `runs/PAUSE`, dirty-tree abort, `git pull --rebase` first, and `DIFF_CAP_FILES` / `DIFF_CAP_LINES` from `THRESHOLDS.md`. Commit scopes: `runs`, `triage`, `gardener`.
