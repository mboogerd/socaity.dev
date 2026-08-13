#!/usr/bin/env bash
# Run the /claim page's three copy-paste blocks, exactly as published.
#
# This is pre-launch test (a) of council/socaity-ipg.md, minus the humans: it
# cannot tell you whether five developers finish in under three minutes, but it
# can tell you that the commands they will paste actually run, in a clean HOME,
# and produce an attestation that verifies both with stock ssh-keygen and with
# this repository's own checker.  A copy-paste block that does not run is the
# failure mode of the whole surface, so this test asserts on the published
# strings rather than on a copy of them: the blocks are read out of
# tools/render/generators/claim.py, which is what the page renders.
#
# Two documented substitutions, and no others:
#   * the login placeholder becomes a test account name;
#   * `-N ''` is appended to step 1, because a human answers the passphrase
#     prompt and a test cannot.  The prompt is the only thing suppressed.
#
#   tools/claim/test_claim_flow.sh            (PYTHON=... to override python3)
#
# Exits non-zero on any failure, so it is safe as a required CI check.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(dirname "$ROOT")"
PY="${PYTHON:-python3}"
LOGIN="claim-flow-test"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# A clean HOME: the flow writes to ~/.socaity, and a test that reuses the
# operator's real key proves nothing about a first-time contributor.
export HOME="$TMP/home"
mkdir -p "$HOME"

