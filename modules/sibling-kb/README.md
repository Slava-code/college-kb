# Module: sibling-kb

Some students keep a second knowledge base: one for a club they run, a research lab, a startup, or a team project. It often lives in its own repo with its own contract and collaborators. This module teaches your agent to route between your personal KB and that **sibling**. Each answer cites which KB it came from, and the two are never mixed silently.

Core AGENTS.md already has the one-line rule (§Routing: "Optional sibling KB"). This module adds the full procedure as a skill, along with the config and the edge cases.

## When to use it

- You keep a second KB that you or your agent maintain, and you sometimes ask questions that span both: "what did the lab decide about the poster, and does it clash with my DEMO 101 exam?"
- Skip it if you have only one KB.

## What's in it

| File (in this module) | Installs to | Purpose |
|---|---|---|
| `.claude/skills/sibling-kb/SKILL.md` | `.claude/skills/sibling-kb/SKILL.md` | Routing, citation prefixes, the never-mix rule, cross-KB writes |

## Install

1. `bash modules/install.sh sibling-kb`. Schema: none needed.
2. In **each machine's** `CLAUDE.local.md` (gitignored), fill in the sibling line and add its name and prefix:
   ```markdown
   - sibling KB (opt.):  `<absolute path to the sibling repo on THIS machine>`
     - name: "<Club / lab / startup name>"   prefix: `<club>:`   (e.g. `robotics:`)
     - entered only when I name it: "<name> KB", "<name> notes", "the lab KB"
   ```
   The path differs per machine and never goes in a committed file. If a machine has no clone of the sibling, leave the line out, and the agent will say the sibling isn't available here.
3. Add one entry to `GLOSSARY.md` → Things: `- **<Name> KB** (aliases: <name> notes, the lab KB) — separate KB for <what>; path in CLAUDE.local.md; cite as <prefix>:`. That is the only mention of the sibling in committed files.
4. Commit as `schema: add sibling-kb-module`.

## Rules (summary; the skill has the procedure)

- **Personal by default.** Unqualified "KB" means this repo. The sibling is read only when you name it, or when you ask a question that explicitly spans both.
- **Never guess the path.** It comes only from `CLAUDE.local.md`.
- **Cite with prefixes.** `kb:folder/slug` for this repo and `<prefix>:folder/slug` for the sibling. A cross-KB answer cites both.
- **Never mix silently.** Facts from the sibling are not copied into personal pages unasked, and personal facts never go into a shared sibling. Collaborators can read it, and your grades, status documents and finances are not theirs to see.
- **Dual-home only by design.** Some material legitimately belongs in both, such as your role in the club or a project you also list on your resume. Keep the full record in the KB that owns it. The other KB gets a short summary page that cites the owner (`[Source: <prefix>:folder/slug, YYYY-MM-DD]`). List these dual-homed topics in the GLOSSARY entry so they stay deliberate.
- **The sibling's contract wins inside the sibling.** Read its `AGENTS.md` (or equivalent) before writing there. Its commit format, review rules and privacy rules apply, and a shared repo may need a pull request rather than a direct commit.
