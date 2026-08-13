"""Validator predicate coverage.  Run:  python3 -m unittest discover ledger"""

import datetime
import hashlib
import os
import tempfile
import unittest

from ledger import canonical, crypto
from ledger.catalog import GENESIS_PREV
from ledger.log import EventLog
from ledger.validator import Ledger, ValidationError, sign_event

DAY = 86400
NOW = int(datetime.datetime(2026, 8, 13, 12, 0, tzinfo=datetime.timezone.utc)
          .timestamp())

FOUNDER = b"\x11" * 32
CKPT = b"\x22" * 32
ALICE = b"\x33" * 32
BOB = b"\x44" * 32
CAROL = b"\x55" * 32

_PUB = {}


def key(secret):
    if secret not in _PUB:
        _PUB[secret] = crypto.encode_key(crypto.public_from_secret(secret))
    return _PUB[secret]


def H(tag):
    return hashlib.sha256(tag.encode()).hexdigest()


def week_of(ts):
    d = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).date()
    y, w, _ = d.isocalendar()
    return "%04d-W%02d" % (y, w)


THIS_WEEK = week_of(NOW)
OLD_WEEK = week_of(NOW - 70 * DAY)


def mk(ledger, secret, etype, payload, ts=NOW, v=1, sig_alg="ed25519", prev=None):
    ev = {"v": v, "type": etype, "prev": ledger.head if prev is None else prev,
          "actor": key(secret), "ts": ts, "payload": payload, "sig_alg": sig_alg}
    return sign_event(secret, ev)


def add(ledger, secret, etype, payload, receipt_ts=NOW, **kw):
    return ledger.append(mk(ledger, secret, etype, payload, **kw),
                         receipt_ts=receipt_ts)


def prologue(ledger=None, epoch0=()):
    """Genesis prologue through epoch.opened(1) -- the point at which the
    catalog opens and a first external entry becomes admissible."""
    led = ledger or Ledger()
    add(led, FOUNDER, "genesis", {"rule_version_hash": H("rv1"),
                                  "meta_rule_hash": H("mr"),
                                  "checkpoint_key": key(CKPT), "L": 1000})
    add(led, FOUNDER, "rule.version_published", {"rule_version": H("rv1"),
                                                 "source_hash": H("src"),
                                                 "params_hash": H("params")})
    add(led, FOUNDER, "rule.meta_published", {"meta_rule_hash": H("mr")})
    for etype, payload in epoch0:
        add(led, FOUNDER, etype, payload)
    add(led, FOUNDER, "epoch.opened", {"epoch": 0, "rule_version_hash": H("rv1")})
    add(led, FOUNDER, "epoch.closed", {"epoch": 0, "checkpoint_hash": H("cp0")})
    add(led, FOUNDER, "rule.attested", {"rule_version_hash": H("rv1"), "epoch": 1,
                                        "statement_hash": H("stmt")})
    add(led, FOUNDER, "epoch.opened", {"epoch": 1, "rule_version_hash": H("rv1")})
    return led


def roll_epoch(led, e):
    """Close the open epoch and open epoch *e*."""
    add(led, FOUNDER, "epoch.closed", {"epoch": e - 1, "checkpoint_hash": H("cp%d" % e)})
    add(led, FOUNDER, "rule.attested", {"rule_version_hash": H("rv1"), "epoch": e,
                                        "statement_hash": H("stmt%d" % e)})
    add(led, FOUNDER, "epoch.opened", {"epoch": e, "rule_version_hash": H("rv1")})


TRIVIAL = {"contributor": None, "category": "docs", "mode": "E",
           "evidence": [H("merge-sha")], "artifact_hash": H("artifact"),
           "week_ref": THIS_WEEK, "claim_binding": H("github:stranger")}


class Base(unittest.TestCase):
    def reject(self, predicate, fn, *a, **kw):
        with self.assertRaises(ValidationError) as cm:
            fn(*a, **kw)
        self.assertEqual(cm.exception.predicate, predicate, str(cm.exception))


