# raw/

Original artifacts that never go into git: syllabus PDFs, slides, scans of documents, offer letters, screenshots, recordings, verbatim transcripts. Git ignores everything here except this README and `manifest.jsonl`. Pages cite artifacts by repo-relative path (`raw/school/2099-08-25-demo-101-syllabus.pdf`).

## Domains

Organize by domain subfolder, not as a flat dump. Typical student domains: `school`, `career`, `id`, `finances`, `housing`, `projects`, plus `misc` as a temporary fallback. Add a domain only with:

```bash
scripts/link-raw.sh <domain>
```

## Where the files actually live

- **Local mode (default):** `raw/<domain>/` are plain local folders. Git does not back them up, so include `raw/` in your own backups (Time Machine, an external drive, a cloud backup tool).
- **Synced store:** set `KB_RAW_STORE` (or `git config kb.rawstore <dir>`) to a folder your sync client already handles, such as an Apple cloud-drive, Dropbox, OneDrive or Syncthing folder. `link-raw.sh` then creates domains in the store and makes each `raw/<domain>` a gitignored symlink into it, so every machine resolves the same repo-relative paths. In this mode never `mkdir` under `raw/` by hand: a plain folder would be machine-local and unsynced. The post-merge hook links new domains after each pull.

## Naming

Date-prefix every file (`YYYY-MM-DD-<slug>.<ext>`). Never overwrite an older copy; add a newer dated file and a new manifest entry.

## `manifest.jsonl`

Create it on your first artifact. One JSON object per line, per file:

```json
{"path": "raw/school/2099-08-25-demo-101-syllabus.pdf", "category": "school", "captured": "2099-08-25", "sha256": "<sha256 of the file bytes>"}
```

Required: `path` (repo-relative), `category` (domain), `captured` (`YYYY-MM-DD`), `sha256` (`shasum -a 256 <file>`). Optional: `source_page`, `notes`, `version`, `redacted`. Secret values never belong in the manifest. Your manifest describes private files; `scripts/leak-gate.sh` refuses to publish it.
