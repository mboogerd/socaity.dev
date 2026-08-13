"""Generator for the golden vectors in ``rule/vectors/``.

The vectors are committed as DATA: the tests and the forkability job read the
JSON, never this file.  This generator exists so the fixtures are reviewable
(the inputs are written here in a compact, commented form) and regenerable
after a deliberate structure change -- never as part of the test run, because a
golden vector that regenerates itself proves nothing.

Regenerate:  python3 -m rule.make_vectors          (rewrites rule/vectors/*.json)
Verify:      python3 -m rule.forkability           (recomputes and compares)

The arithmetic of vectors 02, 03 and 11 is additionally hand-checked in
rule/test_distribute.py, so the expectations are not merely whatever the code
happened to print on the day.
"""

import copy
import hashlib
import json
import os
import sys

from .distribute import canonical_bytes, distribute, table_hash
from .params import PLACEHOLDER_PARAMS
from .publish import build_artifact, meta_rule_artifact

VECTOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vectors")

KEYS = {name: "z6Mk" + hashlib.sha256(name.encode()).hexdigest()[:40]
        for name in ("alice", "bob", "carol", "founder")}


def H(tag):
    return hashlib.sha256(tag.encode()).hexdigest()


def entry(tag, epoch, lineage, quantity_micro, mode="E", category="code",
          native_unit="hours", tier=None):
    row = {"entry_hash": H(tag), "epoch": epoch, "mode": mode,
           "category": category, "native_unit": native_unit,
           "quantity_micro": quantity_micro,
           "lineage": None if lineage is None else KEYS[lineage]}
    if tier is not None:
        row["tier"] = tier
    return row


def epoch(index, closed=True, audited=True):
    return {"index": index, "closed": closed, "audited": audited}


def request(entries, epochs, amount_minor, statuses=None, params=None,
            name="v"):
    snapshot = {"entries": {}}
    for row in entries:
        state = (statuses or {}).get(row["entry_hash"], {"status": "confirmed"})
        snapshot["entries"][row["entry_hash"]] = state
    return {
        "rule_version": H("rule-version-placeholder"),
        "params": copy.deepcopy(params or PLACEHOLDER_PARAMS),
        "ledger_export": {"checkpoint_hash": H("checkpoint:" + name),
                          "epochs": epochs, "entries": entries},
        "validation_snapshot": snapshot,
        "declared": {"distribution_id": H("distribution:" + name),
                     "amount_minor": amount_minor, "currency": "EUR",
                     "cutoff_checkpoint_hash": H("cutoff:" + name)},
    }


def geometric_params(ratio_den):
    params = copy.deepcopy(PLACEHOLDER_PARAMS)
    params["pie"] = {"shape": "geometric_decay", "p0": {"num": 1, "den": 1},
                     "ratio": {"num": 1, "den": ratio_den}}
    return params


def table_params():
    params = copy.deepcopy(PLACEHOLDER_PARAMS)
    params["pie"] = {"shape": "table",
                     "values": [{"num": 4, "den": 1}, {"num": 2, "den": 1}],
                     "tail": {"num": 1, "den": 1}}
    return params


def half_rate_review():
    params = copy.deepcopy(PLACEHOLDER_PARAMS)
    params["rates"]["review:hours"] = {"num": 1, "den": 2}
    return params


# --- the vectors -----------------------------------------------------------

