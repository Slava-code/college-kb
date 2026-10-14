#!/usr/bin/env bash
# leak-gate.sh — privacy gate to run before you make ANY copy of this KB public
# (a template, a fork, a screenshot repo, a blog post's sample folder).
#
# It scans every file git would publish (tracked + untracked-but-not-ignored),
# plus file names, commit messages and git history, and fails on:
#   1. deny-list hits: one extended regex per line in
#        ${KB_DENYLIST:-$HOME/.config/college-kb/denylist.txt}
#      Put YOUR name, nicknames, student ID, school and its domains, employers,
#      professors, roommates, home towns, hostnames and IP prefixes there.
#      Lines that also match a regex in
#        ${KB_ALLOWLIST:-$HOME/.config/college-kb/allowlist.txt}
#      (e.g. your public GitHub handle) are exempt. Lines starting with # are
#      comments. Keep both files OUTSIDE the repo; never commit them.
#   2. raw/ artifacts (anything under raw/ except raw/README.md)
#   3. machine-local files (*.local*, except *.example templates)
#   4. absolute home-directory paths (macOS/Linux/Windows), except placeholders
#   5. IPv4 addresses (except loopback and the RFC 5737 documentation ranges)
#   6. gitleaks findings (publishable tree + git history)
#
# Hits print as file:line and the check name, never the deny-list terms
# themselves, so the output is safe to paste into an issue or CI log.
# A missing deny-list is a warning; the generic checks still run.
# Exit status: 0 clean, 1 any hit.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
DENY="${KB_DENYLIST:-$HOME/.config/college-kb/denylist.txt}"
ALLOW="${KB_ALLOWLIST:-$HOME/.config/college-kb/allowlist.txt}"
TMPBASE="${TMPDIR:-/tmp}"
TMP="$(mktemp -d "${TMPBASE%/}/kb-leak-gate.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

fail=0
hits=0
hit() { printf '  %s  [%s]\n' "$1" "$2"; fail=1; hits=$((hits+1)); }

# Pattern files without comments or blank lines (a blank pattern matches everything).
: > "$TMP/deny"; : > "$TMP/allow"
if [ -f "$DENY" ]; then
  grep -vE '^[[:space:]]*(#|$)' "$DENY" > "$TMP/deny" || true
else
  echo "WARNING: no deny-list at $DENY; running generic checks only." >&2
  echo "         Create it with your own name, school, employers, hosts before publishing." >&2
fi
[ -f "$ALLOW" ] && { grep -vE '^[[:space:]]*(#|$)' "$ALLOW" > "$TMP/allow" || true; }

allowed() {  # stdin: one line of text; true if an allowlist regex matches it
  [ -s "$TMP/allow" ] && grep -qiE -f "$TMP/allow"
}

# [U] keeps this script from matching its own pattern (and common deny-lists).
HOME_RE='(/[U]sers/|/home/|[A-Za-z]:\\[U]sers\\)[A-Za-z0-9._-]+'
HOME_OK='(/[U]sers/|/home/|[A-Za-z]:\\[U]sers\\)(you|your-name|yourname|username|user|example|alex-example|runner)([^A-Za-z0-9._-]|$)'
IP_RE='(^|[^0-9.])([0-9]{1,3}\.){3}[0-9]{1,3}([^0-9.]|$)'
IP_OK='(^|[^0-9.])(127\.0\.0\.1|0\.0\.0\.0|192\.0\.2\.[0-9]{1,3}|198\.51\.100\.[0-9]{1,3}|203\.0\.113\.[0-9]{1,3})([^0-9.]|$)'

git ls-files -z -co --exclude-standard > "$TMP/files"
echo "leak-gate: scanning $(tr -cd '\0' < "$TMP/files" | wc -c | tr -d ' ') publishable files"

