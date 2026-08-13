"""The distribution rule v1 -- the reference implementation.

ONE PURE FUNCTION.  ``distribute(request) -> table``: no I/O, no wall clock,
no environment, no randomness, no dict-iteration-order dependence (every
iteration is over an explicitly sorted list), no floats anywhere
(AST-lint-enforced by ``rule/lint_no_float.py``), exact rationals throughout,
Python standard library only.  Given the same request bytes, every machine
running any CPython >= 3.10 produces byte-identical canonical output.

The formula (socaity-x8o Resolution §1-§5)
------------------------------------------
Weight      w = V(category, unit) * quantity, floored to integer micro-vu,
            times the decided discount factor if the entry was discounted.
Denominator D_e = sum of w over every INCLUDED entry of epoch e, MODE-BLIND:
            mode-A entries count in D_e exactly like mode-E entries, because
            electing A must not pump the shares of E holders.
Claim       R_i = sum over closed+audited epochs of P_e * w_{i,e,E} / D_e.
            Mode-A weights and unclaimed fractions LAPSE -- they are never
            rolled forward into another epoch.
Payout      the declared inflow, net of the capped audit slice, split in
            proportion to R_i: floor to the quantum, then largest remainder,
            ties by entry hash.  The residual goes entirely to contributors.
            The table sums EXACTLY to the declared amount on every replay.

Holds
-----
A claim that is presently unpayable is still computed and still occupies its
exact share; it is booked to an ``escrow`` recipient rather than a ``lineage``
recipient, with a ``hold`` reason:

  * ``challenge``   -- the entry is challenged; socaity-zjr escrows it at its
                       DECLARED weight pending decision;
  * ``attribution`` -- the entry is an escrowed acceptance whose contributor
                       is still null (socaity-ipg): "attribution reserved,
                       awaiting their signature".  The value never expires.

Holds are part of the conservation identity, so a later adjudication changes
who is paid, never how much the table distributes.

What this module deliberately does NOT contain
----------------------------------------------
Any transfer operation, for either mode (legal-counsel (b): non-transferability
is enforced by the absence of the operation).  Any per-unit price for an epoch
weight.  Any currency-style formatting: the only monetary column is
``amount_minor`` beside an explicit ISO currency code, and epoch weights are
never rendered as holdings.
"""

import hashlib
from fractions import Fraction

from ledger.canonical import canonicalize

from . import params as P
from .valuation import compute_credit_micro, weight_micro_vu

__all__ = ["RuleError", "STRUCTURE_VERSION", "distribute", "table_hash",
           "canonical_bytes"]

#: Bumping this is a STRUCTURE change: it may only take effect for epochs that
#: have never been opened, and the meta-rule refuses it as an amendment
#: (socaity-1ux: the formula structure is final for every epoch opened under
#: the rule version that published it).
STRUCTURE_VERSION = 1

#: Statuses from the validation snapshot (socaity-zjr lifecycle).
#: included -> the entry enters D_e;  payable -> its claim is not held.
_STATUS = {
    "confirmed":   {"included": True,  "hold": None},
    "discounted":  {"included": True,  "hold": None},
    "challenged":  {"included": True,  "hold": "challenge"},
    "provisional": {"included": False, "hold": None},
    "withdrawn":   {"included": False, "hold": None},
}

_ENTRY_REQUIRED = ("entry_hash", "epoch", "mode", "category", "native_unit",
                   "quantity_micro", "lineage")
_ENTRY_OPTIONAL = ("tier",)


class RuleError(ValueError):
    """The request is not a well-formed input to the rule."""


def _div(a, b):
    """Exact rational division, written without the `/` operator.

    ``rule/lint_no_float.py`` bans `/` outright: on two ints it silently
    produces a float, and a reviewer cannot tell the safe uses from the unsafe
    ones by looking.  Cross-multiplication is exact for any Fractions and
    needs no operator ban exception.
    """
    if b.numerator == 0:
        raise RuleError("exact division by zero")
    return Fraction(a.numerator * b.denominator, a.denominator * b.numerator)


# --- request validation ----------------------------------------------------

def _int(value, where, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int):
        raise RuleError("%s must be an integer (the rule admits no floats)" % where)
    if value < minimum:
        raise RuleError("%s must be >= %d" % (where, minimum))
    return value


def _obj(value, where):
    if not isinstance(value, dict):
        raise RuleError("%s must be an object" % where)
    return value


