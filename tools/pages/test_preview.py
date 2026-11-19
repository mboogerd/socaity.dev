from pathlib import Path
import tempfile
import unittest

from preview import prepare_preview


class PreviewTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.site = self.root / "site"
        self.site.mkdir()
        (self.site / "index.html").write_text("Candidate", encoding="utf-8")
        (self.site / "blog").mkdir()
        (self.site / "blog/index.html").write_text("Blog", encoding="utf-8")
        self.host = self.root / "host"
        self.host.mkdir()
        self.revision = "a" * 40

    def test_preview_preserves_bytes_and_prior_revisions(self):
        prepare_preview(self.site, self.host, self.revision)
        first = self.host / "revisions" / self.revision
        self.assertEqual((first / "index.html").read_bytes(), b"Candidate")
        self.assertEqual((first / "blog/index.html").read_bytes(), b"Blog")
        prepare_preview(self.site, self.host, self.revision)
        (self.site / "index.html").write_text("Next candidate", encoding="utf-8")
        prepare_preview(self.site, self.host, "b" * 40)
        self.assertEqual((first / "index.html").read_bytes(), b"Candidate")
        self.assertIn("b" * 40, (self.host / "index.html").read_text())
        self.assertTrue((self.host / ".nojekyll").exists())
        self.assertIn("Disallow: /", (self.host / "robots.txt").read_text())

    def test_revision_cannot_be_overwritten(self):
        prepare_preview(self.site, self.host, self.revision)
        (self.site / "index.html").write_text("Changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "different bytes"):
            prepare_preview(self.site, self.host, self.revision)

    def test_invalid_revision_and_symlink_cannot_escape_tree(self):
        with self.assertRaises(ValueError):
            prepare_preview(self.site, self.host, "../../outside")
        (self.site / "external").symlink_to(self.host)
        with self.assertRaisesRegex(ValueError, "symbolic links"):
            prepare_preview(self.site, self.host, self.revision)
        self.assertFalse((self.host / "revisions").exists())


if __name__ == "__main__":
    unittest.main()
