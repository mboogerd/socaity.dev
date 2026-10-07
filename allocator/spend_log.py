# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 MacBoo

"""Append-only JSONL metering for allocator worker sessions.

The file is deliberately boring: one schema-versioned record per completed
session and no update or delete path.  A separate lock file makes appends from
multiple local worker processes serialize before the one-line write.
"""

from __future__ import annotations

import datetime as _datetime
import fcntl
import json
import os
from typing import Any, Iterator, Mapping

SCHEMA_VERSION = 1
RECORD_FIELDS = frozenset(("v", "project", "machine", "work_item", "started", "ended"))
OPTIONAL_FIELDS = frozenset(("starved", "reason"))


class ValidationError(ValueError):
    """Raised when a spend-log record is not a valid v1 record."""


def utc_timestamp(value: _datetime.datetime | None = None) -> str:
    """Return an ISO-8601 UTC timestamp with a stable ``Z`` suffix."""

    value = value or _datetime.datetime.now(_datetime.timezone.utc)
    if value.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return value.astimezone(_datetime.timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _parse_timestamp(value: Any, field: str) -> _datetime.datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValidationError(f"{field} must be an ISO-8601 UTC timestamp")
    try:
        parsed = _datetime.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ValidationError(f"{field} must be an ISO-8601 UTC timestamp") from exc
    if parsed.tzinfo is None:
        raise ValidationError(f"{field} must include a timezone")
    return parsed.astimezone(_datetime.timezone.utc)


def validate_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a copy of one schema-v1 spend record."""

    if not isinstance(record, Mapping):
        raise ValidationError("record must be an object")
    fields = set(record)
    if not RECORD_FIELDS <= fields or fields - RECORD_FIELDS - OPTIONAL_FIELDS:
        raise ValidationError("record fields must be the session fields plus optional observation fields")
    if record["v"] != SCHEMA_VERSION or isinstance(record["v"], bool):
        raise ValidationError("v must be the integer schema version 1")
    for field in ("project", "machine", "work_item"):
        if not isinstance(record[field], str) or not record[field].strip():
            raise ValidationError(f"{field} must be a non-empty string")
    started = _parse_timestamp(record["started"], "started")
    ended = _parse_timestamp(record["ended"], "ended")
    if ended < started:
        raise ValidationError("ended must not precede started")
    if "starved" in record:
        starved = record["starved"]
        if (not isinstance(starved, list) or
                any(not isinstance(project, str) or not project.strip() for project in starved)):
            raise ValidationError("starved must be a list of non-empty project names")
    if "reason" in record:
        if record["reason"] not in {"drawn", "cap-hit", "no-ready-work"}:
            raise ValidationError("reason must be a known draw outcome")
    return dict(record)


class SpendLog:
    """A schema-validating, append-only JSONL spend log."""

    def __init__(self, path: str | os.PathLike[str]):
        self.path = os.fspath(path)
        self.lock_path = self.path + ".lock"

    def append(self, record: Mapping[str, Any]) -> dict[str, Any]:
        """Validate and durably append exactly one JSON line."""

        checked = validate_record(record)
        parent = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(parent, exist_ok=True)
        encoded = (json.dumps(checked, sort_keys=True, separators=(",", ":")) + "\n").encode()
        with open(self.lock_path, "a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                with open(self.path, "ab", buffering=0) as output:
                    output.write(encoded)
                    os.fsync(output.fileno())
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        return checked

    def records(self) -> Iterator[dict[str, Any]]:
        """Yield every valid record, rejecting malformed JSONL."""

        try:
            handle = open(self.path, encoding="utf-8")
        except FileNotFoundError:
            return
        with handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    raise ValidationError(f"line {line_number}: blank records are not allowed")
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValidationError(f"line {line_number}: invalid JSON") from exc
                try:
                    yield validate_record(record)
                except ValidationError as exc:
                    raise ValidationError(f"line {line_number}: {exc}") from exc
