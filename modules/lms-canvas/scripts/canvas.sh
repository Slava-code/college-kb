#!/usr/bin/env bash
# canvas.sh — small read-only wrapper around the Canvas LMS REST API.
#
# Config lives OUTSIDE the repo, in an env file (default ~/.config/canvas/env,
# mode 600; override the location with CANVAS_ENV):
#
#   CANVAS_BASE_URL=https://canvas.example.edu
#   CANVAS_TOKEN=<your access token>
#
# The token is never echoed and never put on a command line (it reaches curl on
# stdin through --config -, so it does not show up in `ps`). Only GET requests
# are supported on purpose: submitting, posting and replying stay with the
# student (see modules/lms-canvas/README.md).
#
# Usage:
#   scripts/canvas.sh get <api-path> [-o FILE] [--no-paginate] [--pretty]
#   scripts/canvas.sh whoami
#   scripts/canvas.sh url <canvas-web-url>
#   scripts/canvas.sh download <file-id> <dest-file-or-dir>
#
# <api-path> is relative to /api/v1, e.g. "courses?enrollment_state=active".
# A leading "/api/v1/" or the full https://<base>/api/v1/... URL also works.
# List endpoints are paginated automatically (per_page=100, following the
# Link: rel="next" header) and the pages are merged into one JSON array.
set -euo pipefail

die() { echo "canvas.sh: $*" >&2; exit 1; }

usage() { sed -n '2,/^set -euo/p' "$0" | sed -e '$d' -e 's/^# \{0,1\}//'; }

load_config() {
  local env_file="${CANVAS_ENV:-${XDG_CONFIG_HOME:-$HOME/.config}/canvas/env}"
  if [ -f "$env_file" ]; then
    if [ -n "$(find "$env_file" \( -perm -g=r -o -perm -o=r \) 2>/dev/null)" ]; then
      echo "canvas.sh: warning: $env_file is readable by other users; run: chmod 600 \"$env_file\"" >&2
    fi
    set -a
    # shellcheck disable=SC1090
    . "$env_file"
    set +a
  fi
  [ -n "${CANVAS_BASE_URL:-}" ] || die "CANVAS_BASE_URL is not set (put it in $env_file)"
  [ -n "${CANVAS_TOKEN:-}" ] || die "CANVAS_TOKEN is not set (put it in $env_file, mode 600)"
  CANVAS_BASE_URL="${CANVAS_BASE_URL%/}"
  case "$CANVAS_BASE_URL" in
    https://*) ;;
    http://localhost:*|http://127.0.0.1:*) ;;   # local mock servers for testing only
    *) die "CANVAS_BASE_URL must start with https:// (got a non-https URL)" ;;
  esac
  command -v curl >/dev/null || die "curl is required"
  command -v python3 >/dev/null || die "python3 is required"
}

# Normalize an API path or URL to a full URL under $CANVAS_BASE_URL/api/v1/.
api_url() {
  local p="$1"
  case "$p" in
    "$CANVAS_BASE_URL"/api/v1/*) printf '%s' "$p"; return ;;
    http://*|https://*) die "refusing a URL outside CANVAS_BASE_URL (the token is only sent to your school's Canvas)" ;;
  esac
  p="${p#/}"; p="${p#api/v1/}"
  printf '%s/api/v1/%s' "$CANVAS_BASE_URL" "$p"
}

add_per_page() {
  case "$1" in
    *per_page=*) printf '%s' "$1" ;;
    *\?*) printf '%s&per_page=100' "$1" ;;
    *) printf '%s?per_page=100' "$1" ;;
  esac
}

# fetch URL BODY_FILE HEADER_FILE -> prints the HTTP status code
fetch() {
  printf 'header = "Authorization: Bearer %s"\n' "$CANVAS_TOKEN" |
    curl -sS --config - --proto '=https,http' -H 'Accept: application/json' \
      -D "$3" -o "$2" -w '%{http_code}' "$1"
}

explain_status() {
  case "$1" in
    401) echo "401 Unauthorized: the token is missing, expired, revoked, or still pending activation (Canvas: Account > Settings > Approved Integrations)." ;;
    403) echo "403 Forbidden: this course hides that tool for students (a disabled Files tab is common; take file IDs from modules instead)." ;;
    404) echo "404 Not Found: check the course/assignment IDs in the path." ;;
    *) echo "HTTP $1" ;;
  esac
}

next_link() {
  tr -d '\r' < "$1" | grep -i '^link:' | sed 's/^[Ll][Ii][Nn][Kk]: *//' | tr ',' '\n' |
    grep 'rel="next"' | sed -E 's/.*<([^>]+)>.*/\1/' | head -n1 || true
}

