"""The forkability check: replay the public artifacts, byte for byte.

socaity-x8o §6 / platform-engineer §3: "given a ledger export at a named
checkpoint hash + declared amount/cutoff + rule version per epoch -> a
byte-identical payout table on any machine".  This driver is what a stranger
runs after cloning the repository, and what CI runs on every change:

  1. the no-float lint over the whole rule package;
  2. every committed golden vector recomputed from its request and compared
     BYTE FOR BYTE against the committed canonical table, plus its table hash;
  3. the rule-version artifact recomputed from the cloned source and compared
     against the committed RULE_VERSION.json -- so the version the vectors
     name is provably the version of the code in the clone;
  4. the whole thing twice in one process, to catch order dependence inside a
     run (the CI job additionally runs it under several PYTHONHASHSEEDs and
     from a fresh `git clone`, which is what catches order dependence across
     processes).

Nothing here reaches the network, and nothing outside the clone is read.

Usage:  python3 -m rule.forkability            (exit 1 on any mismatch)
"""

import json
import os
import sys

from .distribute import canonical_bytes, distribute, table_hash
from .lint_no_float import lint_paths
from .make_vectors import VECTOR_DIR, load_all
from .publish import build_artifact, meta_rule_artifact

HERE = os.path.dirname(os.path.abspath(__file__))
ARTIFACT_PATH = os.path.join(HERE, "RULE_VERSION.json")


def check_vectors(report):
    failures = []
    vectors = load_all()
    if not vectors:
        failures.append("no golden vectors found in %s" % VECTOR_DIR)
    for name, vector in vectors:
        table = distribute(vector["request"])
        got = canonical_bytes(table)
        want = canonical_bytes(vector["expected"]["table"])
        if got != want:
            failures.append("%s: payout table differs from the committed "
                            "vector\n  expected %s\n  got      %s"
                            % (name, want.decode("utf-8")[:400],
                               got.decode("utf-8")[:400]))
        elif table_hash(table) != vector["expected"]["table_hash"]:
            failures.append("%s: table hash differs" % name)
        else:
            report("ok   %s  %s" % (vector["expected"]["table_hash"][:12], name))
    report("     %d golden vector(s) reproduced" % len(vectors))
    return failures


def check_artifact(report):
    failures = []
    if not os.path.exists(ARTIFACT_PATH):
        return ["RULE_VERSION.json is missing: the clone cannot prove which "
                "rule version its source is"]
    with open(ARTIFACT_PATH, "r", encoding="utf-8") as handle:
        committed = json.load(handle)
    rebuilt = {"rule_version_artifact": build_artifact(),
               "meta_rule": meta_rule_artifact()}
    if canonical_bytes(rebuilt) != canonical_bytes(committed):
        failures.append(
            "RULE_VERSION.json does not match the source in this clone.\n"
            "  committed rule_version %s\n  rebuilt   rule_version %s\n"
            "  (regenerate with: python3 -m rule.make_vectors)"
            % (committed["rule_version_artifact"]["rule_version"],
               rebuilt["rule_version_artifact"]["rule_version"]))
    else:
        report("ok   rule_version %s"
               % committed["rule_version_artifact"]["rule_version"])
        report("ok   meta_rule source %s"
               % committed["meta_rule"]["source_hash"][:12])
    # A published artifact must never carry placeholders; a development one
    # must never claim to be final.  Either way, say which it is, loudly.
    params = committed["rule_version_artifact"]["params"]
    if params.get("placeholders"):
        report("NOTE this is a DEVELOPMENT artifact: parameters are "
               "placeholders (%s), gated by %s.  publish() and the ledger's "
               "placeholder_free_params predicate both refuse it."
               % (", ".join(params["placeholders"]),
                  ", ".join(params.get("gated_by", []))))
    return failures


def run(report=None):
    report = report or (lambda line: sys.stdout.write(line + "\n"))
    failures = []

    findings = lint_paths([HERE])
    for finding in findings:
        failures.append("no-float lint: %s" % finding)
    if not findings:
        report("ok   no-float lint clean")

    failures.extend(check_artifact(report))
    failures.extend(check_vectors(report))

    # Twice in one process: a table that changes on the second call would mean
    # hidden state, which is the one thing a pure function cannot have.
    for name, vector in load_all():
        if canonical_bytes(distribute(vector["request"])) != \
                canonical_bytes(distribute(vector["request"])):
            failures.append("%s: two calls, two answers" % name)
    if not failures:
        report("ok   repeated evaluation is stable")
    return failures


def main():
    failures = run()
    for failure in failures:
        sys.stderr.write("FAIL %s\n" % failure)
    if failures:
        sys.stderr.write("forkability: %d failure(s)\n" % len(failures))
        return 1
    sys.stdout.write("forkability: the public artifacts replay byte-identically\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
