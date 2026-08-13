"""Rule parameters (V) and the pie schedule -- the *values* the structure eats.

socaity-x8o §6 splits the rule into STRUCTURE (this repository's code: epoch
mechanics, the formula, the mode-blind denominator, the lapse rule, the
arithmetic) and PARAMETERS (the values in this module).  Structure is final
for every epoch opened under a published rule version; parameters are
amendable for not-yet-opened epochs only, via the meta-rule
(:mod:`rule.metarule`).

Every value in :data:`PLACEHOLDER_PARAMS` is a PLACEHOLDER.  Final values are
delegated to socaity-9cb (L, the P_e curve) and socaity-19p (V rates, founder
rate, absolute rate), collected by socaity-wna.  Per the facilitator's
sequencing note those issues gate PUBLICATION and genesis, not development --
so the placeholders exist to make the rule runnable and testable, and three
independent gates make them impossible to publish by accident:

  1. ``status`` carries the sentinel :data:`PLACEHOLDER_STATUS`, which is not
     a value any final parameter set can hold;
  2. ``placeholders`` lists, by name, every value still awaiting an issue, and
     :func:`placeholder_free` refuses anything with a non-empty list;
  3. :func:`rule.publish.publish` and the meta-rule validity predicate both
     call :func:`assert_publishable`, and ``ledger.validator`` refuses
     ``epoch.opened(e>=1)`` for a params set that fails it (socaity-x8o §7:
     "EpochOpened's validity predicate enforces this mechanically").

Denomination note (socaity-x8o §2, legal-counsel amendments 1-3): P_e is an
EPOCH WEIGHT.  It is never "claim units" or "credits", it confers no
redemption value, and the whole schedule is invariant under multiplication of
every P_e by any positive constant -- which is the formal statement that these
are relative weights and not amounts.  See :data:`DISCLOSURE`.
"""

from fractions import Fraction

__all__ = ["PLACEHOLDER_STATUS", "FINAL_STATUS", "PLACEHOLDER_PARAMS",
           "DISCLOSURE", "MICRO", "ParamsError", "placeholder_free",
           "assert_publishable", "validate_params", "pie", "rate_of",
           "tier_floor_micro", "rational", "to_rational"]

#: Weights are declared in micro-units of their native unit (integer
#: micro-hours, micro-tokens): the declaration granularity of socaity-x8o §5.
MICRO = 10 ** 6

PLACEHOLDER_STATUS = "PLACEHOLDER-DEV-ONLY-NOT-FOR-PUBLICATION"
FINAL_STATUS = "final"

#: Carried inside every published artifact and every payout table
#: (legal-counsel amendment 2, Round 2).
DISCLOSURE = {
    "unit": "epoch weight",
    "confers_no_redemption_value": True,
    "realized_value_source": "discretionary declarations only, in proportion "
                             "to R_i over the sum of R_j",
    "scale_invariance": "multiplying every P_e by any positive constant leaves "
                        "every share unchanged",
}

#: Admissible pie shapes.  The SET of shapes is structure; the numbers inside
#: a shape are parameters.  Every shape must be a pure, non-increasing
#: function of the epoch index (socaity-x8o §2: no stacked premium multiplier,
#: ever -- the growing denominator is the earliness premium).
PIE_SHAPES = ("constant", "geometric_decay", "table")


class ParamsError(ValueError):
    """A parameter set is malformed, or is a placeholder set being published."""


# --- rational helpers ------------------------------------------------------

def rational(value, where="value"):
    """Read a ledger rational ``{"num": int, "den": int}`` as a Fraction."""
    if not isinstance(value, dict) or set(value) != {"num", "den"}:
        raise ParamsError("%s must be {num, den}" % where)
    num, den = value["num"], value["den"]
    for name, x in (("num", num), ("den", den)):
        if isinstance(x, bool) or not isinstance(x, int):
            raise ParamsError("%s.%s must be an integer (no floats)" % (where, name))
    if den <= 0:
        raise ParamsError("%s.den must be positive" % where)
    return Fraction(num, den)


def to_rational(frac):
    """Serialise a Fraction as the ledger's canonical rational object."""
    return {"num": frac.numerator, "den": frac.denominator}


# --- the placeholder parameter set ----------------------------------------

