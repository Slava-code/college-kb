---
title: "Reminder ledger — YYYY"
type: reminder
status: active
description: "Proposed and scheduled YYYY reminders: <headline items>"
updated: YYYY-MM-DD
---

# Reminder ledger — YYYY

<!-- One bullet per reminder. Every bullet carries status: and scheduler_ref:
     (checked by scripts/reminder-ledger-check.py). Times use REMINDER_* from THRESHOLDS.md.
     Bullet shape:
     - YYYY-MM-DD HH:MM <zone> · <what to do> · status: <...> · scheduler_ref: <none|id> · source: `<page>`  -->

## Proposed / not scheduled

- YYYY-MM-DD 08:00 <zone> · <reminder text> · status: proposed-only · scheduler_ref: none · source: `<folder/page>`

## Needs clarification

- <when?> · <text> · status: needs-clarification · scheduler_ref: none · reason: <what is ambiguous> · source: `<folder/page>`

## Scheduled

- YYYY-MM-DD HH:MM <zone> · <text> · status: scheduled · scheduler_ref: <calendar event id or routine id> · source: `<folder/page>`

## Done / cancelled

- YYYY-MM-DD · <text> · status: completed · scheduler_ref: <id or none>
