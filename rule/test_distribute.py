"""Unit tests for the rule, including hand-checked arithmetic.

Run:  python3 -m unittest discover rule
"""

import copy
import json
import unittest
from fractions import Fraction

from rule import params as P
from rule.distribute import RuleError, distribute, table_hash
from rule.make_vectors import H, KEYS, entry, epoch, request
from rule.valuation import compute_credit_micro, weight_micro_vu


class Base(unittest.TestCase):
    def rows(self, table):
        return {(row["kind"], row["id"]): row for row in table["recipients"]}

    def amounts(self, table):
        return {row["id"]: row["amount_minor"] for row in table["recipients"]}


class TestHandCheckedArithmetic(Base):
    def test_audit_slice_and_single_recipient(self):
        # 10000 minor, cap 1/20 -> reserve 500, distributable 9500, one claim.
        table = distribute(request([entry("e1", 0, "alice", 3600000)],
                                   [epoch(0)], 10000, name="01"))
        self.assertEqual(table["audit_reserve_minor"], 500)
        self.assertEqual(table["undistributed_minor"], 0)
        self.assertEqual(self.amounts(table), {KEYS["alice"]: 9500})

    def test_remainder_tie_goes_to_the_smaller_entry_hash(self):
        # 1001 -> reserve floor(1001/20) = 50 -> 951 distributable.
        # Two equal claims: 475.5 each -> 475 + 475, residual 1.
        # Remainders tie at 1/2, so the tie-break decides: ascending entry
        # hash.  H("e1") < H("e2"), so alice takes the unit.
        self.assertLess(H("e1"), H("e2"))
        table = distribute(request([entry("e1", 0, "alice", 1000000),
                                    entry("e2", 0, "bob", 1000000)],
                                   [epoch(0)], 1001, name="02"))
        self.assertEqual(table["audit_reserve_minor"], 50)
        self.assertEqual(self.amounts(table),
                         {KEYS["alice"]: 476, KEYS["bob"]: 475})

    def test_three_way_residual(self):
        # 100 -> reserve 5 -> 95 distributable; 95/3 = 31 remainder 2/3 each.
        # Two units of residual go to the two smallest entry hashes.
        table = distribute(request([entry("e1", 0, "alice", 1000000),
                                    entry("e2", 0, "bob", 1000000),
                                    entry("e3", 0, "carol", 1000000)],
                                   [epoch(0)], 100, name="11"))
        self.assertEqual(sorted(H(t) for t in ("e1", "e2", "e3"))[:2],
                         sorted([H("e1"), H("e2")]))
        self.assertEqual(self.amounts(table),
                         {KEYS["alice"]: 32, KEYS["bob"]: 32, KEYS["carol"]: 31})
        self.assertEqual(32 + 32 + 31 + 5, 100)

    def test_geometric_pie_gives_two_to_one(self):
        params = copy.deepcopy(P.PLACEHOLDER_PARAMS)
        params["pie"] = {"shape": "geometric_decay", "p0": {"num": 1, "den": 1},
                         "ratio": {"num": 1, "den": 2}}
        table = distribute(request([entry("e1", 0, "alice", 1000000),
                                    entry("e2", 1, "bob", 1000000)],
                                   [epoch(0), epoch(1)], 9000, params=params,
                                   name="06"))
        rows = self.rows(table)
        self.assertEqual(rows[("lineage", KEYS["alice"])]["share"],
                         {"num": 2, "den": 3})
        self.assertEqual(rows[("lineage", KEYS["bob"])]["share"],
                         {"num": 1, "den": 3})


class TestDenominatorAndModes(Base):
    def test_mode_a_enters_the_denominator_and_lapses(self):
        table = distribute(request([entry("e1", 0, "alice", 2000000),
                                    entry("e2", 0, "bob", 2000000, mode="A")],
                                   [epoch(0)], 10000, name="05"))
        self.assertEqual(table["epochs"][0]["denominator_micro_vu"], 4000000)
        self.assertEqual(table["epochs"][0]["lapsed_pie"], {"num": 1, "den": 2})
        # Mode A produces a closed-loop compute credit and no claim.
        self.assertEqual(table["compute_credits"],
                         [{"lineage": KEYS["bob"], "micro_credits": 2000000}])
        self.assertEqual(len(table["recipients"]), 1)

    def test_mode_a_cannot_pump_an_e_holders_share(self):
        base = distribute(request([entry("e1", 0, "alice", 1000000),
                                   entry("e2", 0, "bob", 1000000)],
                                  [epoch(0)], 10000, name="x"))
        switched = distribute(request([entry("e1", 0, "alice", 1000000),
                                       entry("e2", 0, "bob", 1000000, mode="A")],
                                      [epoch(0)], 10000, name="x"))
        # Alice's R doubles in absolute terms?  No: the denominator is
        # mode-blind, so her R is 1/2 either way.
        alice = ("lineage", KEYS["alice"])
        self.assertEqual(self.rows(base)[alice]["claim_R"], {"num": 1, "den": 2})
        self.assertEqual(self.rows(switched)[alice]["claim_R"],
                         {"num": 1, "den": 2})

    def test_only_closed_and_audited_epochs_participate(self):
        table = distribute(request([entry("e1", 0, "alice", 1000000),
                                    entry("e2", 1, "bob", 9000000),
                                    entry("e3", 2, "carol", 9000000)],
                                   [epoch(0), epoch(1, audited=False),
                                    epoch(2, closed=False, audited=False)],
                                   10000, name="10"))
        self.assertEqual([e["epoch"] for e in table["epochs"]], [0])
        self.assertEqual(list(self.amounts(table)), [KEYS["alice"]])


