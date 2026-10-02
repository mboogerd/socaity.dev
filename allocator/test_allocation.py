# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 MacBoo

import unittest

from allocator.allocation import AllocationError, validate_allocation


VALID = {
    "schema": 1,
    "window": "monthly",
    "monthly_cap": {"hours": 40},
    "weights": {"socaity.dev": "0.5", "glass-factory": "0.3", "computenet": "0.2"},
}


class TestAllocation(unittest.TestCase):
    def test_validates_declared_three_project_weights(self):
        checked = validate_allocation(VALID)
        self.assertEqual(checked["weights"]["socaity.dev"], "0.5")
        self.assertEqual(checked["monthly_cap"]["hours"], "40")

    def test_rejects_weights_that_do_not_sum_to_one(self):
        candidate = {**VALID, "weights": {"a": "0.5", "b": "0.49"}}
        with self.assertRaisesRegex(AllocationError, "sum exactly to 1"):
            validate_allocation(candidate)

    def test_rejects_missing_or_non_positive_cap(self):
        for cap in ({}, {"hours": 0}, {"hours": -1}):
            candidate = {**VALID, "monthly_cap": cap}
            with self.assertRaises(AllocationError):
                validate_allocation(candidate)


if __name__ == "__main__":
    unittest.main()
