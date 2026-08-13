"""Replay adapter: a validated ledger -> the rule's input.

The rule itself never reads a ledger; it reads a canonical JSON request.  This
module is the (equally deterministic, but I/O-adjacent) bridge that folds an
``ledger.validator.Ledger`` -- already replayed and validated by socaity-124's
engine -- into that request.

It implements two things the observation log deliberately does not store,
because both are VALUATIONS and valuations are always recomputed
(socaity-zyt):

* **epoch assignment, with the clamp.**  socaity-x8o §1: an observation
  appended after ``epoch.closed(e)`` can never be assigned to epoch e.  Since
  append time is chain position and never a field, placement is simply "the
  epoch open at the position where the event sits", which is clamp-correct by
  construction: a self-declared timestamp cannot move it.  Events that sit
  before any epoch was opened belong to epoch 0 (the itemised founder
  position); events in a gap between a close and the next open belong to the
  epoch that opens next.
* **the validation snapshot** (socaity-zjr): provisional / confirmed /
  discounted / challenged / withdrawn, folded from the status, challenge and
  withdrawal events.  Challenged entries stay in the denominator at their
  DECLARED weight; the escrow is on the payout, not on the weight.
"""

from ledger.catalog import ACCRUAL_TYPES

__all__ = ["epoch_assignment", "validation_snapshot", "ledger_export",
           "distribution_request", "meta_state"]

_UNIT_OF = {"work.logged": None,                  # declared in the payload
            "ticket.accepted": "hours",
            "contribution.trivial_accepted": "hours"}


def epoch_assignment(ledger):
    """event_id -> epoch index, for every accrual-bearing observation."""
    assignment = {}
    open_epoch = None
    last_closed = None
    for event_id in ledger.order:
        event = ledger.events[event_id]
        etype = event["type"]
        if etype == "epoch.opened":
            open_epoch = event["payload"]["epoch"]
            continue
        if etype == "epoch.closed":
            last_closed = event["payload"]["epoch"]
            open_epoch = None
            continue
        if etype in ACCRUAL_TYPES:
            if open_epoch is not None:
                assignment[event_id] = open_epoch
            elif last_closed is None:
                assignment[event_id] = 0
            else:
                assignment[event_id] = last_closed + 1
    return assignment


def validation_snapshot(ledger):
    """The zjr lifecycle state of every accrual observation at the head."""
    entries = {}
    for event_id in ledger.order:
        event = ledger.events[event_id]
        if event["type"] in ACCRUAL_TYPES:
            entries[event_id] = {"status": "provisional"}

    open_challenges = {}                      # challenge_id -> target event_id
    for event_id in ledger.order:
        event = ledger.events[event_id]
        payload = event["payload"]
        etype = event["type"]
        if etype == "entry.status_changed" and payload["target_event_id"] in entries:
            entries[payload["target_event_id"]]["status"] = payload["to"]
        elif etype == "entry.withdrawn" and payload["target_event_id"] in entries:
            entries[payload["target_event_id"]]["status"] = "withdrawn"
        elif etype == "challenge.filed":
            target = payload["target_event_id"]
            open_challenges[payload["challenge_id"]] = target
            if target in entries:
                entries[target]["status"] = "challenged"
        elif etype in ("challenge.decided", "appeal.decided"):
            key = payload.get("challenge_id") or payload.get("appeal_id")
            target = open_challenges.get(key)
            if target is None or target not in entries:
                continue
            if payload["outcome"] == "upheld":
                entries[target]["status"] = "discounted"
                entries[target]["discount"] = payload["discount"]
            else:
                entries[target]["status"] = "confirmed"
                entries[target].pop("discount", None)
    return {"entries": entries}


def _entry_row(ledger, event_id, epoch):
    event = ledger.events[event_id]
    payload = event["payload"]
    etype = event["type"]
    row = {
        "entry_hash": event_id,
        "epoch": epoch,
        "mode": payload["mode"],
        "category": payload["category"],
        "native_unit": payload.get("native_unit") or _UNIT_OF[etype],
        "quantity_micro": 0,
        "lineage": None,
    }
    if etype == "work.logged":
        row["quantity_micro"] = payload["quantity"]
        row["lineage"] = ledger.lineage_of(event["actor"])
    elif etype == "ticket.accepted":
        row["quantity_micro"] = payload["attested_micro_hours"]
        row["lineage"] = ledger.attribution_of(event_id)
        opened = ledger.events[payload["ticket_ref"]]
        row["tier"] = opened["payload"]["tier"]
    else:                                     # contribution.trivial_accepted
        # No quantity is attested for a trivial acceptance: it is valued at the
        # published floor for the smallest tier (socaity-ipg's 0.5 vu floor).
        row["tier"] = "T1"
        row["lineage"] = ledger.attribution_of(event_id)
    return row


def ledger_export(ledger, checkpoint_hash=None):
    """The immutable side of the rule's input."""
    assignment = epoch_assignment(ledger)

    epochs = {}
    audited_checkpoints = set()
    for event_id in ledger.order:
        event = ledger.events[event_id]
        payload = event["payload"]
        if event["type"] == "epoch.opened":
            epochs[payload["epoch"]] = {"index": payload["epoch"], "closed": False,
                                        "audited": False, "checkpoint_hash": None}
        elif event["type"] == "epoch.closed":
            record = epochs[payload["epoch"]]
            record["closed"] = True
            record["checkpoint_hash"] = payload["checkpoint_hash"]
        elif event["type"] == "audit.completed":
            audited_checkpoints.add(payload["scope_checkpoint_hash"])
    for index in sorted(epochs):
        record = epochs[index]
        record["audited"] = record["checkpoint_hash"] in audited_checkpoints
        record.pop("checkpoint_hash")

    # Epochs an entry was clamped into may not have been opened yet (an entry
    # sitting in a gap).  It still needs a row, closed and unaudited.
    for epoch in assignment.values():
        epochs.setdefault(epoch, {"index": epoch, "closed": False, "audited": False})

    entries = [_entry_row(ledger, event_id, assignment[event_id])
               for event_id in sorted(assignment)]
    return {"checkpoint_hash": checkpoint_hash or ledger.head,
            "epochs": [epochs[index] for index in sorted(epochs)],
            "entries": sorted(entries, key=lambda row: row["entry_hash"])}


def distribution_request(ledger, artifact, declared, checkpoint_hash=None):
    """Assemble the complete, canonical-JSON-ready rule input."""
    return {"rule_version": artifact["rule_version"],
            "params": artifact["params"],
            "ledger_export": ledger_export(ledger, checkpoint_hash),
            "validation_snapshot": validation_snapshot(ledger),
            "declared": declared}


def meta_state(ledger):
    """The chain-derived state the meta-rule's validity predicate reads."""
    highest = None
    for event_id in ledger.order:
        event = ledger.events[event_id]
        if event["type"] == "epoch.opened":
            epoch = event["payload"]["epoch"]
            highest = epoch if highest is None or epoch > highest else highest
    return {"highest_opened_epoch": highest, "open_epoch": ledger.epoch_open}