class TestHolds(Base):
    def test_challenged_entry_is_escrowed_at_declared_weight(self):
        table = distribute(request([entry("e1", 0, "alice", 1000000),
                                    entry("e2", 0, "bob", 1000000)],
                                   [epoch(0)], 10000,
                                   statuses={H("e1"): {"status": "challenged"},
                                             H("e2"): {"status": "confirmed"}},
                                   name="c"))
        rows = self.rows(table)
        self.assertEqual(rows[("escrow", H("e1"))]["hold"], "challenge")
        self.assertEqual(rows[("escrow", H("e1"))]["share"], {"num": 1, "den": 2})
        self.assertEqual(table["epochs"][0]["denominator_micro_vu"], 2000000)

    def test_null_contributor_is_held_under_attribution(self):
        table = distribute(request([entry("e1", 0, None, 1000000),
                                    entry("e2", 0, "bob", 1000000)],
                                   [epoch(0)], 10000, name="07"))
        rows = self.rows(table)
        self.assertEqual(rows[("escrow", H("e1"))]["hold"], "attribution")
        self.assertEqual(rows[("escrow", H("e1"))]["amount_minor"], 4750)

    def test_provisional_and_withdrawn_never_enter_the_denominator(self):
        table = distribute(request([entry("e1", 0, "alice", 1000000),
                                    entry("e2", 0, "bob", 1000000),
                                    entry("e3", 0, "carol", 1000000)],
                                   [epoch(0)], 10000,
                                   statuses={H("e1"): {"status": "confirmed"},
                                             H("e2"): {"status": "provisional"},
                                             H("e3"): {"status": "withdrawn"}},
                                   name="p"))
        self.assertEqual(table["epochs"][0]["denominator_micro_vu"], 1000000)
        self.assertEqual(self.amounts(table), {KEYS["alice"]: 9500})


class TestDegenerateCases(Base):
    def test_zero_weight_epoch(self):
        table = distribute(request([entry("e1", 0, "alice", 0)], [epoch(0)],
                                   10000, name="03"))
        self.assertEqual(table["recipients"], [])
        self.assertEqual(table["undistributed_minor"], 9500)

    def test_empty_ledger(self):
        table = distribute(request([], [epoch(0)], 10000, name="12"))
        self.assertEqual(table["undistributed_minor"], 9500)

    def test_zero_declared_amount(self):
        table = distribute(request([entry("e1", 0, "alice", 1000000)],
                                   [epoch(0)], 0, name="14"))
        self.assertEqual(table["amount_minor"], 0)
        self.assertEqual(table["audit_reserve_minor"], 0)
        self.assertEqual(self.amounts(table), {KEYS["alice"]: 0})

    def test_sub_quantum_leftover_is_reported_not_absorbed(self):
        params = copy.deepcopy(P.PLACEHOLDER_PARAMS)
        params["quantum_minor"] = 100
        table = distribute(request([entry("e1", 0, "alice", 1000000)],
                                   [epoch(0)], 10000, params=params, name="q"))
        # 9500 distributable, quantum 100 -> 95 whole quanta, 0 left over.
        self.assertEqual(table["undistributed_minor"], 0)
        self.assertEqual(self.amounts(table), {KEYS["alice"]: 9500})


