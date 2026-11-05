import hashlib
import os
import tempfile
import unittest

from ledger.example.seed import build
from tools import checkpoint


class CheckpointToolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = os.path.join(self.tmp.name, "chain.jsonl")
        self.artifact = os.path.join(self.tmp.name, "checkpoint.json")
        build(self.ledger)

    def tearDown(self):
        self.tmp.cleanup()

    def test_export_and_verify(self):
        artifact = checkpoint.export_checkpoint(self.ledger)
        with open(self.artifact, "w", encoding="utf-8") as handle:
            handle.write(checkpoint.canonical.canonicalize(artifact).decode() + "\n")
        verified = checkpoint.verify_checkpoint(self.ledger, self.artifact)
        self.assertEqual(verified["checkpoint_event"]["type"], "checkpoint.published")
        self.assertEqual(verified["ledger_event_count"], 28)

    def test_tampered_ledger_digest_is_rejected(self):
        artifact = checkpoint.export_checkpoint(self.ledger)
        artifact["ledger_sha256"] = hashlib.sha256(b"tampered").hexdigest()
        with open(self.artifact, "w", encoding="utf-8") as handle:
            handle.write(checkpoint.canonical.canonicalize(artifact).decode() + "\n")
        with self.assertRaisesRegex(ValueError, "ledger_sha256"):
            checkpoint.verify_checkpoint(self.ledger, self.artifact)

    def test_no_checkpoint_is_rejected(self):
        path = os.path.join(self.tmp.name, "empty.jsonl")
        open(path, "w", encoding="utf-8").close()
        with self.assertRaisesRegex(ValueError, "no checkpoint"):
            checkpoint.export_checkpoint(path)


if __name__ == "__main__":
    unittest.main()
