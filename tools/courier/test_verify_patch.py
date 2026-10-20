import json
import os
import subprocess
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VERIFY = os.path.join(ROOT, "tools", "courier", "verify_patch.py")


class CourierTests(unittest.TestCase):
    def test_sshsig_round_trip_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            patch = os.path.join(tmp, "change.patch")
            key = os.path.join(tmp, "courier-key")
            sig = patch + ".sig"
            with open(patch, "wb") as out:
                out.write(b"diff --git a/example b/example\n+signed courier patch\n")
            subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "",
                            "-f", key], check=True, stdout=subprocess.PIPE)
            subprocess.run(["ssh-keygen", "-q", "-Y", "sign", "-n",
                            "socaity.dev/courier", "-f", key, patch], check=True)
            os.rename(patch + ".sig", sig)
            result = subprocess.run(["python3", VERIFY, "--patch", patch,
                                     "--signature", sig, "--public-key", key + ".pub",
                                     "--format", "sshsig", "--json"],
                                    check=True, text=True, stdout=subprocess.PIPE)
            data = json.loads(result.stdout)
            self.assertTrue(data["signature_verified"])
            self.assertTrue(data["actor_id"].startswith("ssh:SHA256:"))
            with open(patch, "ab") as out:
                out.write(b"tampered\n")
            self.assertNotEqual(subprocess.run(["python3", VERIFY, "--patch", patch,
                                                "--signature", sig, "--public-key", key + ".pub",
                                                "--format", "sshsig"]).returncode, 0)


if __name__ == "__main__":
    unittest.main()