def _str(value, where, allow_null=False):
    """Identity/label fields are strings, and are type-checked for the same
    reason the numeric fields are: `json.loads` of an untrusted export yields
    whatever the bytes said.  A float landing in an identity column never
    reaches the arithmetic, but it would be copied into the payout table, and
    the table is what gets hashed onto the ledger -- so it is refused at the
    boundary rather than at serialisation.
    """
    if allow_null and value is None:
        return value
    if not isinstance(value, str):
        raise RuleError("%s must be a string (the rule admits no floats)" % where)
    return value


def _check_request(request):
    _obj(request, "request")
    missing = {"rule_version", "params", "ledger_export", "validation_snapshot",
               "declared"} - set(request)
    if missing:
        raise RuleError("request is missing %s" % sorted(missing))
    unknown = set(request) - {"rule_version", "params", "ledger_export",
                              "validation_snapshot", "declared"}
    if unknown:
        raise RuleError("request has unknown keys %s" % sorted(unknown))

    P.validate_params(_obj(request["params"], "params"))
    _str(request["rule_version"], "rule_version")

    export = _obj(request["ledger_export"], "ledger_export")
    for name in ("checkpoint_hash", "epochs", "entries"):
        if name not in export:
            raise RuleError("ledger_export is missing %r" % name)
    _str(export["checkpoint_hash"], "ledger_export.checkpoint_hash")

    declared = _obj(request["declared"], "declared")
    for name in ("distribution_id", "amount_minor", "currency",
                 "cutoff_checkpoint_hash"):
        if name not in declared:
            raise RuleError("declared is missing %r" % name)
    _int(declared["amount_minor"], "declared.amount_minor")
    for name in ("distribution_id", "currency", "cutoff_checkpoint_hash"):
        _str(declared[name], "declared.%s" % name)

    seen = set()
    for index, epoch in enumerate(export["epochs"]):
        _obj(epoch, "epochs[%d]" % index)
        _int(epoch.get("index"), "epochs[%d].index" % index)
        if epoch["index"] in seen:
            raise RuleError("epoch %d appears twice in the export" % epoch["index"])
        seen.add(epoch["index"])
        for flag in ("closed", "audited"):
            if not isinstance(epoch.get(flag), bool):
                raise RuleError("epochs[%d].%s must be a boolean" % (index, flag))

    hashes = set()
    for index, entry in enumerate(export["entries"]):
        _obj(entry, "entries[%d]" % index)
        for name in _ENTRY_REQUIRED:
            if name not in entry:
                raise RuleError("entries[%d] is missing %r" % (index, name))
        unknown = set(entry) - set(_ENTRY_REQUIRED) - set(_ENTRY_OPTIONAL)
        if unknown:
            raise RuleError("entries[%d] has unknown keys %s" % (index, sorted(unknown)))
        if entry["entry_hash"] in hashes:
            raise RuleError("duplicate entry_hash %r" % entry["entry_hash"])
        hashes.add(entry["entry_hash"])
        _int(entry["epoch"], "entries[%d].epoch" % index)
        _int(entry["quantity_micro"], "entries[%d].quantity_micro" % index)
        _str(entry["entry_hash"], "entries[%d].entry_hash" % index)
        _str(entry["lineage"], "entries[%d].lineage" % index, allow_null=True)
        _str(entry["category"], "entries[%d].category" % index)
        _str(entry["native_unit"], "entries[%d].native_unit" % index)
        if "tier" in entry:
            _str(entry["tier"], "entries[%d].tier" % index)
        if entry["mode"] not in ("E", "A"):
            raise RuleError("entries[%d].mode must be 'E' or 'A' -- the election "
                            "is irrevocable and lives in the immutable "
                            "observation" % index)
        if entry["epoch"] not in seen:
            raise RuleError("entries[%d] names epoch %s, which the export does "
                            "not describe" % (index, entry["epoch"]))

    snapshot = _obj(request["validation_snapshot"], "validation_snapshot")
    if "entries" not in snapshot:
        raise RuleError("validation_snapshot is missing 'entries'")
    _obj(snapshot["entries"], "validation_snapshot.entries")
    for key, state in snapshot["entries"].items():
        _obj(state, "validation_snapshot.entries[%s]" % key)
        if state.get("status") not in _STATUS:
            raise RuleError("validation_snapshot.entries[%s].status %r is not one "
                            "of %s" % (key, state.get("status"), sorted(_STATUS)))
        if state["status"] == "discounted" and "discount" not in state:
            # Fail closed.  A snapshot that says "discounted" without saying by
            # how much used to mean "discounted by zero", i.e. full weight --
            # a silent fail-open on the one input that lowers a weight.
            raise RuleError("validation_snapshot.entries[%s] is 'discounted' "
                            "but names no discount factor: the decided "
                            "discount is part of the snapshot (socaity-zjr), "
                            "never a default" % key)
        if "discount" in state:
            factor = P.rational(state["discount"],
                                "validation_snapshot.entries[%s].discount" % key)
            if factor < 0 or factor > 1:
                raise RuleError("discount factor for %s must lie in [0, 1]" % key)
        if key not in hashes:
            raise RuleError("validation_snapshot names unknown entry %r" % key)


