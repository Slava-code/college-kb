#!/usr/bin/env python3
"""Check a commit subject against `<scope>: <verb> <slug-or-summary>` (scopes/verbs from kb-schema.json).

Warning-only by default; set KB_COMMIT_STRICT=1 to reject non-matching subjects.
Usage: commit-msg-check.py <commit-msg-file>   (or pipe a subject on stdin)
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path

SCHEMA = json.loads((Path(__file__).resolve().parent / 'kb-schema.json').read_text(encoding='utf-8'))
SCOPES = '|'.join(map(re.escape, SCHEMA['commit_scopes']))
VERBS = '|'.join(map(re.escape, SCHEMA['commit_verbs']))
PATTERN = re.compile(rf'^({SCOPES}): ({VERBS})(?: .+)?$')
NO_SLUG = set(SCHEMA['commit_no_slug'])


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if path:
        with open(path, encoding='utf-8') as fh:
            subject = fh.readline().strip()
    else:
        subject = sys.stdin.readline().strip()
    if subject in NO_SLUG or (PATTERN.match(subject) and not subject.endswith(' ')):
        return 0
    if subject.startswith(('Merge ', 'Revert ', 'fixup! ', 'squash! ')):
        return 0
    msg = (f'commit subject does not match the KB format: {subject!r}\n'
           f'expected: <scope>: <verb> <slug-or-summary>  (see AGENTS.md §Commit format)')
    if os.environ.get('KB_COMMIT_STRICT') == '1':
        print('ERROR: ' + msg, file=sys.stderr)
        return 1
    print('WARNING: ' + msg, file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
