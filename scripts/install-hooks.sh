#!/usr/bin/env bash
# install-hooks.sh — point git at the versioned hooks in scripts/hooks/.
#
# Hooks are tracked files, so `git pull` updates them; run this once per clone.
#   pre-commit  gitleaks staged scan, INDEX.md rebuild + stage, kb-lint,
#               reminder ledger check, warn-only wikilink check
#   commit-msg  commit subject format check (warn-only unless KB_COMMIT_STRICT=1)
#   post-commit push, ONLY if you opted in: git config kb.autopush true
#   post-merge  re-link raw/ domains after a pull, only when a raw store is set
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if ! git -C "$ROOT" rev-parse --git-dir >/dev/null 2>&1; then
  echo "Not a git repo yet: $ROOT (run: git init -b main)" >&2
  exit 1
fi
chmod +x "$ROOT"/scripts/hooks/* "$ROOT"/scripts/*.sh "$ROOT"/scripts/*.py
git -C "$ROOT" config core.hooksPath scripts/hooks
echo "core.hooksPath = scripts/hooks (pre-commit, commit-msg, post-commit, post-merge)"

if command -v gitleaks >/dev/null 2>&1; then
  echo "gitleaks: $(gitleaks version 2>/dev/null || echo installed)"
else
  echo "WARNING: gitleaks is not installed; commits will be refused until it is." >&2
  echo "  macOS: brew install gitleaks   Windows: scoop install gitleaks (or winget)" >&2
  echo "  Linux: download a release from https://github.com/gitleaks/gitleaks/releases" >&2
fi

if [ "$(git -C "$ROOT" config --bool --get kb.autopush 2>/dev/null || echo false)" = "true" ]; then
  echo "auto-push: ON (post-commit pushes when an upstream exists)"
else
  echo "auto-push: off (opt in with: git config kb.autopush true)"
fi
