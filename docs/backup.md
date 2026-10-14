# Backup and sync

Your KB has three parts, and each needs its own copy somewhere else. Git covers only the first.

| Part | What it is | Backed up by |
|---|---|---|
| **Pages** | everything git tracks: Markdown pages, scripts, `INDEX.md`, `raw/manifest.jsonl` | a private git remote (step 1) |
| **Raw files** | `raw/<domain>/`: PDFs, scans, recordings, transcripts | a synced folder outside git (step 2) and/or your OS backup (step 3) |
| **Machine-local config** | `CLAUDE.local.md`, git config (`kb.autopush`, `kb.rawstore`), module credentials under `~/.config/` | your OS backup (step 3); recreate with `/setup` if lost |

## 1. Pages: a private git remote

- Create a **private** repository (GitHub, GitLab, a self-hosted server) and `git remote add origin <url>`, then `git push -u origin main` once.
- Pushes happen when you ask. To push after every commit, opt in with `git config kb.autopush true`; the post-commit hook then pushes when an upstream exists.
- On a second machine: clone, `bash scripts/install-hooks.sh`, create `CLAUDE.local.md` from the example, and always `git pull --rebase` before the first write of a session. Only one session writes at a time across machines.

## 2. Raw files: out of git, but not only on one disk

Two modes (details in [raw/README.md](../raw/README.md)):

- **Local (default).** `raw/<domain>/` are plain folders on this machine. Nothing else has a copy until your OS backup runs.
- **Synced store.** Set `git config kb.rawstore "<folder>"` (or `KB_RAW_STORE`) to a folder your sync client already handles: an Apple cloud-drive folder, Dropbox, OneDrive, Google Drive, Syncthing. `scripts/link-raw.sh <domain>` creates the domain in the store and symlinks `raw/<domain>` to it, so every clone resolves the same repo-relative paths. The post-merge hook links domains another machine added.

In store mode, add domains only with `link-raw.sh`; a plain `mkdir` under `raw/` makes a local, unsynced folder that looks right and is not backed up.

A sync service is not a backup on its own: a deletion syncs too. Pair it with step 3, or with the sync service's version history.

## 3. OS backup

Include the repo folder, your raw store and `~/.config/` in whatever your OS backs up: Time Machine (macOS), File History (Windows), or a tool such as `restic` or `borg` (Linux). An external drive or a cloud backup service both work.

## 4. Check it works

Once a term:

- `git status` is clean and `git log origin/main..main` is empty (everything is pushed).
- Pick one file from `raw/`, find it in the synced store or backup, and compare its hash with `raw/manifest.jsonl` (`shasum -a 256 <file>`).
- Restore one file from your OS backup to a temp folder and open it.

## 5. Restoring on a new machine

1. Clone the private remote; `bash scripts/install-hooks.sh`.
2. Restore or reconnect the raw store, set `kb.rawstore`, then run bare `bash scripts/link-raw.sh` to link every domain.
3. Run `/setup` again for this machine only (it writes a fresh `CLAUDE.local.md` with this hostname).
4. Re-create module credentials from your password manager.
