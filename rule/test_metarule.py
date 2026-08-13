"""The meta-rule validity predicate, and the placeholder publication gate."""

import copy
import unittest

from rule import metarule, params as P
from rule.publish import (PublicationRefused, build_artifact, meta_rule_hash,
                          publish)

FINAL = copy.deepcopy(P.PLACEHOLDER_PARAMS)
FINAL["status"] = P.FINAL_STATUS
FINAL["placeholders"] = []
FINAL.pop("gated_by", None)


def final_params(**overrides):
    params = copy.deepcopy(FINAL)
    params.update(overrides)
    return params


class TestPlaceholderGate(unittest.TestCase):
    def test_the_shipped_parameters_are_placeholders(self):
        self.assertFalse(P.placeholder_free(P.PLACEHOLDER_PARAMS))
        self.assertIn("socaity-wna", P.PLACEHOLDER_PARAMS["gated_by"])

    def test_publish_refuses_placeholders(self):
        with self.assertRaises(PublicationRefused) as caught:
            publish(P.PLACEHOLDER_PARAMS)
        self.assertIn("socaity-wna", str(caught.exception))

    def test_publish_refuses_a_final_status_that_still_lists_placeholders(self):
        params = final_params()
        params["placeholders"] = ["L_days"]
        self.assertRaises(PublicationRefused, publish, params)

    def test_publish_refuses_the_sentinel_hiding_anywhere_in_the_set(self):
        params = final_params(gated_by=[P.PLACEHOLDER_STATUS])
        self.assertRaises(PublicationRefused, publish, params)

    def test_final_parameters_publish(self):
        artifact, payload = publish(final_params())
        self.assertEqual(payload["rule_version"], artifact["rule_version"])
        self.assertEqual(payload["source_hash"], artifact["structure_hash"])
        self.assertEqual(payload["params_hash"], artifact["params_hash"])

    def test_rule_version_binds_source_and_params(self):
        one = build_artifact(final_params())
        two = build_artifact(final_params(L_days=90))
        self.assertNotEqual(one["rule_version"], two["rule_version"])
        self.assertEqual(one["structure_hash"], two["structure_hash"])

    def test_development_artifact_still_builds(self):
        artifact = build_artifact()
        self.assertEqual(artifact["params"]["status"], P.PLACEHOLDER_STATUS)

    def test_meta_rule_hash_is_stable(self):
        self.assertEqual(meta_rule_hash(), meta_rule_hash())


