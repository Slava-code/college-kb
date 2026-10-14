#!/usr/bin/env bash
# install.sh — copy an optional module into this KB, never overwriting anything.
#
# Usage:
#   bash modules/install.sh --list               # list available modules
#   bash modules/install.sh <module> [--dry-run]  # copy its files into the repo root
#   bash modules/install.sh <module> --check      # only report missing schema additions
#
# Copies every file under modules/<module>/ to the same relative path at the repo
# root, except the module's own README.md and module.json. Existing files are
# skipped and reported. Afterwards it prints the schema additions from
# module.json that are not yet in scripts/kb-schema.json / AGENTS.md. Apply those
# by hand (or let your agent do it), then run python3 scripts/kb-lint.py.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

list_modules() {
  for d in "$HERE"/*/; do
    [ -f "$d/module.json" ] || continue
    python3 -I - "$d/module.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1], encoding='utf-8'))
print(f"{m['name']:<24} {m['summary']}")
PY
  done
}

check_schema() {
  python3 -I - "$1" "$ROOT" <<'PY'
import json, re, sys
from pathlib import Path
mod = json.load(open(sys.argv[1], encoding='utf-8'))
root = Path(sys.argv[2])
add = mod.get('schema_additions') or {}
if not add:
    print('schema: no additions needed')
    raise SystemExit(0)
schema = json.loads((root / 'scripts' / 'kb-schema.json').read_text(encoding='utf-8'))
todo = []
for key in ('valid_types', 'commit_scopes', 'commit_verbs'):
    missing = [x for x in add.get(key, []) if x not in schema.get(key, [])]
    if missing:
        todo.append(f'scripts/kb-schema.json {key}: add {missing}')
for folder, types in (add.get('path_types') or {}).items():
    have = schema.get('path_types', {}).get(folder)
    if have is None or set(types) - set(have):
        todo.append(f'scripts/kb-schema.json path_types: set "{folder}": {json.dumps(types)}')
agents = (root / 'AGENTS.md').read_text(encoding='utf-8') if (root / 'AGENTS.md').exists() else ''
m = re.search(r'^Allowed scopes:\s*\n\s*```text\n(.*?)```', agents, re.S | re.M)
doc = {x.strip() for x in (m.group(1) if m else '').replace('\n', ',').split(',') if x.strip()}
missing = [s for s in add.get('commit_scopes', []) if s not in doc]
if missing:
    todo.append(f'AGENTS.md "Allowed scopes" block: add {missing}')
if todo:
    print('schema: still to do (same commit), then run python3 scripts/kb-lint.py:')
    for t in todo:
        print('  - ' + t)
    raise SystemExit(3)
print('schema: all additions present')
PY
}

main() {
  local name="${1:-}" mode="${2:-}"
  case "$name" in
    ""|-h|--help) sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    --list) list_modules; exit 0 ;;
  esac
  local src="$HERE/$name"
  [ -f "$src/module.json" ] || { echo "install.sh: no module named '$name' (try --list)" >&2; exit 1; }
  if [ "$mode" = "--check" ]; then check_schema "$src/module.json"; exit $?; fi
  [ -z "$mode" ] || [ "$mode" = "--dry-run" ] || { echo "install.sh: unknown option $mode" >&2; exit 1; }

  local copied=0 skipped=0 rel dest
  while IFS= read -r -d '' f; do
    rel="${f#"$src"/}"
    case "$rel" in README.md|module.json|.DS_Store|*/.DS_Store) continue ;; esac
    dest="$ROOT/$rel"
    if [ -e "$dest" ]; then
      echo "skip   $rel (already exists)"; skipped=$((skipped + 1)); continue
    fi
    if [ "$mode" = "--dry-run" ]; then
      echo "would  $rel"
    else
      mkdir -p "$(dirname "$dest")"
      cp "$f" "$dest"
      [ -x "$f" ] && chmod +x "$dest"
      echo "copied $rel"
    fi
    copied=$((copied + 1))
  done < <(find "$src" -type f -print0 | sort -z)

  echo "-- $name: $copied file(s) ${mode:+(dry run) }copied, $skipped skipped"
  check_schema "$src/module.json" || true
  python3 -I - "$src/module.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1], encoding='utf-8'))
steps = m.get('next_steps') or []
if steps:
    print('next steps (see modules/%s/README.md):' % m['name'])
    for s in steps:
        print('  - ' + s)
print(f"commit when done: schema: add {m['name']}-module")
PY
}

main "$@"
