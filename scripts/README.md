# scripts/

Small, boring scripts: capture, index rebuild, lint, link and ledger checks, hooks, raw/ linking, and the pre-publish leak gate. Each script resolves the repo root itself, so it runs from any directory. Python scripts use the standard library only (Python 3.8+); nothing here needs `pip install`. The only external tool is `gitleaks` (8.19 or newer).

## Fresh-clone setup

1. Clone your **private** copy and `cd` into it.
2. Install gitleaks: `brew install gitleaks` (macOS), `scoop install gitleaks` or `winget install gitleaks` (Windows), or a release binary from https://github.com/gitleaks/gitleaks/releases (Linux). The pre-commit hook refuses to commit without it.
3. `bash scripts/install-hooks.sh` — sets `core.hooksPath=scripts/hooks`, so the versioned hooks below run. Hooks update with `git pull`; re-run only on a new clone.
4. Optional: `git config kb.autopush true` to push after every commit (off by default).
5. Optional: set `KB_RAW_STORE` (or `git config kb.rawstore <dir>`) to sync `raw/` through a cloud folder, then `bash scripts/link-raw.sh`. See `raw/README.md`.
6. `cp CLAUDE.local.md.example CLAUDE.local.md` and fill in the hostname and paths before an agent writes (AGENTS.md §Boot).
7. Sanity check: `python3 scripts/kb-lint.py && python3 scripts/wikilink-check.py && python3 scripts/reminder-ledger-check.py && bash scripts/gitleaks-smoke-test.sh`.

## Per-script index

| Script | Purpose | Run by |
|---|---|---|
| `kb-schema.json` | The one schema config: valid `type:` values, folder→type map, required frontmatter, skip lists, commit scopes/verbs. Edit here when adding a type, folder, or scope; scope/verb changes also go in AGENTS.md §Commit format. | loaded by every Python script |
| `kb-lint.py` | Frontmatter lint (required keys, valid type, folder/type match, `updated:` is a real YYYY-MM-DD date, description length) plus a drift check that AGENTS.md scope/verb lists match `kb-schema.json`. `--staged` lints only staged files. | pre-commit, CI, manual |
| `rebuild-indexes.py` | Regenerates root `INDEX.md` from `description:` frontmatter. Never edit `INDEX.md` by hand. | pre-commit (then stages `INDEX.md`) |
| `wikilink-check.py` | Reports `[[wikilinks]]` whose target does not exist. | pre-commit (warning only), manual |
| `commit-msg-check.py` | Checks `<scope>: <verb> <slug>`. Warning-only unless `KB_COMMIT_STRICT=1`. | commit-msg hook |
| `reminder-ledger-check.py` | Validates `reminders/*.md` bullets: `status:` value, `scheduler_ref:` consistency, `reason:` on ambiguous recurrence. | pre-commit, manual |
| `kbdrop.sh` | Fast capture: writes a verbatim `inbox/YYYY-MM-DD-HHMM-<slug>.md` and commits only that file as `inbox: add ...` (other staged changes stay staged). `kbdrop.sh -` reads stdin. Text gitleaks flags as a secret is refused before anything is written; if the commit is refused anyway, the drop is unstaged, renamed to a neutral `...-unsaved-drop.md` and the recovery steps are printed. | capture skill, your shell alias |
| `link-raw.sh` | `link-raw.sh <domain>` adds a raw/ domain (local folder, or store folder plus symlink when `KB_RAW_STORE` is set); bare run links every store domain. | post-merge hook, manual |
| `install-hooks.sh` | Points git at `scripts/hooks/` and reports gitleaks and auto-push status. | once per clone |
| `hooks/pre-commit` | gitleaks staged scan (`KB_SKIP_GITLEAKS=1` to bypass once), then exports the **staged** tree and runs INDEX rebuild + stage, kb-lint, reminder check and warn-only wikilink check against it (`--root`), so untracked or unstaged pages never land in a commit's `INDEX.md`. | git |
| `hooks/commit-msg` | Runs `commit-msg-check.py`. | git |
| `hooks/post-commit` | Pushes only if `git config kb.autopush true` and an upstream exists. | git |
| `hooks/post-merge` | Runs `link-raw.sh` after a pull, only when a raw store is configured. | git |
| `gitleaks-smoke-test.sh` | Plants fake secrets in a temp dir and confirms `.gitleaks.toml` catches them. | manual, gardener |
| `leak-gate.sh` | Pre-publish privacy gate (below). | before making anything public |

## leak-gate.sh — before you make anything public

Your KB repo should stay private. If you ever publish a copy (a template, a sample folder, a fork for a class demo), run the leak gate first:

1. Create a deny-list **outside the repo**, one extended regex per line, `#` for comments:
   ```text
   # ~/.config/college-kb/denylist.txt
   your full name
   your-nickname
   your-student-id
   your school's name and email domain
   employers, professors, roommates, hometown
   your machine's hostname
   ```
   Optional allowlist (matching text is cut out of a line before the deny-list is tested, so only that text is exempt), e.g. your public GitHub handle: `~/.config/college-kb/allowlist.txt`. Override the locations with `KB_DENYLIST` and `KB_ALLOWLIST`.
2. `bash scripts/leak-gate.sh`. It scans everything git would publish, file names, commit messages and authors, and every diff line in history, and fails on deny-list hits, `raw/` files (including your manifest), `*.local*` files, absolute home paths, IPv4 addresses, and gitleaks findings. It prints `file:line [check]` (commit ids for history), never the deny-list terms, so the output is safe to share. It also warns about commits with a non-UTC timezone offset (`KB_REQUIRE_UTC=1` makes that a failure); commit a publishable copy with `TZ=UTC`.
3. Fix every hit. If history is dirty, publish from a fresh `git init` of a cleaned export instead of rewriting history.

CI (`.github/workflows/leak-gate.yml`) runs gitleaks and `kb-lint.py` on every push and pull request; it cannot see your private deny-list, so the local gate is still required.
