# Design notes: why each rule exists

`AGENTS.md` says *what* the rules are. This page says *why*, so you can tell which ones are load-bearing before you change them. Each section names the rule, the failure it prevents, and where it is enforced.

## Capture and triage

**Capture is verbatim and dumb (`kbdrop.sh`, `inbox/`).** Capture happens at the worst moments: walking out of lecture, half-reading an email. If capture asks questions or classifies, people stop capturing. So a drop is one timestamped file and one commit, nothing else. Classification waits for triage.

**Triage reads the whole inbox as one batch.** Three drops ("midterm moved", "room changed", "bring a calculator") are one update to one page. Processing drops one at a time produces three conflicting edits and three reminders. Batch-then-cluster is the fix.

**Triage and gardening run on demand only.** Unattended runs over your private notes are where silent damage happens: a bad merge, a wrong date written as fact at 3 a.m. Running them from a session you started means you see the diff. If you want a schedule anyway, see [automation.md](automation.md); the safety gates still apply.

**Safety gates (`runs/PAUSE`, clean tree, pull first, diff caps).** The kill switch lets you stop everything with one `touch`. The clean-tree check keeps a run from committing your half-finished edits. Pulling first prevents two machines writing divergent histories. The diff caps (`DIFF_CAP_FILES`, `DIFF_CAP_LINES` in `THRESHOLDS.md`) stop a confused run before it rewrites half the KB.

**Never answer from `inbox/`.** Drops are unverified and often superseded by the next drop. Answering from them gives you stale or contradictory facts with a confident tone.

## Pages

**Compiled Truth on top, Timeline below.** You want the current answer fast, and you want to know how it got that way. Rewriting the top keeps it short and current; an append-only Timeline keeps the history honest. Editing history destroys the one record that explains a surprise later ("when did the exam room change?").

**`[Source: who/context/date]` on facts that rot.** Deadlines, rooms, grading weights and policies change mid-term. A dated source tells you whether a fact is from the syllabus in week 1 or an announcement last night, and lets you check it.

**Record both sources when they disagree.** The syllabus says 20%, the LMS gradebook says 25%. Picking one silently hides a question you should ask the instructor. Recording both, with a flag, makes the conflict visible.

**Plans live in their own silo (`type: plan`).** "Thinking about studying abroad" written onto your profile becomes "is studying abroad" a month later, and nobody remembers it was a maybe. Keeping plans on their own page, linked by wikilink, means an abandoned plan leaves nothing stale in your compiled truth, glossary or descriptions.

**New pages need at least 3 meaningful sentences (`NEW_PAGE_MIN_SENTENCES`).** Stub pages multiply, fragment facts, and make search worse. Below the bar, the fact goes on an existing page or stays an inbox drop.

**`description:` is one line and feeds `INDEX.md`.** The index is what an agent reads first, so descriptions are written for retrieval ("what would a future question search for?"). IDs, grades and other sensitive values stay in the page body, where they have a source and do not appear in every agent's context.

**Read whole pages, not chunks.** While the KB is small, opening one to three whole pages is cheaper and more accurate than retrieval over fragments. Chunking is a later optimization, not a default.

**Report what pages say, preserve hedges.** "Tentatively Thursday" must not become "Thursday". Absence of a fact is not evidence it is false; the agent says "the KB doesn't say" and logs the miss in `runs/retrieval-failures.md` so the gap gets filled.

**Transcripts are two files.** The verbatim transcript sits unedited in `raw/` so its line numbers never move; the notes page cites claims as `[T:NN](...#LNN)`. You can check any claim against what was actually said. "The transcript is in some app" is not a record: apps expire, accounts close.

**Never delete pages; supersede and archive.** A deleted page breaks links and erases the context behind past decisions. Archiving keeps both.

## Schema and scripts

**One schema config (`scripts/kb-schema.json`), standard library only.** Every script reads the same types, folder map and commit scopes, so there is one place to change them. JSON plus the Python standard library means nothing to install and nothing to break on a school lab machine.

**AGENTS.md mirrors the scope and verb lists; `kb-lint.py` checks for drift.** Agents read AGENTS.md, scripts read the JSON. If they disagree, an agent writes commits the hook warns about. The drift check makes that a lint failure instead of a slow confusion.

