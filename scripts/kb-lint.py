#!/usr/bin/env python3
"""Frontmatter lint for the KB, plus a drift check between AGENTS.md and kb-schema.json.

Usage:
  python3 scripts/kb-lint.py            # lint every page
  python3 scripts/kb-lint.py --staged   # lint only staged .md files (pre-commit hook)
  python3 scripts/kb-lint.py PATH...    # lint the given repo-relative paths
  --root DIR                            # read pages from DIR instead of the repo
                                        # (the pre-commit hook passes an export
                                        # of the staged tree)
"""
from __future__ import annotations
import argparse, datetime, json, re, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO  # where pages are read from; --root changes it
SCHEMA = json.loads((REPO / 'scripts' / 'kb-schema.json').read_text(encoding='utf-8'))
REQUIRED = set(SCHEMA['required_frontmatter'])
VALID_TYPES = set(SCHEMA['valid_types'])
DESC_MAX = int(SCHEMA.get('description_max_chars', 120))
FREEFORM = set(SCHEMA['freeform_files'])
OPTIONAL_DIRS = set(SCHEMA.get('frontmatter_optional_dirs', []))
SKIP_DIRS = set(SCHEMA['lint_skip_dirs'])
PATH_TYPE = {folder: set(types) for folder, types in SCHEMA['path_types'].items()}
FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.S)
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def staged_files() -> list[str]:
    out = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'],
                                  cwd=REPO, text=True)
    return [x for x in out.splitlines() if x.endswith('.md')]


def valid_date(s: str) -> bool:
    """YYYY-MM-DD and a real calendar date (rejects 2099-13-40)."""
    if not DATE_RE.match(s):
        return False
    try:
        datetime.datetime.strptime(s, '%Y-%m-%d')
    except ValueError:
        return False
    return True


def parse_fm(text: str) -> dict[str, str]:
    m = FM_RE.match(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ':' in line and not line.startswith((' ', '\t', '-')):
            k, v = line.split(':', 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def needs_frontmatter(rel: Path) -> bool:
    if rel.suffix != '.md' or rel.name in FREEFORM:
        return False
    # Inbox drops are verbatim capture (only `via:`/`captured:` metadata); runs/ holds
    # reports and prompts. Neither is indexed or answered from as compiled truth.
    if rel.parts and rel.parts[0] in OPTIONAL_DIRS:
        return False
    return True


def lint_path(rel_s: str) -> list[str]:
    rel = Path(rel_s)
    path = ROOT / rel
    if not path.is_file() or not needs_frontmatter(rel):
        return []
    fm = parse_fm(path.read_text(encoding='utf-8'))
    errs = []
    missing = sorted(REQUIRED - set(fm))
    if missing:
        errs.append(f'missing frontmatter keys: {", ".join(missing)}')
    typ = fm.get('type')
    if typ and typ not in VALID_TYPES:
        errs.append(f'invalid type: {typ} (add it to scripts/kb-schema.json valid_types first)')
    desc = fm.get('description', '')
    if len(desc) > DESC_MAX:
        errs.append(f'description too long: {len(desc)} > {DESC_MAX}')
    upd = fm.get('updated')
    if upd and not valid_date(upd):
        errs.append(f'updated must be a real date in YYYY-MM-DD form: {upd}')
    folder = rel.parts[0] if len(rel.parts) > 1 else ''
    allowed = PATH_TYPE.get(folder)
    if allowed and typ and typ not in allowed:
        errs.append(f'type {typ!r} does not match folder {folder!r} (allowed: {sorted(allowed)})')
    return [f'{rel_s}: {e}' for e in errs]


def agents_list(text: str, heading: str) -> list[str]:
    m = re.search(rf'^{re.escape(heading)}\s*\n\s*```text\n(.*?)```', text, re.S | re.M)
    if not m:
        return []
    return [x.strip() for x in m.group(1).replace('\n', ',').split(',') if x.strip()]


def schema_drift() -> list[str]:
    """AGENTS.md's human-readable scope/verb lists must match scripts/kb-schema.json."""
    errs = []
    bad_types = sorted({t for ts in PATH_TYPE.values() for t in ts} - VALID_TYPES)
    if bad_types:
        errs.append(f'scripts/kb-schema.json: path_types use types missing from valid_types: {bad_types}')
    agents = ROOT / 'AGENTS.md'
    if not agents.exists():
        return errs + ['AGENTS.md is missing']
    text = agents.read_text(encoding='utf-8')
    for heading, key in (('Allowed scopes:', 'commit_scopes'), ('Allowed verbs:', 'commit_verbs')):
        doc = agents_list(text, heading)
        if not doc:
            errs.append(f'AGENTS.md: could not find the {heading!r} code block')
        elif set(doc) != set(SCHEMA[key]):
            only_doc = sorted(set(doc) - set(SCHEMA[key]))
            only_json = sorted(set(SCHEMA[key]) - set(doc))
            errs.append(f'AGENTS.md {heading!r} drifted from scripts/kb-schema.json {key} '
                        f'(only in AGENTS.md: {only_doc}; only in JSON: {only_json})')
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--staged', action='store_true', help='lint only staged .md files')
    ap.add_argument('--root', help='read pages from this directory instead of the repo')
    ap.add_argument('files', nargs='*')
    args = ap.parse_args()
    global ROOT
    if args.root:
        ROOT = Path(args.root).resolve()
    if args.staged:
        files = staged_files()
    else:
        files = args.files or [p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*.md')]
    files = [f for f in files if not (set(Path(f).parts) & SKIP_DIRS)]
    errors = schema_drift()
    for f in files:
        errors.extend(lint_path(f))
    if errors:
        print('kb-lint failed:', file=sys.stderr)
        for e in errors:
            print('  - ' + e, file=sys.stderr)
        return 1
    print(f'kb-lint ok ({len(files)} files checked)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