# --- the rule --------------------------------------------------------------

def distribute(request):
    """The rule.  request (canonical JSON object) -> payout table.

    Pure: the return value depends on nothing but *request*.
    """
    _check_request(request)
    params = request["params"]
    export = request["ledger_export"]
    snapshot = request["validation_snapshot"]["entries"]
    declared = request["declared"]

    # Eligible epochs: closed AND audited only.  Open epochs never participate
    # (socaity-x8o §4); an unaudited epoch is not final (socaity-zjr).
    epochs = sorted(export["epochs"], key=lambda e: e["index"])
    eligible = [e["index"] for e in epochs if e["closed"] and e["audited"]]
    eligible_set = set(eligible)

    # Entries in a fixed order: entry hash ascending.  Nothing downstream may
    # depend on the order they arrived in.
    entries = sorted(export["entries"], key=lambda e: e["entry_hash"])

    weights = {}          # entry_hash -> integer micro-vu
    holds = {}            # entry_hash -> None | "challenge" | "attribution"
    included = []         # entries that enter a denominator
    for entry in entries:
        if entry["epoch"] not in eligible_set:
            continue
        state = snapshot.get(entry["entry_hash"], {"status": "provisional"})
        rules = _STATUS[state["status"]]
        if not rules["included"]:
            continue
        # A challenged entry is escrowed at its DECLARED weight: no discount is
        # applied until a decision lands (socaity-zjr).
        discount = None
        if state["status"] == "discounted":
            # Present by construction: _check_request refuses a discounted
            # entry that names no factor.
            discount = P.rational(state["discount"], "discount")
        weights[entry["entry_hash"]] = weight_micro_vu(entry, params, discount)
        hold = rules["hold"]
        if hold is None and entry["mode"] == "E" and entry["lineage"] is None:
            hold = "attribution"
        holds[entry["entry_hash"]] = hold
        included.append(entry)

    # D_e: mode-blind, over included entries only.
    denominators = {}
    for index in eligible:
        denominators[index] = 0
    for entry in included:
        denominators[entry["epoch"]] += weights[entry["entry_hash"]]

    # R_i, accumulated onto claim holders.  Mode-A weights are in D_e and
    # produce no claim: that fraction lapses.
    claims = {}           # (kind, id) -> Fraction
    tie_breaks = {}       # (kind, id) -> smallest contributing entry hash
    credits = {}          # lineage -> micro-credits (mode A, closed loop)
    lapsed = {}           # epoch -> Fraction of P_e that produced no claim
    for index in eligible:
        lapsed[index] = P.pie(index, params)

    for entry in included:
        entry_hash = entry["entry_hash"]
        weight = weights[entry_hash]
        if entry["mode"] == "A":
            if entry["lineage"] is not None:
                credits[entry["lineage"]] = (credits.get(entry["lineage"], 0)
                                             + compute_credit_micro(weight, params))
            continue
        denominator = denominators[entry["epoch"]]
        if denominator == 0 or weight == 0:
            continue
        share = P.pie(entry["epoch"], params) * Fraction(weight, denominator)
        hold = holds[entry_hash]
        if hold is None:
            holder = ("lineage", entry["lineage"])
        else:
            holder = ("escrow", entry_hash)
        claims[holder] = claims.get(holder, Fraction(0, 1)) + share
        lapsed[entry["epoch"]] = lapsed[entry["epoch"]] - share
        previous = tie_breaks.get(holder)
        if previous is None or entry_hash < previous:
            tie_breaks[holder] = entry_hash

    total_claim = Fraction(0, 1)
    for holder in sorted(claims):
        total_claim += claims[holder]

    # The declared inflow, net of the capped audit slice (socaity-zjr).
    amount_minor = declared["amount_minor"]
    cap = P.rational(params["audit_slice_cap"], "audit_slice_cap")
    audit_exact = Fraction(amount_minor, 1) * cap
    audit_reserve = audit_exact.numerator // audit_exact.denominator
    distributable = amount_minor - audit_reserve

    quantum = params["quantum_minor"]
    allocations, undistributed = _allocate(claims, total_claim, distributable,
                                           quantum, tie_breaks)

    rows = []
    for holder in sorted(claims):
        kind, ident = holder
        share = (Fraction(0, 1) if total_claim == 0
                 else _div(claims[holder], total_claim))
        row = {
            "kind": kind,
            "id": ident,
            "claim_R": P.to_rational(claims[holder]),
            "share": P.to_rational(share),
            "amount_minor": allocations[holder],
            "tie_break": tie_breaks[holder],
        }
        if kind == "escrow":
            row["hold"] = holds[ident]
        rows.append(row)

    table = {
        "structure_version": STRUCTURE_VERSION,
        "rule_version": request["rule_version"],
        "distribution_id": declared["distribution_id"],
        "currency": declared["currency"],
        "amount_minor": amount_minor,
        "audit_reserve_minor": audit_reserve,
        "undistributed_minor": undistributed,
        "checkpoint_hash": export["checkpoint_hash"],
        "cutoff_checkpoint_hash": declared["cutoff_checkpoint_hash"],
        "epochs": [
            {
                "epoch": index,
                "pie": P.to_rational(P.pie(index, params)),
                "denominator_micro_vu": denominators[index],
                "lapsed_pie": P.to_rational(lapsed[index]),
            }
            for index in eligible
        ],
        "recipients": rows,
        "compute_credits": [
            {"lineage": lineage, "micro_credits": credits[lineage]}
            for lineage in sorted(credits)
        ],
        "notice": P.DISCLOSURE,
    }
    _assert_conservation(table)
    return table


