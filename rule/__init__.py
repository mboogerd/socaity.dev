"""socaity distribution rule v1 -- the reference implementation.

Adopted architecture: council/socaity-x8o.md (the rule), council/socaity-1ux.md
(the Standing Commitment), council/socaity-zyt.md (the event schema this reads),
council/socaity-zjr.md (the validation lifecycle).

  rule.distribute.distribute   the pure function: request -> payout table
  rule.params                  V and the pie schedule -- PLACEHOLDER values,
                               gated by socaity-wna; unpublishable by design
  rule.metarule                the amendment validity predicate
  rule.publish                 rule_version = hash(source + canonical params)
  rule.replay                  ledger -> rule input (epoch clamp, zjr snapshot)
  rule.lint_no_float           the AST gate: no floats on the mechanism path
  rule.forkability             replay the public artifacts, byte-for-byte
  rule/vectors/                the golden vectors, committed as data

Python standard library only, on any CPython >= 3.10.
"""

from .distribute import RuleError, STRUCTURE_VERSION, canonical_bytes, distribute, table_hash
from .metarule import MetaRuleError, is_valid_amendment, violations
from .params import PLACEHOLDER_PARAMS, ParamsError, assert_publishable, placeholder_free

__all__ = ["distribute", "table_hash", "canonical_bytes", "RuleError",
           "STRUCTURE_VERSION", "PLACEHOLDER_PARAMS", "ParamsError",
           "placeholder_free", "assert_publishable", "violations",
           "is_valid_amendment", "MetaRuleError"]