# --------------------------------------------------------------------------
class TestCanonical(Base):
    def test_jcs_ordering_and_form(self):
        self.assertEqual(
            canonical.canonicalize({"b": 1, "a": [1, {"d": None, "c": True}]}),
            b'{"a":[1,{"c":true,"d":null}],"b":1}')

    def test_utf16_key_order(self):
        # JCS sorts by UTF-16 code units, so a non-BMP key (surrogate pair
        # 0xD83D...) sorts BEFORE U+FFFF -- the opposite of code-point order.
        out = canonical.canonicalize({"￿": 2, "\U0001f600": 1}).decode()
        self.assertTrue(out.index('"\U0001f600"') < out.index('"￿"'))

    def test_no_floats(self):
        self.assertRaises(canonical.CanonicalError, canonical.canonicalize, {"x": 1.5})
        self.assertRaises(canonical.CanonicalError, canonical.loads, '{"x":1.5}')
        self.assertRaises(canonical.CanonicalError, canonical.loads, '{"x":NaN}')

    def test_rfc8785_worked_example(self):
        # RFC 8785 3.2.3 worked example, float members omitted (the ledger
        # admits no floats).  Input and expected output taken from the RFC.
        src = {"string": "\u20ac$\u000F\u000aA'\u0042\u0022\u005c\u005c\u0022/",
               "literals": [None, True, False]}
        expected = ('{"literals":[null,true,false],"string":'
                    '"\u20ac$\\u000f\\nA\'B\\"\\\\\\\\\\"/"}')
        self.assertEqual(canonical.canonicalize(src).decode(), expected)

    def test_control_char_escaping(self):
        out = canonical.canonicalize("".join(chr(i) for i in range(0x20))).decode()
        # C0 controls as lowercase \uhhhh, with the five JSON shortcuts
        self.assertIn("\\u000f", out)
        for short in ("\\b", "\\t", "\\n", "\\f", "\\r"):
            self.assertIn(short, out)
        # everything outside the C0 range stays literal; solidus is not escaped
        self.assertEqual(canonical.canonicalize("/").decode(),
                         '"/"')

    def test_lone_surrogate_rejected(self):
        # RFC 8785 3.2.2.2: invalid Unicode MUST terminate with an error, and
        # it must be *our* error type -- an escaping UnicodeEncodeError would
        # crash the append path instead of rejecting the event.
        self.assertRaises(canonical.CanonicalError,
                          canonical.canonicalize, {"a": "\ud800"})
        self.assertRaises(canonical.CanonicalError,
                          canonical.canonicalize, {"\ud800": "a"})

    def test_integers_outside_es_safe_range_rejected(self):
        # inside the range this module agrees with ECMA-262 exactly
        self.assertEqual(canonical.canonicalize(2 ** 53 - 1), b"9007199254740991")
        self.assertEqual(canonical.canonicalize(-(2 ** 53 - 1)), b"-9007199254740991")
        # outside it a conformant JCS emits "9007199254740992" / "1e+21", so the
        # exact decimal expansion here would fork the event_id.  Reject instead.
        for bad in (2 ** 53, -(2 ** 53), 10 ** 21):
            self.assertRaises(canonical.CanonicalError, canonical.canonicalize, bad)


