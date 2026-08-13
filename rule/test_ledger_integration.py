"""End to end: a real validated chain -> the rule -> a payout table.

This is the join between socaity-124's ledger and this package: nothing here
constructs a fixture by hand, every event goes through the append-time
validator, and the rule reads only what replay derives from the chain.
"""

import unittest

from ledger.test_ledger import (ALICE, BOB, CAROL, CKPT, FOUNDER, H, THIS_WEEK,
                                add, key, prologue, roll_epoch)
from ledger.validator import Ledger, ValidationError
from rule import replay
from rule.distribute import distribute
from rule.params import FINAL_STATUS, PLACEHOLDER_PARAMS
from rule.publish import build_artifact

WORK = {"category": "code", "native_unit": "hours", "mode": "E",
        "evidence": [H("evidence")], "week_ref": THIS_WEEK,
        "artifact_hash": H("artifact")}


def confirm(led, event_id):
    """socaity-zjr: an accrual observation is provisional until confirmed, and
    only confirmed weight enters a denominator."""
    return add(led, FOUNDER, "entry.status_changed",
               {"target_event_id": event_id, "from": "provisional",
                "to": "confirmed", "basis_refs": [event_id]})


def work(quantity, mode="E", tag="a", category="code"):
    payload = dict(WORK)
    payload.update({"quantity": quantity, "mode": mode, "category": category,
                    "artifact_hash": H("artifact-" + tag),
                    "evidence": [H("evidence-" + tag)]})
    return payload


