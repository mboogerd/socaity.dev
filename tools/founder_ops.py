#!/usr/bin/env python3
"""Signed maintainer operations for the append-only ledger.

This is deliberately a thin command-line boundary: it never edits JSONL
directly.  Every operation constructs one event, signs it, and delegates
validation and durable append to :class:`ledger.log.EventLog`.
"""

import argparse
import hashlib
import json
import time

from ledger import crypto
from ledger.log import EventLog, ValidationError
from ledger.validator import sign_event


def _secret(path):
    """Read a 32-byte secret from a file (raw bytes or 64-char hex)."""
    with open(path, "rb") as handle:
        raw = handle.read()
    try:
        decoded = bytes.fromhex(raw.decode("ascii").strip())
    except (UnicodeDecodeError, ValueError):
        decoded = raw
    if len(decoded) != 32:
        raise ValueError("secret file must contain exactly 32 raw bytes or 64 hex characters")
    return decoded


def _hash(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hashes(values):
    return [_hash(value) for value in values]


def _payload(args):
    if args.payload_file:
        with open(args.payload_file, encoding="utf-8") as handle:
            payload = json.load(handle)
    else:
        payload = json.loads(args.payload)
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    return payload


def _append(log, secret, event_type, payload, timestamp):
    event = {
        "v": 1,
        "type": event_type,
        "prev": log.head,
        "actor": crypto.encode_key(crypto.public_from_secret(secret)),
        "ts": timestamp,
        "payload": payload,
        "sig_alg": crypto.SIG_ALG,
    }
    return log.append(sign_event(secret, event), receipt_ts=timestamp)


def _timestamp(args):
    return args.ts if args.ts is not None else int(time.time())


def _add_common(parser):
    parser.add_argument("--ledger", required=True, help="append-only JSONL ledger path")
    parser.add_argument("--secret-file", required=True, help="founder signing secret")
    parser.add_argument("--ts", type=int, help="event timestamp (defaults to current UTC time)")


def _command_append(args):
    log = EventLog(args.ledger)
    eid = _append(log, _secret(args.secret_file), args.type,
                  _payload(args), _timestamp(args))
    print(json.dumps({"event_id": eid, "head": log.head, "count": log.count}))


def _command_checkpoint(args):
    log = EventLog(args.ledger)
    secret = _secret(args.secret_file)
    if log.ledger.checkpoint_key != crypto.encode_key(crypto.public_from_secret(secret)):
        raise ValueError("checkpoint secret does not match the genesis checkpoint key")
    seq = log.ledger.checkpoint_seq + 1
    payload = {
        "checkpoint_seq": seq,
        "head_event_id": log.head,
        "event_count": log.count,
        "prev_checkpoint_ref": log.ledger.last_checkpoint_id,
    }
    eid = _append(log, secret, "checkpoint.published", payload, _timestamp(args))
    print(json.dumps({"event_id": eid, "checkpoint_seq": seq,
                      "head": log.head, "count": log.count}))


def _command_verify(args):
    log = EventLog(args.ledger)
    print(json.dumps({"valid": True, "head": log.head, "count": log.count}))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    append = sub.add_parser("append", help="sign and append one catalogued event")
    _add_common(append)
    append.add_argument("--type", required=True, help="v1 event type")
    payload = append.add_mutually_exclusive_group(required=True)
    payload.add_argument("--payload", help="payload JSON object")
    payload.add_argument("--payload-file", help="file containing payload JSON")
    append.set_defaults(run=_command_append)

    checkpoint = sub.add_parser("checkpoint", help="publish the next signed checkpoint")
    _add_common(checkpoint)
    checkpoint.set_defaults(run=_command_checkpoint)

    verify = sub.add_parser("verify", help="replay and validate an existing ledger")
    verify.add_argument("--ledger", required=True, help="append-only JSONL ledger path")
    verify.set_defaults(run=_command_verify)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.run(args)
    except (OSError, ValueError, ValidationError, json.JSONDecodeError) as exc:
        raise SystemExit("founder-ops: %s" % exc)


if __name__ == "__main__":
    main()
