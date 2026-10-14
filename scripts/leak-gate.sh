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
#      Text matching a regex in
#        ${KB_ALLOWLIST:-$HOME/.config/college-kb/allowlist.txt}
#      (e.g. your public GitHub handle) is cut out of a line before the
#      deny-list is tested, so a deny term next to an allowed one still fails.
#      Lines starting with # are comments. Keep both files OUTSIDE the repo;
#      never commit them. Checked in file contents, file names, commit
#      messages and authors, and every diff line in git history.
#   2. raw/ artifacts (anything under raw/ except raw/README.md)
#   3. machine-local files (*.local*, except *.example templates)
#   4. absolute home-directory paths (macOS/Linux/Windows), except placeholders
#   5. IPv4 addresses (except loopback and the RFC 5737 documentation ranges)
#   6. gitleaks findings (publishable tree + git history)
# It also warns (fails with KB_REQUIRE_UTC=1) when a commit carries a
# non-UTC timezone offset, which hints at where you live. Commit with
# TZ=UTC to avoid it (see docs/privacy.md).
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

strip_allowed() {  # $1: one line of text; prints it with every allowlist match blanked out
  local l="$1" m
  if [ -s "$TMP/allow" ]; then
    while IFS= read -r m; do
      [ -n "$m" ] && l="${l//"$m"/ }"
    done < <(printf '%s\n' "$l" | grep -oiE -f "$TMP/allow" || true)
  fi
  printf '%s\n' "$l"
}
denied() {  # $1: one line of text; true if a deny regex matches what the allowlist leaves
  [ -s "$TMP/deny" ] && strip_allowed "$1" | grep -qiE -f "$TMP/deny"
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
  if denied "$f"; then
    hit "$f" "deny-list (file name)"
  fi
  if [ -s "$TMP/deny" ]; then
    { grep -nIiE -f "$TMP/deny" -- "$f" || true; } | while IFS= read -r line; do
      denied "${line#*:}" || continue
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

# History: commit messages, author identities, every diff line (including
# files deleted later), and commit timezones. Reports counts and commit ids only.
if git rev-parse --verify -q HEAD >/dev/null; then
  if [ -s "$TMP/deny" ]; then
    git log --all --format='%H %an <%ae> %cn <%ce>%n%B' > "$TMP/log"
    n=0
    while IFS= read -r line; do
      denied "$line" && n=$((n+1))
    done < <(grep -iE -f "$TMP/deny" "$TMP/log" || true)
    [ "$n" -eq 0 ] || hit "git log ($n line(s))" "deny-list (commit messages/authors)"

    git log -p --all --no-color --no-ext-diff --format='@@kb-commit %h' \
      | awk '/^@@kb-commit /{c=$2; next} {print c "\t" $0}' > "$TMP/hist"
    : > "$TMP/hist-hits"
    while IFS= read -r line; do
      denied "${line#*$'\t'}" && printf '%s\n' "${line%%$'\t'*}" >> "$TMP/hist-hits"
    done < <(grep -iE -f "$TMP/deny" "$TMP/hist" || true)
    if [ -s "$TMP/hist-hits" ]; then
      n="$(wc -l < "$TMP/hist-hits" | tr -d ' ')"
      commits="$(sort -u "$TMP/hist-hits" | tr '\n' ' ')"
      hit "git history diffs ($n line(s) in: ${commits% })" "deny-list (history content)"
    fi
  fi
  tz="$(git log --all --format='%h %ad %cd' --date=format:%z | awk '$2!="+0000" || $3!="+0000" {print $1}' | sort -u)"
  if [ -n "$tz" ]; then
    ntz="$(printf '%s\n' "$tz" | wc -l | tr -d ' ')"
    if [ "${KB_REQUIRE_UTC:-0}" = "1" ]; then
      hit "git history ($ntz commit(s) with a non-UTC offset)" "commit timezone"
    else
      echo "WARNING: $ntz commit(s) carry a non-UTC timezone offset (a location hint). Rewrite them in UTC before publishing; see docs/privacy.md." >&2
    fi
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
