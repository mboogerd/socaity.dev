#!/usr/bin/env bash
# Serve the current worktree's rendered site from a sandbox-readable snapshot.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
SITE="$ROOT/site"
PORT="${1:-8749}"

if [ ! -d "$SITE" ]; then
  echo "preview: missing $SITE; run tools/check.sh or render the site first" >&2
  exit 1
fi

STAGING="$(mktemp -d "${TMPDIR:-/tmp}/socaity-preview.XXXXXX")"
cleanup() {
  rm -rf "$STAGING"
}
trap cleanup EXIT INT TERM
cp -R "$SITE"/. "$STAGING"/

# Avoid inheriting a worktree cwd that a preview sandbox may not be able to read.
cd /tmp
python3 - "$STAGING" "$PORT" <<'PY'
import functools
import http.server
import socketserver
import sys

directory, port = sys.argv[1], int(sys.argv[2])
handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                            directory=directory)
server = socketserver.TCPServer(("127.0.0.1", port), handler)
server.allow_reuse_address = True
try:
    server.serve_forever()
finally:
    server.server_close()
PY
