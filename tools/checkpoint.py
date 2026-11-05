#!/usr/bin/env python3
"""Export and verify portable signed ledger checkpoint anchors.

The ledger event is the signed source of truth.  This tool packages the latest
checkpoint together with the exact ledger head and file digest so the package
can be copied to a public mirror and checked without trusting that mirror.
"""

import argparse
import hashlib
import sys

from ledger import canonical
from ledger.log import EventLog
from ledger.validator import event_id


FORMAT = "socaity.dev/ledger-checkpoint-v1"


def _file_digest(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _latest(log):
    for event in reversed(log.events()):
        if event["type"] == "checkpoint.published":
            return event
    raise ValueError("ledger has no checkpoint.published event")


def export_checkpoint(ledger_path):
    log = EventLog(ledger_path)
    event = _latest(log)
    artifact = {
        "format": FORMAT,
        "checkpoint_event": event,
        "checkpoint_event_id": event_id(event),
        "ledger_event_count": log.count,
        "ledger_head": log.head,
        "ledger_sha256": _file_digest(ledger_path),
    }
    return artifact


def _read_artifact(path):
    with open(path, encoding="utf-8") as handle:
        raw = handle.read()
    artifact = canonical.loads(raw)
    if canonical.canonicalize(artifact).decode("utf-8") != raw.rstrip("\n"):
        raise ValueError("checkpoint artifact is not canonical JSON")
    return artifact


def verify_checkpoint(ledger_path, artifact_path):
    artifact = _read_artifact(artifact_path)
    if artifact.get("format") != FORMAT:
        raise ValueError("unsupported checkpoint artifact format")
    expected = export_checkpoint(ledger_path)
    for field in ("checkpoint_event", "checkpoint_event_id", "ledger_event_count",
                  "ledger_head", "ledger_sha256"):
        if artifact.get(field) != expected[field]:
            raise ValueError("checkpoint artifact does not match ledger: %s" % field)
    return artifact


def _write_artifact(path, artifact):
    output = canonical.canonicalize(artifact).decode("utf-8") + "\n"
    if path == "-":
        sys.stdout.write(output)
        return
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(output)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    export = sub.add_parser("export", help="export the latest signed checkpoint")
    export.add_argument("--ledger", required=True)
    export.add_argument("--out", default="-", help="artifact path, or - for stdout")

    verify = sub.add_parser("verify", help="verify an artifact against a ledger")
    verify.add_argument("--ledger", required=True)
    verify.add_argument("--checkpoint", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "export":
            artifact = export_checkpoint(args.ledger)
            _write_artifact(args.out, artifact)
            print("checkpoint_event_id=%s" % artifact["checkpoint_event_id"], file=sys.stderr)
            print("checkpoint_artifact_sha256=%s" % hashlib.sha256(
                canonical.canonicalize(artifact)).hexdigest(), file=sys.stderr)
        else:
            artifact = verify_checkpoint(args.ledger, args.checkpoint)
            print("verified checkpoint_event_id=%s" % artifact["checkpoint_event_id"])
    except (OSError, ValueError, canonical.CanonicalError) as exc:
        raise SystemExit("checkpoint: %s" % exc)


if __name__ == "__main__":
    main()
