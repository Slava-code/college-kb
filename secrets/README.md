# secrets/

Pointers to an external secret store only. Secret values never enter this repo; git ignores everything in this folder except this README.

## Policy

- Keep passwords, API keys, tokens, recovery codes and private keys in a password manager (any vault with a CLI or app works).
- This file may hold only pointer metadata: the vault item name, what it is for, the account it belongs to, where it is used, and rotation notes.
- Never store secret values, masked or partial values, recovery codes, private-key material, OAuth tokens, `.env` contents, screenshots of secrets, or command output containing secrets.
- Agents use the vault only after the student asks for a secret-dependent action in the current session. The student unlocks it in their own shell; the agent fetches the minimum field, passes it to the one command that needs it, never prints or persists it, and the vault is locked afterwards.
- If a secret shows up in the repo or in tool output: stop, rotate or revoke it, and record only a pointer plus a short incident note.

## Pointer entry template

```markdown
- **Service / purpose:** <what the secret unlocks>
  - Vault item: `<item name in your password manager>`
  - Used by: `<config file, CLI, or project>`
  - Owner/account: `<account label>`
  - Rotation/review: <when it expires or should be reviewed>
  - Notes: pointer only; no values
```

## Pointer entries

- **Service / purpose:** DEMO — API key for the DEMO 101 course project (fictional; delete once you add real entries)
  - Vault item: `DEMO 101 project API key`
  - Used by: `~/.config/demo-101/env`, sourced by the project's run script
  - Owner/account: Alex Example's course project account (example.edu)
  - Rotation/review: expires at the end of the fall 2099 term
  - Notes: pointer only; no values
