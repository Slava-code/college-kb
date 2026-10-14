#!/usr/bin/env bash
# link-raw.sh — manage raw/<domain> folders (gitignored binaries: scans, PDFs, transcripts).
#
# Two modes:
#   Local (default, no store configured): raw/<domain> folders are plain local
#     directories. Back them up yourself (see raw/README.md).
#   Synced store: set KB_RAW_STORE (or `git config kb.rawstore <dir>`) to a
#     folder your sync client already backs up, for example
#       Apple cloud drive  ~/Library/Mobile Documents/com~apple~CloudDocs/my-kb-raw
#       Dropbox            ~/Dropbox/my-kb-raw
#       OneDrive           ~/OneDrive/my-kb-raw
#       Syncthing          ~/Sync/my-kb-raw
#     Domain folders then live in the store and raw/<domain> is a gitignored
#     symlink into it, so repo-relative paths (raw/school/...) keep working on
#     every machine.
#
# Usage:
#   scripts/link-raw.sh            # (store mode) link every domain present in the store
#   scripts/link-raw.sh <domain>   # create a new domain (the only sanctioned way)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STORE="${KB_RAW_STORE:-$(git -C "$ROOT" config --get kb.rawstore 2>/dev/null || true)}"
STORE="${STORE/#\~/$HOME}"
DOMAIN="${1:-}"

if [ -n "$DOMAIN" ] && ! printf '%s' "$DOMAIN" | grep -Eq '^[a-z0-9][a-z0-9-]*$'; then
  echo "link-raw: domain must be lowercase letters, digits and dashes: $DOMAIN" >&2
  exit 2
fi

mkdir -p "$ROOT/raw"

if [ -z "$STORE" ]; then
  if [ -n "$DOMAIN" ]; then
    mkdir -p "$ROOT/raw/$DOMAIN"
    echo "created local raw/$DOMAIN (local mode; set KB_RAW_STORE to sync raw/ across machines)"
  else
    echo "local mode (no KB_RAW_STORE / kb.rawstore set): nothing to link."
  fi
  exit 0
fi

mkdir -p "$STORE"
[ -z "$DOMAIN" ] || mkdir -p "$STORE/$DOMAIN"

linked=0
for d in "$STORE"/*/; do
  [ -d "$d" ] || continue
  name="$(basename "$d")"
  target="$ROOT/raw/$name"
  if [ -L "$target" ]; then
    continue
  fi
  if [ -e "$target" ]; then
    echo "WARN: raw/$name exists as a real directory; move its contents into" >&2
    echo "      $STORE/$name, remove raw/$name, then rerun." >&2
    continue
  fi
  ln -s "${d%/}" "$target"
  echo "linked raw/$name -> ${d%/}"
  linked=$((linked+1))
done
echo "done ($linked new link(s))."
