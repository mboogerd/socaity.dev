"""Append-time validator engine for the socaity ledger.

Every named predicate from the socaity-zyt / socaity-ipg / socaity-a8o
resolutions is implemented here and raises ValidationError with the predicate
name, so callers (and tests) can assert on *which* rule rejected an event.

Predicates
----------
envelope                    exact envelope shape {v,type,prev,actor,ts,payload,sig_alg,sig}
closed_catalog              v is a known version; type is in that version's catalog
closed_catalog_fields       payload has exactly the schema's required+optional fields
no_floats                   the event has an RFC 8785 canonical form at all: no
                            float anywhere (parse and serialise), no lone
                            surrogate, no integer outside +/-(2**53-1)
no_free_text                every string field matches a machine-checkable kind
closed_enum                 enum-kind fields are members of the V-versioned enum
hash_only_evidence          evidence is a non-empty list of SHA-256 hex digests
rational_bounds             {num,den} well formed; discount/stake factors in [0,1]
provenance_completeness     accrual-bearing observations carry every mandatory field
hash_chain                  prev == current head (genesis: 64 zeros)
timestamp                   ts is an integer, at most V.ts_future_grace_s ahead
signature                   sig_alg supported; sig verifies over canonical(event - sig)
genesis_prologue            the fixed prologue order is enforced mechanically
epoch_sequence              epochs open/close in order, one at a time
epoch_attestation           epoch.opened(e>=1) requires a matching rule.attested
attestation_uniqueness      one rule.attested per (rule_version, epoch)
checkpoint                  signed by the genesis checkpoint key; head/count/prev exact
week_ref_staleness          week_ref within window S of the checkpoint-bounded position
self_acceptance             ticket.accepted actor lineage != payload.contributor lineage
duplicate_open              no ticket.opened on an unclosed ticket_id / spec_hash
reference_integrity         every *_ref / target_event_id resolves in-chain
rotation_rate_limit         <= V.rotations_per_lineage_per_epoch rotations per epoch
fresh_key                   a successor/new/claimant key is not active in another lineage
pending_rebind_limit        one pending key.rebind_requested per orphaned lineage
escrow_binding              contributor==null <=> claim_binding present
claim_validity              attribution.claimed against an unclaimed matching escrow,
                            not self-claimed, adjudicated after N epochs
"""

import datetime
import hashlib
import re

from . import canonical, catalog, crypto
from .catalog import CATALOGS, GENESIS_PREV

__all__ = ["ValidationError", "DEFAULT_V", "Ledger", "event_id",
           "signing_bytes", "sign_event"]

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_WEEK = re.compile(r"^(\d{4})-W(\d{2})$")
_DAY = 86400

#: Rule parameters (V).  socaity-zyt/a8o put every one of these in V, not in
#: code; these are the adopted defaults pending socaity-wna final values.
DEFAULT_V = {
    "S_weeks": 2,                          # week_ref staleness window
    "claim_auto_epochs": 2,                # N: auto-claim hardens to adjudication
    "rotations_per_lineage_per_epoch": 1,
    "ts_future_grace_s": 300,
    "enums": catalog.ZERO_ENUMS,
}


class ValidationError(Exception):
    def __init__(self, predicate, message):
        self.predicate = predicate
        super().__init__("%s: %s" % (predicate, message))


# --- envelope helpers ------------------------------------------------------

ENVELOPE_KEYS = {"v", "type", "prev", "actor", "ts", "payload", "sig_alg", "sig"}


def signing_bytes(event) -> bytes:
    """The signed region: the canonical form of the envelope minus `sig`."""
    return canonical.canonicalize({k: v for k, v in event.items() if k != "sig"})


def event_id(event) -> str:
    """SHA-256 over the canonical form of the whole event, signature included."""
    return hashlib.sha256(canonical.canonicalize(event)).hexdigest()


def sign_event(secret_key: bytes, event) -> dict:
    """Return *event* with `sig` filled in (hex).  Test/ops convenience."""
    ev = dict(event)
    ev.pop("sig", None)
    ev["sig"] = crypto.sign(secret_key, signing_bytes(ev)).hex()
    return ev


def _week_bounds(w):
    m = _WEEK.match(w)
    if not m:
        raise ValidationError("no_free_text", "week_ref must be YYYY-Www: %r" % (w,))
    try:
        d = datetime.date.fromisocalendar(int(m.group(1)), int(m.group(2)), 1)
    except ValueError:
        raise ValidationError("no_free_text", "not an ISO week: %r" % (w,))
    start = int(datetime.datetime(d.year, d.month, d.day,
                                 tzinfo=datetime.timezone.utc).timestamp())
    return start, start + 7 * _DAY - 1