class TestRequestValidation(Base):
    def bad(self, mutate):
        req = request([entry("e1", 0, "alice", 1000000)], [epoch(0)], 10000,
                      name="bad")
        mutate(req)
        self.assertRaises(RuleError, distribute, req)

    def test_float_amount_rejected(self):
        # A float cannot be written here -- the no-float lint covers the tests
        # too -- so it enters the way a real one would: parsed from outside.
        def mutate(req):
            req["declared"]["amount_minor"] = json.loads("1.5")
        self.bad(mutate)

    def test_unknown_status_rejected(self):
        def mutate(req):
            req["validation_snapshot"]["entries"][H("e1")] = {"status": "meh"}
        self.bad(mutate)

    def test_unknown_mode_rejected(self):
        def mutate(req):
            req["ledger_export"]["entries"][0]["mode"] = "X"
        self.bad(mutate)

    def test_duplicate_entry_hash_rejected(self):
        def mutate(req):
            req["ledger_export"]["entries"].append(
                dict(req["ledger_export"]["entries"][0]))
        self.bad(mutate)

    def test_entry_in_an_undescribed_epoch_rejected(self):
        def mutate(req):
            req["ledger_export"]["entries"][0]["epoch"] = 7
        self.bad(mutate)

    def test_unknown_request_key_rejected(self):
        def mutate(req):
            req["extra"] = 1
        self.bad(mutate)

    def test_a_float_in_an_identity_column_is_rejected(self):
        # Identity columns are copied straight into the payout table, and the
        # table is what gets hashed onto the ledger.  A float arriving from a
        # parsed export must not get that far.
        for path in (("rule_version",),
                     ("ledger_export", "checkpoint_hash"),
                     ("declared", "currency"),
                     ("declared", "distribution_id"),
                     ("declared", "cutoff_checkpoint_hash")):
            def mutate(req, path=path):
                node = req
                for step in path[:-1]:
                    node = node[step]
                node[path[-1]] = json.loads("1.5")
            self.bad(mutate)
        for field in ("entry_hash", "lineage", "category", "native_unit",
                      "tier"):
            def mutate(req, field=field):
                req["ledger_export"]["entries"][0][field] = json.loads("1.5")
            self.bad(mutate)

    def test_discounted_without_a_factor_is_rejected(self):
        # Fail closed: "discounted" with no factor must not silently mean
        # "discounted by nothing", which is full weight.
        def mutate(req):
            req["validation_snapshot"]["entries"][H("e1")] = \
                {"status": "discounted"}
        self.bad(mutate)

    def test_missing_rate_is_refused(self):
        req = request([entry("e1", 0, "alice", 1000000, category="code",
                             native_unit="tokens")], [epoch(0)], 10000, name="r")
        self.assertRaises(P.ParamsError, distribute, req)


class TestValuation(Base):
    def test_weight_is_floored_integer_micro_vu(self):
        params = copy.deepcopy(P.PLACEHOLDER_PARAMS)
        params["rates"]["code:hours"] = {"num": 1, "den": 3}
        row = entry("e1", 0, "alice", 1000000)
        self.assertEqual(weight_micro_vu(row, params), 333333)

    def test_discount_never_increases_a_weight(self):
        params = P.PLACEHOLDER_PARAMS
        row = entry("e1", 0, "alice", 1000001)
        full = weight_micro_vu(row, params)
        for num in range(0, 5):
            discounted = weight_micro_vu(row, params, Fraction(num, 4))
            self.assertLessEqual(discounted, full)

    def test_tier_floor(self):
        params = P.PLACEHOLDER_PARAMS
        low = entry("e1", 0, "alice", 100000, tier="T1")
        self.assertEqual(weight_micro_vu(low, params), 500000)
        high = entry("e2", 0, "alice", 900000, tier="T1")
        self.assertEqual(weight_micro_vu(high, params), 900000)

    def test_compute_credit(self):
        params = copy.deepcopy(P.PLACEHOLDER_PARAMS)
        params["absolute_rate"] = {"num": 3, "den": 2}
        self.assertEqual(compute_credit_micro(1000001, params), 1500001)


class TestOutputDiscipline(Base):
    def test_table_carries_the_required_disclosures(self):
        table = distribute(request([entry("e1", 0, "alice", 1000000)],
                                   [epoch(0)], 10000, name="d"))
        self.assertEqual(table["notice"]["unit"], "epoch weight")
        self.assertTrue(table["notice"]["confers_no_redemption_value"])
        self.assertIn("scale_invariance", table["notice"])

    def test_no_currency_style_or_per_unit_price_columns(self):
        table = distribute(request([entry("e1", 0, "alice", 1000000)],
                                   [epoch(0)], 10000, name="d"))
        keys = set(table) | set(table["recipients"][0])
        for banned in ("price", "value", "balance", "holdings", "cu", "credits_eur"):
            self.assertNotIn(banned, keys)
        self.assertEqual(table["currency"], "EUR")

    def test_table_hash_is_stable(self):
        req = request([entry("e1", 0, "alice", 1000000)], [epoch(0)], 10000,
                      name="d")
        self.assertEqual(table_hash(distribute(req)),
                         table_hash(distribute(copy.deepcopy(req))))

    def test_no_transfer_operation_exists_anywhere_in_the_package(self):
        import rule
        from rule import distribute as dmod, params as pmod, valuation as vmod
        for module in (rule, dmod, pmod, vmod):
            for name in dir(module):
                self.assertNotIn("transfer", name.lower())


if __name__ == "__main__":
    unittest.main()