def vectors():
    out = []

    out.append(("01-single-contributor",
                "One confirmed mode-E entry in one closed, audited epoch: the "
                "whole distributable amount, and the audit slice withheld.",
                request([entry("e1", 0, "alice", 3600000)], [epoch(0)], 10000,
                        name="01")))

    out.append(("02-remainder-tie",
                "Two equal weights and an odd distributable amount: the "
                "largest-remainder residual is broken by ascending entry hash.",
                request([entry("e1", 0, "alice", 1000000),
                         entry("e2", 0, "bob", 1000000)], [epoch(0)], 1001,
                        name="02")))

    out.append(("03-zero-weight-epoch",
                "Every weight in the epoch is zero: D_e is zero, no claim "
                "exists, and the amount is reported undistributed rather than "
                "silently absorbed.",
                request([entry("e1", 0, "alice", 0)], [epoch(0)], 10000,
                        name="03")))

    out.append(("04-all-challenged",
                "Every entry is challenged: each stays in D_e at its declared "
                "weight and its share is booked to an escrow row with hold "
                "'challenge'.",
                request([entry("e1", 0, "alice", 1000000),
                         entry("e2", 0, "bob", 3000000)], [epoch(0)], 10000,
                        statuses={H("e1"): {"status": "challenged"},
                                  H("e2"): {"status": "challenged"}},
                        name="04")))

    out.append(("05-mode-a-dilutes",
                "A mode-A entry enters the denominator and produces no claim: "
                "half of P_0 lapses, and the mode-E holder still takes the "
                "whole declared inflow because the split is proportional.",
                request([entry("e1", 0, "alice", 2000000),
                         entry("e2", 0, "bob", 2000000, mode="A")], [epoch(0)],
                        10000, name="05")))

    out.append(("06-decaying-pie",
                "Geometric pie (ratio 1/2) over two epochs: equal weights in "
                "epoch 0 and epoch 1 give a 2:1 split -- the earliness "
                "premium with no premium multiplier anywhere.",
                request([entry("e1", 0, "alice", 1000000),
                         entry("e2", 1, "bob", 1000000)],
                        [epoch(0), epoch(1)], 9000,
                        params=geometric_params(2), name="06")))

    out.append(("07-unclaimed-escrow",
                "An accepted contribution whose contributor is still null "
                "(socaity-ipg): the share is computed and held under "
                "'attribution', never redistributed.",
                request([entry("e1", 0, None, 1000000),
                         entry("e2", 0, "bob", 1000000)], [epoch(0)], 10000,
                        name="07")))

    out.append(("08-discounted-entry",
                "A decided challenge discounted an entry to one half: the "
                "weight, and therefore the denominator, shrink exactly.",
                request([entry("e1", 0, "alice", 2000000),
                         entry("e2", 0, "bob", 2000000)], [epoch(0)], 10000,
                        statuses={H("e1"): {"status": "discounted",
                                            "discount": {"num": 1, "den": 2}},
                                  H("e2"): {"status": "confirmed"}},
                        name="08")))

    out.append(("09-founder-epoch-zero",
                "The itemised epoch-0 founder position under the same V "
                "table, plus an external contributor in epoch 1, with a "
                "table-shaped pie.",
                request([entry("f1", 0, "founder", 40000000,
                               category="governance"),
                         entry("f2", 0, "founder", 20000000, category="code"),
                         entry("e1", 1, "alice", 10000000)],
                        [epoch(0), epoch(1)], 100000,
                        params=table_params(), name="09")))

    out.append(("10-open-and-unaudited-excluded",
                "Only closed AND audited epochs participate: the unaudited "
                "epoch 1 and the still-open epoch 2 contribute nothing.",
                request([entry("e1", 0, "alice", 1000000),
                         entry("e2", 1, "bob", 9000000),
                         entry("e3", 2, "carol", 9000000)],
                        [epoch(0), epoch(1, audited=False),
                         epoch(2, closed=False, audited=False)],
                        10000, name="10")))

    out.append(("11-three-way-residual",
                "100 minor units across three equal claims: floor gives 31 "
                "each, and the two-unit residual goes to the two smallest "
                "entry hashes.",
                request([entry("e1", 0, "alice", 1000000),
                         entry("e2", 0, "bob", 1000000),
                         entry("e3", 0, "carol", 1000000)], [epoch(0)], 100,
                        name="11")))

    out.append(("12-empty-ledger",
                "A closed, audited epoch with no entries at all: nothing is "
                "claimable and the whole net amount is undistributed.",
                request([], [epoch(0)], 10000, name="12")))

    out.append(("13-tier-floor",
                "A tiered acceptance below the published floor is valued at "
                "the floor (socaity-ipg's 0.5 h), so the two entries split "
                "evenly.",
                request([entry("e1", 0, "alice", 100000, tier="T1"),
                         entry("e2", 0, "bob", 500000)], [epoch(0)], 10000,
                        name="13")))

    out.append(("14-zero-declared-amount",
                "A declaration of zero: every column is zero and conservation "
                "still holds exactly.",
                request([entry("e1", 0, "alice", 1000000)], [epoch(0)], 0,
                        name="14")))

    out.append(("15-heterogeneous-rates",
                "Two categories at different V rates: an hour of review at "
                "rate 1/2 is worth half an hour of code at rate 1.",
                request([entry("e1", 0, "alice", 2000000, category="review"),
                         entry("e2", 0, "bob", 1000000, category="code")],
                        [epoch(0)], 10000, params=half_rate_review(),
                        name="15")))

    return out


def build():
    written = []
    for name, description, req in vectors():
        table = distribute(req)
        vector = {"name": name, "description": description, "request": req,
                  "expected": {"table": table, "table_hash": table_hash(table)}}
        path = os.path.join(VECTOR_DIR, name + ".json")
        with open(path, "wb") as handle:
            handle.write(canonical_bytes(vector))
            handle.write(b"\n")
        written.append(path)
    # The development rule-version artifact, committed so a forker can verify
    # that the source they cloned hashes to the version the vectors name.  It
    # carries the PLACEHOLDER parameters and is therefore unpublishable by
    # construction: rule.publish.publish refuses it, and so does the ledger's
    # placeholder_free_params predicate.
    artifact = {"rule_version_artifact": build_artifact(),
                "meta_rule": meta_rule_artifact()}
    path = os.path.join(os.path.dirname(VECTOR_DIR), "RULE_VERSION.json")
    with open(path, "wb") as handle:
        handle.write(canonical_bytes(artifact))
        handle.write(b"\n")
    written.append(path)

    vectors_written = [os.path.basename(p) for p in sorted(written)
                       if p.endswith(".json") and "vectors" in p]
    index = {"count": len(vectors_written), "vectors": vectors_written}
    with open(os.path.join(VECTOR_DIR, "index.json"), "wb") as handle:
        handle.write(canonical_bytes(index))
        handle.write(b"\n")
    return written


def load_all():
    """Every committed vector, in file-name order."""
    out = []
    for name in sorted(os.listdir(VECTOR_DIR)):
        if name.endswith(".json") and name != "index.json":
            with open(os.path.join(VECTOR_DIR, name), "r", encoding="utf-8") as handle:
                out.append((name, json.load(handle)))
    return out


if __name__ == "__main__":
    for path in build():
        sys.stdout.write("wrote %s\n" % path)
