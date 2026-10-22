#!/usr/bin/env python3
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import checkpoint_cadence  # noqa: E402


def event(etype, ts=100):
    return {"type": etype, "ts": ts}


class CheckpointCadenceTests(unittest.TestCase):
    def test_mandatory_event_must_be_followed_immediately(self):
        with self.assertRaisesRegex(checkpoint_cadence.CadenceError, "epoch.opened"):
            checkpoint_cadence.check_events([event("epoch.opened"), event("work.logged")])

    def test_mandatory_event_may_be_followed_by_checkpoint(self):
        checkpoint_cadence.check_events([
            event("epoch.opened"), event("checkpoint.published"),
            event("work.logged"), event("audit.completed"),
            event("checkpoint.published"),
        ])

    def test_event_limit_is_enforced(self):
        with self.assertRaisesRegex(checkpoint_cadence.CadenceError, "maximum 2"):
            checkpoint_cadence.check_events(
                [event("work.logged"), event("work.logged"), event("work.logged")],
                max_events=2)

    def test_time_limit_is_enforced(self):
        with self.assertRaisesRegex(checkpoint_cadence.CadenceError, "maximum 10"):
            checkpoint_cadence.check_events(
                [event("work.logged", 100), event("work.logged", 111)],
                max_seconds=10)


if __name__ == "__main__":
    unittest.main()
