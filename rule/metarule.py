"""The meta-rule: the validity predicate that gates amendments.

socaity-1ux / socaity-x8o §6: the rule ships at M0 as versioned executable
code, authoritative over prose.  The formula STRUCTURE is final for every
epoch opened under it; PARAMETER VALUES are amendable, but only for epochs
that have never been opened, and only through an amendment the meta-rule's own
validity predicate accepts.  An amendment is a ``rule.version_published``
event; this module decides whether the ledger may accept it.

Every check is named, and :func:`violations` returns the names, so a rejected
amendment tells the community *which* clause it broke rather than "invalid".

The predicate is pure: it reads two artifacts and a small state summary
(highest epoch ever opened, currently open epoch) that a replayer derives from
the chain.  It performs no I/O.
"""

from fractions import Fraction

from . import params as P

__all__ = ["MetaRuleError", "CHECKS", "violations", "is_valid_amendment",
           "assert_valid_amendment", "requires_placeholder_free"]

#: Every clause of the meta-rule, in the order it is evaluated.  This tuple is
#: itself part of the published meta-rule artifact: adding or removing a clause
#: is a meta-rule amendment, not a rule amendment.
CHECKS = (
    "artifact_wellformed",       # both artifacts have the published shape
    "structure_unchanged",       # identical structure hash and structure version
    "predecessor_named",         # the amendment chains to the version it replaces
    "params_wellformed",         # the proposed parameter set validates
    "prospective_only",          # effective_from_epoch is an epoch never opened
    "notice_respected",          # published at least meta_min_notice_epochs early
    "non_increasing_pie",        # P_e is non-increasing in e (structure invariant)
    "no_placeholders",           # no placeholder value may be published
    "no_transfer_operation",     # the rule package exposes no transfer surface
)

_ARTIFACT_KEYS = {"structure_version", "structure_hash", "sources", "params",
                  "params_hash", "rule_version", "prev_rule_version", "notice"}

#: How far ahead the pie schedule is checked for monotonicity.  The shapes in
#: :data:`rule.params.PIE_SHAPES` are all provably non-increasing by
#: construction; this finite check is a belt-and-braces guard that also covers
#: the table shape's tail.
_PIE_HORIZON = 64


class MetaRuleError(ValueError):
    def __init__(self, names):
        self.checks = list(names)
        super().__init__("amendment rejected by the meta-rule: %s"
                         % ", ".join(self.checks))


def requires_placeholder_free(params):
    """True iff *params* may be published / may open an epoch >= 1."""
    try:
        P.assert_publishable(params)
    except P.ParamsError:
        return False
    return True


def violations(current, proposed, state):
    """Return the names of the meta-rule clauses *proposed* breaks.

    *state* is ``{"highest_opened_epoch": int | None, "open_epoch": int | None}``
    as derived from the chain by replay.  An empty result means the amendment
    is valid.
    """
    broken = []

    def fail(name):
        if name not in broken:
            broken.append(name)

    for artifact in (current, proposed):
        if not isinstance(artifact, dict) or set(artifact) != _ARTIFACT_KEYS:
            fail("artifact_wellformed")
    if broken:
        return broken

    if (proposed["structure_hash"] != current["structure_hash"]
            or proposed["structure_version"] != current["structure_version"]
            or proposed["sources"] != current["sources"]):
        fail("structure_unchanged")

    if proposed["prev_rule_version"] != current["rule_version"]:
        fail("predecessor_named")

    params = proposed["params"]
    try:
        P.validate_params(params)
    except P.ParamsError:
        fail("params_wellformed")
        return broken

    highest = state.get("highest_opened_epoch")
    target = params["effective_from_epoch"]
    if highest is not None and target <= highest:
        fail("prospective_only")

    open_epoch = state.get("open_epoch")
    notice = current["params"]["meta_min_notice_epochs"]
    if open_epoch is not None and target < open_epoch + 1 + notice:
        fail("notice_respected")

    previous = None
    for epoch in range(_PIE_HORIZON):
        current_pie = P.pie(epoch, params)
        if current_pie <= Fraction(0, 1):
            fail("non_increasing_pie")
            break
        if previous is not None and current_pie > previous:
            fail("non_increasing_pie")
            break
        previous = current_pie

    if not requires_placeholder_free(params):
        fail("no_placeholders")

    if not _no_transfer_operation():
        fail("no_transfer_operation")

    return broken


def is_valid_amendment(current, proposed, state):
    return not violations(current, proposed, state)


def assert_valid_amendment(current, proposed, state):
    broken = violations(current, proposed, state)
    if broken:
        raise MetaRuleError(broken)
    return True


def _no_transfer_operation():
    """No transfer surface exists in the rule package.

    legal-counsel (b), Round 1: "non-transferability must be enforced in the
    rule itself -- no transfer operation exists in the code", not merely stated
    in prose.  This walks the public API of every rule module and fails on any
    name that would move a position between holders.  It is checked here, in
    the amendment gate, so the property cannot be lost by a future edit that
    keeps the parameters valid.
    """
    from . import distribute, valuation
    forbidden = ("transfer", "assign", "sell", "trade", "send", "reassign",
                 "delegate")
    for module in (P, valuation, distribute):
        for name in getattr(module, "__all__", ()):
            lowered = name.lower()
            for word in forbidden:
                if word in lowered:
                    return False
    return True