class TestCrypto(Base):
    def test_rfc8032_vector1(self):
        sk = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc4"
                           "4449c5697b326919703bac031cae7f60")
        self.assertEqual(crypto.public_from_secret(sk).hex(),
                         "d75a980182b10ab7d54bfed3c964073a"
                         "0ee172f3daa62325af021a68f707511a")

    def test_rfc8032_vectors(self):
        # RFC 8032 7.1 TEST 1/2/3: keygen, signature bytes and verification.
        for sk, pk, msg, sig in [
            ("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
             "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
             "",
             "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555f"
             "b8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"),
            ("4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
             "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c",
             "72",
             "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da08"
             "5ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00"),
            ("c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7",
             "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025",
             "af82",
             "6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac18"
             "ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a"),
        ]:
            sk, pk, msg, sig = (bytes.fromhex(x) for x in (sk, pk, msg, sig))
            self.assertEqual(crypto.public_from_secret(sk), pk)
            self.assertEqual(crypto.sign(sk, msg), sig)
            self.assertTrue(crypto.ed25519_verify(pk, msg, sig))
            # a flipped signature bit, a flipped message and a foreign key
            # must all fail, and a non-canonical scalar s >= L must too
            self.assertFalse(crypto.ed25519_verify(
                pk, msg, bytes([sig[0] ^ 1]) + sig[1:]))
            self.assertFalse(crypto.ed25519_verify(pk, msg + b"\x00", sig))
            self.assertFalse(crypto.ed25519_verify(pk, msg, sig[:32] + b"\xff" * 32))

    def test_sign_verify_roundtrip_and_tamper(self):
        pub = crypto.public_from_secret(ALICE)
        sig = crypto.sign(ALICE, b"payload")
        self.assertTrue(crypto.verify("ed25519", pub, b"payload", sig))
        self.assertFalse(crypto.verify("ed25519", pub, b"payload!", sig))
        self.assertFalse(crypto.verify("unknown-alg", pub, b"payload", sig))

    def test_multibase_z6mk(self):
        k = key(ALICE)
        self.assertTrue(k.startswith("z6Mk"))
        self.assertEqual(crypto.decode_key(k), crypto.public_from_secret(ALICE))
        self.assertRaises(ValueError, crypto.decode_key, "github:someone")


class TestEnvelope(Base):
    def setUp(self):
        self.led = prologue()

    def test_envelope_shape(self):
        ev = mk(self.led, ALICE, "rule.meta_published", {"meta_rule_hash": H("m")})
        ev["seq"] = 7                       # derived data gets no authoritative field
        self.reject("envelope", self.led.append, ev)

    def test_closed_catalog_type_and_version(self):
        self.reject("closed_catalog", add, self.led, ALICE, "vu.awarded", {})
        self.reject("closed_catalog", add, self.led, ALICE, "rule.meta_published",
                    {"meta_rule_hash": H("m")}, v=2)

    def test_closed_catalog_fields(self):
        self.reject("closed_catalog_fields", add, self.led, ALICE, "ticket.opened",
                    {"ticket_id": H("t"), "tier": "T1", "category": "code",
                     "spec_hash": H("s"), "budget_vu": 5})

    def test_no_floats_in_payload(self):
        ev = mk(self.led, ALICE, "epoch.closed", {"epoch": 1, "checkpoint_hash": H("c")})
        ev["payload"]["epoch"] = 1.0        # as it would arrive over the wire
        self.reject("no_floats", self.led.append, ev)
        # and integer-kinded fields reject non-integers even when signed
        self.reject("no_floats", add, self.led, ALICE, "genesis",
                    {"rule_version_hash": H("r"), "meta_rule_hash": H("m"),
                     "checkpoint_key": key(CKPT), "L": -1})

    def test_no_free_text(self):
        self.reject("no_free_text", add, self.led, ALICE, "ticket.opened",
                    {"ticket_id": "fix the login bug", "tier": "T1",
                     "category": "code", "spec_hash": H("s")})

    def test_closed_enum(self):
        self.reject("closed_enum", add, self.led, ALICE, "ticket.opened",
                    {"ticket_id": H("t"), "tier": "PLATINUM",
                     "category": "code", "spec_hash": H("s")})

    def test_hash_only_evidence(self):
        p = dict(TRIVIAL, evidence=["https://github.com/x/y/pull/1"])
        self.reject("hash_only_evidence", add, self.led, FOUNDER,
                    "contribution.trivial_accepted", p)
        p = dict(TRIVIAL, evidence=[])
        self.reject("hash_only_evidence", add, self.led, FOUNDER,
                    "contribution.trivial_accepted", p)

    def test_provenance_completeness(self):
        p = {"category": "code", "native_unit": "hours", "quantity": 3600000,
             "mode": "E", "evidence": [H("e")], "week_ref": THIS_WEEK}
        self.reject("provenance_completeness", add, self.led, ALICE,
                    "work.logged", p)          # artifact_hash missing

    def test_rational_bounds(self):
        for bad in ({"num": 3, "den": 2}, {"num": 1, "den": 0}):
            self.reject("rational_bounds", add, self.led, ALICE, "challenge.decided",
                        {"challenge_id": H("c"), "outcome": "upheld", "discount": bad})

    def test_hash_chain(self):
        ev = mk(self.led, ALICE, "rule.meta_published", {"meta_rule_hash": H("m")},
                prev=H("not the head"))
        ev = sign_event(ALICE, ev)
        self.reject("hash_chain", self.led.append, ev)

    def test_signature(self):
        ev = mk(self.led, ALICE, "rule.meta_published", {"meta_rule_hash": H("m")})
        ev["payload"]["meta_rule_hash"] = H("tampered")
        self.reject("signature", self.led.append, ev)
        ev2 = mk(self.led, ALICE, "rule.meta_published", {"meta_rule_hash": H("m")},
                 sig_alg="hmac-sha256")
        self.reject("signature", self.led.append, ev2)

    def test_timestamp_future_bound(self):
        self.reject("timestamp", add, self.led, ALICE, "rule.meta_published",
                    {"meta_rule_hash": H("m")}, ts=NOW + 3600)

    def test_event_id_is_hash_chain_link(self):
        eid = add(self.led, ALICE, "rule.meta_published", {"meta_rule_hash": H("m")})
        self.assertEqual(self.led.head, eid)
        self.assertRegex(eid, r"^[0-9a-f]{64}$")