PLACEHOLDER_PARAMS = {
    "status": PLACEHOLDER_STATUS,
    "gated_by": ["socaity-wna", "socaity-9cb", "socaity-19p"],
    "placeholders": ["L_days", "pie", "rates", "tier_floor_micro",
                     "absolute_rate", "audit_slice_cap"],
    "effective_from_epoch": 1,

    # socaity-9cb: epoch length and the P_e curve.
    "L_days": 91,
    "pie": {"shape": "constant", "value": {"num": 1, "den": 1}},

    # socaity-19p: V.  vu per whole native unit; 1 vu = 1 standard
    # contributor-hour, so the "hours" rates read directly as rate multiples.
    # The founder rate is this same table applied to founder hours -- there is
    # deliberately no founder key here, because there is no founder column.
    "rates": {
        "code:hours": {"num": 1, "den": 1},
        "review:hours": {"num": 1, "den": 1},
        "docs:hours": {"num": 1, "den": 1},
        "ops:hours": {"num": 1, "den": 1},
        "design:hours": {"num": 1, "den": 1},
        "governance:hours": {"num": 1, "den": 1},
    },
    # socaity-ipg / socaity-19p: the floor rule, per ticket tier, in
    # micro-hours (500000 = the 0.5 h floor ipg names for a T1 acceptance).
    "tier_floor_micro": {"T1": 500000, "T2": 500000, "T3": 500000},

    # socaity-19p: mode-A compute credit, in micro-credits per vu.  Redeemable
    # solely against the platform's own compute (legal tripwire, Round 2).
    "absolute_rate": {"num": 1, "den": 1},

    # socaity-zjr: the capped audit slice, withheld from the declared inflow
    # before the contributor split.
    "audit_slice_cap": {"num": 1, "den": 20},

    # Structure-side constants that still carry a number.
    "quantum_minor": 1,
    "meta_min_notice_epochs": 1,
}


def placeholder_free(params):
    """True iff *params* carries no placeholder marker of any kind."""
    return (params.get("status") == FINAL_STATUS
            and not params.get("placeholders")
            and PLACEHOLDER_STATUS not in repr(params))


def assert_publishable(params):
    """Raise unless *params* may be published / may open an epoch."""
    validate_params(params)
    if not placeholder_free(params):
        raise ParamsError(
            "refusing to publish placeholder parameters (status=%r, "
            "placeholders=%s, gated by %s): socaity-wna fixes the values, and "
            "socaity-x8o §7 makes a placeholder-free V a precondition of "
            "epoch.opened(1)"
            % (params.get("status"), params.get("placeholders"),
               params.get("gated_by")))


# --- validation ------------------------------------------------------------

_REQUIRED = ("status", "placeholders", "effective_from_epoch", "L_days", "pie",
             "rates", "tier_floor_micro", "absolute_rate", "audit_slice_cap",
             "quantum_minor", "meta_min_notice_epochs")
_OPTIONAL = ("gated_by",)


def validate_params(params):
    """Structural validity of a parameter set (placeholder or final).

    Closed key set: an unknown key is a structure change wearing a parameter's
    clothes, so it is rejected here rather than ignored.
    """
    if not isinstance(params, dict):
        raise ParamsError("params must be an object")
    unknown = set(params) - set(_REQUIRED) - set(_OPTIONAL)
    if unknown:
        raise ParamsError("unknown parameter keys: %s" % sorted(unknown))
    missing = set(_REQUIRED) - set(params)
    if missing:
        raise ParamsError("missing parameters: %s" % sorted(missing))

    for name in ("L_days", "quantum_minor"):
        v = params[name]
        if isinstance(v, bool) or not isinstance(v, int) or v < 1:
            raise ParamsError("%s must be a positive integer" % name)
    for name in ("effective_from_epoch", "meta_min_notice_epochs"):
        v = params[name]
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise ParamsError("%s must be a non-negative integer" % name)

    _validate_pie(params["pie"])

    if not isinstance(params["rates"], dict) or not params["rates"]:
        raise ParamsError("rates must be a non-empty object")
    for key, value in params["rates"].items():
        if not isinstance(key, str) or key.count(":") != 1:
            raise ParamsError("rate key %r must be 'category:unit'" % (key,))
        if rational(value, "rates[%s]" % key) < 0:
            raise ParamsError("rates[%s] must be non-negative" % key)

    if not isinstance(params["tier_floor_micro"], dict):
        raise ParamsError("tier_floor_micro must be an object")
    for key, value in params["tier_floor_micro"].items():
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ParamsError("tier_floor_micro[%s] must be a non-negative "
                              "integer of micro-units" % key)

    if rational(params["absolute_rate"], "absolute_rate") < 0:
        raise ParamsError("absolute_rate must be non-negative")

    cap = rational(params["audit_slice_cap"], "audit_slice_cap")
    if cap < 0 or cap > 1:
        raise ParamsError("audit_slice_cap must lie in [0, 1]")

    if params["status"] not in (PLACEHOLDER_STATUS, FINAL_STATUS):
        raise ParamsError("status must be %r or %r"
                          % (FINAL_STATUS, PLACEHOLDER_STATUS))
    if not isinstance(params["placeholders"], list):
        raise ParamsError("placeholders must be a list of parameter names")
    if params["status"] == PLACEHOLDER_STATUS and not params["placeholders"]:
        raise ParamsError("placeholder status with an empty placeholder list")
    return True


