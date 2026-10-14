---
name: sibling-kb
description: Use when the student names their other knowledge base (a club, lab, startup, or team KB) or asks a question spanning it and this personal KB, or asks to copy something between them; routes reads, cites each source with its prefix, and never mixes the two silently.
---

# sibling-kb — two KBs, never mixed silently

`AGENTS.md` §Routing is canonical. Module docs: `modules/sibling-kb/README.md`.

## 1. Locate

1. Read `CLAUDE.local.md` for the sibling's path, name and citation prefix. If there is no line, or the path does not exist on this machine, say "the <name> KB isn't available on this machine" and answer from this KB only. Never guess or search the disk for it.
2. Before the first read of the session, read the sibling's own contract (`AGENTS.md`, `CLAUDE.md` or `README.md`) and its index. Follow its read rules while you are inside it.

## 2. Route

- Unqualified "KB", "my notes": this repo only.
- The sibling by name ("the robotics KB", "lab notes"): the sibling only.
- An explicit cross question ("does the lab's poster deadline clash with my exams?"): read both and answer in two labeled parts, then give the combined conclusion.
- An ambiguous question that could belong to either: answer from this KB and offer to check the sibling. Do not enter it unasked.

## 3. Cite

- `kb:folder/slug` for this repo and `<prefix>:folder/slug` for the sibling, on every claim in a cross answer.
- If the two KBs disagree (a date, for instance), report both with their prefixes and do not pick one.

## 4. Write

- Writes land in the KB that owns the fact. If unsure, ask.
- Never copy a sibling fact into a personal page, or a personal fact into the sibling, unless the student asks for that specific copy. The sibling may be shared, so grades, status documents, health, finances and other private matters never go there.
- A deliberate dual-home topic (listed in the GLOSSARY entry) is copied as a summary page that cites the owner: `[Source: <prefix>:folder/slug, YYYY-MM-DD]`. Do not duplicate it in full.
- Inside the sibling, its contract governs commits, branches and review. Pull first, follow its commit format, and open a pull request if it says to. Commit each repo separately; one commit never spans both.
