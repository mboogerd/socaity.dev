#!/usr/bin/env python3
"""Verify a pasted claim attestation and derive what the record needs.

The human half of this is council/socaity-ipg.md clause 3 and the /claim page
it produces: a contributor runs three `ssh-keygen` commands and pastes the
result as a comment on their merged pull request.  This is the other half --
the mechanical check a maintainer (or any stranger auditing the record) runs
over that comment.

What the attestation proves, and in which direction
---------------------------------------------------
socaity-7mk requires the GitHub linkage to be *bidirectional*, and neither
direction is worth anything alone:

  key -> account   the signed line names the account, and only the holder of
                   the private key can produce that signature.  Checked here.
  account -> key   the comment is published under that account, so the account
                   holder asserts the key.  GitHub attests this, not us: the
                   check is "the comment author's login equals --login", and
                   it is done by looking at the comment, which is why --login
                   is an argument and not something this tool sniffs.

So: this tool verifies the first direction and *computes* what the second one
must be compared against.  It never claims to have checked authorship.

What it prints
--------------
  actor_key       the contributor's ledger identity: multibase z6Mk...
                  (socaity-7mk clause 1).  A pure function of the same 32 key
                  bytes the OpenSSH public key carries -- no new key, no
                  second identity, nothing to re-generate.
  claim_binding   sha256("github:<login>") hex, the login folded to lower
                  case.  The escrow fixes this value at acceptance time
                  (socaity-ipg clause 2) from the pull request author's login,
                  and the claimant reproduces it from whatever they typed at
                  step 2 of the /claim page; a GitHub login is
                  case-insensitive, so the two agree only if both sides fold
                  case, and a claim is valid only against a matching escrow.
                  Hash only: the plaintext handle never reaches the record.
  attestation_hash sha256 of the normalised attestation text, for
                  attribution.claimed.payload.attestation_hash.

Normalisation, because a comment box is not a file: CRLF becomes LF, trailing
whitespace goes per line, leading and trailing blank lines go, and a Markdown
code fence around the block is ignored.  Everything else is byte-exact.

No network, no wall clock, no dependency outside the standard library and
`ledger.crypto` (the repo's own Ed25519).  The same command verifies an
attestation published as a gist, or mailed down the courier path: the input is
text, not a GitHub API object.

Usage:
  python3 tools/claim/verify_claim.py --login OCTOCAT < pasted-comment.txt
  ... --namespace socaity.dev/claim   (the default; the signing namespace)
  ... --json                          (machine-readable, sorted keys)

Exit status is 0 only if the signature verifies and every field agrees.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from ledger import crypto  # noqa: E402

#: PROTOCOL.sshsig: every signed blob and every armoured signature starts here.
MAGIC = b"SSHSIG"
SSHSIG_VERSION = 1
KEY_TYPE = b"ssh-ed25519"
DEFAULT_NAMESPACE = "socaity.dev/claim"

#: The one line the contributor signs.  socaity-7mk clause 5 fixes the shape
#: `link:github:<user>:<pubkey>`; the pubkey here is the OpenSSH one-line form,
#: which carries exactly the 32 bytes the z6Mk string is built from.
LINK_LINE = re.compile(
    r"^link:github:(?P<login>[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?):"
    r"(?P<keytype>ssh-ed25519) (?P<blob>[A-Za-z0-9+/=]+)$")

ARMOUR = re.compile(
    r"-----BEGIN SSH SIGNATURE-----\s*\n(.*?)\n-----END SSH SIGNATURE-----",
    re.DOTALL)

FENCE = re.compile(r"^\s*(```+|~~~+).*$")


class ClaimError(Exception):
    """A named reason the attestation is not usable.  Never a stack trace."""


# --- SSH wire format -------------------------------------------------------

def _strings(buf):
    """Iterate the `string` fields of an SSH wire blob (uint32 length + body)."""
    i = 0
    while i < len(buf):
        if i + 4 > len(buf):
            raise ClaimError("truncated SSH wire field")
        n = int.from_bytes(buf[i:i + 4], "big")
        i += 4
        if i + n > len(buf):
            raise ClaimError("truncated SSH wire field")
        yield buf[i:i + n]
        i += n


def _string(value):
    return len(value).to_bytes(4, "big") + value


def _take(it, what):
    try:
        return next(it)
    except StopIteration:
        raise ClaimError("missing %s in SSH wire blob" % what)


def parse_public_key(blob_b64):
    """OpenSSH one-line public key body -> 32 raw Ed25519 bytes."""
    try:
        blob = base64.b64decode(blob_b64, validate=True)
    except Exception:
        raise ClaimError("public key is not valid base64")
    fields = _strings(blob)
    if _take(fields, "key type") != KEY_TYPE:
        raise ClaimError("public key is not ssh-ed25519")
    key = _take(fields, "key bytes")
    if len(key) != 32:
        raise ClaimError("Ed25519 public key must be 32 bytes")
    return key


def parse_signature(armoured):
    """Armoured SSHSIG -> (public key bytes, namespace, hash name, signature)."""
    try:
        blob = base64.b64decode("".join(armoured.split()), validate=True)
    except Exception:
        raise ClaimError("signature block is not valid base64")
    if not blob.startswith(MAGIC):
        raise ClaimError("signature block is not an SSH signature")
    body = blob[len(MAGIC):]
    if len(body) < 4 or int.from_bytes(body[:4], "big") != SSHSIG_VERSION:
        raise ClaimError("unsupported SSH signature version")
    fields = _strings(body[4:])
    pubkey_blob = _take(fields, "public key")
    namespace = _take(fields, "namespace")
    _reserved = _take(fields, "reserved")
    hash_alg = _take(fields, "hash algorithm")
    sig_blob = _take(fields, "signature")

    key_fields = _strings(pubkey_blob)
    if _take(key_fields, "key type") != KEY_TYPE:
        raise ClaimError("signature was not made by an ssh-ed25519 key")
    key = _take(key_fields, "key bytes")

    sig_fields = _strings(sig_blob)
    if _take(sig_fields, "signature algorithm") != KEY_TYPE:
        raise ClaimError("signature algorithm is not ssh-ed25519")
    signature = _take(sig_fields, "signature bytes")
    return key, namespace.decode("utf-8", "replace"), hash_alg.decode(), signature


def signed_blob(namespace, hash_alg, message):
    """The bytes ssh-keygen actually signs (PROTOCOL.sshsig)."""
    if hash_alg == "sha512":
        digest = hashlib.sha512(message).digest()
    elif hash_alg == "sha256":
        digest = hashlib.sha256(message).digest()
    else:
        raise ClaimError("unsupported signature hash: %s" % hash_alg)
    return (MAGIC + _string(namespace.encode()) + _string(b"")
            + _string(hash_alg.encode()) + _string(digest))


# --- the attestation -------------------------------------------------------

def normalise(text):
    """A pasted comment made byte-stable: see the module docstring."""
    lines = [line.rstrip() for line in text.replace("\r\n", "\n")
             .replace("\r", "\n").split("\n")]
    lines = [line for line in lines if not FENCE.match(line)]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + "\n"


def verify(text, login, namespace=DEFAULT_NAMESPACE):
    """Verify one pasted attestation.  Raises ClaimError, or returns a dict."""
    attestation = normalise(text)

    link = None
    for line in attestation.split("\n"):
        match = LINK_LINE.match(line)
        if match:
            if link is not None:
                raise ClaimError("more than one link line in the comment")
            link = match
    if link is None:
        raise ClaimError("no `link:github:<account>:ssh-ed25519 ...` line found")

    armour = ARMOUR.search(attestation)
    if armour is None:
        raise ClaimError("no BEGIN/END SSH SIGNATURE block found")

    if link.group("login").lower() != login.lower():
        raise ClaimError("the signed line names %s, not %s"
                         % (link.group("login"), login))

    stated_key = parse_public_key(link.group("blob"))
    # The message is the signed file: the link line and its newline, nothing
    # else.  Step 2 on the /claim page writes exactly that file.
    message = (link.group(0) + "\n").encode("utf-8")

    key, sig_namespace, hash_alg, signature = parse_signature(armour.group(1))
    if key != stated_key:
        raise ClaimError("the signature was made by a different key than the "
                         "line names")
    if sig_namespace != namespace:
        raise ClaimError("signature namespace is %r, expected %r"
                         % (sig_namespace, namespace))
    if not crypto.verify(crypto.SIG_ALG, key,
                         signed_blob(sig_namespace, hash_alg, message), signature):
        raise ClaimError("the signature does not verify against the key")

    return {
        "login": link.group("login"),
        "actor_key": crypto.encode_key(key),
        "claim_binding": hashlib.sha256(
            ("github:" + link.group("login").lower()).encode("utf-8")
        ).hexdigest(),
        "attestation_hash": hashlib.sha256(
            attestation.encode("utf-8")).hexdigest(),
        "namespace": sig_namespace,
        "openssh_fingerprint": "SHA256:" + base64.b64encode(
            hashlib.sha256(_string(KEY_TYPE) + _string(key)).digest()
        ).decode().rstrip("="),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--login", required=True,
                    help="the GitHub account that published the comment")
    ap.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("file", nargs="?", help="the pasted comment (default: stdin)")
    args = ap.parse_args(argv)

    text = (open(args.file, encoding="utf-8").read() if args.file
            else sys.stdin.read())
    try:
        result = verify(text, args.login, args.namespace)
    except ClaimError as exc:
        sys.stderr.write("NOT VERIFIED: %s\n" % exc)
        return 1

    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    print("VERIFIED  the key signed `link:github:%s:...` in namespace %s"
          % (result["login"], result["namespace"]))
    print("  key fingerprint   %s" % result["openssh_fingerprint"])
    print("  actor_key         %s" % result["actor_key"])
    print("  claim_binding     %s" % result["claim_binding"])
    print("  attestation_hash  %s" % result["attestation_hash"])
    print("Still to check by eye: the comment is published by github.com/%s."
          % result["login"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
