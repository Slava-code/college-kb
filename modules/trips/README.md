# Module: trips

Use this for spring break, trips home, conference or hackathon travel, a visiting family member, or a study-abroad scouting trip. Each trip is a **planning silo**: it gets its own page, and that page links to people, course and device pages. Those entity pages never absorb any of the trip content. When a plan changes or is dropped, it stays separate from what is actually true about your life.

The silo rule itself is core (AGENTS.md §Write: "Plans live in their own silo"). This module adds a home and a page shape for the most common kind of plan.

## What's in it

| File (in this module) | Installs to | Purpose |
|---|---|---|
| `trips/README.md` | `trips/README.md` | Folder rules |
| `trips/2100-03-example-spring-break.md` | same path | DEMO trip page, mid-planning |
| `schema/templates/trip.md` | `schema/templates/trip.md` | Blank template (the installer skips it if your core already ships one) |

There is no skill or script. The core write loop and the reminders module, if installed, cover this folder.

## Install

1. `bash modules/install.sh trips` (add `--dry-run` to preview).
2. **Schema additions** go in `scripts/kb-schema.json`, plus the AGENTS.md "Allowed scopes" block, in one commit:
   ```json
   "valid_types":   [..., "trip"],
   "path_types":    { ..., "trips": ["trip", "note"] },
   "commit_scopes": [..., "trips"]
   ```
   Then run `python3 scripts/kb-lint.py` and commit as `schema: add trips-module`.

## Rules

- One page per trip, named `YYYY-MM-<slug>.md` after the month it starts (`2100-03-example-spring-break.md`). If a trip outgrows one page, promote it to a folder `trips/YYYY-MM-<slug>/` with a `README.md`. A companion page such as `<slug>-finds.md` (places, food, ideas) is fine.
- **Entity pages never absorb trip content.** A person page may get a single Timeline line linking to the trip, and only after the trip happened. `GLOSSARY.md` and `description:` fields never mention a planned trip, and a plan is never phrased as fact ("visiting in March"). Link to the trip page instead.
- `status:` moves from `planning` to `booked`, then `done` or `cancelled`. A cancelled trip page stays as it is. Never delete it.
- Bookings: record the confirmation *existence*, the dates and the carrier. Confirmation PDFs go to `raw/` (for example `raw/travel/`, created with `scripts/link-raw.sh travel`). Never record passport numbers or payment details. Booking-site passwords go in your password manager.
- Deadlines (book by, check in by) go to the reminders ledger if that module is installed.
- International students: travel can touch status documents. Link the trip to `international/status` and confirm requirements with your office (see the international-student module).
