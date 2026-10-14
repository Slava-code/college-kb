#!/usr/bin/env python3
"""Report [[wikilinks]] whose target page or folder does not exist.

A target resolves if `<target>`, `<target>.md` or `<target>/README.md` exists
relative to the repo root. Exit 1 when anything is missing (the pre-commit hook
treats that as a warning only).

Usage: wikilink-check.py [--root DIR]   (DIR defaults to this repo; the
pre-commit hook passes an export of the staged tree)
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path


def _root_from_argv() -> Path:
    """`--root DIR` points the script at another checkout of the KB, such as the
    staged tree the pre-commit hook exports; the default is this repo."""
    argv = sys.argv[1:]
    for i, a in enumerate(argv):
        if a == '--root' and i + 1 < len(argv):
            return Path(argv[i + 1]).resolve()
        if a.startswith('--root='):
            return Path(a.split('=', 1)[1]).resolve()
    return Path(__file__).resolve().parents[1]


ROOT = _root_from_argv()
SCHEMA = json.loads((Path(__file__).resolve().parent / 'kb-schema.json').read_text(encoding='utf-8'))
SKIP = set(SCHEMA['link_skip_dirs'])
LINK_RE = re.compile(r'\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]')
CODE_RE = re.compile(r'```.*?```|`[^`\n]*`', re.S)


def exists(target: str) -> bool:
    t = target.strip().lstrip('/')
    return any(c.exists() for c in (ROOT / t, ROOT / f'{t}.md', ROOT / t / 'README.md'))


def main() -> int:
    missing = []
    for path in sorted(ROOT.rglob('*.md')):
        rel = path.relative_to(ROOT)
        if any(part in SKIP for part in rel.parts):
            continue
        text = CODE_RE.sub('', path.read_text(encoding='utf-8'))  # links inside code are examples
        for m in LINK_RE.finditer(text):
            target = m.group(1).strip()
            if target.startswith(('http://', 'https://')):
                continue
            if not exists(target):
                missing.append(f'{rel.as_posix()}: missing [[{target}]]')
    if missing:
        print('wikilink-check warnings:', file=sys.stderr)
        for x in missing:
            print('  - ' + x, file=sys.stderr)
        return 1
    print('wikilink-check ok')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