class TestMetaRule(unittest.TestCase):
    def setUp(self):
        self.current = build_artifact(final_params(effective_from_epoch=1))
        self.state = {"highest_opened_epoch": 3, "open_epoch": 3}

    def amend(self, params, **artifact_overrides):
        """An artifact proposing *params*, built WITHOUT validating them.

        build_artifact() refuses a malformed set outright, so a malformed
        amendment can never reach the ledger through the supported path.  The
        meta-rule must still refuse it on its own, because a forker who hand
        writes the artifact JSON does not go through build_artifact() -- these
        tests exercise that second, independent gate.
        """
        artifact = dict(self.current)
        artifact["params"] = params
        artifact["params_hash"] = "0" * 64
        artifact["rule_version"] = "1" * 64
        artifact["prev_rule_version"] = self.current["rule_version"]
        artifact.update(artifact_overrides)
        return artifact

    def test_a_prospective_parameter_change_is_valid(self):
        proposed = self.amend(final_params(effective_from_epoch=5, L_days=60))
        self.assertEqual(metarule.violations(self.current, proposed, self.state), [])
        self.assertTrue(metarule.is_valid_amendment(self.current, proposed,
                                                    self.state))

    def test_an_opened_epoch_may_never_be_amended(self):
        proposed = self.amend(final_params(effective_from_epoch=3, L_days=60))
        self.assertIn("prospective_only",
                      metarule.violations(self.current, proposed, self.state))

    def test_notice_must_be_respected(self):
        # meta_min_notice_epochs = 1, open epoch 3 -> the earliest amendable
        # epoch is 5.
        self.assertIn("notice_respected", metarule.violations(
            self.current, self.amend(final_params(effective_from_epoch=4)),
            self.state))
        self.assertNotIn("notice_respected", metarule.violations(
            self.current, self.amend(final_params(effective_from_epoch=5)),
            self.state))

    def test_structure_may_not_change(self):
        proposed = self.amend(final_params(effective_from_epoch=5))
        proposed["structure_hash"] = "0" * 64
        self.assertIn("structure_unchanged",
                      metarule.violations(self.current, proposed, self.state))

    def test_source_edits_are_caught_even_if_the_hash_is_forged(self):
        proposed = self.amend(final_params(effective_from_epoch=5))
        proposed["sources"] = dict(proposed["sources"])
        proposed["sources"]["distribute.py"] = "0" * 64
        self.assertIn("structure_unchanged",
                      metarule.violations(self.current, proposed, self.state))

    def test_build_artifact_refuses_malformed_parameters_outright(self):
        params = final_params(effective_from_epoch=5)
        params["earliness_multiplier"] = {"num": 2, "den": 1}
        self.assertRaises(P.ParamsError, build_artifact, params)

    def test_the_amendment_must_name_its_predecessor(self):
        proposed = build_artifact(final_params(effective_from_epoch=5))
        self.assertIn("predecessor_named",
                      metarule.violations(self.current, proposed, self.state))

    def test_placeholders_may_never_be_amended_in(self):
        proposed = self.amend(copy.deepcopy(P.PLACEHOLDER_PARAMS))
        self.assertIn("no_placeholders",
                      metarule.violations(self.current, proposed, self.state))

    def test_a_rising_pie_is_refused(self):
        params = final_params(effective_from_epoch=5)
        params["pie"] = {"shape": "table",
                         "values": [{"num": 1, "den": 1}, {"num": 2, "den": 1}],
                         "tail": {"num": 1, "den": 1}}
        # A rising table is refused at the parameter-validation layer, which
        # the meta-rule reports as params_wellformed; either way it cannot be
        # published.
        broken = metarule.violations(self.current, self.amend(params), self.state)
        self.assertTrue({"params_wellformed", "non_increasing_pie"} & set(broken),
                        broken)

    def test_a_growing_geometric_ratio_is_refused(self):
        params = final_params(effective_from_epoch=5)
        params["pie"] = {"shape": "geometric_decay", "p0": {"num": 1, "den": 1},
                         "ratio": {"num": 3, "den": 2}}
        broken = metarule.violations(self.current, self.amend(params), self.state)
        self.assertTrue({"params_wellformed", "non_increasing_pie"} & set(broken),
                        broken)

    def test_unknown_parameter_keys_are_refused(self):
        params = final_params(effective_from_epoch=5)
        params["earliness_multiplier"] = {"num": 2, "den": 1}
        self.assertIn("params_wellformed",
                      metarule.violations(self.current, self.amend(params),
                                          self.state))

    def test_malformed_artifacts_are_refused(self):
        self.assertEqual(metarule.violations(self.current, {"nope": 1},
                                             self.state),
                         ["artifact_wellformed"])

    def test_assert_valid_amendment_names_the_broken_clauses(self):
        proposed = self.amend(final_params(effective_from_epoch=1))
        with self.assertRaises(metarule.MetaRuleError) as caught:
            metarule.assert_valid_amendment(self.current, proposed, self.state)
        self.assertIn("prospective_only", caught.exception.checks)

    def test_no_transfer_operation_exists(self):
        self.assertTrue(metarule._no_transfer_operation())

    def test_first_publication_needs_no_predecessor(self):
        self.assertEqual(metarule.violations(
            self.current,
            self.amend(final_params(effective_from_epoch=5)),
            {"highest_opened_epoch": None, "open_epoch": None}), [])

    def test_publish_routes_amendments_through_the_meta_rule(self):
        self.assertRaises(
            metarule.MetaRuleError, publish,
            final_params(effective_from_epoch=2), self.current, self.state)


class TestParams(unittest.TestCase):
    def test_pie_shapes_are_non_increasing(self):
        table = {"shape": "table",
                 "values": [{"num": 4, "den": 1}, {"num": 2, "den": 1}],
                 "tail": {"num": 1, "den": 1}}
        params = final_params()
        params["pie"] = table
        previous = None
        for epoch in range(8):
            current = P.pie(epoch, params)
            if previous is not None:
                self.assertLessEqual(current, previous)
            previous = current

    def test_rate_lookup_refuses_unknown_pairs(self):
        self.assertRaises(P.ParamsError, P.rate_of, "code", "tokens", FINAL)

    def test_rational_rejects_floats_and_zero_denominators(self):
        import json
        self.assertRaises(P.ParamsError, P.rational,
                          {"num": json.loads("1.5"), "den": 1})
        self.assertRaises(P.ParamsError, P.rational, {"num": 1, "den": 0})


if __name__ == "__main__":
    unittest.main()