class TestPrologue(Base):
    def test_first_event_must_be_genesis(self):
        led = Ledger()
        self.reject("genesis_prologue", add, led, FOUNDER, "rule.meta_published",
                    {"meta_rule_hash": H("m")})

    def test_genesis_prev_is_zeroes(self):
        led = Ledger()
        self.assertEqual(led.head, GENESIS_PREV)
        prologue(led)
        self.assertTrue(led.prologue_complete)

    def test_out_of_order_prologue(self):
        led = Ledger()
        add(led, FOUNDER, "genesis", {"rule_version_hash": H("rv1"),
                                      "meta_rule_hash": H("mr"),
                                      "checkpoint_key": key(CKPT), "L": 1000})
        self.reject("genesis_prologue", add, led, FOUNDER, "epoch.opened",
                    {"epoch": 0, "rule_version_hash": H("rv1")})

    def test_no_external_entry_before_prologue_completes(self):
        led = Ledger()
        add(led, FOUNDER, "genesis", {"rule_version_hash": H("rv1"),
                                      "meta_rule_hash": H("mr"),
                                      "checkpoint_key": key(CKPT), "L": 1000})
        add(led, FOUNDER, "rule.version_published", {"rule_version": H("rv1"),
                                                     "source_hash": H("src"),
                                                     "params_hash": H("params")})
        add(led, FOUNDER, "rule.meta_published", {"meta_rule_hash": H("mr")})
        # stage 3 admits founder epoch-0 itemisation only -- not a stranger's entry
        self.reject("genesis_prologue", add, led, ALICE,
                    "contribution.trivial_accepted", dict(TRIVIAL))

    def test_epoch0_itemisation_then_first_external_entry(self):
        item = {k: v for k, v in TRIVIAL.items() if k != "claim_binding"}
        item["contributor"] = key(ALICE)
        led = prologue(epoch0=[("contribution.trivial_accepted", item)])
        # the founder position is itemised as ordinary observations
        self.assertTrue(led.prologue_complete)
        add(led, FOUNDER, "contribution.trivial_accepted", dict(TRIVIAL))
        self.assertEqual(led.count, 9)

    def test_epoch_attestation_required(self):
        led = Ledger()
        add(led, FOUNDER, "genesis", {"rule_version_hash": H("rv1"),
                                      "meta_rule_hash": H("mr"),
                                      "checkpoint_key": key(CKPT), "L": 1000})
        add(led, FOUNDER, "rule.version_published", {"rule_version": H("rv1"),
                                                     "source_hash": H("src"),
                                                     "params_hash": H("params")})
        add(led, FOUNDER, "rule.meta_published", {"meta_rule_hash": H("mr")})
        add(led, FOUNDER, "epoch.opened", {"epoch": 0, "rule_version_hash": H("rv1")})
        add(led, FOUNDER, "epoch.closed", {"epoch": 0, "checkpoint_hash": H("c")})
        # prologue wants rule.attested here; skipping it is caught by sequencing
        self.reject("genesis_prologue", add, led, FOUNDER, "epoch.opened",
                    {"epoch": 1, "rule_version_hash": H("rv1")})

    def test_epoch_attestation_required_after_prologue(self):
        # past the prologue the sequencing predicate no longer masks it: an
        # epoch may not open without a rule.attested for that exact epoch.
        led = prologue()
        add(led, FOUNDER, "epoch.closed", {"epoch": 1, "checkpoint_hash": H("c1")})
        self.reject("epoch_attestation", add, led, FOUNDER, "epoch.opened",
                    {"epoch": 2, "rule_version_hash": H("rv1")})

    def test_epoch_sequence(self):
        led = prologue()
        # epoch 1 is open: it may not be opened again, nor may 2 open over it
        self.reject("epoch_sequence", add, led, FOUNDER, "epoch.opened",
                    {"epoch": 2, "rule_version_hash": H("rv1")})
        # and only the open epoch may be closed
        self.reject("epoch_sequence", add, led, FOUNDER, "epoch.closed",
                    {"epoch": 0, "checkpoint_hash": H("c")})

    def test_attestation_uniqueness(self):
        led = prologue()
        add(led, FOUNDER, "epoch.closed", {"epoch": 1, "checkpoint_hash": H("c1")})
        add(led, FOUNDER, "rule.attested", {"rule_version_hash": H("rv1"),
                                            "epoch": 2, "statement_hash": H("s2")})
        self.reject("attestation_uniqueness", add, led, FOUNDER, "rule.attested",
                    {"rule_version_hash": H("rv1"), "epoch": 2,
                     "statement_hash": H("s2-again")})