def _validate_pie(spec):
    if not isinstance(spec, dict) or "shape" not in spec:
        raise ParamsError("pie must be an object with a shape")
    shape = spec["shape"]
    if shape not in PIE_SHAPES:
        raise ParamsError("pie shape %r is not one of %s" % (shape, list(PIE_SHAPES)))
    if shape == "constant":
        if set(spec) != {"shape", "value"}:
            raise ParamsError("constant pie takes exactly {shape, value}")
        if rational(spec["value"], "pie.value") <= 0:
            raise ParamsError("pie.value must be positive")
    elif shape == "geometric_decay":
        if set(spec) != {"shape", "p0", "ratio"}:
            raise ParamsError("geometric_decay pie takes exactly {shape, p0, ratio}")
        if rational(spec["p0"], "pie.p0") <= 0:
            raise ParamsError("pie.p0 must be positive")
        ratio = rational(spec["ratio"], "pie.ratio")
        if ratio <= 0 or ratio > 1:
            raise ParamsError("pie.ratio must lie in (0, 1] -- P_e is "
                              "non-increasing in e by structure")
    else:                                              # table
        if set(spec) != {"shape", "values", "tail"}:
            raise ParamsError("table pie takes exactly {shape, values, tail}")
        values = spec["values"]
        if not isinstance(values, list) or not values:
            raise ParamsError("pie.values must be a non-empty list")
        previous = None
        for i, value in enumerate(values):
            current = rational(value, "pie.values[%d]" % i)
            if current <= 0:
                raise ParamsError("pie.values[%d] must be positive" % i)
            if previous is not None and current > previous:
                raise ParamsError("pie.values must be non-increasing "
                                  "(index %d rises)" % i)
            previous = current
        tail = rational(spec["tail"], "pie.tail")
        if tail <= 0 or tail > previous:
            raise ParamsError("pie.tail must be positive and <= the last value")
    return True


# --- the pie schedule ------------------------------------------------------

def pie(epoch, params):
    """P_e: the epoch weight of epoch *e*.  Pure, non-increasing in e.

    Scale invariance (socaity-x8o §2, MD Round 2): replacing every P_e by
    c*P_e for any positive rational c leaves every payout identical, because
    the distribution is proportional to R_i normalised by the sum of R_j.
    That is exactly why P_e is a weight and not an amount.
    """
    if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
        raise ParamsError("epoch index must be a non-negative integer")
    spec = params["pie"]
    shape = spec["shape"]
    if shape == "constant":
        return rational(spec["value"], "pie.value")
    if shape == "geometric_decay":
        p0 = rational(spec["p0"], "pie.p0")
        ratio = rational(spec["ratio"], "pie.ratio")
        return p0 * (ratio ** epoch)
    values = spec["values"]
    if epoch < len(values):
        return rational(values[epoch], "pie.values[%d]" % epoch)
    return rational(spec["tail"], "pie.tail")


def rate_of(category, native_unit, params):
    """V: the vu rate of one whole native unit of (category, unit)."""
    key = "%s:%s" % (category, native_unit)
    if key not in params["rates"]:
        raise ParamsError("V has no rate for %r -- an observation cannot be "
                          "valued outside the published conversion schedule" % key)
    return rational(params["rates"][key], "rates[%s]" % key)


def tier_floor_micro(tier, params):
    """The floor rule: a tiered acceptance is never valued below its floor."""
    if tier is None:
        return 0
    return params["tier_floor_micro"].get(tier, 0)
