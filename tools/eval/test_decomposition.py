import unittest

from decomposition import calibration_report, score_case, variance


class DecompositionHarnessTest(unittest.TestCase):
    def setUp(self):
        self.golden = {
            "nodes": [{"id": "need"}, {"id": "a"}, {"id": "b"}, {"id": "shared"}],
            "alternatives": [["a", "b"]],
            "dependencies": [{"from": "a", "to": "shared"}],
        }

    def test_scores_alternatives_and_phantom_dependencies(self):
        result = score_case(self.golden, {
            "nodes": [{"id": "need"}, {"id": "a"}, {"id": "b"}, {"id": "shared"}],
            "alternatives": [["a", "b"]],
            "dependencies": [{"from": "a", "to": "shared"}, {"from": "b", "to": "need"}],
        })
        self.assertEqual(result["alternative_coverage"], 1.0)
        self.assertEqual(result["phantom_dependency_edges"], ["b->need"])
        self.assertEqual(result["phantom_dependencies"], 0.5)

    def test_variance_is_zero_for_identical_runs(self):
        prediction = {"nodes": [{"id": "a"}], "alternatives": [], "dependencies": []}
        self.assertEqual(variance([prediction, prediction])["pairwise_disagreement"], 0.0)

    def test_calibration_matches_external_refs_before_semantic_proposals(self):
        report = calibration_report({
            "schema": 1,
            "provenance": {"fixture": "test", "basis": "hand-labelled"},
            "pairs": [
                {"id": "exact", "left": "a", "right": "b", "label": "duplicate",
                 "match_type": "external_ref", "source": "test"},
                {"id": "near-duplicate", "left": "c", "right": "d", "label": "duplicate",
                 "match_type": "semantic", "similarity": 0.90, "source": "test"},
                {"id": "false-merge", "left": "e", "right": "f", "label": "non_duplicate",
                 "match_type": "semantic", "similarity": 0.90, "source": "test"},
            ],
        }, thresholds=(0.90,))
        band = report["bands"][0]
        self.assertEqual(band["proposals"], 3)
        self.assertEqual(band["duplicate_rate"], 1.0)
        self.assertEqual(band["false_merge_rate"], 1.0)
        self.assertIsNone(report["selection"]["selected_threshold"])


if __name__ == "__main__":
    unittest.main()
