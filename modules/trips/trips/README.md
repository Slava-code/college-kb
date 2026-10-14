# trips/

One page per trip (`type: trip`), named `YYYY-MM-<slug>.md` after the month it starts. Trips are planning silos: they link to people, course and device pages, and those pages never absorb trip content (AGENTS.md §Write). Installed by `modules/trips`.

- `status:` is one of `planning`, `booked`, `done`, `cancelled`. Cancelled trips stay as they are.
- Sections: Compiled Truth (dates, who, where, bookings, budget), Open Threads (decisions not made yet), Timeline (append-only).
- Booking PDFs go to `raw/travel/` with manifest entries. Never record passport numbers, payment details or passwords.
- A trip that grows gets a folder `trips/YYYY-MM-<slug>/README.md` plus companion pages (`<slug>-finds.md`).

Allowed types: `trip`, `note`. Commit scope: `trips`. Template: `schema/templates/trip.md`.
