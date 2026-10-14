#!/usr/bin/env python3
"""What's-due sweep over Canvas: assignments due soon (and recently overdue) across active courses.

Read-only. Fetches through scripts/canvas.sh, so the token handling and pagination
live in one place. Prints a Markdown table (or JSON with --json); it never writes
into the KB. The agent compares the result with course pages and records changes
itself (see the canvas skill).

Usage:
  python3 scripts/canvas-due.py                      # next 14 days, plus 7 days overdue
  python3 scripts/canvas-due.py --days 7 --overdue-days 0
  python3 scripts/canvas-due.py --term "Fall 2099"   # only courses whose term name matches
  python3 scripts/canvas-due.py --course 12345 --course 67890
  python3 scripts/canvas-due.py --undated --json
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CANVAS_SH = Path(__file__).resolve().parent / 'canvas.sh'


def get(path: str):
    r = subprocess.run(['bash', str(CANVAS_SH), 'get', path], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or f'canvas.sh failed for {path}')
    return json.loads(r.stdout)


def parse_ts(s: str | None) -> datetime | None:
    if not s:
        return None
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def state_of(a: dict, now: datetime) -> str:
    sub = a.get('submission') or {}
    flags = [f for f in ('missing', 'late', 'excused') if sub.get(f)]
    ws = sub.get('workflow_state') or 'unsubmitted'
    due = parse_ts(a.get('due_at'))
    if ws == 'unsubmitted' and due and due < now and not sub.get('excused'):
        flags.append('OVERDUE')
    return ws + (f" ({', '.join(flags)})" if flags else '')


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--days', type=int, default=14, help='look this many days ahead (default 14)')
    ap.add_argument('--overdue-days', type=int, default=7, help='also show items due this many days back (default 7)')
    ap.add_argument('--term', help='substring of the Canvas term name to keep (e.g. "Fall 2099")')
    ap.add_argument('--course', action='append', default=[], help='course id to include (repeatable)')
    ap.add_argument('--undated', action='store_true', help='also list assignments with no due date')
    ap.add_argument('--json', action='store_true', help='print JSON instead of a Markdown table')
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    lo, hi = now - timedelta(days=args.overdue_days), now + timedelta(days=args.days)
    try:
        courses = get('courses?enrollment_state=active&include[]=term')
    except RuntimeError as e:
        print(e, file=sys.stderr)
        return 2
    courses = [c for c in courses if isinstance(c, dict) and c.get('id') and not c.get('access_restricted_by_date')]
    if args.course:
        courses = [c for c in courses if str(c['id']) in set(args.course)]
    if args.term:
        courses = [c for c in courses if args.term.lower() in ((c.get('term') or {}).get('name') or '').lower()]

    rows, errors = [], []
    for c in courses:
        try:
            items = get(f"courses/{c['id']}/assignments?include[]=submission&order_by=due_at")
        except RuntimeError as e:
            errors.append(f"{c.get('course_code') or c['id']}: {(str(e).splitlines() or ['error'])[0]}")
            continue
        for a in items:
            if not a.get('published', True):
                continue
            due = parse_ts(a.get('due_at'))
            if due is None and not args.undated:
                continue
            if due is not None and not (lo <= due <= hi):
                continue
            rows.append({
                'due': due.astimezone().strftime('%Y-%m-%d %a %H:%M') if due else 'undated',
                'sort': due.timestamp() if due else float('inf'),
                'course': c.get('course_code') or c.get('name') or str(c['id']),
                'course_id': c['id'],
                'assignment': (a.get('name') or '').replace('|', '/'),
                'assignment_id': a.get('id'),
                'points': a.get('points_possible'),
                'state': state_of(a, now),
                'url': a.get('html_url') or '',
            })
    rows.sort(key=lambda r: r['sort'])

    if args.json:
        json.dump({'generated': now.isoformat(), 'window_days': [-args.overdue_days, args.days],
                   'items': [{k: v for k, v in r.items() if k != 'sort'} for r in rows], 'errors': errors},
                  sys.stdout, indent=2, ensure_ascii=False)
        print()
    else:
        print(f"Canvas sweep {now.astimezone().strftime('%Y-%m-%d %H:%M')} — due between "
              f"{lo.astimezone():%Y-%m-%d} and {hi.astimezone():%Y-%m-%d}, {len(courses)} course(s)\n")
        print('| Due (local) | Course | Assignment | Pts | State | Link |')
        print('|---|---|---|---|---|---|')
        for r in rows:
            pts = '' if r['points'] is None else f"{r['points']:g}"
            print(f"| {r['due']} | {r['course']} | {r['assignment']} | {pts} | {r['state']} | {r['url']} |")
        if not rows:
            print('| — | — | nothing due in this window | | | |')
        for e in errors:
            print(f'\nwarning: {e}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