class TestReplayToRule(unittest.TestCase):
    def setUp(self):
        # Epoch 0: the itemised founder position, inside the genesis prologue.
        self.led = prologue(epoch0=[("work.logged", work(4000000, tag="f1",
                                                         category="governance")),
                                    ("work.logged", work(2000000, tag="f2"))])
        # Epoch 1: two external contributors, one of them mode A.
        self.alice_entry = add(self.led, ALICE, "work.logged", work(3000000, tag="a1"))
        self.bob_entry = add(self.led, BOB, "work.logged",
                             work(1000000, mode="A", tag="b1"))
        self.carol_entry = add(self.led, CAROL, "work.logged", work(1000000, tag="c1"))
        for event_id in list(self.led.entry_epoch):
            confirm(self.led, event_id)
        # Close epoch 1, open epoch 2, and complete the audit of epoch 1.
        roll_epoch(self.led, 2)
        add(self.led, FOUNDER, "audit.completed",
            {"distribution_id": H("d1"), "scope_checkpoint_hash": H("cp2"),
             "report_hash": H("report")})
        add(self.led, FOUNDER, "audit.completed",
            {"distribution_id": H("d1"), "scope_checkpoint_hash": H("cp0"),
             "report_hash": H("report0")})
        self.artifact = build_artifact()
        self.declared = {"distribution_id": H("d1"), "amount_minor": 100000,
                         "currency": "EUR", "cutoff_checkpoint_hash": H("cp2")}

    def request(self):
        return replay.distribution_request(self.led, self.artifact, self.declared)

    def test_epoch_assignment_clamps_to_chain_position(self):
        assignment = replay.epoch_assignment(self.led)
        # The founder's prologue observations sit before any epoch was opened.
        for event_id, epoch in assignment.items():
            if self.led.events[event_id]["actor"] == key(FOUNDER):
                self.assertEqual(epoch, 0)
        # Every external entry was appended while epoch 1 was open.
        self.assertEqual(assignment[self.alice_entry], 1)
        self.assertEqual(assignment[self.carol_entry], 1)

    def test_the_validator_records_the_same_assignment(self):
        self.assertEqual(self.led.entry_epoch, replay.epoch_assignment(self.led))

    def test_a_late_entry_cannot_land_in_a_closed_epoch(self):
        late = add(self.led, ALICE, "work.logged", work(9000000, tag="late"))
        confirm(self.led, late)
        assignment = replay.epoch_assignment(self.led)
        self.assertEqual(assignment[late], 2)          # not 1, which is closed
        table = distribute(self.request())
        # Epoch 2 is open, so the late entry cannot touch the payout at all.
        self.assertEqual([e["epoch"] for e in table["epochs"]], [0, 1])

    def test_end_to_end_payout(self):
        table = distribute(self.request())
        self.assertEqual([e["epoch"] for e in table["epochs"]], [0, 1])
        paid = sum(row["amount_minor"] for row in table["recipients"])
        self.assertEqual(paid + table["audit_reserve_minor"]
                         + table["undistributed_minor"], 100000)
        holders = {row["id"] for row in table["recipients"]}
        self.assertIn(key(ALICE), holders)
        self.assertIn(key(FOUNDER), holders)
        # Mode A earns a compute credit and no epoch share.
        self.assertNotIn(key(BOB), holders)
        self.assertEqual([c["lineage"] for c in table["compute_credits"]],
                         [key(BOB)])
        # ... but it is still in the epoch-1 denominator: 3 + 1 + 1 hours.
        epoch1 = [e for e in table["epochs"] if e["epoch"] == 1][0]
        self.assertEqual(epoch1["denominator_micro_vu"], 5000000)

    def test_a_rotated_key_keeps_one_lineage(self):
        add(self.led, ALICE, "key.rotated", {"new_key": key(b"\x66" * 32)})
        table = distribute(replay.distribution_request(
            self.led, self.artifact, self.declared))
        holders = [row["id"] for row in table["recipients"]]
        self.assertIn(key(ALICE), holders)             # the lineage root
        self.assertNotIn(key(b"\x66" * 32), holders)

    def test_challenge_moves_the_entry_into_escrow(self):
        add(self.led, BOB, "stake.escrowed",
            {"stake_id": H("s1"), "weight": {"num": 1, "den": 10}})
        add(self.led, BOB, "challenge.filed",
            {"challenge_id": H("ch1"), "target_event_id": self.alice_entry,
             "grounds": "overstated_quantity", "stake_ref": self.led.head})
        snapshot = replay.validation_snapshot(self.led)
        self.assertEqual(snapshot["entries"][self.alice_entry]["status"],
                         "challenged")
        table = distribute(self.request())
        rows = {(row["kind"], row["id"]): row for row in table["recipients"]}
        self.assertEqual(rows[("escrow", self.alice_entry)]["hold"], "challenge")
        # The escrow sits at the DECLARED weight: epoch 1's denominator is
        # unchanged by the challenge.
        epoch1 = [e for e in table["epochs"] if e["epoch"] == 1][0]
        self.assertEqual(epoch1["denominator_micro_vu"], 5000000)

    def test_decided_challenge_discounts_the_weight(self):
        add(self.led, BOB, "stake.escrowed",
            {"stake_id": H("s1"), "weight": {"num": 1, "den": 10}})
        add(self.led, BOB, "challenge.filed",
            {"challenge_id": H("ch1"), "target_event_id": self.alice_entry,
             "grounds": "overstated_quantity", "stake_ref": self.led.head})
        add(self.led, FOUNDER, "challenge.decided",
            {"challenge_id": H("ch1"), "outcome": "upheld",
             "discount": {"num": 1, "den": 3}})
        table = distribute(self.request())
        epoch1 = [e for e in table["epochs"] if e["epoch"] == 1][0]
        # Alice's 3 000 000 micro-vu becomes 2 000 000 (a 1/3 discount).
        self.assertEqual(epoch1["denominator_micro_vu"], 4000000)

    def test_unclaimed_escrow_is_held_and_a_claim_releases_it(self):
        ticket = add(self.led, FOUNDER, "ticket.opened",
                     {"ticket_id": H("t1"), "tier": "T1", "category": "docs",
                      "spec_hash": H("spec1")})
        accepted = add(self.led, FOUNDER, "ticket.accepted",
                       {"ticket_ref": ticket, "ticket_id": H("t1"),
                        "contributor": None, "attested_micro_hours": 1000000,
                        "mode": "E", "category": "docs",
                        "evidence": [H("merge")], "artifact_hash": H("pr1"),
                        "week_ref": THIS_WEEK,
                        "claim_binding": H("github:stranger")})
        confirm(self.led, accepted)
        add(self.led, FOUNDER, "epoch.closed",
            {"epoch": 2, "checkpoint_hash": H("cp3")})
        add(self.led, FOUNDER, "audit.completed",
            {"distribution_id": H("d2"), "scope_checkpoint_hash": H("cp3"),
             "report_hash": H("report2")})

        table = distribute(replay.distribution_request(
            self.led, self.artifact, self.declared))
        rows = {(row["kind"], row["id"]): row for row in table["recipients"]}
        self.assertEqual(rows[("escrow", accepted)]["hold"], "attribution")

        add(self.led, ALICE, "attribution.claimed",
            {"escrow_ref": accepted, "claim_binding": H("github:stranger"),
             "attestation_hash": H("attestation")})
        after = distribute(replay.distribution_request(
            self.led, self.artifact, self.declared))
        rows = {(row["kind"], row["id"]): row for row in after["recipients"]}
        self.assertNotIn(("escrow", accepted), rows)
        self.assertIn(("lineage", key(ALICE)), rows)

    def test_meta_state_reads_the_chain(self):
        self.assertEqual(replay.meta_state(self.led),
                         {"highest_opened_epoch": 2, "open_epoch": 2})