class TestObservations(Base):
    def setUp(self):
        self.led = prologue()
        self.ticket = add(self.led, FOUNDER, "ticket.opened",
                          {"ticket_id": H("t1"), "tier": "T1", "category": "code",
                           "spec_hash": H("spec1")})

    def accept(self, actor, contributor, **over):
        p = {"ticket_ref": self.ticket, "ticket_id": H("t1"),
             "contributor": contributor, "attested_micro_hours": 3600000,
             "mode": "E", "category": "code", "evidence": [H("merge")],
             "artifact_hash": H("art"), "week_ref": THIS_WEEK}
        p.update(over)
        return add(self.led, actor, "ticket.accepted", p)

    def test_self_acceptance_rejected(self):
        self.reject("self_acceptance", self.accept, ALICE, key(ALICE))

    def test_acceptance_by_maintainer_ok(self):
        eid = self.accept(FOUNDER, key(ALICE))
        self.assertEqual(self.led.attribution_of(eid), key(ALICE))

    def test_self_acceptance_across_rotation_rejected(self):
        add(self.led, ALICE, "key.rotated", {"new_key": key(BOB)})
        self.reject("self_acceptance", self.accept, BOB, key(ALICE))

    def test_duplicate_open_rejected_until_closed(self):
        self.reject("duplicate_open", add, self.led, FOUNDER, "ticket.opened",
                    {"ticket_id": H("t1"), "tier": "T3", "category": "code",
                     "spec_hash": H("other")})
        self.reject("duplicate_open", add, self.led, FOUNDER, "ticket.opened",
                    {"ticket_id": H("t9"), "tier": "T3", "category": "code",
                     "spec_hash": H("spec1")})
        add(self.led, FOUNDER, "ticket.closed",
            {"ticket_id": H("t1"), "reason": "withdrawn"})
        add(self.led, FOUNDER, "ticket.opened",
            {"ticket_id": H("t1"), "tier": "T3", "category": "code",
             "spec_hash": H("spec1")})

    def test_week_ref_staleness(self):
        self.reject("week_ref_staleness", add, self.led, ALICE, "work.logged",
                    {"category": "code", "native_unit": "hours", "quantity": 3600000,
                     "mode": "E", "evidence": [H("e")], "week_ref": OLD_WEEK,
                     "artifact_hash": H("a")})
        add(self.led, ALICE, "work.logged",
            {"category": "code", "native_unit": "hours", "quantity": 3600000,
             "mode": "E", "evidence": [H("e")], "week_ref": week_of(NOW - 7 * DAY),
             "artifact_hash": H("a")})

    def test_week_ref_not_yet_begun(self):
        self.reject("week_ref_staleness", add, self.led, ALICE, "work.logged",
                    {"category": "code", "native_unit": "hours", "quantity": 1,
                     "mode": "E", "evidence": [H("e")],
                     "week_ref": week_of(NOW + 14 * DAY), "artifact_hash": H("a")})

    def test_staleness_bound_moves_with_checkpoints(self):
        add(self.led, CKPT, "checkpoint.published",
            {"checkpoint_seq": 1, "head_event_id": self.led.head,
             "event_count": self.led.count, "prev_checkpoint_ref": GENESIS_PREV},
            ts=NOW)
        self.reject("week_ref_staleness", add, self.led, ALICE, "work.logged",
                    {"category": "code", "native_unit": "hours", "quantity": 1,
                     "mode": "E", "evidence": [H("e")], "week_ref": OLD_WEEK,
                     "artifact_hash": H("a")})

    def test_checkpoint_key_and_commitment(self):
        self.reject("checkpoint", add, self.led, ALICE, "checkpoint.published",
                    {"checkpoint_seq": 1, "head_event_id": self.led.head,
                     "event_count": self.led.count,
                     "prev_checkpoint_ref": GENESIS_PREV})
        self.reject("checkpoint", add, self.led, CKPT, "checkpoint.published",
                    {"checkpoint_seq": 1, "head_event_id": H("wrong"),
                     "event_count": self.led.count,
                     "prev_checkpoint_ref": GENESIS_PREV})

    def test_reference_integrity(self):
        self.reject("reference_integrity", add, self.led, FOUNDER, "challenge.filed",
                    {"challenge_id": H("c"), "target_event_id": H("nope"),
                     "grounds": "duplicate", "stake_ref": H("s")})

    def test_withdrawal_only_by_own_lineage(self):
        eid = self.accept(FOUNDER, key(ALICE))
        self.reject("reference_integrity", add, self.led, ALICE, "entry.withdrawn",
                    {"target_event_id": eid})
        add(self.led, FOUNDER, "entry.withdrawn", {"target_event_id": eid})


