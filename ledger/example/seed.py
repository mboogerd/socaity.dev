#!/usr/bin/env python3
"""Regenerate the EXAMPLE chain that /ledger renders.

WHAT THIS IS, IN ONE SENTENCE: an obviously-labelled example ledger, signed by
an example key whose secret is printed in this file, so that the /ledger page
can render real arithmetic before the real genesis has run.

WHY IT EXISTS.  socaity-x8o §7 makes a placeholder-free V a hard precondition
of ``epoch.opened(1)``: the real chain cannot be opened until socaity-wna
fixes the parameter values.  Until then the ledger page would have nothing to
render, and a page that hand-writes its numbers is exactly the page the
vocabulary-and-visual standard V5 exists to prevent.  So the numbers on
/ledger are computed by the published rule (``rule/distribute.py``,
``rule/valuation.py``, ``rule/params.py``) from THIS chain, which is a
fixture.  Every entry in it is founder-only, matching the socaity-xuz
"one contributor" reality; nothing here depicts a contributor who does not
exist or activity that did not occur (V12): it depicts a fixture, and the page
says so above the table, not in a footnote.

WHAT IS REAL IN IT.  The chain is validated by ``ledger/validator.py`` on every
read, including the signatures and the genesis-prologue sequencing.  The rule
version, meta-rule and V hashes it names are the real hashes in
``rule/RULE_VERSION.json``.  The attestation statement it names really is
``ledger/example/attestation.txt``.

WHAT IS NOT REAL IN IT.  The founder key is an example key (secret below).
The hours are example hours; the evidence and artifact digests are the SHA-256
of the label strings in :data:`EPOCH0` / :data:`EPOCH1` below, not of any
merged pull request.  The audit event is an example audit.

Regenerate (deterministic -- the same bytes every time, no wall clock):

    python3 ledger/example/seed.py

Verify what the renderer verifies:

    python3 -c "from ledger.log import EventLog; \
                print(EventLog('ledger/example/chain.jsonl').count)"
"""

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

from ledger import crypto                                        # noqa: E402
from ledger.log import EventLog                                  # noqa: E402
from ledger.validator import sign_event                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CHAIN = os.path.join(HERE, "chain.jsonl")
ATTESTATION = os.path.join(HERE, "attestation.txt")

#: The example keys.  Published, on purpose: a key whose secret is in the
#: repository cannot be mistaken for a key that guards anything.
FOUNDER_SECRET = hashlib.sha256(b"socaity.dev EXAMPLE founder key -- not a real key").digest()
CKPT_SECRET = hashlib.sha256(b"socaity.dev EXAMPLE checkpoint key -- not a real key").digest()

#: Fixed ledger time.  No wall clock anywhere: the fixture is a constant.
TS = 1786622400                       # 2026-08-13T12:00:00Z
WEEK = "2026-W33"

MICRO = 10 ** 6

#: (category, hours, label).  The label is the pre-image of the entry's
#: evidence and artifact digests, so a reader can recompute both.
EPOCH0 = [
    ("governance", 12, "example-epoch0-governance"),
    ("design", 8, "example-epoch0-design"),
    ("docs", 6, "example-epoch0-docs"),
    ("code", 20, "example-epoch0-code"),
    ("review", 4, "example-epoch0-review"),
]
EPOCH1 = [
    ("code", 9, "example-epoch1-code"),
    ("docs", 3, "example-epoch1-docs"),
]

CHECKPOINT_0 = hashlib.sha256(b"example-checkpoint-epoch-0").hexdigest()
DISTRIBUTION_0 = hashlib.sha256(b"example-audit-epoch-0").hexdigest()
REPORT_0 = hashlib.sha256(b"example-audit-report-epoch-0").hexdigest()


def key(secret):
    return crypto.encode_key(crypto.public_from_secret(secret))


