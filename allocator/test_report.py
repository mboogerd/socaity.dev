# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 MacBoo

import datetime
import subprocess
import tempfile
import unittest
from pathlib import Path

from allocator.report import render_report, replay
from allocator.spend_log import SpendLog


class TestReport(unittest.TestCase):
    def test_replay_uses_committed_weights_and_explains_starvation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
            (root / "allocation.yaml").write_text(
                "schema: 1\nwindow: monthly\nmonthly_cap:\n  hours: 10\n"
                "weights:\n  a: 0.6\n  b: 0.4\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "allocation.yaml"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "allocation"], check=True)
            log = SpendLog(root / "spend.jsonl")
            log.append({"v": 1, "project": "b", "machine": "m", "work_item": "w",
                        "started": "2099-01-02T00:00:00.000000Z",
                        "ended": "2099-01-02T01:00:00.000000Z",
                        "starved": ["a"]})
            data = replay(root, root / "spend.jsonl",
                          at=datetime.datetime(2099, 1, 2, 2, tzinfo=datetime.timezone.utc))
            self.assertEqual(data["hours"], "1.00")
            self.assertEqual(data["projects"]["b"]["enacted_share"], "1.00")
            self.assertEqual(data["projects"]["a"]["starvation_events"], 1)
            self.assertIn("Starvation", render_report(data))


if __name__ == "__main__":
    unittest.main()
