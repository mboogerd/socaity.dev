"""RFC 8785 (JCS) canonical JSON, restricted to the ledger's value subset.

The ledger admits only: objects, arrays, strings, integers, booleans and null.
Floats are rejected at parse time and at serialisation time (socaity-zyt:
"exact rationals, no floats"; rationals are objects {num, den}).
"""

import json

__all__ = ["CanonicalError", "canonicalize", "loads"]

#: RFC 8785 3.2.2.3 serialises numbers per ECMA-262 7.1.12.1, i.e. as IEEE-754
#: doubles: a conformant implementation emits 2**53+1 as "9007199254740992" and
#: 10**21 as "1e+21".  This module emits the exact decimal expansion instead,
#: which agrees with ECMAScript for every integer in the safe range and
#: diverges silently outside it -- a divergence that would give a forker's
#: JCS implementation a different event_id and a signature that fails to
#: verify.  The RFC's own guidance is that true integers SHOULD stay within
#: +/-(2**53-1); since the ledger admits no floats at all, that bound is
#: enforced structurally here rather than left to review.
_MAX_SAFE_INT = 2 ** 53 - 1


class CanonicalError(ValueError):
    pass


def _string(s):
    """JCS string serialisation.  json.dumps produces exactly the JSON.stringify
    escaping RFC 8785 3.2.2.2 requires (lowercase \\uhhhh for C0 controls, the
    \\b \\t \\n \\f \\r shortcuts, everything else literal bar " and \\)."""
    try:
        s.encode("utf-8")
    except UnicodeEncodeError:
        # RFC 8785 3.2.2.2: lone surrogates MUST terminate with an error.
        raise CanonicalError("invalid Unicode (lone surrogate) in string")
    return json.dumps(s, ensure_ascii=False)


def _key(k):
    # JCS sorts member names by their UTF-16 code units.
    if not isinstance(k, str):
        raise CanonicalError("non-string object key")
    try:
        return k.encode("utf-16-be")
    except UnicodeEncodeError:
        raise CanonicalError("invalid Unicode (lone surrogate) in object key")


def _ser(v, out):
    if v is None:
        out.append("null")
    elif v is True:
        out.append("true")
    elif v is False:
        out.append("false")
    elif isinstance(v, float):
        raise CanonicalError("float values are not permitted on the ledger")
    elif isinstance(v, int):
        if not -_MAX_SAFE_INT <= v <= _MAX_SAFE_INT:
            raise CanonicalError(
                "integer %d is outside the RFC 8785 / ECMA-262 exactly "
                "representable range +/-(2**53-1)" % v)
        out.append(str(v))
    elif isinstance(v, str):
        out.append(_string(v))
    elif isinstance(v, (list, tuple)):
        out.append("[")
        for i, x in enumerate(v):
            if i:
                out.append(",")
            _ser(x, out)
        out.append("]")
    elif isinstance(v, dict):
        out.append("{")
        for i, k in enumerate(sorted(v, key=_key)):
            if i:
                out.append(",")
            out.append(_string(k))
            out.append(":")
            _ser(v[k], out)
        out.append("}")
    else:
        raise CanonicalError("unserialisable type: %s" % type(v).__name__)


def canonicalize(obj) -> bytes:
    """Return the RFC 8785 canonical UTF-8 serialisation of *obj*."""
    out = []
    _ser(obj, out)
    return "".join(out).encode("utf-8")


def _no_float(_s):
    raise CanonicalError("float literal in ledger JSON")


def loads(text):
    """json.loads with every float path (incl. NaN/Infinity) rejected."""
    return json.loads(text, parse_float=_no_float, parse_constant=_no_float)
