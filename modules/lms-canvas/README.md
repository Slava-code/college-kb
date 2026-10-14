# Module: lms-canvas

Read your Canvas LMS from the shell so your agent can answer "what's due this week?", pull an assignment's rubric, or file a syllabus into the KB, without opening a browser. It is plain `curl` against the Canvas REST API with a personal access token. There is no MCP server, no sync job and no cron.

## When to use it

- Your school runs Canvas (Instructure), and you can get a personal access token.
- You want the agent to read courses, assignments, due dates, grades, modules, announcements and files on request.

Skip it if your school uses another LMS. The pattern carries over to Moodle, Blackboard or D2L, since each has a token-based REST API, but this module only implements Canvas. An adapter would be a new `scripts/<lms>.sh` with the same `get`, `url` and `download` verbs, plus its own skill.

## What's in it

| File (in this module) | Installs to | Purpose |
|---|---|---|
| `scripts/canvas.sh` | `scripts/canvas.sh` | A GET-only curl wrapper. It reads the token from an env file outside the repo, paginates automatically, translates URLs and downloads files. |
| `scripts/canvas-due.py` | `scripts/canvas-due.py` | A what's-due sweep across your active courses. It prints a Markdown table (standard library only). |
| `.claude/skills/canvas/SKILL.md` | `.claude/skills/canvas/SKILL.md` | Agent procedure: API first, the endpoint table, the what's-due sweep, and what never to do. |
| `school/lms-canvas.md` | `school/lms-canvas.md` | A DEMO record of your Canvas access: base URL, token policy and renewal history. Rewrite it with your own facts or delete it. |

## Install

1. Copy the files, without overwriting anything you already have:
   ```bash
   bash modules/install.sh lms-canvas            # add --dry-run to preview
   ```
   Or copy by hand: `cp -n modules/lms-canvas/scripts/canvas.sh modules/lms-canvas/scripts/canvas-due.py scripts/`, `mkdir -p .claude/skills/canvas && cp -n modules/lms-canvas/.claude/skills/canvas/SKILL.md .claude/skills/canvas/`, `cp -n modules/lms-canvas/school/lms-canvas.md school/`.
2. Schema: none needed. The DEMO page is `type: note` in `school/`, which the core schema already allows. Commits use the `school` and `scripts` scopes.
3. Create the env file **outside the repo** (step "Get a token" below):
   ```bash
   mkdir -p ~/.config/canvas && touch ~/.config/canvas/env && chmod 600 ~/.config/canvas/env
   # then edit it so it holds exactly two lines:
   # CANVAS_BASE_URL=https://canvas.example.edu
   # CANVAS_TOKEN=<paste token here>
   ```
   Paste the token with an editor or from your password manager. Do not paste it into an agent chat, and do not use `echo` (shell history).
4. Add a pointer entry in `secrets/README.md`: the vault item name, "used by `~/.config/canvas/env`", and the expiry date. Store the pointer, never the value.
5. Check it: `scripts/canvas.sh whoami` should print `ok: user id ...`.
6. Record in this machine's `CLAUDE.local.md` that lms-canvas is enabled and where the env file lives (the path only, never the contents).
7. Commit: `schema: add lms-canvas-module`.

## Get a token

Token policies **differ by school**:

- **Self-service:** in Canvas, open Account → Settings → Approved Integrations → "+ New Access Token". Give it a purpose label such as "my coding agent" and an expiry date.
- **Disabled for students:** many schools turn self-service off. The button may still render but greyed out, and its tooltip says to contact your Canvas administrators. Request a token through your IT help desk or service catalog by searching for "Canvas access token". Expect a human approval step, a set maximum lifetime (often a few months), and delivery through a secure channel that may expire within days, so collect it promptly.
- **Admin-issued tokens may arrive pending.** Until you click the small "activate" link next to the token under Approved Integrations, the API returns `401 Invalid access token` even though the token is correct.
- Put the expiry date in your KB. A renewal reminder is a good use of the `reminders` module. Request the renewal early enough to cover the approval turnaround.

Check your school's acceptable-use policy for API and automation use. Some schools want tokens used only for personal, read-only access, which is all this module does.

## Configuration

| Setting | Where | Default |
|---|---|---|
| `CANVAS_BASE_URL` | env file | none (required), e.g. `https://canvas.example.edu`. Must be https. |
| `CANVAS_TOKEN` | env file | none (required) |
| `CANVAS_ENV` | environment | `${XDG_CONFIG_HOME:-~/.config}/canvas/env` |

`canvas.sh` warns if the env file is readable by other users. It passes the token to curl on stdin, not as an argument, so the token never shows up in process listings. It refuses to send the token to any host other than `CANVAS_BASE_URL`, including pagination links.

## Usage

```bash
scripts/canvas.sh get 'courses?enrollment_state=active&include[]=term' --pretty
scripts/canvas.sh get 'courses/123/assignments?include[]=submission' -o /tmp/a.json
scripts/canvas.sh url 'https://canvas.example.edu/courses/123/assignments/456'
scripts/canvas.sh download 789 raw/school/
python3 scripts/canvas-due.py --days 7 --term "Fall 2099"
```

Quote paths that contain `?`, `&` or `[]`, because the shell expands them otherwise.

## Caveats

- **Read-only on purpose.** The wrapper never submits, posts, replies or changes settings. You submit your own work.
- **Academic integrity.** Your courses' AI-use policies still apply, and the course page has a slot to record each one. This module reads your course data; it does not do graded work.
- **Coverage gaps.** Content inside LTI tools (external homework platforms, video, proctoring) and iframes is not in the Canvas API. A course's Files tab can be disabled (403), in which case you get file IDs from modules. The `syllabus_body` field is often empty because the real syllabus is a PDF.
- **Meeting times and rooms** usually come from your school's course catalog or registrar, not from Canvas.
- **No sync.** Nothing polls Canvas. Run the sweep when you want it. If you want a weekly digest, ask your agent each week, or wire up a scheduler yourself and record it in `reminders/`.
