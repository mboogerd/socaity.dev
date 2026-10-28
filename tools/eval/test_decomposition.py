import unittest

from decomposition import score_case, variance


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


if __name__ == "__main__":
    unittest.main()
