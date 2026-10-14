#!/usr/bin/env bash
# Plant fake secrets in a temp dir and confirm .gitleaks.toml catches them.
# Nothing is written inside the repo and the planted values are never printed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if ! command -v gitleaks >/dev/null 2>&1; then
  echo "ERROR: gitleaks not installed (see scripts/README.md for install options)" >&2
  exit 1
fi
TMPBASE="${TMPDIR:-/tmp}"
TMP="$(mktemp -d "${TMPBASE%/}/kb-gitleaks-smoke.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
mkdir "$TMP/tree"
# Build the fake values at runtime so this script itself never contains one.
printf 'github_pat=%s\n' "ghp_$(printf 'a%.0s' $(seq 1 36))" > "$TMP/tree/github-pat.txt"
printf 'api_key=%s\n' "$(printf 'b%.0s' $(seq 1 32))" > "$TMP/tree/assignment.txt"
set +e
gitleaks dir "$TMP/tree" --config "$ROOT/.gitleaks.toml" --no-banner --redact >"$TMP/out" 2>&1
status=$?
set -e
if [ "$status" -eq 0 ]; then
  echo "ERROR: gitleaks smoke test failed; planted ghp_/api_key-style secrets were not detected" >&2
  cat "$TMP/out" >&2
  exit 1
fi
echo "gitleaks-smoke-test ok"
