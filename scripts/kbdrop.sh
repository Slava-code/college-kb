#!/usr/bin/env bash
# kbdrop.sh — fast verbatim capture into inbox/.
#
# Usage:
#   scripts/kbdrop.sh <text-or-url>...     # capture the arguments
#   echo "multi-line note" | scripts/kbdrop.sh -   # capture stdin
#
# Writes inbox/YYYY-MM-DD-HHMM-<slug>.md, commits ONLY that file as
# "inbox: add <name>" (anything else you had staged stays staged, uncommitted),
# and prints the file path. Pushing is left to the post-commit hook, which
# pushes only when you opted in with `git config kb.autopush true`.
# Text that gitleaks flags as a secret is refused before anything is written;
# store the value in your password manager and capture a pointer instead.
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
if command -v gitleaks >/dev/null 2>&1 && [ "${KB_SKIP_GITLEAKS:-0}" != "1" ]; then
  if ! printf '%s\n' "$TEXT" | gitleaks stdin --no-banner --redact --log-level error \
       --config "$ROOT/.gitleaks.toml" >/dev/null 2>&1; then
    {
      echo "kbdrop: refused: the text looks like it contains a secret (gitleaks). Nothing was written."
      echo "  Put the value in your password manager and capture a pointer instead"
      echo "  (see secrets/README.md and the kb-secrets skill)."
    } >&2
    exit 1
  fi
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
if ! git commit -q -m "inbox: add ${NAME}" -- "$FILE"; then
  # Unstage the drop so the next commit is not blocked by it, and move it to a
  # neutral name in case the slug repeats something sensitive from the text.
  git reset -q -- "$FILE" 2>/dev/null || git rm -q --cached -- "$FILE" 2>/dev/null || true
  KEPT="$ROOT/inbox/${TS}-unsaved-drop.md"
  n=2
  while [ -e "$KEPT" ]; do KEPT="$ROOT/inbox/${TS}-unsaved-drop-${n}.md"; n=$((n+1)); done
  mv -- "$FILE" "$KEPT"
  {
    echo "kbdrop: the commit was refused (see the hook output above), so nothing was committed."
    echo "  The drop is unstaged and kept, uncommitted, at: $KEPT"
    echo "  If gitleaks flagged a secret: delete it (rm \"$KEPT\"), rotate the secret if it was"
    echo "  real, and store a pointer instead (secrets/README.md, kb-secrets skill)."
    echo "  Otherwise fix the reported problem and run: git add -- \"$KEPT\" && git commit -- \"$KEPT\""
  } >&2
  exit 1
fi
printf '%s\n' "$FILE"
