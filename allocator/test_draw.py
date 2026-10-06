# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 MacBoo

import unittest

from allocator.draw import DrawError, draw_project


class TestDraw(unittest.TestCase):
    WEIGHTS = {"socaity.dev": "0.6", "glass-factory": "0.4"}

    def test_spillover_renormalizes_all_but_one_starved(self):
        decision = draw_project(self.WEIGHTS, {"glass-factory"}, seed=1)
        self.assertEqual(decision.project, "glass-factory")
        self.assertEqual(decision.starved, ("socaity.dev",))
        self.assertEqual(decision.as_record()["starved"], ["socaity.dev"])

    def test_seeded_draw_is_repeatable(self):
        first = draw_project(self.WEIGHTS, self.WEIGHTS, seed=7)
        second = draw_project(self.WEIGHTS, self.WEIGHTS, seed=7)
        self.assertEqual(first, second)

    def test_cap_hit_produces_no_draw(self):
        decision = draw_project(self.WEIGHTS, self.WEIGHTS, seed=7,
                                spent_hours="10", monthly_cap="10")
        self.assertIsNone(decision.project)
        self.assertTrue(decision.cap_hit)
        self.assertEqual(decision.starved, ())

    def test_no_ready_work_is_reported(self):
        decision = draw_project(self.WEIGHTS, set(), seed=7)
        self.assertIsNone(decision.project)
        self.assertEqual(decision.reason, "no-ready-work")
        self.assertEqual(decision.starved, tuple(self.WEIGHTS))

    def test_rejects_invalid_draw_inputs(self):
        with self.assertRaises(DrawError):
            draw_project({"a": 0}, {"a"}, seed=1)
        with self.assertRaises(DrawError):
            draw_project(self.WEIGHTS, {"a"}, seed=1, spent_hours=-1, monthly_cap=10)


if __name__ == "__main__":
    unittest.main()
