---
name: international-student
description: Use when the student mentions their visa or student status documents — eligibility certificate (e.g. I-20, DS-2019), passport, visa stamp, entry record, travel signature, work authorization, or an email with the international office — or asks "when does X expire" / "can I work". Files records into international/ pages; never gives legal advice.
---

# international-student — status records, not advice

`AGENTS.md` is canonical. Module rules: `modules/international-student/README.md` and `international/README.md`.

## 0. Preconditions

- If `international/README.md` is missing at the repo root, the module is not installed: say so and point to `modules/international-student/README.md`. Stop.

## 1. Stance

- **Never advise on status or immigration questions.** Say what the student's pages record, with the source and date, and say when a row is past its re-verify date. If the pages don't answer the question, say "the KB doesn't say", log it in `runs/retrieval-failures.md`, and offer to draft a question to the international office.
- Do not answer status questions from the web or from memory. If the student asks you to look something up, cite the official page you read, label it as background rather than guidance, and recommend confirming with the office.
- Every page carries the not-legal-advice banner. Keep it.

## 2. New or re-issued document

1. Ask for (or locate) the scan. Save it as `raw/international/YYYY-MM-DD-<class>.<ext>`, add a `raw/manifest.jsonl` entry, and never overwrite an older scan.
2. Open the class page (`international/<class>.md`) or create it from `schema/templates/international-document.md`. Rewrite Compiled Truth for the new version and add a Timeline entry.
3. Update `international/documents.md` (the inventory row) and `international/status.md` (any date that changed), citing the scan.
4. **Never copy identifying numbers into a page**: student-record ID, passport, visa or receipt numbers, national or tax IDs. If the student pastes one, leave it out of the page and say why.
5. Commit with scope `international` (for example `international: update eligibility-certificate`).

## 3. Email or meeting with the office

- Create `international/YYYY-MM-DD-advising-email-<topic>.md` from the template. Summarize what was asked and what was answered, quote only the decisive sentence exactly, and cite the message (with the school-mail module installed, `scripts/school-mail.py cite <id>`). If a verbatim copy matters, save it as `.eml` in `raw/international/`.
- Copy each answered point into the relevant reference page with its date and a re-verify date. Mark unanswered questions as Open Threads.

## 4. Plans

- An internship, travel, a reduced course load, or an extension each gets its own planning silo page (AGENTS.md §Write), which links to these pages. `status.md` and the class pages hold only facts on record.
- Dated deadlines (an insurance waiver, a renewal window) go to the reminders ledger if that module is installed: `status: proposed-only` unless the student asks to schedule.
