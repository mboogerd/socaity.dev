# Contributing by signed patch

The courier path is for contributors who want to use a keypair without a
GitHub account. It accepts a patch, a detached signature, and the matching
public key. The patch is opened as received; a maintainer does not rewrite its
content or claim authorship.

1. Create a patch with `git format-patch --stdout BASE..HEAD > change.patch`.
2. Sign the exact file with one supported tool:
   `ssh-keygen -Y sign -n socaity.dev/courier -f KEY change.patch`,
   `minisign -Sm change.patch -s KEY`, or detached OpenPGP (`gpg --detach-sign`).
3. Send `change.patch`, its detached signature, and the public key to the
   current published courier inbox shown on the site. Never send a private key.
4. A maintainer runs `tools/courier/verify_patch.py` with the three files and
   the selected format. Verification is offline and checks the signature over
   the exact patch bytes.
5. The maintainer opens the patch verbatim in a pull request. The PR records
   the verifier's JSON as provenance: algorithm, public-key fingerprint/hash,
   and patch hash. The public key is the contributor author; the maintainer is
   recorded separately as the person who opened the PR.

The signer identity is pseudonymous. Do not put names, email addresses, or
resolvable account URLs in graph or ledger records. A failed verification is
rejected, never repaired by editing the patch. Example:

```sh
python3 tools/courier/verify_patch.py \
  --patch change.patch --signature change.patch.sig \
  --public-key courier-key.pub --format sshsig --json
```
