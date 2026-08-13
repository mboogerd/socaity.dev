#!/usr/bin/env bash
# The one command: validate the graph, render the site, prove the build is
# byte-identical across two runs, and prove the validator actually fails.
#
#   tools/check.sh            (uses python3; PYTHON=... to override)
#
# The HTML gate runs over the render this script just produced, because the
# render is what the public loads (council/socaity-0hb.md §J).
#
# Exits non-zero on any failure, so it is safe as a required CI check.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${PYTHON:-python3}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "== 1/5 validate the example graph"
"$PY" "$ROOT/tools/validate/validate.py" --root "$ROOT"

echo "== 2/5 render twice"
"$PY" "$ROOT/tools/render/render.py" --root "$ROOT" --out "$ROOT/site"
"$PY" "$ROOT/tools/render/render.py" --root "$ROOT" --out "$TMP/site-again"

echo "== 3/5 assert the two renders are byte-identical"
diff -r "$ROOT/site" "$TMP/site-again"
A="$(cd "$ROOT/site" && find . -type f | sort | xargs shasum -a 256 | shasum -a 256)"
B="$(cd "$TMP/site-again" && find . -type f | sort | xargs shasum -a 256 | shasum -a 256)"
if [ "$A" != "$B" ]; then
  echo "FAIL: render is not reproducible"
  exit 1
fi
echo "identical, tree digest: $A"

echo "== 4/5 run the HTML gate over the render"
"$PY" "$ROOT/tools/gates/html_gate.py" --root "$ROOT" --site site

echo "== 5/5 assert the validator rejects a broken graph"
mkdir -p "$TMP/broken/graph"
cp -R "$ROOT/graph/nodes" "$TMP/broken/graph/nodes"
cp -R "$ROOT/graph/tickets" "$TMP/broken/graph/tickets"
BROKEN="$(ls "$TMP/broken/graph/nodes" | head -1)"
# Point an edge at a node that does not exist, and break the slug pinning.
"$PY" - "$TMP/broken/graph/nodes/$BROKEN" <<'PYEOF'
import sys
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
text = text.replace("to: n-", "to: n-aaaaaaaaaaaaaaaaaaaaaaaaaa # ", 1)
open(path, "w", encoding="utf-8").write(text.replace("schema: 1", "schema: 2", 1))
PYEOF
if "$PY" "$ROOT/tools/validate/validate.py" --root "$TMP/broken" >"$TMP/out" 2>&1; then
  echo "FAIL: validator accepted a broken graph"
  cat "$TMP/out"
  exit 1
fi
grep -q "FAIL" "$TMP/out"
echo "validator rejected it:"
sed 's/^/    /' "$TMP/out"

echo "== all checks passed"