class TestEscrowAndClaim(Base):
    def setUp(self):
        self.led = prologue()
        self.escrow = add(self.led, FOUNDER, "contribution.trivial_accepted",
                          dict(TRIVIAL))

    def claim(self, secret, **over):
        p = {"escrow_ref": self.escrow, "claim_binding": H("github:stranger"),
             "attestation_hash": H("attestation")}
        p.update(over)
        return add(self.led, secret, "attribution.claimed", p)

    def test_null_contributor_requires_claim_binding(self):
        p = dict(TRIVIAL)
        del p["claim_binding"]
        self.reject("escrow_binding", add, self.led, FOUNDER,
                    "contribution.trivial_accepted", p)

    def test_named_contributor_may_not_carry_claim_binding(self):
        p = dict(TRIVIAL, contributor=key(ALICE))
        self.reject("escrow_binding", add, self.led, FOUNDER,
                    "contribution.trivial_accepted", p)

    def test_escrow_is_unattributed_until_claimed(self):
        self.assertIsNone(self.led.attribution_of(self.escrow))
        self.claim(ALICE)
        self.assertEqual(self.led.attribution_of(self.escrow), key(ALICE))

    def test_claim_binding_must_match(self):
        self.reject("claim_validity", self.claim, ALICE,
                    claim_binding=H("github:squatter"))

    def test_double_claim_rejected(self):
        self.claim(ALICE)
        self.reject("claim_validity", self.claim, BOB)

    def test_acceptor_cannot_claim_own_escrow(self):
        self.reject("claim_validity", self.claim, FOUNDER)

    def test_acceptor_cannot_launder_self_claim_through_rotation(self):
        # the check is lineage-keyed, so rotating to a fresh key before
        # claiming does not turn a self-claim into an external one.
        add(self.led, FOUNDER, "key.rotated", {"new_key": key(CAROL)})
        self.reject("claim_validity", self.claim, CAROL)

    def test_unknown_escrow_ref(self):
        self.reject("claim_validity", self.claim, ALICE, escrow_ref=H("nothing"))

    def test_auto_claim_hardens_after_N_epochs(self):
        roll_epoch(self.led, 2)
        self.claim(BOB)                      # 1 epoch later: still auto-claimable
        escrow2 = add(self.led, FOUNDER, "contribution.trivial_accepted",
                      dict(TRIVIAL, artifact_hash=H("art2"),
                           claim_binding=H("github:other")))
        roll_epoch(self.led, 3)
        roll_epoch(self.led, 4)
        p = {"escrow_ref": escrow2, "claim_binding": H("github:other"),
             "attestation_hash": H("att2")}
        self.reject("claim_validity", add, self.led, ALICE, "attribution.claimed", p)
        p["adjudication_ref"] = self.led.head
        add(self.led, ALICE, "attribution.claimed", p)


