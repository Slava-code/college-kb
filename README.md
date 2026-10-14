# college-kb

**A blueprint for a college student's knowledge base — kept by your coding agent.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) ![Works with Claude Code](https://img.shields.io/badge/works%20with-Claude%20Code-555) ![AGENTS.md](https://img.shields.io/badge/contract-AGENTS.md-555) ![Python 3 stdlib](https://img.shields.io/badge/python-3.8%2B%20stdlib%20only-555)

Drop anything into it from a terminal: a syllabus link, an advisor's email, an internship posting, "the midterm moved to Thursday". Your agent files it into course, semester, career and decision pages. Every rot-prone fact is cited and dated, history is append-only, and sensitive scans stay out of git. Then ask it "when is the midterm and what's allowed on the note sheet?" and get an answer that cites a page.

It is plain git plus Markdown. It works with [Claude Code](https://claude.com/claude-code) out of the box (skills in `.claude/skills/`) and with any agent that reads [`AGENTS.md`](AGENTS.md). Obsidian is optional.

> [!WARNING]
> **Make your copy PRIVATE.** This repo will hold your courses, grades, professors' names, applications and deadlines. Click **Use this template → Create a new repository → Private**. Do **not** fork it: a fork of a public repo cannot be made private. The `/setup` skill checks your repo's visibility and stops if it is public.

---

## Quickstart

1. **Get a private copy.** On GitHub: **Use this template → Private**, then clone it. (Or clone this repo, delete `.git`, `git init`, and push to a new private repo.)
2. **Install gitleaks** (the pre-commit hook refuses to commit without it):
   - macOS: `brew install gitleaks`
   - Linux: your distro's package if it is 8.19 or newer, otherwise a release binary from <https://github.com/gitleaks/gitleaks/releases>
   - Windows: `scoop install gitleaks` or `winget install gitleaks` (Git Bash or WSL runs the shell scripts)
3. **Install the hooks:**
   ```bash
   cd your-kb
   bash scripts/install-hooks.sh
   ```
4. **Start your agent and run setup:**
   ```bash
   claude
   > /setup
   ```
   `/setup` interviews you once (name, school, term, courses, LMS, timezone, modules), writes your machine-local `CLAUDE.local.md`, your academic profile and current semester page, and offers to delete the DEMO pages.
5. **Add each course:** "set up DEMO 101, here's the syllabus" runs the `course-setup` skill.

Requirements: git, Python 3.8+ (standard library only, nothing to `pip install`), gitleaks. Optional: `gh` for the visibility check.

---

## What you get

The repo ships with a fictional student, **Alex Example** at **Example State University**, so you can try it before adding anything real. Ask the agent:

| You ask | It answers (from DEMO pages) | Cites |
|---|---|---|
| "When is the DEMO 101 midterm and what can I bring?" | Tue 2099-10-06, 6:30–8:00 p.m., Example Hall 140; one handwritten note sheet, no calculator. | `kb:school/courses/demo-101-midterm-1-prep` |
| "What's due this week?" | A dated list across courses, with a note that DEMO 101 homework lives on ExampleHW, so an empty LMS cell before the deadline is ignored. | `kb:school/semesters/2099-fall`, `kb:school/courses/demo-101` |
| "Can I use AI on the DEMO 101 homework?" | To explain concepts, yes; to produce submitted work, no; name any tool used on each homework. Quoted from the syllabus. | `kb:school/courses/demo-101` |
| "Which internships did I apply to, with which resume?" | Three applications, the resume variant used for each, and the next step: an online assessment due 2099-10-08. | `kb:career/application-log-2100-summer` |
| "Why did I drop MATH 2XX-EXAMPLE?" | About 12 hours a week of problem sets during internship season; dropped in week 2 (16 → 13 credits); revisit when planning spring 2100. | `kb:decisions/2099-09-04-drop-math-2xx-example` |

When the KB doesn't know, the agent says "the KB doesn't say" and logs the miss in `runs/retrieval-failures.md`, so gaps get filled instead of guessed.

---

## How it works

```text
 you ──"save this"──▶ inbox/ drop ──triage (on demand)──▶ compiled pages ──▶ cited answer
                      (verbatim,         clusters drops,       Compiled Truth     "kb:school/courses/demo-101
                       one commit)       updates pages,        + Timeline          [Source: syllabus, 2099-08-25]"
                                         proposes reminders
```

1. **Capture** is instant and dumb: `scripts/kbdrop.sh "text"` writes a verbatim, timestamped `inbox/` file and commits it. No classifying at capture time.
2. **Triage** runs when you ask ("process my inbox"). It reads all drops as one batch, clusters related ones, and updates the right pages, behind safety gates (kill switch, clean tree, diff caps).
3. **Compiled pages** hold the current truth at the top and dated, append-only history below. Facts that can rot carry `[Source: who/context/date]`.
4. **Answers** read `INDEX.md` first, open one to three whole pages, and cite them.

The pattern is Andrej Karpathy's **LLM Wiki** idea (an LLM incrementally maintains a Markdown wiki between you and your raw sources), adapted to student life:

| LLM Wiki concept | In college-kb |
|---|---|
| Raw sources (immutable) | `raw/` (out of git) + `sources/` pages that summarize them |
| The wiki (LLM-maintained pages) | `school/`, `career/`, `projects/`, `decisions/`, `people/`, … |
| The schema (how the LLM should maintain it) | `AGENTS.md` + `scripts/kb-schema.json` + `schema/templates/` |
| Ingest | `kb-capture` → `kb-triage`, `kb-ingest-source`, `course-setup` |
| Query | Cited answers (`kb:folder/slug`), `whats-due` |
| Lint | `kb-garden`, `scripts/kb-lint.py`, `scripts/wikilink-check.py` |
| `index.md` | `INDEX.md`, generated from each page's `description:` |
| `log.md` | Each page's `## Timeline`, `runs/triage/` reports, and git history |

---

## Folder tree

```text
college-kb/
├── AGENTS.md                 # the contract every agent follows
├── CLAUDE.md                 # @AGENTS.md (Claude Code entry point)
├── CLAUDE.local.md.example   # machine-local paths/hostname → copy to CLAUDE.local.md (gitignored)
├── INDEX.md                  # generated; never edit by hand
├── GLOSSARY.md               # aliases: course nicknames, people, clubs
├── THRESHOLDS.md             # diff caps, staleness windows, reminder defaults
├── .claude/skills/           # setup, kb-capture, kb-write, kb-triage, ... (see below)
├── scripts/                  # lint, index, link check, hooks, kbdrop, link-raw, leak-gate
├── schema/templates/         # one copy-ready template per page type
├── docs/                     # DESIGN, privacy, backup, automation
│
│  ── core content ──
├── school/                   # academic profile, courses/, semesters/, plan silos
├── career/                   # application profile, application logs, resume pointer, lab prospects
├── projects/  decisions/  sources/  research/  brainstorms/  people/  lists/
├── reminders/                # yearly reminder ledgers (proposed-only unless you ask)
├── inbox/                    # unabsorbed captures (never answered from)
├── archive/  runs/           # superseded pages; maintenance prompts, reports, retrieval misses
├── secrets/README.md         # pointer map only, never values
├── raw/                      # gitignored originals (PDFs, scans, transcripts)
│
│  ── optional ──
└── modules/                  # lms-canvas, school-mail, international-student, reminders,
                              # devices, trips, sibling-kb (inactive until installed)
```

---

## Page model

- **Frontmatter:** `title`, `type`, `status`, `description` (one line, ≤120 chars, feeds `INDEX.md`), `updated`. Types and the folder→type map live in [`scripts/kb-schema.json`](scripts/kb-schema.json); templates in [`schema/templates/`](schema/templates/README.md).
- **Compiled Truth / Timeline:** the top of a page is rewritten as facts change; the `## Timeline` below is dated and append-only.
- **Citations:** `[Source: syllabus §Grading, 2099-08-25]`. Conflicting sources are both recorded, never silently resolved. Lecture transcripts live in `raw/` and notes cite them line by line as `[T:NN](...#LNN)`.
- **Resolution stamps:** when new content settles an open question elsewhere, that page gets `**Resolved YYYY-MM-DD → [[page]]:** one line`.
- **Plans live in their own silo.** "Might study abroad" gets a `type: plan` page linked from the profile, never a sentence on the profile. If the plan dies, nothing stale is left in your compiled truth.
- **DEMO pages** start with `> DEMO — fictional example; delete once you add real pages.` Find them all with `grep -rl '^> DEMO — fictional' --include='*.md' .`

---

## Skills

Claude Code picks a skill when your request matches it, or you type `/<name>`. Other agents can read the same files as plain procedures. Details: [`.claude/skills/README.md`](.claude/skills/README.md).

| Skill | Use it for |
|---|---|
| `setup` | First run: interview, `CLAUDE.local.md`, academic profile, semester page, modules, deny-list, auto-push opt-in, DEMO removal. |
| `kb-capture` | "Save this in my KB": fast verbatim inbox drops through `scripts/kbdrop.sh`. |
| `kb-write` | Durable facts, corrections and decisions; creating or updating any page. |
| `kb-ingest-source` | Articles, papers, PDFs, slides, recordings, transcripts → `sources/`, `research/`, `raw/`. |
| `course-setup` | Syllabus or LMS → course page, semester rows, reminder-ledger bullets. |
| `exam-prep` | An exam-prep silo: facts, coverage map, past-exam pattern, countdown plan. |
| `whats-due` | A dated, cited due list from semester and course pages, reminders, and the LMS module if installed. |
| `kb-triage` | On-demand inbox triage behind safety gates. |
| `kb-garden` | On-demand checks, mechanical fixes, proposals for judgment calls. |
| `kb-secrets` | Pointer-first secret lookup; minimal, never-printed password-manager use. |

Modules add `canvas`, `school-mail`, `international-student`, `reminders` and `sibling-kb` when installed.

---

## Privacy and security

- **Raw files stay out of git.** `raw/` is gitignored; pages cite artifacts by path. Back it up yourself or point it at a synced folder ([docs/backup.md](docs/backup.md)).
- **Secrets are pointers only.** `secrets/README.md` says which password-manager item holds what, never the value.
- **gitleaks on every commit.** The pre-commit hook scans staged changes with [`.gitleaks.toml`](.gitleaks.toml) and refuses to commit if gitleaks is missing. CI runs it again.
- **A leak gate before anything goes public.** `bash scripts/leak-gate.sh` checks everything git would publish (files, names, commit messages, history) against **your own deny-list** kept outside the repo (`~/.config/college-kb/denylist.txt`), plus raw files, `*.local*` files, home paths, IP addresses and gitleaks findings.
- **Auto-push is off by default.** Turn it on with `git config kb.autopush true`.
- Untrusted text (web pages, emails, PDFs) is treated as data; agents ignore instructions inside it.

More in [docs/privacy.md](docs/privacy.md).

---

## Optional modules

Inactive until installed: `bash modules/install.sh --list`, then `bash modules/install.sh <name>` and the module README's steps. See [modules/README.md](modules/README.md).

| Module | What it adds |
|---|---|
| [**school-mail**](modules/school-mail/README.md) | **Read your school Outlook / Microsoft 365 mail without Graph API or MCP access.** Many schools block third-party app consent; this module reads Thunderbird's local offline copy instead, read-only, and cites messages without committing them. Also works for Gmail and IMAP. |
| [lms-canvas](modules/lms-canvas/README.md) | Read-only Canvas from the shell: courses, assignments, due dates, grades, files; a what's-due sweep. Never submits. |
| [international-student](modules/international-student/README.md) | Status-document pages, key dates, advising-email records; scans stay in `raw/`. Not legal advice. |
| [reminders](modules/reminders/README.md) | Ledger dedupe, date resolution, `.ics` export, and an optional hookup to whatever scheduler you use. |
| [devices](modules/devices/README.md) | One page per machine and incident write-ups. |
| [trips](modules/trips/README.md) | Trip-planning silos. |
| [sibling-kb](modules/sibling-kb/README.md) | Route between this KB and a club, lab or startup KB without mixing them. |

---

## Academic integrity

- **Your courses' AI policies apply.** Every course page has a slot for the course's AI-use and collaboration policy, quoted from the syllabus with its source, and the skills read it first. `exam-prep` builds coverage maps and study schedules from your own materials; it does not write graded work.
- **Course materials stay out of git.** Slides, past exams and textbooks belong in `raw/` or a local course folder named in `CLAUDE.local.md`, not in your repo, and never in a public one.
- When a policy is unclear, the agent writes "not stated in the syllabus" and suggests asking the instructor.

---

## Works with Obsidian (optional)

Open the repo folder as a vault. Pages use `[[wikilinks]]` and YAML frontmatter, so links, backlinks and graph view work as-is. Obsidian's workspace and cache files are gitignored. You never need Obsidian; the agent and the scripts don't.

Linux and WSL work the same as macOS. On Windows, run the scripts from Git Bash or WSL.

---

## For agents

Read [`AGENTS.md`](AGENTS.md) first; it is the contract. Then `INDEX.md` and `GLOSSARY.md`. Task procedures are in `.claude/skills/<name>/SKILL.md`. Why each rule exists: [docs/DESIGN.md](docs/DESIGN.md).

---

## Credits and license

- The core idea is Andrej Karpathy's **LLM Wiki** pattern: an LLM that maintains a persistent, interlinked Markdown wiki instead of re-deriving answers from raw documents every time.
- Sibling project: [**slava-stack**](https://github.com/Slava-code/slava-stack), the same approach for a startup's knowledge base.
- [MIT License](LICENSE).
