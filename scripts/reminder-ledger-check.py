#!/usr/bin/env python3
"""Validate reminder ledger bullets in reminders/*.md.

Each bullet (`- ...`) must carry `status:` and `scheduler_ref:`:
  status: proposed-only        scheduler_ref: none   (default: recorded, not scheduled anywhere)
  status: needs-clarification  scheduler_ref: none   (+ reason: for ambiguous recurrence)
  status: scheduled            scheduler_ref: <id>   (calendar event id, routine id, ...)
  status: sent | completed | cancelled
"""
from __future__ import annotations
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID = {'proposed-only', 'scheduled', 'sent', 'completed', 'cancelled', 'needs-clarification'}
STATUS_RE = re.compile(r'\bstatus:\s*([A-Za-z-]+)')
REF_RE = re.compile(r'\bscheduler_ref:\s*([^·\n]+)')


def main() -> int:
    errors = []
    ledger_dir = ROOT / 'reminders'
    for path in sorted(ledger_dir.glob('*.md')) if ledger_dir.is_dir() else []:
        if path.name == 'README.md':
            continue
        rel = path.relative_to(ROOT).as_posix()
        in_code = False
        for lineno, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if line.lstrip().startswith('```'):
                in_code = not in_code
                continue
            if in_code or not line.startswith('- '):
                continue
            status_m = STATUS_RE.search(line)
            if not status_m:
                errors.append(f'{rel}:{lineno}: reminder bullet missing status:')
                continue
            status = status_m.group(1).strip()
            if status not in VALID:
                errors.append(f'{rel}:{lineno}: invalid status {status!r}; expected one of {sorted(VALID)}')
            ref_m = REF_RE.search(line)
            if not ref_m:
                errors.append(f'{rel}:{lineno}: reminder bullet missing scheduler_ref:')
                continue
            ref = ref_m.group(1).strip().rstrip('.')
            if status == 'scheduled' and ref == 'none':
                errors.append(f'{rel}:{lineno}: scheduled reminder must record a real scheduler_ref')
            if ref != 'none' and status in {'proposed-only', 'needs-clarification'}:
                errors.append(f'{rel}:{lineno}: {status} reminder must use scheduler_ref: none')
            if (status == 'needs-clarification' and re.search(r'\b(every|recurring|repeat)\b', line, re.I)
                    and 'reason:' not in line):
                errors.append(f'{rel}:{lineno}: ambiguous recurrence should include reason:')
    if errors:
        print('reminder-ledger-check failed:', file=sys.stderr)
        for e in errors:
            print('  - ' + e, file=sys.stderr)
        return 1
    print('reminder-ledger-check ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
