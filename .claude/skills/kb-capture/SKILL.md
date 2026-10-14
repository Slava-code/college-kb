---
name: kb-capture
description: Use when the student says "put/save/add this in the KB", "remember this", "note this down", or dictates a quick thought, link, or deadline to keep; makes a verbatim inbox/ drop via scripts/kbdrop.sh.
---

# kb-capture

`AGENTS.md` is canonical (§Capture); this is only a thin task pointer. This is the fast path: do not read `INDEX.md`, `GLOSSARY.md`, folder READMEs or existing pages.

1. If the student names a sibling KB (a club, lab or startup KB listed in `CLAUDE.local.md`), capture there instead, using that repo's own capture path. Unqualified "KB" means this repo.
2. If the content was already analyzed in this conversation and has a clear destination page, write that page with `kb-write` instead of hiding finished work in the inbox.
3. Otherwise capture verbatim, preserving the student's wording and any source (URL, sender, course):
   ```bash
   scripts/kbdrop.sh "<text or url>"
   # multi-line:
   printf '%s\n' "<text>" | scripts/kbdrop.sh -
   ```
   Pass multi-line or quote-heavy text through stdin so the shell does not mangle it.
4. Do not classify, fetch, dedupe, schedule or ask follow-ups at capture time unless the student asked for immediate action ("and remind me", "add it to DEMO 101's page now").
5. Never put a secret value in a drop. If the text contains a password, token or recovery code, stop and point to `kb-secrets`.
6. Check the result: the script prints the new file path and commits `inbox: add <timestamp-slug>`. Confirm with `git log -1 --oneline`. Pushing happens only if `kb.autopush` is on; otherwise do not push unless asked.
7. Reply in one line: the drop's path, and that triage (`kb-triage`) will file it.
