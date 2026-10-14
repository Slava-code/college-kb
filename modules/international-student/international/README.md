# international/

Records for a student or exchange-visitor status: one page per **document class**, a key-dates page, a guidance reference page, and dated records of exchanges with the international office. Installed by `modules/international-student`.

> Not legal advice. Your international student office and official government sources are the authority; confirm before acting.

- **One page per document class** (`type: document`), named by class, e.g. `eligibility-certificate.md`, `passport.md`, `visa.md`, `entry-record.md`, `work-authorization-<kind>.md`, `tax-id.md`. Compiled Truth holds the current version (issued, valid until, issuer, raw pointer); the Timeline records every re-issue, correction, and replacement.
- **Scans live only in `raw/international/`** (`scripts/link-raw.sh international`), date-prefixed (`2099-08-13-eligibility-certificate.pdf`), each with a `raw/manifest.jsonl` entry. Never in git, not even in a private repo.
- **No identifying numbers in pages:** student-record IDs, passport, visa, receipt, national-ID or tax numbers stay in the scan.
- `status.md`: key dates across all documents; `documents.md`: the inventory; `work-authorization-reference.md`: guidance you received, cited and dated with a re-verify date; `YYYY-MM-DD-advising-email-<topic>.md`: one page per exchange with the office.
- In-flight plans (an internship that needs authorization, travel, a program extension) get their own silo page that links here; never phrase a plan as status fact.

Allowed types: `document`, `note`. Commit scope: `international`. Templates: `schema/templates/international-*.md`.