def _allocate(claims, total_claim, distributable, quantum, tie_breaks):
    """Floor to the quantum, then largest remainder, ties by entry hash.

    The residual is allocated entirely to claim holders (legal-counsel (c):
    never to the platform or the founder).  If there is no claim at all, the
    whole distributable amount is reported as undistributed rather than
    silently absorbed.
    """
    holders = sorted(claims)
    allocations = {}
    if total_claim == 0 or distributable == 0 or not holders:
        for holder in holders:
            allocations[holder] = 0
        return allocations, distributable

    units = distributable // quantum
    leftover = distributable - units * quantum      # sub-quantum remainder

    remainders = []
    assigned = 0
    for holder in holders:
        exact = _div(Fraction(units, 1) * claims[holder], total_claim)
        whole = exact.numerator // exact.denominator
        allocations[holder] = whole
        assigned += whole
        remainders.append((exact - Fraction(whole, 1), tie_breaks[holder], holder))

    # Largest remainder first; ties by ascending entry hash.  The hash is
    # unpredictable at contribution time and fork-stable, which is why
    # socaity-x8o chose it over ingestion id or chain position.
    remainders.sort(key=lambda item: (-item[0], item[1]))
    for _remainder, _hash, holder in remainders[:units - assigned]:
        allocations[holder] += 1

    for holder in holders:
        allocations[holder] = allocations[holder] * quantum
    return allocations, leftover


def _assert_conservation(table):
    """Exact conservation, checked on every call: the table sums to the
    declared amount, always, on every machine."""
    paid = 0
    for row in table["recipients"]:
        paid += row["amount_minor"]
    total = paid + table["audit_reserve_minor"] + table["undistributed_minor"]
    if total != table["amount_minor"]:
        raise RuleError("conservation violated: %d != %d"
                        % (total, table["amount_minor"]))
    shares = Fraction(0, 1)
    for row in table["recipients"]:
        shares += Fraction(row["share"]["num"], row["share"]["den"])
    if table["recipients"] and shares != Fraction(1, 1):
        raise RuleError("shares sum to %s, not 1" % shares)


# --- canonical output ------------------------------------------------------

def canonical_bytes(table):
    """RFC 8785 canonical serialisation of a payout table."""
    return canonicalize(table)


def table_hash(table):
    """The payout-table hash that goes on the ledger as
    ``distribution.table_published.table_hash`` (socaity-x8o §6)."""
    return hashlib.sha256(canonical_bytes(table)).hexdigest()
