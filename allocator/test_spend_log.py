# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 MacBoo

import datetime
import json
import tempfile
import threading
import unittest
from pathlib import Path

from allocator.session import Session, run_session
from allocator.spend_log import SpendLog, ValidationError, validate_record


START = datetime.datetime(2026, 9, 30, 10, 0, tzinfo=datetime.timezone.utc)


class TestSpendLog(unittest.TestCase):
    def test_session_records_success_and_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            log = SpendLog(Path(directory) / "spend.jsonl")
            ticks = iter((START, START + datetime.timedelta(seconds=3),
                          START + datetime.timedelta(seconds=8),
                          START + datetime.timedelta(seconds=13)))
            clock = lambda: next(ticks)
            self.assertEqual(run_session(log, "socaity.dev", "mac-1", "socaity-1", lambda: 42,
                                         clock), 42)
            with self.assertRaisesRegex(RuntimeError, "worker failed"):
                run_session(log, "glass-factory", "mac-2", "gf-7",
                            lambda: (_ for _ in ()).throw(RuntimeError("worker failed")), clock)
            records = list(log.records())
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]["v"], 1)
            self.assertEqual(records[1]["project"], "glass-factory")
            self.assertEqual(records[1]["started"], "2026-09-30T10:00:08.000000Z")

    def test_concurrent_appends_are_complete_records(self):
        with tempfile.TemporaryDirectory() as directory:
            log = SpendLog(Path(directory) / "spend.jsonl")
            barrier = threading.Barrier(20)

            def append(index):
                barrier.wait()
                log.append({"v": 1, "project": "p", "machine": f"m-{index}",
                            "work_item": f"w-{index}", "started": "2026-09-30T00:00:00.000000Z",
                            "ended": "2026-09-30T00:00:01.000000Z"})

            threads = [threading.Thread(target=append, args=(index,)) for index in range(20)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            records = list(log.records())
            self.assertEqual(len(records), 20)
            self.assertEqual({record["machine"] for record in records}, {f"m-{i}" for i in range(20)})

    def test_validator_rejects_malformed_record(self):
        valid = {"v": 1, "project": "p", "machine": "m", "work_item": "w",
                 "started": "2026-09-30T00:00:00.000000Z", "ended": "2026-09-30T00:00:01.000000Z"}
        for field, value in (("v", 2), ("project", ""), ("ended", "2026-09-29T00:00:01.000000Z")):
            candidate = dict(valid)
            candidate[field] = value
            with self.assertRaises(ValidationError):
                validate_record(candidate)

    def test_invalid_jsonl_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spend.jsonl"
            path.write_text("not json\n", encoding="utf-8")
            with self.assertRaises(ValidationError):
                list(SpendLog(path).records())


if __name__ == "__main__":
    unittest.main()
