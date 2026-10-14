# Module: devices

Use this module to keep a page for each machine you rely on: your laptop, a desktop, a lab workstation, a Raspberry Pi, a tablet you take notes on. Each page records what the machine is, how it is set up for coursework, and what happened to it over time. Incidents (a dead SSD the night before a deadline, Wi-Fi that drops in one lecture hall) get short write-ups, so the next fix is faster.

It's most useful for CS and engineering students with course toolchains, multiple machines or a home server. Others can skip it.

## What's in it

| File (in this module) | Installs to | Purpose |
|---|---|---|
| `devices/README.md` | `devices/README.md` | Folder rules (page shape, the line test, no credentials) |
| `devices/example-laptop.md` | `devices/example-laptop.md` | DEMO device page |
| `devices/incidents/2099-09-25-example-laptop-wifi-drops.md` | same path | DEMO incident write-up, including the theories that turned out wrong |
| `schema/templates/device.md`, `schema/templates/incident.md` | `schema/templates/` | Blank templates |

There is no skill and no script. The core write loop (AGENTS.md §Write) covers this folder.

## Install

1. `bash modules/install.sh devices` (add `--dry-run` to preview).
2. **Schema additions** go in `scripts/kb-schema.json`, plus the AGENTS.md "Allowed scopes" block, in one commit:
   ```json
   "valid_types":   [..., "device", "incident"],
   "path_types":    { ..., "devices": ["device", "incident", "note"] },
   "commit_scopes": [..., "devices"]
   ```
   Then run `python3 scripts/kb-lint.py`.
3. Add each machine to `GLOSSARY.md` under Things, with its hostname and nicknames as aliases. Commit as `schema: add devices-module`.
4. Optional: name each machine's page in its `CLAUDE.local.md` (for example "KB page: `devices/<slug>.md`"), so the agent knows which page describes the machine it is running on.

## The line test (from AGENTS.md §Security)

A note that only **reduces an attacker's effort** (hostname, OS version, which VPN client you use, where coursework lives) may go in your private KB. Anything that **grants access** (passwords, Wi-Fi keys, SSH private keys, disk-encryption recovery keys, MFA backup codes, API tokens) never does. Those go in your password manager, with a pointer in `secrets/README.md`. Masking doesn't make a secret safe to write down.

Serial numbers, MAC addresses and IP addresses are fine in a private repo. `scripts/leak-gate.sh` flags IPs if you ever publish a copy.

## Caveats

- A device page describes the machine, not the KB clone on it. Clone-specific paths stay in that machine's gitignored `CLAUDE.local.md`. Never copy an absolute path into a committed page.
- When a machine is retired, set `status: archived` and add a final Timeline entry. Keep the page; never delete it.