class TestPlaceholderPredicate(unittest.TestCase):
    """socaity-x8o §7: a placeholder V may neither be published nor open an
    epoch.  The chain carries hashes only, so the predicate fires for a
    replayer that holds the artifact behind the hash -- which is exactly the
    forker running the CI job."""

    def chain(self, params):
        """Genesis prologue whose rule.version_published names *params*."""
        artifact = build_artifact(params)

        def resolver(params_hash):
            if params_hash == artifact["params_hash"]:
                return artifact["params"]
            return None

        led = Ledger(params_resolver=resolver)
        rule_version = artifact["rule_version"]
        add(led, FOUNDER, "genesis",
            {"rule_version_hash": rule_version, "meta_rule_hash": H("mr"),
             "checkpoint_key": key(CKPT), "L": 1000})
        add(led, FOUNDER, "rule.version_published",
            {"rule_version": rule_version,
             "source_hash": artifact["structure_hash"],
             "params_hash": artifact["params_hash"]})
        add(led, FOUNDER, "rule.meta_published", {"meta_rule_hash": H("mr")})
        add(led, FOUNDER, "epoch.opened",
            {"epoch": 0, "rule_version_hash": rule_version})
        add(led, FOUNDER, "epoch.closed",
            {"epoch": 0, "checkpoint_hash": H("cp0")})
        add(led, FOUNDER, "rule.attested",
            {"rule_version_hash": rule_version, "epoch": 1,
             "statement_hash": H("stmt")})
        add(led, FOUNDER, "epoch.opened",
            {"epoch": 1, "rule_version_hash": rule_version})
        return led

    def final_params(self):
        params = dict(PLACEHOLDER_PARAMS)
        params["status"] = FINAL_STATUS
        params["placeholders"] = []
        params.pop("gated_by", None)
        return params

    def test_a_placeholder_params_set_cannot_be_published(self):
        with self.assertRaises(ValidationError) as caught:
            self.chain(PLACEHOLDER_PARAMS)
        self.assertEqual(caught.exception.predicate, "placeholder_free_params")
        self.assertIn("socaity-wna", str(caught.exception))

    def test_a_final_params_set_opens_epoch_one(self):
        led = self.chain(self.final_params())
        self.assertEqual(led.epoch_open, 1)
        self.assertTrue(led.prologue_complete)

    def test_epoch_one_is_refused_if_the_params_turn_out_to_be_placeholders(self):
        # A chain published under a resolver that knew nothing, replayed later
        # by someone who does hold the artifact: the epoch gate fires even
        # though the publication event slipped past.
        final = build_artifact(self.final_params())
        placeholder = build_artifact(PLACEHOLDER_PARAMS)
        led = Ledger(params_resolver=lambda h: (
            PLACEHOLDER_PARAMS if h == final["params_hash"] else None))
        rule_version = final["rule_version"]
        add(led, FOUNDER, "genesis",
            {"rule_version_hash": rule_version, "meta_rule_hash": H("mr"),
             "checkpoint_key": key(CKPT), "L": 1000})
        with self.assertRaises(ValidationError) as caught:
            add(led, FOUNDER, "rule.version_published",
                {"rule_version": rule_version,
                 "source_hash": final["structure_hash"],
                 "params_hash": final["params_hash"]})
        self.assertEqual(caught.exception.predicate, "placeholder_free_params")
        self.assertNotEqual(final["rule_version"], placeholder["rule_version"])

    def test_the_predicate_is_inert_without_a_resolver(self):
        led = prologue()                     # nothing to judge, nothing judged
        self.assertEqual(led.epoch_open, 1)

    def test_the_validator_binds_epochs_to_their_rule_version(self):
        led = prologue()
        self.assertEqual(led.epoch_rule_version, {0: H("rv1"), 1: H("rv1")})
        self.assertEqual(led.epoch_checkpoint, {0: H("cp0")})
        self.assertEqual(led.rule_params[H("rv1")], H("params"))


if __name__ == "__main__":
    unittest.main()
