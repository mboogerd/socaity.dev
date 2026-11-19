"""Verify a failed infrastructure check cannot be mistaken for a usable slot."""

import unittest
from pathlib import Path
from unittest.mock import patch

import preflight


class PreflightTests(unittest.TestCase):
    @patch("preflight.executable", side_effect=lambda name: name)
    @patch("preflight.run")
    def test_sync_failure_stops_before_fetch_or_github(self, run, executable):
        run.side_effect = ["https://github.com/mboogerd/socaity.dev.git\n",
                           RuntimeError("DNS unavailable")]
        with self.assertRaisesRegex(RuntimeError, "DNS unavailable"):
            preflight.preflight(Path("/tmp"))
        self.assertEqual(run.call_count, 2)

    @patch("preflight.executable", side_effect=lambda name: name)
    @patch("preflight.run")
    def test_read_only_github_account_is_rejected(self, run, executable):
        run.side_effect = ["https://github.com/mboogerd/socaity.dev.git\n", "", "",
                           '{"viewerPermission":"READ"}']
        with self.assertRaisesRegex(RuntimeError, "lacks branch/PR write access"):
            preflight.preflight(Path("/tmp"))

    @patch("preflight.executable", side_effect=lambda name: name)
    @patch("preflight.run")
    def test_wrong_repository_has_no_sync_side_effect(self, run, executable):
        run.return_value = "https://github.com/someone/other.git\n"
        with self.assertRaisesRegex(RuntimeError, "Unexpected origin"):
            preflight.preflight(Path("/tmp"))
        self.assertEqual(run.call_count, 1)


if __name__ == "__main__":
    unittest.main()
