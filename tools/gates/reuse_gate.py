#!/usr/bin/env python3
"""REUSE gate — license and copyright compliance.

socaity-a0s commits the project to REUSE compliance in the NLnet application
and to a fixed license set; clause 6 of that resolution makes enforcement a CI
property: "republished output redistributable under the declared licenses with
zero manual steps, verified per run".  A license choice inexpressible as a
green CI check is a promise, not a guarantee.

Checks, each naming the file and the rule on failure:

  R1  every tracked file has a license and a copyright holder — from an
      SPDX-FileCopyrightText / SPDX-License-Identifier tag in the file itself,
      or from a REUSE.toml annotation whose path glob matches it.
  R2  every license identifier in use has its text in LICENSES/<id>.txt.
  R3  every file in LICENSES/ is actually used — dead license texts state a
      grant nobody makes.
  R4  every identifier in use is in the a0s license set.  Adding a license is
      a council decision, not a file-by-file choice.

Not a re-implementation of the `reuse` tool: it is the subset that runs with
the standard library alone, before any dependency is installed, so the gate
cannot be skipped on a cold checkout.

Usage:
  python3 tools/gates/reuse_gate.py [--root .] [--verbose]
"""

import argparse
import os
import re
import subprocess
import sys
import tomllib

# council/socaity-a0s.md §"The license set".
ALLOWED = {
    "AGPL-3.0-or-later": "platform core (network copyleft, DCO inbound, no CLA)",
    "Apache-2.0": "permissive shell: rule module, renderer, export, fork tooling",
    "CC0-1.0": "platform-originated graph and ledger records",
    "CC-BY-4.0": "documents, council records, standards, the M2 index",
}

# The value must look like an SPDX expression, so that a source file which
# merely *mentions* the tag (this one does) is not read as declaring one.
TAG_LICENSE = re.compile(
    r"SPDX-License-Identifier:[ \t]*"
    r"([A-Za-z0-9][A-Za-z0-9.+-]*(?:[ ](?:OR|AND|WITH)[ ][A-Za-z0-9][A-Za-z0-9.+-]*)*)")
TAG_COPYRIGHT = re.compile(r"SPDX-FileCopyrightText:\s*(\S.*)")
SKIP_DIRS = {".git", "__pycache__", "site", ".dolt"}


def glob_match(pattern, path):
    """REUSE path globs: `*` inside a segment, `**` across segments."""
    def literal(chunk):
        return re.escape(chunk).replace(r"\*", "[^/]*").replace(r"\?", "[^/]")

    rx = ".*".join(literal(chunk) for chunk in pattern.split("**"))
    return re.fullmatch(rx, path) is not None


def tracked_files(root):
    """git ls-files, falling back to a walk outside a checkout."""
    try:
        out = subprocess.run(["git", "-C", root, "ls-files", "-z"],
                             capture_output=True, check=True)
        files = [f for f in out.stdout.decode().split("\0") if f]
        if files:
            return sorted(files)
    except (OSError, subprocess.CalledProcessError):
        pass
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            found.append(rel.replace(os.sep, "/"))
    return sorted(found)


def file_tags(path):
    """(license, copyright) declared in the file's own header, if any."""
    try:
        with open(path, "rb") as handle:
            head = handle.read(8192).decode("utf-8", "replace")
    except OSError:
        return None, None
    lic = TAG_LICENSE.search(head)
    cop = TAG_COPYRIGHT.search(head)
    return (lic.group(1) if lic else None,
            cop.group(1).strip() if cop else None)


def load_annotations(root):
    path = os.path.join(root, "REUSE.toml")
    if not os.path.isfile(path):
        raise SystemExit("FAIL REUSE.toml:0: REUSE — no REUSE.toml; the license "
                         "set of council/socaity-a0s.md is undeclared")
    with open(path, "rb") as handle:
        data = tomllib.load(handle)
    out = []
    for block in data.get("annotations", []):
        paths = block.get("path")
        paths = [paths] if isinstance(paths, str) else list(paths or [])
        out.append({
            "paths": paths,
            "license": block.get("SPDX-License-Identifier"),
            "copyright": block.get("SPDX-FileCopyrightText"),
            "precedence": block.get("precedence", "aggregate"),
        })
    return out


def resolve(rel, annotations, tag_license, tag_copyright):
    """A file's (license, copyright, source). Last matching annotation wins."""
    lic, cop, source = tag_license, tag_copyright, "file header"
    for block in annotations:
        if not any(glob_match(p, rel) for p in block["paths"]):
            continue
        if block["precedence"] == "override" or lic is None:
            lic, source = block["license"], "REUSE.toml"
        if block["precedence"] == "override" or cop is None:
            cop = block["copyright"]
    return lic, cop, source


def main(argv=None):
    ap = argparse.ArgumentParser(description="REUSE license/copyright gate")
    ap.add_argument("--root", default=".")
    ap.add_argument("--verbose", action="store_true", help="print every file's license")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    annotations = load_annotations(root)
    files = [f for f in tracked_files(root) if not f.startswith("LICENSES/")]

    print("== REUSE gate")
    print("   %d annotation block(s) over %d tracked files"
          % (len(annotations), len(files)))

    failures, used, matched = [], {}, set()
    for rel in files:
        tag_lic, tag_cop = file_tags(os.path.join(root, rel))
        lic, cop, source = resolve(rel, annotations, tag_lic, tag_cop)
        for block in annotations:
            for pattern in block["paths"]:
                if glob_match(pattern, rel):
                    matched.add(pattern)
        if not lic:
            failures.append((rel, "R1", "no SPDX-License-Identifier in the file and "
                                        "no REUSE.toml annotation covers it"))
            continue
        if not cop:
            failures.append((rel, "R1", "licensed %s but no SPDX-FileCopyrightText" % lic))
        used.setdefault(lic, []).append(rel)
        if args.verbose:
            print("   %-60s %-18s (%s)" % (rel, lic, source))

    licenses_dir = os.path.join(root, "LICENSES")
    on_disk = set()
    if os.path.isdir(licenses_dir):
        on_disk = {os.path.splitext(n)[0] for n in os.listdir(licenses_dir)
                   if n.endswith(".txt")}

    for lic, users in sorted(used.items()):
        if lic not in ALLOWED:
            failures.append(("REUSE.toml", "R4",
                             "%s is not in the socaity-a0s license set %s (first "
                             "used by %s) — changing the set is a council decision"
                             % (lic, sorted(ALLOWED), users[0])))
        if lic not in on_disk:
            failures.append(("LICENSES/%s.txt" % lic, "R2",
                             "missing license text for %s, used by %d file(s) "
                             "including %s" % (lic, len(users), users[0])))
    for lic in sorted(on_disk - set(used)):
        failures.append(("LICENSES/%s.txt" % lic, "R3",
                         "license text present but no file is licensed under it"))

    stale = [p for block in annotations for p in block["paths"] if p not in matched]
    if stale:
        print("   NOTE: annotation path(s) matching nothing yet: %s"
              % ", ".join(sorted(set(stale))))

    print("   licenses in use: %s"
          % ", ".join("%s (%d)" % (k, len(v)) for k, v in sorted(used.items())))

    for rel, rule, message in failures:
        print("FAIL %s:0: REUSE %s — %s" % (rel, rule, message))

    if failures:
        print("   %d compliance failure(s)" % len(failures))
        return 1
    print("== REUSE gate: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