mkdir "$TMP/tree"
while IFS= read -r -d '' f; do
  [ -f "$f" ] || continue   # tracked but deleted in the worktree
  case "$f" in
    raw/README.md) ;;
    raw/*) hit "$f" "raw artifact" ;;
  esac
  base="$(basename "$f")"
  case "$base" in
    *.example) ;;
    *.local*) hit "$f" "machine-local file" ;;
  esac
  if [ -s "$TMP/deny" ] && printf '%s\n' "$f" | grep -qiE -f "$TMP/deny" \
     && ! printf '%s\n' "$f" | allowed; then
    hit "$f" "deny-list (file name)"
  fi
  if [ -s "$TMP/deny" ]; then
    { grep -nIiE -f "$TMP/deny" -- "$f" || true; } | while IFS= read -r line; do
      printf '%s\n' "${line#*:}" | allowed && continue
      printf '  %s:%s  [deny-list]\n' "$f" "${line%%:*}"
    done >> "$TMP/deny-hits"
  fi
  { grep -nIE "$HOME_RE" -- "$f" || true; } | while IFS= read -r line; do
    printf '%s\n' "${line#*:}" | sed -E "s#$HOME_OK##g" | grep -qE "$HOME_RE" || continue
    printf '  %s:%s  [absolute home path]\n' "$f" "${line%%:*}"
  done >> "$TMP/generic-hits"
  { grep -nIE "$IP_RE" -- "$f" || true; } | while IFS= read -r line; do
    printf '%s\n' "${line#*:}" | sed -E "s#$IP_OK# #g" | grep -qE "$IP_RE" || continue
    printf '  %s:%s  [IPv4 address]\n' "$f" "${line%%:*}"
  done >> "$TMP/generic-hits"
  mkdir -p "$TMP/tree/$(dirname "$f")"
  cp -p "$f" "$TMP/tree/$f"
done < "$TMP/files"

for h in "$TMP/deny-hits" "$TMP/generic-hits"; do
  if [ -s "$h" ]; then
    cat "$h"; fail=1; hits=$((hits + $(wc -l < "$h")))
  fi
done

# Commit messages and author identities in history.
if git rev-parse --verify -q HEAD >/dev/null; then
  if [ -s "$TMP/deny" ]; then
    git log --all --format='%H %an <%ae> %cn <%ce>%n%B' > "$TMP/log"
    n="$(grep -iE -f "$TMP/deny" "$TMP/log" | { if [ -s "$TMP/allow" ]; then grep -viE -f "$TMP/allow"; else cat; fi; } | wc -l | tr -d ' ' || true)"
    [ "${n:-0}" -eq 0 ] || hit "git log ($n line(s))" "deny-list (commit messages/authors)"
  fi
fi

# gitleaks: the publishable tree, then history.
if [ "${KB_SKIP_GITLEAKS:-0}" = "1" ]; then
  echo "WARNING: KB_SKIP_GITLEAKS=1, skipping gitleaks." >&2
elif ! command -v gitleaks >/dev/null 2>&1; then
  hit "gitleaks" "not installed (see scripts/README.md)"
else
  if ! gitleaks dir "$TMP/tree" --config "$ROOT/.gitleaks.toml" --no-banner --no-color --redact -v >"$TMP/gl-dir" 2>&1; then
    sed "s#$TMP/tree/##g" "$TMP/gl-dir" | grep -E '^(File|Line|RuleID):' | sed 's/^/    /' || true
    hit "working tree" "gitleaks"
  fi
  if git rev-parse --verify -q HEAD >/dev/null; then
    if ! gitleaks git "$ROOT" --config "$ROOT/.gitleaks.toml" --no-banner --no-color --redact -v >"$TMP/gl-git" 2>&1; then
      grep -E '^(File|Line|Commit|RuleID):' "$TMP/gl-git" | sed 's/^/    /' || true
      hit "git history" "gitleaks"
    fi
  fi
fi

if [ "$fail" -ne 0 ]; then
  echo "leak-gate: FAILED ($hits hit(s)). Fix or allowlist each one before publishing." >&2
  exit 1
fi
echo "leak-gate ok"
