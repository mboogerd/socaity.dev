"""Valuation: native units -> vu, and mode-A vu -> compute credits.

socaity-124 implemented the observation side of the ledger and left exactly
this boundary open ("zero valuation event types exist; the vu/cu valuation
functions are yours").  Valuations are never events: they are recomputed by
replay from immutable observations plus a parameter set (socaity-zyt).

Arithmetic discipline (socaity-x8o §5, platform-engineer §2):

* quantities are declared as integers in micro-units of their native unit;
* weights are quantised to integer MICRO-VU here -- this is a declaration
  granularity, applied once, monotone, and identical on every machine.  It is
  not the monetary rounding: the single monetary rounding happens once, at
  materialisation, in :mod:`rule.distribute`;
* everything downstream of this module is an exact rational.
"""

from fractions import Fraction

from .params import rate_of, rational, tier_floor_micro

__all__ = ["ValuationError", "weight_micro_vu", "compute_credit_micro",
           "effective_quantity_micro"]


class ValuationError(ValueError):
    pass


def effective_quantity_micro(entry, params):
    """Declared quantity in micro native units, after the tier floor rule."""
    quantity = entry["quantity_micro"]
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
        raise ValuationError("quantity_micro must be a non-negative integer")
    floor_micro = tier_floor_micro(entry.get("tier"), params)
    return quantity if quantity > floor_micro else floor_micro


def weight_micro_vu(entry, params, discount=None):
    """w for one observation, as an integer count of micro-vu.

    ``discount`` is the [0, 1] factor a decided challenge (socaity-zjr) put on
    the entry; ``None`` means undiscounted.  The value is floored, so a
    discount can never increase a weight and the quantisation error is always
    borne by the entry, never by the pool.
    """
    quantity = effective_quantity_micro(entry, params)
    rate = rate_of(entry["category"], entry["native_unit"], params)
    exact = Fraction(quantity, 1) * rate
    if discount is not None:
        if discount < 0 or discount > 1:
            raise ValuationError("discount factor must lie in [0, 1]")
        exact = exact * (Fraction(1, 1) - discount)
    return exact.numerator // exact.denominator


def compute_credit_micro(weight_micro, params):
    """Mode A: closed-loop compute credit, in micro-credits.

    Redeemable solely against the platform's own compute (legal-counsel's
    standing tripwire, Round 2).  There is deliberately no transfer function
    anywhere in this package -- non-transferability is enforced by the absence
    of the operation, not by prose (legal-counsel (b)).
    """
    rate = rational(params["absolute_rate"], "absolute_rate")
    exact = Fraction(weight_micro, 1) * rate
    return exact.numerator // exact.denominator
