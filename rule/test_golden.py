"""The golden vectors, and the lint that guards the arithmetic they lock in."""

import json
import os
import unittest

from rule import lint_no_float, make_vectors
from rule.distribute import canonical_bytes, distribute, table_hash
from rule.forkability import run as forkability_run
from rule.lint_no_float import lint_source

REQUIRED_MINIMUM = 10          # socaity-x8o §6: ">= 10 golden vectors"


class TestGoldenVectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vectors = make_vectors.load_all()

    def test_at_least_ten_vectors_are_committed(self):
        self.assertGreaterEqual(len(self.vectors), REQUIRED_MINIMUM)

    def test_index_matches_the_directory(self):
        with open(os.path.join(make_vectors.VECTOR_DIR, "index.json"),
                  "r", encoding="utf-8") as handle:
            index = json.load(handle)
        self.assertEqual(index["count"], len(self.vectors))
        self.assertEqual(index["vectors"], [name for name, _ in self.vectors])

    def test_every_vector_reproduces_byte_for_byte(self):
        for name, vector in self.vectors:
            with self.subTest(vector=name):
                table = distribute(vector["request"])
                self.assertEqual(canonical_bytes(table),
                                 canonical_bytes(vector["expected"]["table"]))
                self.assertEqual(table_hash(table),
                                 vector["expected"]["table_hash"])

    def test_vector_files_are_themselves_canonical(self):
        # A vector that is not in canonical form would let two clones disagree
        # about what the fixture even says.
        for name, vector in self.vectors:
            with self.subTest(vector=name):
                path = os.path.join(make_vectors.VECTOR_DIR, name)
                with open(path, "rb") as handle:
                    raw = handle.read()
                self.assertEqual(raw, canonical_bytes(vector) + b"\n")

    def test_the_named_edge_cases_are_all_present(self):
        names = " ".join(name for name, _ in self.vectors)
        for required in ("single-contributor", "zero-weight-epoch",
                         "all-challenged", "remainder-tie", "founder",
                         "empty-ledger", "unclaimed-escrow"):
            self.assertIn(required, names)

    def test_forkability_driver_passes(self):
        self.assertEqual(forkability_run(report=lambda _line: None), [])


class TestNoFloatLint(unittest.TestCase):
    def kinds(self, source):
        return {finding.kind for finding in
                lint_source(source, "<test>", lint_no_float.CORE_IMPORTS)}

    def test_the_real_package_is_clean(self):
        self.assertEqual(lint_no_float.lint_paths(
            [os.path.dirname(os.path.abspath(lint_no_float.__file__))]), [])

    def test_float_literal_is_caught(self):
        self.assertIn("float_literal", self.kinds("x = 0" + ".5\n"))

    def test_true_division_is_caught(self):
        self.assertIn("float_op", self.kinds("x = a / b\n"))
        self.assertIn("float_op", self.kinds("x = 1\nx /= 2\n"))

    def test_float_builtins_are_caught(self):
        self.assertIn("float_name", self.kinds("x = float(a)\n"))
        self.assertIn("float_name", self.kinds("x = round(a)\n"))
        self.assertIn("float_name", self.kinds("x = math.sqrt(a)\n"))

    def test_negative_exponent_is_caught(self):
        self.assertIn("negative_pow", self.kinds("x = a ** -1\n"))

    def test_io_and_clock_imports_are_caught_in_core(self):
        for source in ("import os\n", "import time\n", "import random\n",
                       "from datetime import date\n", "import requests\n"):
            self.assertIn("banned_import", self.kinds(source), source)

    def test_exact_arithmetic_passes(self):
        source = ("from fractions import Fraction\n"
                  "def f(a, b):\n"
                  "    return Fraction(a, b) * Fraction(2, 3) + Fraction(1, 1)\n")
        self.assertEqual(self.kinds(source), set())

    def test_only_the_linter_itself_is_exempt(self):
        self.assertEqual(lint_no_float.SELF_EXEMPT, ("lint_no_float.py",))


if __name__ == "__main__":
    unittest.main()
