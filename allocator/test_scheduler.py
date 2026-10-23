import datetime
import tempfile
import unittest
from pathlib import Path

from allocator.scheduler import Scheduler


ROOT = Path(__file__).parents[1]


class TestSchedulerAcceptance(unittest.TestCase):
    def test_two_machines_three_projects_spillover_and_cap(self):
        with tempfile.TemporaryDirectory() as directory:
            scheduler = Scheduler.from_files(
                ROOT / "projects.yaml", ROOT / "allocation.yaml",
                Path(directory) / "spend.jsonl",
            )
            start = datetime.datetime(2026, 10, 1, tzinfo=datetime.timezone.utc)
            ticks = iter(start + datetime.timedelta(hours=index)
                         for index in range(20))
            ready = {"socaity.dev", "glass-factory", "computenet"}
            executed = []

            def next_item(project):
                return f"{project}-item"

            def run(project, item):
                executed.append((project, item))

            for machine, seed in (("mac-1", 1), ("mac-2", 2)):
                scheduler.slot(machine, seed, ready, next_item, run, clock=lambda: next(ticks))

            # Emptying one backlog spills its declared weight to the others.
            decision = scheduler.slot(
                "mac-1", 3, {"glass-factory", "computenet"}, next_item, run,
                clock=lambda: next(ticks),
            )
            self.assertEqual(decision.starved, ("socaity.dev",))
            self.assertEqual(len(executed), 3)

            # The hard cap is checked before a draw; no work is started at it.
            stopped = scheduler.slot(
                "mac-2", 4, ready, next_item, run,
                spent_hours=40, clock=lambda: next(ticks),
            )
            self.assertTrue(stopped.cap_hit)
            self.assertEqual(len(executed), 3)

            records = list(scheduler.log.records())
            self.assertEqual(len(records), 3)
            self.assertEqual(records[-1]["starved"], ["socaity.dev"])


if __name__ == "__main__":
    unittest.main()
