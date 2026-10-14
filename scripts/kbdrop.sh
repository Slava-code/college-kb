#!/usr/bin/env bash
# kbdrop.sh — fast verbatim capture into inbox/.
#
# Usage:
#   scripts/kbdrop.sh <text-or-url>...     # capture the arguments
#   echo "multi-line note" | scripts/kbdrop.sh -   # capture stdin
#
# Writes inbox/YYYY-MM-DD-HHMM-<slug>.md, commits "inbox: add <name>", and
# prints the file path. Pushing is left to the post-commit hook, which pushes
# only when you opted in with `git config kb.autopush true`.
# Tip: alias kbdrop="$HOME/path/to/your-kb/scripts/kbdrop.sh"
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [ "$#" -lt 1 ]; then
  echo "usage: kbdrop <text-or-url>...   |   ... | kbdrop -" >&2
  exit 2
fi
if [ "$*" = "-" ]; then
  TEXT="$(cat)"
else
  TEXT="$*"
fi
if [ -z "${TEXT//[[:space:]]/}" ]; then
  echo "kbdrop: nothing to capture" >&2
  exit 2
fi
TS="$(date +%Y-%m-%d-%H%M)"
SLUG="$(printf '%s' "$TEXT" | head -n 1 | tr '[:upper:]' '[:lower:]' \
  | sed -E 's#https?://##g; s/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/(.{48}).*/\1/; s/-+$//')"
[ -n "$SLUG" ] || SLUG="drop"
NAME="${TS}-${SLUG}"
FILE="$ROOT/inbox/${NAME}.md"
n=2
while [ -e "$FILE" ]; do
  NAME="${TS}-${SLUG}-${n}"; FILE="$ROOT/inbox/${NAME}.md"; n=$((n+1))
done
mkdir -p "$ROOT/inbox"
{
  printf -- '---\nvia: kbdrop\ncaptured: "%s"\n---\n\n' "$(date +%Y-%m-%dT%H:%M:%S%z)"
  printf '%s\n' "$TEXT"
} > "$FILE"
cd "$ROOT"
git add -- "$FILE"
git commit -q -m "inbox: add ${NAME}"
printf '%s\n' "$FILE"