def digest(label):
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def file_digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def rule_hashes():
    """The real hashes the working tree's rule module publishes."""
    with open(os.path.join(ROOT, "rule", "RULE_VERSION.json"), encoding="utf-8") as fh:
        artifact = json.load(fh)
    return {
        "rule_version": artifact["rule_version_artifact"]["rule_version"],
        "structure_hash": artifact["rule_version_artifact"]["structure_hash"],
        "params_hash": artifact["rule_version_artifact"]["params_hash"],
        "meta_rule_hash": hashlib.sha256(json.dumps(
            artifact["meta_rule"], sort_keys=True, separators=(",", ":")
        ).encode("utf-8")).hexdigest(),
    }


def work(category, hours, label):
    return ("work.logged", {
        "category": category,
        "native_unit": "hours",
        "quantity": hours * MICRO,
        "mode": "E",
        "evidence": [digest("evidence:" + label)],
        "week_ref": WEEK,
        "artifact_hash": digest("artifact:" + label),
    })


def build(path):
    if os.path.exists(path):
        os.remove(path)
    log = EventLog(path)
    rule = rule_hashes()
    ids = {}

    def add(secret, etype, payload):
        event = {"v": 1, "type": etype, "prev": log.head, "actor": key(secret),
                 "ts": TS, "payload": payload, "sig_alg": "ed25519"}
        return log.append(sign_event(secret, event), receipt_ts=TS)

    def founder(etype, payload):
        return add(FOUNDER_SECRET, etype, payload)

    # --- the genesis prologue (socaity-x8o §7, socaity-zyt) ----------------
    founder("genesis", {"rule_version_hash": rule["rule_version"],
                        "meta_rule_hash": rule["meta_rule_hash"],
                        "checkpoint_key": key(CKPT_SECRET), "L": 91})
    founder("rule.version_published", {"rule_version": rule["rule_version"],
                                       "source_hash": rule["structure_hash"],
                                       "params_hash": rule["params_hash"]})
    founder("rule.meta_published", {"meta_rule_hash": rule["meta_rule_hash"]})
    # V itself, by the hash of the parameter set the rate card is rendered from.
    founder("V.draft_published", {"draft_hash": rule["params_hash"]})

    # Epoch 0: the itemised founder position.  One event per observation --
    # never one lump (socaity-xuz).
    for category, hours, label in EPOCH0:
        etype, payload = work(category, hours, label)
        ids[label] = founder(etype, payload)

    founder("epoch.opened", {"epoch": 0, "rule_version_hash": rule["rule_version"]})
    founder("epoch.closed", {"epoch": 0, "checkpoint_hash": CHECKPOINT_0})
    founder("rule.attested", {"rule_version_hash": rule["rule_version"], "epoch": 1,
                              "statement_hash": file_digest(ATTESTATION)})
    founder("epoch.opened", {"epoch": 1, "rule_version_hash": rule["rule_version"]})

    # --- after the prologue: confirmations, epoch 1, the epoch-0 audit -----
    for _c, _h, label in EPOCH0:
        founder("entry.status_changed", {"target_event_id": ids[label],
                                         "from": "provisional", "to": "confirmed",
                                         "basis_refs": [ids[label]]})
    for category, hours, label in EPOCH1:
        etype, payload = work(category, hours, label)
        ids[label] = founder(etype, payload)
    for _c, _h, label in EPOCH1:
        founder("entry.status_changed", {"target_event_id": ids[label],
                                         "from": "provisional", "to": "confirmed",
                                         "basis_refs": [ids[label]]})
    founder("audit.completed", {"distribution_id": DISTRIBUTION_0,
                                "scope_checkpoint_hash": CHECKPOINT_0,
                                "report_hash": REPORT_0})
    add(CKPT_SECRET, "checkpoint.published",
        {"checkpoint_seq": 1, "head_event_id": log.head,
         "event_count": log.count, "prev_checkpoint_ref": "0" * 64})
    return log


if __name__ == "__main__":
    log = build(CHAIN)
    print("wrote %s: %d validated events, head %s"
          % (os.path.relpath(CHAIN, ROOT), log.count, log.head[:12]))
