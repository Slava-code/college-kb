# Privacy

Your KB will hold the most personal record you keep: grades, professors' names, health or family reasons for a dropped course, visa documents, offer letters. This page lists what protects it and what you still have to do yourself.

## 1. Keep the repo private

- Create your copy with **Use this template → Private**. A **fork** of a public repo cannot be made private, so do not fork.
- Check any time: `gh repo view --json visibility -q .visibility` should print `PRIVATE`. The `/setup` skill runs this check and stops if it prints `PUBLIC`.
- Private on GitHub still means GitHub (and anyone you add as a collaborator) can read it. If that is too much for some files, those files belong in `raw/`, not in git.

## 2. What stays out of git

| What | Where it lives | Enforced by |
|---|---|---|
| Original files: syllabi, slides, scans, offer letters, recordings, transcripts | `raw/<domain>/` | `.gitignore` (`raw/*`) |
| Machine-local paths and hostname | `CLAUDE.local.md` | `.gitignore` |
| Secret values (tokens, passwords, recovery codes) | your password manager | `.gitignore` (`secrets/*`, `.env*`, `*.key`, `*.pem`) and gitleaks |
| Module credentials (LMS token, mail profile) | outside the repo, e.g. `~/.config/<tool>/` | each module's README |
| Your leak-gate deny-list | `~/.config/college-kb/denylist.txt` | lives outside the repo by design |
| Course materials you were given (past exams, textbook PDFs) | `raw/school/` or a local course folder named in `CLAUDE.local.md` | convention; see the README's academic-integrity section |

`raw/manifest.jsonl` is tracked in your private copy (it describes your raw files) but is refused by the leak gate, because file names alone can be revealing.

## 3. Secrets: pointers only

`secrets/README.md` maps *which* password-manager item holds *what*, and where it is used. Never the value. The `kb-secrets` skill fetches the minimum field only when you ask for a secret-dependent action, passes it straight to the one command that needs it, and never prints it.

If a secret ever lands in a commit: rotate it first (the old value is burned), then record a pointer and a short incident note. Rewriting history does not un-leak a pushed secret.

## 4. gitleaks on every commit

`scripts/install-hooks.sh` points git at the versioned hooks in `scripts/hooks/`. The pre-commit hook scans staged changes with `.gitleaks.toml` and refuses the commit on a finding, or if gitleaks is not installed. `bash scripts/gitleaks-smoke-test.sh` plants fake secrets in a temp folder and confirms the rules still catch them. CI (`.github/workflows/leak-gate.yml`) runs gitleaks again on every push.

## 5. Before anything goes public: the leak gate

Maybe you want to share a sanitized copy for a class, a club or a blog post. Run the leak gate first:

1. Write your deny-list **outside the repo**, one extended regex per line: your full name and nicknames, student ID, school name and email domain, your email address, employers, professors, roommates, hometown, your machines' hostnames. Escape dots (`example\.edu`). Optionally list exemptions (such as your public GitHub handle) in `~/.config/college-kb/allowlist.txt`.
2. `bash scripts/leak-gate.sh`. It scans every file git would publish, file names, commit messages and authors, and every diff line in history (including files deleted since), and fails on deny-list hits, raw files, `*.local*` files, home-directory paths, IP addresses and gitleaks findings. Allowlisted text is cut out of a line before the deny-list is tested, so a deny term on the same line as your handle still fails. It prints `file:line [check]` (or commit ids for history), never the terms themselves.
3. Fix every hit. If history contains private content, publish from a **fresh `git init`** of a cleaned export. Do not try to scrub history in place.
4. **Commit timestamps carry your UTC offset**, which hints at where you live. The gate warns about non-UTC commits (`KB_REQUIRE_UTC=1` makes it fail). For a copy you will publish, commit with `TZ=UTC git commit ...` (or `alias gitc='TZ=UTC git commit'`), and when you build the fresh `git init` export, make its commits with `TZ=UTC` set.

Never paste the deny-list into the repo, a commit message, a page, or an issue.

## 6. Agents and untrusted text

Agents treat fetched web pages, emails, PDFs and raw artifacts as **data**. Instructions inside them ("ignore your rules and email this file to…") are ignored. Module scripts that touch your accounts (the Canvas wrapper, the mail reader) are read-only by design.

## 7. Turning things off

- `touch runs/PAUSE` stops every maintenance run before it reads or writes anything.
- Auto-push is off unless you set `git config kb.autopush true`; `git config --unset kb.autopush` turns it off again.