extract() {
  "$PY" - "$ROOT" "$1" "$LOGIN" <<'PYEOF'
import importlib.util, sys
root, which, login = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location(
    "claim_gen", root + "/tools/render/generators/claim.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
if which == "verify":
    lines = list(mod.VERIFY_SSH)
elif which == "repo":
    lines = list(mod.VERIFY_REPO)
elif which == "recompute":
    lines = list(mod.RECOMPUTE)
else:
    lines = list(mod.STEPS[int(which) - 1]["commands"])
    if which == "1":
        lines[-1] += " -N ''"          # the documented substitution
sys.stdout.write("\n".join(
    line.replace(mod.LOGIN_PLACEHOLDER, login) for line in lines) + "\n")
PYEOF
}

echo "== the three published blocks, as they will be pasted"
for n in 1 2 3; do
  echo "-- step $n"
  extract "$n" | sed 's/^/     /'
done

echo
echo "== step 1: make a key"
eval "$(extract 1)"
test -f "$HOME/.socaity/claim-key" || { echo "FAIL: no private key"; exit 1; }
test -f "$HOME/.socaity/claim-key.pub" || { echo "FAIL: no public key"; exit 1; }
PERMS="$(ls -l "$HOME/.socaity/claim-key" | cut -c1-10)"
echo "     private key mode $PERMS (the page says it stays on your machine)"

echo "== step 2: sign one line"
eval "$(extract 2)"
test -f "$HOME/.socaity/claim.txt.sig" || { echo "FAIL: no signature"; exit 1; }
grep -q "^link:github:$LOGIN:ssh-ed25519 " "$HOME/.socaity/claim.txt" \
  || { echo "FAIL: the signed line is not the documented shape"; cat "$HOME/.socaity/claim.txt"; exit 1; }

echo "== step 3: print it for pasting"
eval "$(extract 3)" > "$TMP/pasted.txt"
grep -q "BEGIN SSH SIGNATURE" "$TMP/pasted.txt" \
  || { echo "FAIL: step 3 printed no signature block"; exit 1; }
echo "     $(wc -l < "$TMP/pasted.txt" | tr -d ' ') lines to paste"

echo "== the published verification, with stock ssh-keygen"
# Deliberately run from a directory that holds none of the files.  The reader
# pastes this block wherever their terminal happens to be, so a test that first
# cd'd into the key directory (or copied the files next to itself) would pass
# on a block that fails for every human who runs it.
mkdir -p "$TMP/somewhere-else"
cd "$TMP/somewhere-else"
eval "$(extract verify)"

echo "== the same check through this repository's tool, as the page publishes it"
# The page's block is a pipeline run from a checkout, so run it from one.
cd "$ROOT"
eval "$(extract repo)"

echo "== the tool refuses what it should refuse"
fail_case() {
  if "$PY" "$ROOT/tools/claim/verify_claim.py" --login "$2" "$3" >"$TMP/out" 2>&1; then
    echo "FAIL: accepted $1"; exit 1
  fi
  echo "     rejected $1: $(cat "$TMP/out")"
}
sed "s/link:github:$LOGIN:/link:github:someone-else:/" "$TMP/pasted.txt" > "$TMP/tampered.txt"
fail_case "a tampered link line" "someone-else" "$TMP/tampered.txt"
fail_case "an attestation naming another account" "someone-else" "$TMP/pasted.txt"
sed '/BEGIN SSH SIGNATURE/,/END SSH SIGNATURE/d' "$TMP/pasted.txt" > "$TMP/nosig.txt"
fail_case "an attestation with the signature removed" "$LOGIN" "$TMP/nosig.txt"

# The namespace is the only thing stopping a signature made for some other
# purpose -- a git commit, an SSH login -- from being replayed as a claim, so
# a genuine signature over the *same line* in a different namespace must fail.
cp "$HOME/.socaity/claim.txt" "$TMP/otherns.txt"
ssh-keygen -Y sign -q -n git -f "$HOME/.socaity/claim-key" "$TMP/otherns.txt"
cat "$HOME/.socaity/claim.txt" "$TMP/otherns.txt.sig" > "$TMP/wrongns.txt"
fail_case "a valid signature made in another namespace" "$LOGIN" "$TMP/wrongns.txt"

echo "== the binding does not depend on how the login was capitalised"
# The maintainer fixes claim_binding from the pull request author's login; the
# contributor types their own login at step 2 in whatever case they please, and
# signs it.  If the two hashes disagree the validator refuses the claim against
# its escrow, so this has to hold on a *genuinely re-signed* line, not on a
# rewritten one -- the link line is signed, so sed cannot produce this case.
UPPER="$("$PY" -c 'import sys;print(sys.argv[1].upper())' "$LOGIN")"
printf 'link:github:%s:%s\n' "$UPPER" \
  "$(cut -d' ' -f1,2 "$HOME/.socaity/claim-key.pub")" > "$TMP/upper.txt"
ssh-keygen -Y sign -q -n socaity.dev/claim -f "$HOME/.socaity/claim-key" "$TMP/upper.txt"
cat "$TMP/upper.txt" "$TMP/upper.txt.sig" > "$TMP/upper-attestation.txt"
binding() {
  "$PY" "$ROOT/tools/claim/verify_claim.py" --json --login "$2" "$1" \
    | "$PY" -c 'import json,sys;print(json.load(sys.stdin)["claim_binding"])'
}
a="$(binding "$TMP/pasted.txt" "$LOGIN")"
b="$(binding "$TMP/upper-attestation.txt" "$UPPER")"
[ "$a" = "$b" ] || { echo "FAIL: claim_binding is case-sensitive: $a != $b"; exit 1; }
echo "     '$LOGIN' and '$UPPER' both bind to $a"

echo "== the round-trip the record depends on"
"$PY" - "$ROOT" "$LOGIN" "$TMP/pasted.txt" <<'PYEOF'
import base64, hashlib, importlib.util, subprocess, sys
root, login, pasted = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, root)
spec = importlib.util.spec_from_file_location(
    "verify_claim", root + "/tools/claim/verify_claim.py")
vc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vc)
from ledger import crypto

result = vc.verify(open(pasted, encoding="utf-8").read(), login)

# 1. the z6Mk actor key decodes back to the same 32 bytes the OpenSSH key has.
line = [l for l in open(pasted, encoding="utf-8") if l.startswith("link:github:")][0]
raw = vc.parse_public_key(line.rstrip("\n").split("ssh-ed25519 ")[1])
assert crypto.decode_key(result["actor_key"]) == raw, "z6Mk does not round-trip"

# 2. claim_binding is what the page tells a contributor to recompute.
want = hashlib.sha256(("github:" + login.lower()).encode()).hexdigest()
assert result["claim_binding"] == want, \
    "claim_binding is not sha256(github:<login lowercased>)"

print("     actor_key        %s" % result["actor_key"])
print("     claim_binding    %s" % result["claim_binding"])
print("     attestation_hash %s" % result["attestation_hash"])
print("     z6Mk round-trips to the same 32 key bytes: yes")
PYEOF

echo
echo "== all checks passed"
echo "NOT covered here, and not automatable: whether a human finishes in under"
echo "three minutes, and whether they can say what the key is for afterwards."
echo "That is doc/research/m0-claim-flow-test/PROTOCOL.md, and it needs people."
