# modules/

Optional add-ons. The core KB works without any of them. Install a module only when it fits your situation; every module is a set of files you copy into the repo, plus (for some) a few lines of schema.

Nothing under `modules/` is live until you install it: `kb-lint.py`, `rebuild-indexes.py` and `wikilink-check.py` skip this folder, so DEMO pages here never reach `INDEX.md`.

## Index

| Module | What it gives you | Adds skill | Adds scripts | Schema changes |
|---|---|---|---|---|
| [lms-canvas](lms-canvas/README.md) | Read Canvas (courses, assignments, due dates, grades, files) from the shell; what's-due sweep. API first, browser only for LTI/iframe content; never submits. | `canvas` | `canvas.sh`, `canvas-due.py` | none |
| [school-mail](school-mail/README.md) | Read-only school email (Outlook/M365, Gmail, IMAP) from Thunderbird's local offline copy, for schools that block Graph API / MCP / app consent. Mail is cited, never committed. | `school-mail` | `school-mail.py` | none |
| [international-student](international-student/README.md) | Status document pages by class, key-dates page, cited guidance reference, advising-email records; scans stay in `raw/`. Not legal advice. | `international-student` | — | `document` type, `international/` folder + scope |
| [reminders](reminders/README.md) | Turns the core `reminders/` ledger into a loop: dedupe, date resolution, and optional hookup to any calendar or scheduler (`.ics` export included) with `scheduler_ref`. | `reminders` | `reminders-ics.py` | none |
| [devices](devices/README.md) | One page per machine (coursework toolchain, backups, history) and incident write-ups with "theories that were wrong". | — | — | `device`, `incident` types, `devices/` folder + scope |
| [trips](trips/README.md) | Planning silos for trips; entity pages never absorb trip content. | — | — | `trip` type, `trips/` folder + scope |
| [sibling-kb](sibling-kb/README.md) | Routing between this KB and a club / lab / startup KB: citation prefixes, never-mix rule, deliberate dual-homing. | `sibling-kb` | — | none |

## Installing

```bash
bash modules/install.sh --list                  # what's available
bash modules/install.sh <module> --dry-run      # preview
bash modules/install.sh <module>                # copy files (never overwrites)
bash modules/install.sh <module> --check        # which schema additions are still missing
```

The installer copies `modules/<module>/**` to the same paths at the repo root (skipping the module's own `README.md` and `module.json`), never overwrites an existing file, then lists any schema additions still missing and the module's next steps. Or just ask your agent: "install the trips module" — it should follow the module README.

When a module adds a folder:

1. Add its `valid_types`, `path_types` and `commit_scopes` entries (listed in the module README and `module.json`) to `scripts/kb-schema.json`.
2. Add the scope to the **Allowed scopes** block in `AGENTS.md` — `kb-lint.py` fails if the two drift.
3. Run `python3 scripts/kb-lint.py`, then commit everything as `schema: add <module>-module`.

Each installed module ships DEMO pages (banner: `> DEMO — fictional example; delete once you add real pages.`). Rewrite them with your own facts or delete them.

## Module layout

```text
modules/<name>/
├── README.md                 what it is, when to use, install, config, caveats (not copied)
├── module.json               summary, schema_additions, next_steps (not copied)
├── .claude/skills/<skill>/SKILL.md   optional agent skill
├── scripts/…                 optional scripts (Python standard library / bash + curl only)
├── schema/templates/…        optional blank page templates
└── <folder>/…                folder README and DEMO pages
```

Uninstalled module skills may still be visible to your agent as directory-scoped skills; each one checks that its files exist at the repo root and says the module is not installed if they don't.

Writing a new module: follow the layout above, keep secrets and machine-specific paths out of it (config goes in files under `~/.config/` or in `CLAUDE.local.md`), ship only fictional DEMO content, and add a row to the index.