class TestKeyLifecycle(Base):
    def setUp(self):
        self.led = prologue()
        add(self.led, ALICE, "work.logged",
            {"category": "code", "native_unit": "hours", "quantity": 1, "mode": "E",
             "evidence": [H("e")], "week_ref": THIS_WEEK, "artifact_hash": H("a")})

    def test_rotation_rate_limit_per_lineage_per_epoch(self):
        add(self.led, ALICE, "key.rotated", {"new_key": key(BOB)})
        self.reject("rotation_rate_limit", add, self.led, BOB, "key.rotated",
                    {"new_key": key(CAROL)})
        roll_epoch(self.led, 2)
        add(self.led, BOB, "key.rotated", {"new_key": key(CAROL)})

    def test_lineage_resolution_survives_rotation(self):
        add(self.led, ALICE, "key.rotated", {"new_key": key(BOB)})
        self.assertEqual(self.led.lineage_of(key(BOB)), key(ALICE))
        self.assertEqual(self.led.lineage_map()[key(BOB)], key(ALICE))

    def test_fresh_key_rule(self):
        add(self.led, CAROL, "work.logged",
            {"category": "code", "native_unit": "hours", "quantity": 1, "mode": "E",
             "evidence": [H("e")], "week_ref": THIS_WEEK, "artifact_hash": H("a")})
        self.reject("fresh_key", add, self.led, ALICE, "key.rotated",
                    {"new_key": key(CAROL)})
        self.reject("fresh_key", add, self.led, ALICE, "key.successor_designated",
                    {"successor_key": key(CAROL)})

    def test_one_pending_rebind_per_orphaned_lineage(self):
        req = {"orphan_key": key(ALICE), "claimant_key": key(BOB),
               "evidence": [H("anchor")]}
        rid = add(self.led, FOUNDER, "key.rebind_requested", req)
        self.reject("pending_rebind_limit", add, self.led, FOUNDER,
                    "key.rebind_requested",
                    {"orphan_key": key(ALICE), "claimant_key": key(CAROL),
                     "evidence": [H("anchor2")]})
        adj = add(self.led, FOUNDER, "audit.review_opened",
                  {"review_id": H("r"), "target_event_id": rid})
        add(self.led, FOUNDER, "key.rebound",
            {"orphan_key": key(ALICE), "rebind_request_ref": rid,
             "adjudication_ref": adj})
        # rebinding merges the claimant into the orphaned lineage
        self.assertEqual(self.led.lineage_of(key(BOB)), key(ALICE))
        add(self.led, FOUNDER, "key.rebind_requested",
            {"orphan_key": key(ALICE), "claimant_key": key(CAROL),
             "evidence": [H("anchor2")]})

    def test_rebind_requires_known_orphan(self):
        self.reject("reference_integrity", add, self.led, FOUNDER,
                    "key.rebind_requested",
                    {"orphan_key": key(BOB), "claimant_key": key(CAROL),
                     "evidence": [H("x")]})


