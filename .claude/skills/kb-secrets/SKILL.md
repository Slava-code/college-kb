---
name: kb-secrets
description: Use when the student asks about passwords, API keys, tokens, an LMS token, a password manager or its CLI, .env files, "where is my X key", or a command that needs a secret; pointer-first lookup, then a minimal, never-printed vault fetch.
---

# kb-secrets

`AGENTS.md` is canonical (§Security); this is only a thin task pointer. Policy and pointer format: `secrets/README.md`.

1. **Never** write a secret value anywhere: not in pages, drops, commit messages, chat, prompts, shell profiles, or command output you echo. That includes masked or partial values, recovery codes, private keys, OAuth tokens, session tokens and `.env` contents.
2. **Pointer first.** For "where is X / what holds X", answer from `secrets/README.md` (vault item name, where it is used). If a pointer answers the question, do not touch the vault.
3. **Vault only on request.** Use the password manager only after the student asks for a secret-dependent action in this session. They unlock it in their own terminal (for example `bw unlock`, `op signin`, or the desktop app's CLI integration) before starting the session; never ask them to paste a master password or session token into chat.
4. **Minimum, piped, not printed.** Fetch the one field needed and hand it straight to the one command that needs it, for example `SOME_TOKEN="$(<vault-cli> get <field> '<item name>')" <command>`, or the manager's own injection feature (such as `op run --env-file`). Never `echo` it, never print full item JSON, never write it to a file in the repo.
5. **Lock when done** (`bw lock`, `op signout`, or the equivalent) and remind the student to clear any exported session variable in their shell.
6. **New secret?** Add only a pointer entry to `secrets/README.md` using its template, and commit `schema: update secrets-pointers`.
7. **Leak found** (in the repo, a drop, or tool output): stop, tell the student to rotate or revoke it now, and record only a pointer plus a short incident note. Removing it from git history is a separate, deliberate step the student approves.
8. Maintenance runs (`kb-triage`, `kb-garden`) never depend on an unlocked vault.
