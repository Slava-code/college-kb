---
title: "Canvas API access"
type: note
status: active
description: "DEMO: Example State University Canvas API token, how it was obtained, where it lives, when it expires"
aliases: ["Canvas", "Canvas API", "Canvas token", "LMS"]
updated: 2099-09-05
---

> DEMO — fictional example; delete once you add real pages.

# Canvas API access

## Compiled Truth

Example State University runs Canvas at `https://canvas.example.edu`. **Students cannot generate their own access tokens there**; the token option is not offered on student accounts, so a token has to come from IT. [Source: Canvas settings page, 2099-08-25]

**How the token was obtained:** an "API access" request through the IT help desk portal, naming the purpose (read-only access for a personal study tool). IT issued the token and handed it over through the help desk ticket. It worked on the first `whoami`. [Source: IT help desk ticket and session, 2099-09-03]

**Expiry:** IT issues student tokens for one term at a time, so this one expires at the end of fall finals, **2099-12-11**. Renewal is a recurring chore; the request goes in about two weeks early because approval took a few days. [Source: IT help desk ticket, 2099-09-03]

**Where it lives:** password-manager item `Canvas token (DEMO)`, pointer in `secrets/README.md`. The working copy is in `~/.config/canvas/env` (mode 600), outside the repo. It never goes in git or in chat.

**How the agent uses it:** on request only, through `scripts/canvas.sh` and the `canvas` skill. It reads the API first and uses the browser only for LTI or iframe content. It never submits or posts.

## Open Threads

- Does the DEMO 101 Files tab stay disabled all term? If so, syllabus updates have to be pulled from modules.

## Timeline

### 2099-08-25 — Self-service not available

No token option on the student account, so a request went in through the IT help desk. [Source: Canvas settings page, 2099-08-25]

### 2099-09-05 — Token active

The token was issued on 2099-09-03 and stored on 2099-09-05. `scripts/canvas.sh whoami` returned ok. Renewal reminder proposed for 2099-11-27. [Source: session, 2099-09-05]
