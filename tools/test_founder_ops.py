import hashlib
import contextlib
import io
import json
import os
import tempfile
import unittest

from ledger import crypto
from ledger.example.seed import build
from tools import founder_ops


FOUNDER = hashlib.sha256(b"socaity founder test").digest()
class FounderOpsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.chain = os.path.join(self.tmp.name, "chain.jsonl")
        # The fixture has a known checkpoint key, so use its published secret
        # for checkpoint tests and a regular key for an ordinary append.
        build(self.chain)
        self.checkpoint_secret = hashlib.sha256(
            b"socaity.dev EXAMPLE checkpoint key -- not a real key").digest()
        self.secret_path = os.path.join(self.tmp.name, "secret")
        with open(self.secret_path, "wb") as handle:
            handle.write(FOUNDER.hex().encode("ascii"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_verify_replays_and_reports_chain(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            founder_ops.main(["verify", "--ledger", self.chain])
        result = json.loads(output.getvalue())
        self.assertTrue(result["valid"])
        self.assertGreater(result["count"], 0)

    def test_checkpoint_derives_head_and_sequence(self):
        path = os.path.join(self.tmp.name, "checkpoint-secret")
        with open(path, "wb") as handle:
            handle.write(self.checkpoint_secret)
        founder_ops.main(["checkpoint", "--ledger", self.chain,
                          "--secret-file", path, "--ts", "1786622400"])
        from ledger.log import EventLog
        log = EventLog(self.chain)
        self.assertEqual(log.ledger.checkpoint_seq, 5)
        self.assertEqual(log.count, 29)

    def test_append_rejects_payload_outside_catalog(self):
        with self.assertRaises(SystemExit):
            founder_ops.main(["append", "--ledger", self.chain,
                              "--secret-file", self.secret_path,
                              "--type", "commitment.precommitted",
                              "--payload", json.dumps({"wrong": "field"}),
                              "--ts", "1786622400"])


if __name__ == "__main__":
    unittest.main()
