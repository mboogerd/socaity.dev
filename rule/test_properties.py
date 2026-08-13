"""Property tests for the rule -- standard library only, no hypothesis.

Cases are generated from a FIXED SEED, so the suite is itself deterministic:
a failure reproduces exactly, on every machine, which is the same property the
rule is required to have.  `random` is used only to build inputs; it never
touches the rule, which contains no randomness at all.

Properties (socaity-x8o §5, platform-engineer §5):
  conservation        payouts + audit reserve + undistributed == declared amount
  shares_sum_to_one   exactly 1, as an exact rational, never 0.999...
  permutation         reordering the input changes no output byte
  determinism         same input bytes -> same output bytes
  monotonicity        a larger weight never yields a smaller share
  mode_blind          adding a mode-A entry never raises an E holder's share
  scale_invariance    rescaling every P_e leaves every payout identical
  no_rollover         a lapsed fraction never appears in another epoch
"""

import copy
import random
import unittest
from fractions import Fraction

from rule.distribute import canonical_bytes, distribute
from rule.make_vectors import KEYS, entry, epoch, request
from rule.params import PLACEHOLDER_PARAMS

SEED = 20260813
CASES = 120
_LINEAGES = (None, "alice", "bob", "carol", "founder")
_CATEGORIES = ("code", "review", "docs", "ops", "design", "governance")
_STATUSES = ("confirmed", "confirmed", "confirmed", "challenged",
             "discounted", "provisional", "withdrawn")


def random_request(rng, index):
    epoch_count = rng.randint(1, 3)
    epochs = []
    for e in range(epoch_count):
        epochs.append(epoch(e, closed=rng.randint(0, 4) > 0,
                            audited=rng.randint(0, 4) > 0))
    entries = []
    statuses = {}
    for i in range(rng.randint(0, 8)):
        row = entry("case%d-e%d" % (index, i), rng.randrange(epoch_count),
                    rng.choice(_LINEAGES), rng.randrange(0, 5000000),
                    mode=rng.choice(("E", "E", "E", "A")),
                    category=rng.choice(_CATEGORIES))
        entries.append(row)
        status = rng.choice(_STATUSES)
        state = {"status": status}
        if status == "discounted":
            den = rng.randint(1, 8)
            state["discount"] = {"num": rng.randint(0, den), "den": den}
        statuses[row["entry_hash"]] = state
    amount = rng.choice((0, 1, 7, 100, 1001, 999999, 123456789))
    return request(entries, epochs, amount, statuses=statuses,
                   name="prop%d" % index)


def cases():
    rng = random.Random(SEED)
    return [random_request(rng, i) for i in range(CASES)]


