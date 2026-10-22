#!/usr/bin/env python3
"""Check the publication cadence promised by the ledger schema.

This is deliberately a read-only CI gate: cadence is a publication obligation,
not an append-time admissibility rule.  The ledger validator remains free to
validate an event before its checkpoint is published.
"""

import argparse
import json
import sys


MAX_EVENTS = 256
MAX_SECONDS = 24 * 60 * 60
MANDATORY_PREFIXES = ("epoch.", "distribution.")
MANDATORY_TYPES = {"audit.completed"}


class CadenceError(ValueError):
    """The exported log missed a required checkpoint boundary."""


def check_events(events, max_events=MAX_EVENTS, max_seconds=MAX_SECONDS):
    """Validate checkpoint spacing and mandatory post-event checkpoints.

    ``events`` must be in chain order.  A checkpoint resets both counters;
    checkpoint events themselves are not counted as ordinary events.
    """
    if not events:
        raise CadenceError("ledger is empty; no checkpoint cadence to audit")

    since_checkpoint = 0
    checkpoint_ts = events[0]["ts"]
    pending = None
    for line, event in enumerate(events, 1):
        etype = event.get("type")
        if etype == "checkpoint.published":
            # A checkpoint is the required boundary for the preceding
            # mandatory event, and also resets the ordinary spacing counters.
            pending = None
            since_checkpoint = 0
            checkpoint_ts = event["ts"]
            continue

        since_checkpoint += 1
        if since_checkpoint > max_events:
            raise CadenceError(
                "line %d: %d events since the last checkpoint (maximum %d)"
                % (line, since_checkpoint, max_events))
        if event["ts"] - checkpoint_ts > max_seconds:
            raise CadenceError(
                "line %d: %d seconds since the last checkpoint (maximum %d)"
                % (line, event["ts"] - checkpoint_ts, max_seconds))
        if pending is not None:
            raise CadenceError(
                "line %d: checkpoint required immediately after %s" % (line, pending))
        if (etype in MANDATORY_TYPES or
                any(etype.startswith(prefix) for prefix in MANDATORY_PREFIXES)):
            pending = etype

    if pending is not None:
        raise CadenceError("end of log: checkpoint required immediately after %s" % pending)


def check_path(path):
    with open(path, encoding="utf-8") as handle:
        events = [json.loads(line) for line in handle if line.strip()]
    check_events(events)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="canonical exported ledger JSONL")
    args = parser.parse_args(argv)
    try:
        check_path(args.path)
    except (OSError, ValueError, KeyError) as exc:
        print("FAIL: checkpoint cadence: %s" % exc, file=sys.stderr)
        return 1
    print("PASS: checkpoint cadence")
    return 0


if __name__ == "__main__":
    sys.exit(main())