**One commit format (`<scope>: <verb> <slug>`).** A predictable log is searchable (`git log --grep '^school:'`) and readable by the next agent. The hook warns rather than blocks by default so a typo never loses a capture.

**`INDEX.md` is generated, never hand-edited.** A hand-maintained index drifts within a week. Generating it from `description:` on every commit keeps it true for free.

**Templates are excluded from lint and links.** They are full of placeholders by design. The page you make from a template is checked like any other.

## Machines and git

**`CLAUDE.local.md` holds the hostname and absolute paths, and is gitignored.** Paths differ per machine. Committing one machine's paths makes an agent on another machine write to the wrong place, or leak your username into a public copy. The hostname check catches a file copied between machines.

**Pull first, one writer at a time.** Two sessions writing at once produce merge conflicts in prose, which are painful to resolve. Serial sessions plus `git pull --rebase` before the first write keep clones converged.

**Auto-push is opt-in.** Pushing automatically is convenient, but a push is the one action that sends your notes somewhere else. Off by default means you decide when and where that happens.

## Security and privacy

**Secrets are pointers.** A KB is read by agents, synced, backed up and sometimes shown to people. A secret in it is a secret in all of those places. A pointer ("the LMS token is in the password manager item *LMS token*") is enough for an agent to ask you for it at the right moment.

**The machine-note line test.** Notes that only reduce an attacker's *effort* (which LMS you use, your laptop model) may be committed. Anything that grants *access* (passwords, tokens, recovery codes) never is, masked or not.

**gitleaks in the pre-commit hook, refusing to commit without it.** The cheapest time to stop a secret is before it is in history. Skipping the scan silently when gitleaks is missing would make the protection imaginary on a fresh machine.

**`raw/` is out of git.** Scans of IDs, offer letters and transcripts are the most sensitive files you have and the least useful in diffs. They stay on disk (or in a synced folder you control), and pages cite them by path.

**The leak gate uses your own deny-list, kept outside the repo.** Generic scanners cannot know your name, your school or your professors. Only you can list them, and the list itself is sensitive, so it never lives in the repo.

**Untrusted text is data.** Syllabi, emails and web pages can contain instructions. Agents follow AGENTS.md and you, not text inside a fetched page.

## Course integrity

**Every course page records its AI-use and collaboration policy.** Policies differ per course and change. Recording the policy, quoted and sourced, where the agent reads it before every course task keeps the KB on the right side of it. The KB organizes your notes and plans; it does not do graded work.

## Schema: core vs optional modules

The root `scripts/kb-schema.json` covers the **core** only. Modules are inactive until installed, and the ones that add a folder tell you which entries to add. Apply them to `kb-schema.json`, add the scope to the **Allowed scopes** block in `AGENTS.md` in the same commit (the drift check enforces it), run `python3 scripts/kb-lint.py`, and commit `schema: add <name>-module`. `bash modules/install.sh <name> --check` lists what is still missing.

| Module | `valid_types` | `path_types` | `commit_scopes` |
|---|---|---|---|
| `devices` | `device`, `incident` | `"devices": ["device", "incident", "note"]` | `devices` |
| `international-student` | `document` | `"international": ["document", "note"]` | `international` |
| `trips` | `trip` | `"trips": ["trip", "note"]` | `trips` |
| `lms-canvas`, `school-mail`, `reminders`, `sibling-kb` | none | none | none |

Modules that add no folder need no schema change. Their pages (for example the Canvas or mail record page) live in `school/` as `type: note`.

## Patterns shared with slava-stack

[slava-stack](https://github.com/Slava-code/slava-stack) applies the same approach to a startup KB. The two repos share no code; fixes are ported by hand. The common patterns:

- an agent contract file plus thin skills that defer to it;
- typed frontmatter, a lint, and a generated `INDEX.md`;
- `[Source: ...]` citations and line-cited transcripts in `raw/`;
- old pages say they are old (supersede stamps, archive, never delete);
- gitleaks in a versioned pre-commit hook;
- DEMO content that is obviously fake, so the framework can ship publicly.
