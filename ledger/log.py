"""Append-only JSONL event log.

One canonical (RFC 8785) JSON object per line, in chain order.  The file is
opened for append only; there is no update or delete path -- corrections are
new signed events (entry.status_changed / entry.withdrawn).  Nothing is written
until the validator has accepted the event.
"""

import os

from . import canonical
from .validator import Ledger, ValidationError, event_id

__all__ = ["EventLog", "ValidationError"]


class EventLog:
    def __init__(self, path, V=None):
        self.path = path
        self.ledger = Ledger(V)
        if os.path.exists(path):
            self._replay()

    def _replay(self):
        with open(self.path, "r", encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                event = canonical.loads(line)
                if canonical.canonicalize(event).decode("utf-8") != line:
                    raise ValidationError("canonical_form",
                                          "line %d is not RFC 8785 canonical" % n)
                try:
                    # Replay re-checks every predicate, with the event's own
                    # declared ts as the receipt bound (append time is already
                    # fixed by chain position + checkpoints).
                    self.ledger.append(event)
                except ValidationError as exc:
                    raise ValidationError(exc.predicate,
                                          "line %d: %s" % (n, exc.args[0]))

    def append(self, event, receipt_ts=None):
        """Validate then durably append.  Returns the event_id."""
        eid = self.ledger.append(event, receipt_ts)
        with open(self.path, "a", encoding="utf-8") as fh:
            fh.write(canonical.canonicalize(event).decode("utf-8") + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        return eid

    # convenience read surface
    @property
    def head(self):
        return self.ledger.head

    @property
    def count(self):
        return self.ledger.count

    def events(self):
        return [self.ledger.events[i] for i in self.ledger.order]
