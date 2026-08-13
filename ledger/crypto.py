"""Ed25519 + multibase z6Mk key encoding, Python standard library only.

socaity-7mk fixes actor_key = multibase z6Mk Ed25519 and requires every event
to carry a signature over the canonical serialisation.  The stdlib ships no
Ed25519 primitive, so this module contains the RFC 8032 reference arithmetic
(extended homogeneous coordinates) directly -- no third-party dependency.

Verification is pluggable: `VERIFIERS` maps a `sig_alg` string to a callable
(public_key_bytes, message_bytes, signature_bytes) -> bool.  The documented
default is `"ed25519"` bound to the pure-Python implementation below.  A
deployment that wants a native/faster verifier registers it under the same key:

    from ledger import crypto
    crypto.VERIFIERS["ed25519"] = my_libsodium_verify

Any sig_alg absent from VERIFIERS is rejected at append time.
"""

import hashlib

__all__ = [
    "VERIFIERS", "verify", "sign", "public_from_secret",
    "encode_key", "decode_key", "SIG_ALG",
]

SIG_ALG = "ed25519"

# --- RFC 8032 Ed25519 ------------------------------------------------------

_p = 2 ** 255 - 19
_q = 2 ** 252 + 27742317777372353535851937790883648493


def _inv(x):
    return pow(x, _p - 2, _p)


_d = -121665 * _inv(121666) % _p
_sqrt_m1 = pow(2, (_p - 1) // 4, _p)


def _sha512_modq(s):
    return int.from_bytes(hashlib.sha512(s).digest(), "little") % _q


def _add(P, Q):
    A = (P[1] - P[0]) * (Q[1] - Q[0]) % _p
    B = (P[1] + P[0]) * (Q[1] + Q[0]) % _p
    C = 2 * P[3] * Q[3] * _d % _p
    D = 2 * P[2] * Q[2] % _p
    E, F, G, H = B - A, D - C, D + C, B + A
    return (E * F % _p, G * H % _p, F * G % _p, E * H % _p)


def _mul(s, P):
    R = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            R = _add(R, P)
        P = _add(P, P)
        s >>= 1
    return R


def _equal(P, Q):
    return ((P[0] * Q[2] - Q[0] * P[2]) % _p == 0
            and (P[1] * Q[2] - Q[1] * P[2]) % _p == 0)


def _recover_x(y, sign):
    if y >= _p:
        return None
    x2 = (y * y - 1) * _inv(_d * y * y + 1) % _p
    if x2 == 0:
        return None if sign else 0
    x = pow(x2, (_p + 3) // 8, _p)
    if (x * x - x2) % _p != 0:
        x = x * _sqrt_m1 % _p
    if (x * x - x2) % _p != 0:
        return None
    if (x & 1) != sign:
        x = _p - x
    return x


_gy = 4 * _inv(5) % _p
_gx = _recover_x(_gy, 0)
_G = (_gx, _gy, 1, _gx * _gy % _p)


def _compress(P):
    zi = _inv(P[2])
    x, y = P[0] * zi % _p, P[1] * zi % _p
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def _decompress(s):
    if len(s) != 32:
        return None
    y = int.from_bytes(s, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    x = _recover_x(y, sign)
    return None if x is None else (x, y, 1, x * y % _p)


def _expand(secret):
    h = hashlib.sha512(secret).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a, h[32:]


def public_from_secret(secret: bytes) -> bytes:
    a, _ = _expand(secret)
    return _compress(_mul(a, _G))


def sign(secret: bytes, msg: bytes) -> bytes:
    a, prefix = _expand(secret)
    A = _compress(_mul(a, _G))
    r = _sha512_modq(prefix + msg)
    Rs = _compress(_mul(r, _G))
    h = _sha512_modq(Rs + A + msg)
    return Rs + int.to_bytes((r + h * a) % _q, 32, "little")


def ed25519_verify(public: bytes, msg: bytes, signature: bytes) -> bool:
    if len(signature) != 64 or len(public) != 32:
        return False
    A = _decompress(public)
    R = _decompress(signature[:32])
    if A is None or R is None:
        return False
    s = int.from_bytes(signature[32:], "little")
    if s >= _q:
        return False
    h = _sha512_modq(signature[:32] + public + msg)
    return _equal(_mul(s, _G), _add(R, _mul(h, A)))


VERIFIERS = {SIG_ALG: ed25519_verify}


def verify(sig_alg: str, public: bytes, msg: bytes, signature: bytes) -> bool:
    fn = VERIFIERS.get(sig_alg)
    if fn is None:
        return False
    return fn(public, msg, signature)


# --- multibase base58btc / did:key z6Mk -----------------------------------

_B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_ED_MULTICODEC = b"\xed\x01"


def _b58encode(b: bytes) -> str:
    n = int.from_bytes(b, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = _B58[r] + out
    return "1" * (len(b) - len(b.lstrip(b"\x00"))) + out


def _b58decode(s: str) -> bytes:
    n = 0
    for c in s:
        i = _B58.find(c)
        if i < 0:
            raise ValueError("bad base58 character")
        n = n * 58 + i
    pad = len(s) - len(s.lstrip("1"))
    body = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return b"\x00" * pad + body


def encode_key(public: bytes) -> str:
    """32-byte Ed25519 public key -> multibase z6Mk... string."""
    if len(public) != 32:
        raise ValueError("Ed25519 public key must be 32 bytes")
    return "z" + _b58encode(_ED_MULTICODEC + public)


def decode_key(key: str) -> bytes:
    """z6Mk... -> 32-byte Ed25519 public key.  Raises ValueError if malformed."""
    if not isinstance(key, str) or not key.startswith("z6Mk"):
        raise ValueError("actor key must be multibase z6Mk Ed25519")
    raw = _b58decode(key[1:])
    if len(raw) != 34 or raw[:2] != _ED_MULTICODEC:
        raise ValueError("actor key is not an Ed25519 multicodec key")
    return raw[2:]


def is_key(value) -> bool:
    try:
        decode_key(value)
        return True
    except Exception:
        return False