class TestJSONLLog(Base):
    def test_append_only_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "ledger.jsonl")
            log = EventLog(path)
            for e in _chain_events():
                log.append(e, receipt_ts=NOW)
            eid = log.append(mk(log.ledger, FOUNDER, "contribution.trivial_accepted",
                                dict(TRIVIAL)), receipt_ts=NOW)
            with open(path) as fh:
                lines = fh.read().splitlines()
            self.assertEqual(len(lines), log.count)
            self.assertEqual(canonical.loads(lines[-1])["type"],
                             "contribution.trivial_accepted")
            # every line is already canonical, and the whole file replays
            reloaded = EventLog(path)
            self.assertEqual(reloaded.head, eid)
            self.assertEqual(reloaded.count, log.count)

    def test_tampered_line_is_rejected_on_replay(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "l.jsonl")
            log = EventLog(path)
            for e in _chain_events():
                log.append(e, receipt_ts=NOW)
            with open(path) as fh:
                lines = fh.read().splitlines()
            lines[0] = lines[0].replace('"L":1000', '"L":1001')
            with open(path, "w") as fh:
                fh.write("\n".join(lines) + "\n")
            with self.assertRaises(ValidationError) as cm:
                EventLog(path)
            self.assertEqual(cm.exception.predicate, "signature")

    def _replay_mutated(self, mutate):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "l.jsonl")
            log = EventLog(path)
            for e in _chain_events():
                log.append(e, receipt_ts=NOW)
            with open(path) as fh:
                lines = fh.read().splitlines()
            with open(path, "w") as fh:
                fh.write("\n".join(mutate(lines)) + "\n")
            with self.assertRaises(ValidationError) as cm:
                EventLog(path)
            return cm.exception.predicate

    def test_relinked_line_is_rejected_on_replay(self):
        def mutate(lines):
            ev = canonical.loads(lines[2])
            ev["prev"] = GENESIS_PREV
            lines[2] = canonical.canonicalize(ev).decode()
            return lines
        self.assertEqual(self._replay_mutated(mutate), "hash_chain")

    def test_dropped_line_is_rejected_on_replay(self):
        self.assertEqual(self._replay_mutated(lambda ls: ls[:1] + ls[2:]),
                         "hash_chain")

    def test_non_canonical_line_is_rejected_on_replay(self):
        # a line that decodes to a valid, correctly signed event but is not
        # byte-identical to its canonical form still fails: the file is the
        # artifact forkers replay, so its bytes are part of the commitment.
        import json as _json

        def mutate(lines):
            lines[1] = _json.dumps(canonical.loads(lines[1]), indent=None,
                                   separators=(", ", ": "))
            return lines
        self.assertEqual(self._replay_mutated(mutate), "canonical_form")

    def test_week_ref_is_not_backdatable_before_the_first_checkpoint(self):
        # the staleness window's lower bound must be the receipt bound, never
        # the actor's own declared ts -- otherwise an actor declaring a stale
        # ts alongside a stale week_ref validates itself past the cap bucket.
        led = prologue()
        self.reject("week_ref_staleness", add, led, ALICE, "work.logged",
                    {"category": "code", "native_unit": "hours",
                     "quantity": 3600000, "mode": "E", "evidence": [H("e")],
                     "week_ref": OLD_WEEK, "artifact_hash": H("a")},
                    ts=NOW - 70 * DAY, receipt_ts=NOW)


def _chain_events():
    """A prologue's events, built against a throwaway ledger, for log tests."""
    led = Ledger()
    prologue(led)
    return [led.events[i] for i in led.order]


if __name__ == "__main__":
    unittest.main()
