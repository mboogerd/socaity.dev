"""socaity ledger: append-only JSONL event log + append-time validator.

Implements the schema and predicates adopted in council/socaity-zyt.md
(envelope, closed catalog, validator predicates), council/socaity-ipg.md
(escrow acceptance + attribution.claimed) and council/socaity-a8o.md
(key.rebind_requested, lineage resolution, rotation/rebind rate limits).

Python standard library only.
"""

from .canonical import CanonicalError, canonicalize
from .catalog import CATALOGS, GENESIS_PREV
from .log import EventLog
from .validator import (DEFAULT_V, Ledger, ValidationError, event_id,
                        sign_event, signing_bytes)

__all__ = ["CanonicalError", "canonicalize", "CATALOGS", "GENESIS_PREV",
           "EventLog", "DEFAULT_V", "Ledger", "ValidationError", "event_id",
           "sign_event", "signing_bytes"]