cmd_get() {
  local path="" out="" paginate=1 pretty=0
  while [ $# -gt 0 ]; do
    case "$1" in
      -o) out="${2:?-o needs a file}"; shift 2 ;;
      --no-paginate) paginate=0; shift ;;
      --pretty) pretty=1; shift ;;
      -*) die "unknown option $1" ;;
      *) [ -z "$path" ] || die "one api path at a time"; path="$1"; shift ;;
    esac
  done
  [ -n "$path" ] || die "get needs an api path (try: scripts/canvas.sh get courses)"
  local url
  url="$(api_url "$path")" || exit 1
  url="$(add_per_page "$url")"
  CANVAS_TMP="$(mktemp -d "${TMPDIR:-/tmp}/canvas.XXXXXX")"
  trap 'rm -rf "${CANVAS_TMP:-}"' EXIT
  local tmp="$CANVAS_TMP"
  local n=0 code
  while [ -n "$url" ]; do
    n=$((n + 1))
    code="$(fetch "$url" "$tmp/page$n.json" "$tmp/head$n.txt")"
    if [ "$code" -lt 200 ] || [ "$code" -ge 300 ]; then
      explain_status "$code" >&2
      head -c 500 "$tmp/page$n.json" >&2 || true; echo >&2
      exit 2
    fi
    [ "$paginate" = 1 ] || break
    url="$(next_link "$tmp/head$n.txt")"
    case "$url" in ""|"$CANVAS_BASE_URL"/*) ;; *) die "pagination link left CANVAS_BASE_URL; stopping" ;; esac
    [ "$n" -lt 200 ] || die "stopped after 200 pages"
  done
  python3 -I - "$tmp" "$n" "$pretty" > "$tmp/merged.json" <<'PY'
import json, sys
d, n, pretty = sys.argv[1], int(sys.argv[2]), sys.argv[3] == '1'
pages = [json.load(open(f'{d}/page{i}.json', encoding='utf-8')) for i in range(1, n + 1)]
if all(isinstance(p, list) for p in pages):
    out = [x for p in pages for x in p]
elif len(pages) == 1:
    out = pages[0]
else:  # paginated object, e.g. {"quiz_submissions": [...]}: concatenate list values
    out = pages[0]
    for p in pages[1:]:
        for k, v in p.items():
            if isinstance(v, list) and isinstance(out.get(k), list):
                out[k].extend(v)
json.dump(out, sys.stdout, indent=2 if pretty else None, ensure_ascii=False)
sys.stdout.write('\n')
PY
  if [ -n "$out" ]; then mv "$tmp/merged.json" "$out"; echo "wrote $out ($n page(s))" >&2
  else cat "$tmp/merged.json"; fi
}

cmd_whoami() {
  local me; me="$(cmd_get users/self --no-paginate)" || exit 2
  printf '%s' "$me" | python3 -I -c 'import json,sys; u=json.load(sys.stdin); print("ok: user id %s (%s)" % (u.get("id"), u.get("name")))'
}

# Turn a Canvas web URL into the matching API path (no network call).
cmd_url() {
  local u="${1:?url needs a Canvas web URL}"
  python3 -I - "$u" <<'PY'
import re, sys
from urllib.parse import urlsplit
p = urlsplit(sys.argv[1]).path.strip('/')
p = re.sub(r'^api/v1/', '', p)
special = [
    (r'^courses/(\d+)$', r'courses/\1?include[]=syllabus_body'),
    (r'^courses/(\d+)/assignments/syllabus$', r'courses/\1?include[]=syllabus_body'),
    (r'^courses/(\d+)/announcements$', r'courses/\1/discussion_topics?only_announcements=true'),
    (r'^courses/(\d+)/grades$', r'courses/\1/assignments?include[]=submission'),
    (r'^courses/(\d+)/assignments/(\d+)$', r'courses/\1/assignments/\2?include[]=submission'),
    (r'^courses/(\d+)/files/(\d+)(/.*)?$', r'courses/\1/files/\2'),
    (r'^courses/(\d+)/modules/items/(\d+)$', r'courses/\1/module_item_redirect/\2  (web-only redirect; list courses/\1/modules?include[]=items instead)'),
]
for pat, rep in special:
    if re.match(pat, p):
        print(re.sub(pat, rep, p)); break
else:
    print(p)  # most course paths map 1:1 (quizzes/<id>, pages/<slug>, discussion_topics/<id>, modules)
PY
}

cmd_download() {
  local fid="${1:?download needs a file id}" dest="${2:?download needs a destination}"
  case "$fid" in *[!0-9]*) die "file id must be numeric (take it from modules?include[]=items content_id)";; esac
  local meta; meta="$(cmd_get "files/$fid" --no-paginate)" || exit 2
  local name url
  name="$(printf '%s' "$meta" | python3 -I -c 'import json,sys,re; m=json.load(sys.stdin); print(re.sub(r"[^A-Za-z0-9._-]+","-",m.get("display_name") or m.get("filename") or "file").strip("-") or "file")')"
  url="$(printf '%s' "$meta" | python3 -I -c 'import json,sys; print(json.load(sys.stdin).get("url") or "")')"
  [ -n "$url" ] || die "Canvas returned no download URL for file $fid (locked or unpublished?)"
  if [ -d "$dest" ]; then dest="${dest%/}/$name"; fi
  [ ! -e "$dest" ] || die "refusing to overwrite $dest"
  # The returned URL is pre-signed (it carries a verifier), so no token is sent with it.
  curl -sS -L --fail --proto '=https,http' -o "$dest" "$url"
  echo "saved $dest" >&2
}

main() {
  local cmd="${1:-}"; [ $# -gt 0 ] && shift
  case "$cmd" in
    get) load_config; cmd_get "$@" ;;
    whoami) load_config; cmd_whoami ;;
    url) CANVAS_BASE_URL="${CANVAS_BASE_URL:-}"; cmd_url "$@" ;;
    download) load_config; cmd_download "$@" ;;
    -h|--help|help|"") usage ;;
    *) die "unknown command $cmd (try --help)" ;;
  esac
}

main "$@"