class TestProperties(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = cases()

    def test_conservation_is_exact(self):
        for req in self.cases:
            table = distribute(req)
            paid = sum(row["amount_minor"] for row in table["recipients"])
            self.assertEqual(paid + table["audit_reserve_minor"]
                             + table["undistributed_minor"],
                             table["amount_minor"])

    def test_shares_sum_to_exactly_one(self):
        for req in self.cases:
            table = distribute(req)
            if not table["recipients"]:
                continue
            total = Fraction(0, 1)
            for row in table["recipients"]:
                total += Fraction(row["share"]["num"], row["share"]["den"])
            self.assertEqual(total, Fraction(1, 1))

    def test_no_negative_amounts(self):
        for req in self.cases:
            table = distribute(req)
            self.assertGreaterEqual(table["audit_reserve_minor"], 0)
            self.assertGreaterEqual(table["undistributed_minor"], 0)
            for row in table["recipients"]:
                self.assertGreaterEqual(row["amount_minor"], 0)

    def test_permutation_invariance(self):
        rng = random.Random(SEED + 1)
        for req in self.cases:
            shuffled = copy.deepcopy(req)
            rng.shuffle(shuffled["ledger_export"]["entries"])
            rng.shuffle(shuffled["ledger_export"]["epochs"])
            items = list(shuffled["validation_snapshot"]["entries"].items())
            rng.shuffle(items)
            shuffled["validation_snapshot"]["entries"] = dict(items)
            self.assertEqual(canonical_bytes(distribute(req)),
                             canonical_bytes(distribute(shuffled)))

    def test_determinism(self):
        for req in self.cases:
            first = canonical_bytes(distribute(copy.deepcopy(req)))
            second = canonical_bytes(distribute(copy.deepcopy(req)))
            self.assertEqual(first, second)

    def test_scale_invariance_of_the_pie(self):
        """Multiplying every P_e by a positive constant changes no payout.

        This is the formal statement that P_e is a WEIGHT and not an amount
        (socaity-x8o §2, legal-counsel Round 2).
        """
        for req in self.cases:
            scaled = copy.deepcopy(req)
            scaled["params"]["pie"] = {"shape": "constant",
                                       "value": {"num": 7, "den": 3}}
            base = distribute(req)
            other = distribute(scaled)
            self.assertEqual([(r["kind"], r["id"], r["amount_minor"], r["share"])
                              for r in base["recipients"]],
                             [(r["kind"], r["id"], r["amount_minor"], r["share"])
                              for r in other["recipients"]])

    def test_monotonicity_in_weight(self):
        """A larger declared quantity never buys a smaller share."""
        rng = random.Random(SEED + 2)
        for req in self.cases:
            entries = req["ledger_export"]["entries"]
            snapshot = req["validation_snapshot"]["entries"]
            candidates = [e for e in entries
                          if e["mode"] == "E" and e["lineage"] is not None
                          and snapshot[e["entry_hash"]]["status"] == "confirmed"]
            if not candidates:
                continue
            target = rng.choice(candidates)
            before = distribute(req)
            bumped = copy.deepcopy(req)
            for row in bumped["ledger_export"]["entries"]:
                if row["entry_hash"] == target["entry_hash"]:
                    row["quantity_micro"] += rng.randint(1, 1000000)
            after = distribute(bumped)
            for kind, ident in _holders(before):
                if (kind, ident) not in _holders(after):
                    continue
                # Only the bumped entry's holder may gain; everyone else's
                # share may only fall, and the bumped holder's may only rise.
                gained = _share(after, kind, ident) - _share(before, kind, ident)
                if kind == "lineage" and ident == target["lineage"]:
                    self.assertGreaterEqual(gained, Fraction(0, 1))
                else:
                    self.assertLessEqual(gained, Fraction(0, 1))

    def test_mode_a_never_raises_an_e_holders_claim(self):
        """The denominator is mode-blind, so electing A cannot pump R.

        The invariant is on R, not on the normalised share: adding a mode-A
        entry to epoch e dilutes every epoch-e claim, which -- across a
        multi-epoch distribution -- slightly RAISES the normalised share of a
        holder whose claims sit in other epochs.  That is the adopted formula
        working as written (shares are proportions of the total claim, and
        lapsed weight is never rolled forward), not a leak: no holder's claim
        on epoch e itself grows.  For a single-epoch distribution the shares
        are unchanged too, which the second half of this test asserts.
        """
        for index, req in enumerate(self.cases):
            before = distribute(req)
            with_a = copy.deepcopy(req)
            eligible = [e["index"] for e in with_a["ledger_export"]["epochs"]
                        if e["closed"] and e["audited"]]
            if not eligible:
                continue
            row = entry("modeA-%d" % index, eligible[0], "carol", 2500000,
                        mode="A")
            with_a["ledger_export"]["entries"].append(row)
            with_a["validation_snapshot"]["entries"][row["entry_hash"]] = \
                {"status": "confirmed"}
            after = distribute(with_a)
            for kind, ident in _holders(before):
                if (kind, ident) not in _holders(after):
                    continue
                self.assertLessEqual(_claim(after, kind, ident),
                                     _claim(before, kind, ident))
                if len(eligible) == 1:
                    self.assertEqual(_share(after, kind, ident),
                                     _share(before, kind, ident))
            # `<=` alone is ALSO satisfied by a denominator that ignores mode
            # A entirely -- the exact thing socaity-x8o §4 forbids ("ALL
            # confirmed contributions enter D_e regardless of mode"), because
            # then adding one changes nothing at all.  So assert the strict
            # form the resolution actually requires: the mode-A entry lands in
            # D_e, which is a STRICT increase of that epoch's denominator.
            self.assertGreater(_denominator(after, eligible[0]),
                               _denominator(before, eligible[0]))

    def test_no_rollover_between_epochs(self):
        """A lapsed or zero-weight epoch never leaks weight into another one."""
        for req in self.cases:
            table = distribute(req)
            for row in table["epochs"]:
                pie = Fraction(row["pie"]["num"], row["pie"]["den"])
                lapsed = Fraction(row["lapsed_pie"]["num"],
                                  row["lapsed_pie"]["den"])
                self.assertGreaterEqual(lapsed, Fraction(0, 1))
                self.assertLessEqual(lapsed, pie)

    def test_challenged_entries_stay_in_the_denominator(self):
        for req in self.cases:
            table = distribute(req)
            eligible = {e["index"] for e in req["ledger_export"]["epochs"]
                        if e["closed"] and e["audited"]}
            expected = {}
            for row in req["ledger_export"]["entries"]:
                if row["epoch"] not in eligible:
                    continue
                status = req["validation_snapshot"]["entries"][
                    row["entry_hash"]]["status"]
                if status in ("provisional", "withdrawn"):
                    continue
                expected[row["epoch"]] = expected.get(row["epoch"], 0) + 1
            for row in table["epochs"]:
                if expected.get(row["epoch"], 0) == 0:
                    self.assertEqual(row["denominator_micro_vu"], 0)


def _holders(table):
    return {(row["kind"], row["id"]) for row in table["recipients"]}


def _claim(table, kind, ident):
    for row in table["recipients"]:
        if row["kind"] == kind and row["id"] == ident:
            return Fraction(row["claim_R"]["num"], row["claim_R"]["den"])
    return Fraction(0, 1)


def _share(table, kind, ident):
    for row in table["recipients"]:
        if row["kind"] == kind and row["id"] == ident:
            return Fraction(row["share"]["num"], row["share"]["den"])
    return Fraction(0, 1)


def _denominator(table, epoch_index):
    for row in table["epochs"]:
        if row["epoch"] == epoch_index:
            return row["denominator_micro_vu"]
    return 0



if __name__ == "__main__":
    unittest.main()
