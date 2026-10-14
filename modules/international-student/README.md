# Module: international-student

> **Not legal advice.** This module gives you pages for organizing your own documents and the guidance you have received. It contains no immigration rules and makes no claim about what you may or may not do. Your school's international student office (the designated school official or responsible officer) and official government sources are the authority. Rules change, and they depend on your exact situation. Confirm with your office before you act on anything a page or an agent tells you, and keep that confirmation on the page.

This is an optional module for students on a student or exchange-visitor status, such as US F-1 or J-1, or the equivalent elsewhere: a study permit, a student visa, a residence permit. These students carry recurring documents and dates that are expensive to get wrong. The module gives each **class** of document one page with the current version, a pointer to the scan kept outside git, and an append-only history. It also gives you a key-dates page, a reference page for work-authorization guidance (cited, dated, with a re-verify date), and a record for each advising exchange with your office.

## When to use it

- You hold student or exchange-visitor status and get documents re-issued: an updated eligibility certificate, a new travel signature, a new visa, a work-authorization approval.
- You want an agent to answer "when does my passport expire?" or "what did the international office tell me about working this summer?" from your own cited records, not from the web.

Skip it if none of this applies. The same pattern (one page per document class, scans in `raw/`) also fits financial aid, leases and insurance. Reuse the templates for those if you like.

## What's in it

| File (in this module) | Installs to | Purpose |
|---|---|---|
| `international/README.md` | `international/README.md` | Folder rules: one page per document class, scans only in `raw/international/`, no document numbers in pages |
| `international/status.md` | `international/status.md` | DEMO key-dates page: program dates, document expiries, upcoming deadlines |
| `international/documents.md` | `international/documents.md` | DEMO inventory of every document **class** → its page → its current raw file |
| `international/eligibility-certificate.md` | `international/eligibility-certificate.md` | DEMO document-class page (current version + Timeline) |
| `international/work-authorization-reference.md` | `international/work-authorization-reference.md` | DEMO reference page: the guidance *you* received or read, each item cited, dated, with a re-verify date |
| `international/2099-09-08-advising-email-summer-work.md` | same path | DEMO record of one exchange with the international office |
| `schema/templates/international-*.md` | `schema/templates/` | Blank templates for the four page shapes |
| `.claude/skills/international-student/SKILL.md` | `.claude/skills/international-student/SKILL.md` | Agent procedure: routing, the not-legal-advice stance, document-number rule |

## Install

1. `bash modules/install.sh international-student` (add `--dry-run` to preview). The installer never overwrites a file.
2. **Schema additions.** Edit `scripts/kb-schema.json` and AGENTS.md §Commit format in the same commit:
   ```json
   "valid_types":   [..., "document"],
   "path_types":    { ..., "international": ["document", "note"] },
   "commit_scopes": [..., "international"]
   ```
   Add `international` to the "Allowed scopes" block in `AGENTS.md`, because `kb-lint.py` fails when the two lists drift. Then run `python3 scripts/kb-lint.py`.
3. **Raw domain for scans:** `bash scripts/link-raw.sh international`. With a synced raw store (`KB_RAW_STORE`), choose a store with end-to-end encryption for identity documents, or keep this domain local and back it up to an encrypted drive.
4. Add a `GLOSSARY.md` entry for your international office (name, aliases) linking to `international/status`.
5. Delete the DEMO pages or rewrite them with your own facts, then commit as `schema: add international-student-module`.

## Rules this module adds

- **One page per document class, not per file.** A re-issued certificate updates the same page: rewrite Compiled Truth and add a Timeline entry. Each new scan is a new dated file in `raw/international/` with its own manifest entry.
- **Scans never enter git**, not even in a private repo: passports, visas, certificates, entry records, government ID numbers, approval notices. Pages cite `raw/international/...` paths only.
- **No identifying numbers in pages.** Leave out student-record IDs, passport, visa and receipt numbers, and national ID or tax numbers. They are in the scan. A page may say "receipt number: see scan".
- **Guidance is cited, dated, and has a re-verify date.** The reference page records what your office or an official page said, when, and where, and never what an agent inferred. Two sources that disagree are both recorded (AGENTS.md §Write), and the question goes to your office.
- **Plans stay in silos.** "Maybe a summer internship" or "maybe study abroad" goes on its own planning page. `status.md` holds only facts on record.
- **The agent may organize your records and draft questions to your office; it never advises.** If a page doesn't answer a status question, the agent says so and suggests asking the office.

## Caveats

- The DEMO pages use US-style document names as **examples of document classes**. Rename the classes to match your country and status.
- The module ships no school policy and no government rule on purpose, because both go stale and differ by school. Fill the reference page from your own office's materials.