# --- the ledger state machine ---------------------------------------------

class Ledger:
    """In-memory replay state + the append-time validator.

    `append(event, receipt_ts)` validates against every predicate and, only if
    all pass, folds the event into state and returns its event_id.
    """

    def __init__(self, V=None):
        self.V = dict(DEFAULT_V if V is None else V)
        self.V.setdefault("enums", catalog.ZERO_ENUMS)
        self.head = GENESIS_PREV
        self.count = 0
        self.events = {}                # event_id -> event
        self.order = []                 # event_ids in chain order
        self.stage = 0                  # genesis-prologue stage
        self.founder_key = None
        self.checkpoint_key = None
        self.last_checkpoint_id = GENESIS_PREV
        self.last_checkpoint_ts = None
        self.checkpoint_seq = 0
        self.epoch_open = None
        self.last_epoch_closed = None
        self.attestations = set()       # (rule_version_hash, epoch)
        self.lineage = {}               # key -> lineage root key
        self.successors = {}            # lineage root -> designated successor
        self.rotations = {}             # (lineage, epoch) -> count
        self.pending_rebinds = {}       # orphan lineage -> rebind_requested id
        self.open_tickets = {}          # ticket_id -> ticket.opened event_id
        self.open_specs = {}            # spec_hash -> ticket_id
        self.escrows = {}               # acceptance event_id -> escrow record

    # -- lineage resolution (socaity-a8o) ---------------------------------
    def lineage_of(self, key):
        """Resolve a key to its lineage root, following the forward-only key
        lifecycle events already folded in (rotation and adjudicated rebinding).
        All audit surfaces are keyed to this value, never to the raw key."""
        seen = set()
        while key in self.lineage and self.lineage[key] != key:
            if key in seen:
                break
            seen.add(key)
            key = self.lineage[key]
        return key

    def lineage_map(self):
        """key -> lineage root, for every key the chain has ever seen."""
        return {k: self.lineage_of(k) for k in self.lineage}

    @property
    def current_epoch(self):
        if self.epoch_open is not None:
            return self.epoch_open
        return self.last_epoch_closed if self.last_epoch_closed is not None else 0

    @property
    def prologue_complete(self):
        return self.stage == 7

    # -- field kinds ------------------------------------------------------
    def _field(self, kind, value, where):
        E = ValidationError
        if kind == "hash" or kind == "id":
            if kind == "id" and value == GENESIS_PREV:
                return
            if not isinstance(value, str) or not _HEX64.match(value):
                raise E("no_free_text", "%s must be a sha-256 hex digest" % where)
        elif kind == "key":
            if not crypto.is_key(value):
                raise E("no_free_text", "%s must be a z6Mk key" % where)
        elif kind == "key?":
            if value is not None and not crypto.is_key(value):
                raise E("no_free_text", "%s must be a z6Mk key or null" % where)
        elif kind == "int":
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise E("no_floats", "%s must be a non-negative integer" % where)
        elif kind in ("rational", "unit"):
            if (not isinstance(value, dict) or set(value) != {"num", "den"}
                    or isinstance(value["num"], bool)
                    or isinstance(value["den"], bool)
                    or not isinstance(value["num"], int)
                    or not isinstance(value["den"], int)):
                raise E("rational_bounds", "%s must be {num:int, den:int}" % where)
            if value["den"] <= 0 or value["num"] < 0:
                raise E("rational_bounds", "%s must have den > 0, num >= 0" % where)
            if kind == "unit" and value["num"] > value["den"]:
                raise E("rational_bounds", "%s factor must lie in [0,1]" % where)
        elif kind == "week":
            _week_bounds(value if isinstance(value, str) else "")
        elif kind == "hashes":
            if not isinstance(value, list) or not value:
                raise E("hash_only_evidence", "%s must be a non-empty list" % where)
            for h in value:
                if not isinstance(h, str) or not _HEX64.match(h):
                    raise E("hash_only_evidence",
                            "%s may contain hashes only (no plaintext)" % where)
        elif kind == "ids":
            if not isinstance(value, list):
                raise E("no_free_text", "%s must be a list of event ids" % where)
            for i in value:
                self._field("id", i, where)
        elif kind.startswith("enum:"):
            name = kind[5:]
            allowed = self.V["enums"].get(name, ())
            if value not in allowed:
                raise E("closed_enum", "%s: %r not in closed enum %s"
                        % (where, value, name))
        else:                                             # pragma: no cover
            raise E("closed_catalog_fields", "unknown field kind %r" % kind)

    # -- append -----------------------------------------------------------
    def append(self, event, receipt_ts=None):
        if not isinstance(event, dict):
            raise ValidationError("envelope", "event must be a JSON object")
        if set(event) != ENVELOPE_KEYS:
            raise ValidationError(
                "envelope", "envelope keys must be exactly %s" % sorted(ENVELOPE_KEYS))

        # closed per-version catalog
        version = event["v"]
        if isinstance(version, bool) or not isinstance(version, int) \
                or version not in CATALOGS:
            raise ValidationError("closed_catalog", "unknown schema version %r" % (version,))
        cat = CATALOGS[version]
        etype = event["type"]
        if etype not in cat:
            raise ValidationError("closed_catalog",
                                  "type %r is not in the v%s catalog" % (etype, version))

        # no floats anywhere (also rejects unserialisable types)
        try:
            canonical.canonicalize(event)
        except canonical.CanonicalError as exc:
            raise ValidationError("no_floats", str(exc))

        # payload schema: exact field set, machine-checkable kinds
        _cls, required, optional = cat[etype]
        payload = event["payload"]
        if not isinstance(payload, dict):
            raise ValidationError("closed_catalog_fields", "payload must be an object")
        extra = set(payload) - set(required) - set(optional)
        if extra:
            raise ValidationError("closed_catalog_fields",
                                  "%s: unknown payload fields %s" % (etype, sorted(extra)))
        missing = set(required) - set(payload)
        if missing:
            pred = ("provenance_completeness" if etype in catalog.ACCRUAL_TYPES
                    else "closed_catalog_fields")
            raise ValidationError(pred, "%s: missing fields %s" % (etype, sorted(missing)))
        for name, kind in list(required.items()) + list(optional.items()):
            if name in payload:
                self._field(kind, payload[name], "%s.%s" % (etype, name))

        # provenance completeness as its own named predicate
        for name in catalog.ACCRUAL_MANDATORY.get(etype, ()):
            if payload.get(name) in (None, [], ""):
                raise ValidationError("provenance_completeness",
                                      "%s: mandatory field %r is empty" % (etype, name))

        # hash chain
        if event["prev"] != self.head:
            raise ValidationError("hash_chain",
                                  "prev %r does not match head %r" % (event["prev"], self.head))

        # timestamp
        ts = event["ts"]
        if isinstance(ts, bool) or not isinstance(ts, int):
            raise ValidationError("timestamp", "ts must be integer seconds since epoch")
        rts = ts if receipt_ts is None else receipt_ts
        if ts > rts + self.V["ts_future_grace_s"]:
            raise ValidationError("timestamp", "ts is more than %ss in the future"
                                  % self.V["ts_future_grace_s"])

        # signature over the canonical signed region
        actor = event["actor"]
        try:
            pub = crypto.decode_key(actor)
        except ValueError as exc:
            raise ValidationError("signature", str(exc))
        if event["sig_alg"] not in crypto.VERIFIERS:
            raise ValidationError("signature", "unsupported sig_alg %r" % (event["sig_alg"],))
        try:
            raw = bytes.fromhex(event["sig"])
        except (ValueError, TypeError):
            raise ValidationError("signature", "sig must be hex")
        if not crypto.verify(event["sig_alg"], pub, signing_bytes(event), raw):
            raise ValidationError("signature", "signature does not verify for actor")

        # sequencing + semantics
        self._prologue(etype, event)
        self._semantics(etype, event, rts)

        eid = event_id(event)
        self._commit(eid, etype, event)
        return eid

    # -- genesis prologue --------------------------------------------------
    def _prologue(self, etype, event):
        stage = self.stage
        if stage == 0:
            if etype != "genesis":
                raise ValidationError("genesis_prologue",
                                      "the first event must be `genesis`, got %r" % etype)
            return
        # checkpoints may be published at any point without advancing the prologue
        if etype == "checkpoint.published":
            return
        if stage < 7 and event["actor"] != self.founder_key:
            raise ValidationError("genesis_prologue",
                                  "prologue events must be signed by the genesis actor")
        expected = {1: "rule.version_published", 2: "rule.meta_published",
                    4: "epoch.closed", 5: "rule.attested", 6: "epoch.opened"}
        if stage == 3:
            if etype in catalog.EPOCH0_TYPES:
                return
            if etype == "epoch.opened" and event["payload"]["epoch"] == 0:
                return
            raise ValidationError(
                "genesis_prologue",
                "expected epoch-0 founder observations or epoch.opened(0), got %r" % etype)
        if stage in expected:
            if etype != expected[stage]:
                raise ValidationError("genesis_prologue",
                                      "expected %r at this position, got %r"
                                      % (expected[stage], etype))
            if stage == 6 and event["payload"]["epoch"] != 1:
                raise ValidationError("genesis_prologue",
                                      "the prologue ends with epoch.opened(1)")
            return
        # stage 7: prologue complete, the whole catalog is open

    # -- type-specific predicates -----------------------------------------
    def _semantics(self, etype, event, rts):
        p = event["payload"]
        actor = event["actor"]
        lin = self.lineage_of(actor)
        V = self.V

        def ref(name, kinds=None):
            target = self.events.get(p[name])
            if target is None:
                raise ValidationError("reference_integrity",
                                      "%s.%s does not resolve in-chain" % (etype, name))
            if kinds and target["type"] not in kinds:
                raise ValidationError("reference_integrity",
                                      "%s.%s must reference %s" % (etype, name, kinds))
            return target

        if etype == "checkpoint.published":
            if self.checkpoint_key is None or \
                    self.lineage_of(actor) != self.lineage_of(self.checkpoint_key):
                raise ValidationError("checkpoint",
                                      "checkpoints must be signed by the genesis checkpoint key")
            if p["head_event_id"] != self.head or p["event_count"] != self.count \
                    or p["prev_checkpoint_ref"] != self.last_checkpoint_id \
                    or p["checkpoint_seq"] != self.checkpoint_seq + 1:
                raise ValidationError("checkpoint",
                                      "checkpoint does not commit to the current head/count/seq")

        elif etype == "epoch.opened":
            nxt = 0 if self.last_epoch_closed is None else self.last_epoch_closed + 1
            if self.epoch_open is not None:
                raise ValidationError("epoch_sequence",
                                      "epoch %s is still open" % self.epoch_open)
            if p["epoch"] != nxt:
                raise ValidationError("epoch_sequence",
                                      "expected epoch %s, got %s" % (nxt, p["epoch"]))
            if p["epoch"] >= 1 and (p["rule_version_hash"], p["epoch"]) not in self.attestations:
                raise ValidationError("epoch_attestation",
                                      "no rule.attested for (rule_version, epoch %s)" % p["epoch"])

        elif etype == "epoch.closed":
            if self.epoch_open is None or p["epoch"] != self.epoch_open:
                raise ValidationError("epoch_sequence",
                                      "epoch %s is not open" % p["epoch"])

        elif etype == "rule.attested":
            if (p["rule_version_hash"], p["epoch"]) in self.attestations:
                raise ValidationError("attestation_uniqueness",
                                      "attestation for this (rule_version, epoch) exists")

        elif etype == "ticket.opened":
            if p["ticket_id"] in self.open_tickets:
                raise ValidationError("duplicate_open",
                                      "ticket %s is already open" % p["ticket_id"][:12])
            if p["spec_hash"] in self.open_specs:
                raise ValidationError("duplicate_open",
                                      "an unclosed ticket already carries this spec_hash")

        elif etype == "ticket.closed":
            if p["ticket_id"] not in self.open_tickets:
                raise ValidationError("reference_integrity",
                                      "ticket %s is not open" % p["ticket_id"][:12])

        elif etype in ("ticket.accepted", "contribution.trivial_accepted"):
            if etype == "ticket.accepted":
                target = ref("ticket_ref", ("ticket.opened",))
                if target["payload"]["ticket_id"] != p["ticket_id"]:
                    raise ValidationError("reference_integrity",
                                          "ticket_ref/ticket_id disagree")
            self._staleness(etype, p["week_ref"], rts)
            if p["contributor"] is None:
                if "claim_binding" not in p:
                    raise ValidationError("escrow_binding",
                                          "contributor=null requires claim_binding")
            else:
                if "claim_binding" in p:
                    raise ValidationError("escrow_binding",
                                          "claim_binding is for escrowed (null-contributor) entries")
                if self.lineage_of(p["contributor"]) == lin:
                    raise ValidationError("self_acceptance",
                                          "the acceptor may not be the contributor")

        elif etype == "work.logged":
            self._staleness(etype, p["week_ref"], rts)

        elif etype == "attribution.claimed":
            escrow = self.escrows.get(p["escrow_ref"])
            if escrow is None:
                raise ValidationError("claim_validity",
                                      "escrow_ref is not an escrowed acceptance")
            if escrow["claimed"]:
                raise ValidationError("claim_validity", "escrow is already claimed")
            if p["claim_binding"] != escrow["claim_binding"]:
                raise ValidationError("claim_validity",
                                      "claim_binding does not match the escrow's binding")
            # DERIVED PREDICATE (not verbatim in any resolution).  socaity-zyt
            # adopts "self-acceptance rejected" as a validator predicate and
            # binds it to ticket.accepted via actor != payload.contributor.
            # socaity-ipg then made contributor nullable, which moves the
            # naming of the contributor out of the acceptance and into
            # attribution.claimed -- so without this check the adopted
            # predicate is bypassable by escrowing to oneself and claiming it,
            # which is what MD's "attribution slush fund" paramount and the
            # "escrow against a puppet account" objection are about.  It is an
            # extension of an adopted predicate to the path ipg created, not a
            # new policy; if a council rules otherwise, delete this block --
            # nothing else depends on it.
            if self.lineage_of(escrow["acceptor"]) == lin:
                raise ValidationError("claim_validity",
                                      "the accepting maintainer may not claim their own escrow")
            if self.current_epoch - escrow["epoch"] >= V["claim_auto_epochs"] \
                    and "adjudication_ref" not in p:
                raise ValidationError(
                    "claim_validity",
                    "after %s epochs the claim requires an adjudication_ref"
                    % V["claim_auto_epochs"])
            if "adjudication_ref" in p:
                ref("adjudication_ref")

        elif etype == "key.successor_designated":
            self._fresh_key(p["successor_key"], lin)

        elif etype == "key.rotated":
            self._fresh_key(p["new_key"], lin)
            used = self.rotations.get((lin, self.current_epoch), 0)
            if used >= V["rotations_per_lineage_per_epoch"]:
                raise ValidationError(
                    "rotation_rate_limit",
                    "lineage already rotated %s time(s) in epoch %s"
                    % (used, self.current_epoch))

        elif etype == "key.rebind_requested":
            orphan = self.lineage_of(p["orphan_key"])
            if p["orphan_key"] not in self.lineage:
                raise ValidationError("reference_integrity",
                                      "orphan_key has never appeared on the chain")
            if orphan in self.pending_rebinds:
                raise ValidationError("pending_rebind_limit",
                                      "a rebind request is already pending for this lineage")
            self._fresh_key(p["claimant_key"], orphan)

        elif etype == "key.rebound":
            req = ref("rebind_request_ref", ("key.rebind_requested",))
            ref("adjudication_ref")
            orphan = self.lineage_of(p["orphan_key"])
            if req["payload"]["orphan_key"] != p["orphan_key"]:
                raise ValidationError("reference_integrity",
                                      "rebind_request_ref names a different orphan_key")
            if self.pending_rebinds.get(orphan) != p["rebind_request_ref"]:
                raise ValidationError("reference_integrity",
                                      "no matching pending rebind request")

        elif etype in ("entry.withdrawn", "entry.status_changed"):
            target = ref("target_event_id")
            if etype == "entry.withdrawn" and \
                    self.lineage_of(target["actor"]) != lin:
                raise ValidationError("reference_integrity",
                                      "only the entry's own lineage may withdraw it")

        elif etype in ("challenge.filed", "audit.review_opened"):
            ref("target_event_id")

    def _fresh_key(self, key, lin):
        """No cross-lineage key reuse (socaity-a8o); merges only via adjudication."""
        if key in self.lineage and self.lineage_of(key) != lin:
            raise ValidationError("fresh_key",
                                  "key is already active in another lineage")

    def _staleness(self, etype, week_ref, rts):
        """week_ref window S, evaluated against the checkpoint-bounded position.

        Lower bound of the append position = the ts of the last published
        checkpoint (chain position, never a field); before the first checkpoint
        the receipt bound is used.  The declared week must already have begun,
        and must not have ended more than S weeks before the bound.

        The fallback must NOT be the event's own declared `ts`: socaity-zyt
        adopted this predicate precisely because the cap bucket has to be
        "week-granular AND not actor-backdatable", and an actor who declares a
        stale ts alongside a stale week_ref would otherwise validate itself.
        On replay the receipt bound degrades to the declared ts by
        construction (append time is not a field) -- there the checkpoints are
        the bound, which is why they are mandatory rather than advisory.
        """
        start, end = _week_bounds(week_ref)
        lower = self.last_checkpoint_ts if self.last_checkpoint_ts is not None else rts
        if start > rts + self.V["ts_future_grace_s"]:
            raise ValidationError("week_ref_staleness",
                                  "%s: week_ref %s has not begun" % (etype, week_ref))
        if end < lower - self.V["S_weeks"] * 7 * _DAY:
            raise ValidationError("week_ref_staleness",
                                  "%s: week_ref %s is older than the %s-week window"
                                  % (etype, week_ref, self.V["S_weeks"]))

    # -- state fold --------------------------------------------------------
    def _commit(self, eid, etype, event):
        p = event["payload"]
        actor = event["actor"]
        self.lineage.setdefault(actor, actor)
        lin = self.lineage_of(actor)

        if etype == "genesis":
            self.founder_key = actor
            self.checkpoint_key = p["checkpoint_key"]
            self.lineage.setdefault(p["checkpoint_key"], p["checkpoint_key"])
            self.stage = 1
        elif etype == "checkpoint.published":
            self.last_checkpoint_id = eid
            self.last_checkpoint_ts = event["ts"]
            self.checkpoint_seq = p["checkpoint_seq"]
        elif etype == "rule.version_published" and self.stage == 1:
            self.stage = 2
        elif etype == "rule.meta_published" and self.stage == 2:
            self.stage = 3

        if etype == "epoch.opened":
            self.epoch_open = p["epoch"]
            if self.stage == 3 and p["epoch"] == 0:
                self.stage = 4
            elif self.stage == 6:
                self.stage = 7
        elif etype == "epoch.closed":
            self.last_epoch_closed = p["epoch"]
            self.epoch_open = None
            if self.stage == 4:
                self.stage = 5
        elif etype == "rule.attested":
            self.attestations.add((p["rule_version_hash"], p["epoch"]))
            if self.stage == 5:
                self.stage = 6
        elif etype == "ticket.opened":
            self.open_tickets[p["ticket_id"]] = eid
            self.open_specs[p["spec_hash"]] = p["ticket_id"]
        elif etype == "ticket.closed":
            spec = self.events[self.open_tickets.pop(p["ticket_id"])]["payload"]["spec_hash"]
            self.open_specs.pop(spec, None)
        elif etype in ("ticket.accepted", "contribution.trivial_accepted"):
            if p["contributor"] is None:
                self.escrows[eid] = {"claim_binding": p["claim_binding"],
                                     "acceptor": actor, "epoch": self.current_epoch,
                                     "claimed": False, "claimant": None}
            else:
                self.lineage.setdefault(p["contributor"], p["contributor"])
        elif etype == "attribution.claimed":
            esc = self.escrows[p["escrow_ref"]]
            esc["claimed"] = True
            esc["claimant"] = actor
        elif etype == "key.successor_designated":
            self.successors[lin] = p["successor_key"]
        elif etype == "key.rotated":
            self.lineage[p["new_key"]] = lin
            k = (lin, self.current_epoch)
            self.rotations[k] = self.rotations.get(k, 0) + 1
        elif etype == "key.rebind_requested":
            self.pending_rebinds[self.lineage_of(p["orphan_key"])] = eid
        elif etype == "key.rebound":
            orphan = self.lineage_of(p["orphan_key"])
            claimant = self.events[p["rebind_request_ref"]]["payload"]["claimant_key"]
            self.lineage[claimant] = orphan
            self.pending_rebinds.pop(orphan, None)

        self.events[eid] = event
        self.order.append(eid)
        self.head = eid
        self.count += 1

    # -- replay helpers ----------------------------------------------------
    def attribution_of(self, acceptance_event_id):
        """Resolved contributor lineage for an acceptance, escrowed or not."""
        ev = self.events[acceptance_event_id]
        contributor = ev["payload"].get("contributor")
        if contributor is not None:
            return self.lineage_of(contributor)
        esc = self.escrows.get(acceptance_event_id)
        if esc and esc["claimed"]:
            return self.lineage_of(esc["claimant"])
        return None            # attribution reserved, awaiting the claim
