#!/usr/bin/env python3
"""Verify a signed courier patch and print its provenance.

The patch bytes are the canonical content: no normalisation, checkout, or
network lookup is performed.  The detached signature and the supplied public
key must agree.  Supported formats are OpenSSH SSHSIG, minisign, and detached
OpenPGP.  The JSON result is suitable for copying into a PR provenance block;
the public key itself is never copied into the graph or ledger.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile


class CourierError(Exception):
    """A safe, user-facing verification failure."""


def run(command, **kwargs):
    try:
        return subprocess.run(command, check=True, text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              **kwargs)
    except FileNotFoundError:
        raise CourierError("required verifier is not installed: %s" % command[0])
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "verification failed").strip()
        raise CourierError(detail.splitlines()[-1])


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_sshsig(patch, signature, public_key):
    fingerprint = run(["ssh-keygen", "-lf", public_key, "-E", "sha256"]).stdout.split()[1]
    with tempfile.TemporaryDirectory() as tmp:
        allowed = os.path.join(tmp, "allowed_signers")
        with open(allowed, "w", encoding="utf-8") as out:
            key = " ".join(open(public_key, encoding="utf-8").read().split()[:2])
            out.write("courier namespaces=\"socaity.dev/courier\" %s\n" % key)
        with open(patch, "rb") as content:
            run(["ssh-keygen", "-Y", "verify", "-f", allowed, "-I", "courier",
                 "-n", "socaity.dev/courier", "-s", signature], stdin=content)
    return "sshsig", "ssh:%s" % fingerprint


def verify_minisign(patch, signature, public_key):
    if not shutil.which("minisign"):
        raise CourierError("required verifier is not installed: minisign")
    run(["minisign", "-Vm", patch, "-x", signature, "-p", public_key])
    return "minisign", "minisign:sha256:%s" % sha256(public_key)


def verify_pgp(patch, signature, public_key):
    with tempfile.TemporaryDirectory() as home:
        env = dict(os.environ, GNUPGHOME=home)
        run(["gpg", "--batch", "--import", public_key], env=env)
        status = run(["gpg", "--batch", "--status-fd", "1", "--verify",
                      signature, patch], env=env).stdout
    matches = re.findall(r"^\[GNUPG:\] VALIDSIG ([0-9A-F]+)", status, re.MULTILINE)
    if not matches:
        raise CourierError("OpenPGP verifier returned no VALIDSIG fingerprint")
    return "pgp", "pgp:%s" % matches[-1]


def verify(args):
    if not all(os.path.isfile(path) for path in (args.patch, args.signature, args.public_key)):
        raise CourierError("patch, signature, and public-key files are required")
    verifiers = {"sshsig": verify_sshsig, "minisign": verify_minisign,
                 "pgp": verify_pgp}
    algorithm, actor_id = verifiers[args.format](args.patch, args.signature,
                                                  args.public_key)
    return {
        "schema": 1,
        "algorithm": algorithm,
        "actor_id": actor_id,
        "actor_kind": "human",
        "patch_sha256": "sha256:" + sha256(args.patch),
        "public_key_sha256": "sha256:" + sha256(args.public_key),
        "signature_verified": True,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--patch", required=True)
    parser.add_argument("--signature", required=True)
    parser.add_argument("--public-key", required=True)
    parser.add_argument("--format", choices=("sshsig", "minisign", "pgp"),
                        required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = verify(args)
    except CourierError as exc:
        print("NOT VERIFIED: %s" % exc, file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print("VERIFIED %s %s" % (result["algorithm"], result["actor_id"]))
        print("  patch          %s" % result["patch_sha256"])
        print("  public key     %s" % result["public_key_sha256"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
