# devices/

One page per long-lived machine (`type: device`), named by a short slug (`example-laptop.md`). Incident write-ups go in `devices/incidents/YYYY-MM-DD-<slug>.md` (`type: incident`). Installed by `modules/devices`.

- **Device page:** Compiled Truth (what it is, its role, OS, coursework setup, backups), Open Threads, and an append-only Timeline that runs from purchase to retirement. When a machine is retired, set `status: archived` and keep the page.
- **Incident page:** TL;DR, a dated timeline of evidence, root cause, **theories that were wrong**, the diagnostics that helped, and prevention. The wrong theories are the most useful part next time.
- **Never store credentials:** no passwords, Wi-Fi keys, SSH private keys, disk-encryption recovery keys or MFA backup codes. Pointers go in `secrets/` (AGENTS.md §Security, line test).
- Clone-specific absolute paths stay in each machine's gitignored `CLAUDE.local.md`, not here.

Allowed types: `device`, `incident`, `note`. Commit scope: `devices`. Templates: `schema/templates/device.md`, `schema/templates/incident.md`.
