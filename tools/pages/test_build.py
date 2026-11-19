"""Exercise the published blog tree, not just the Markdown parser."""
from pathlib import Path
import tempfile
import unittest
from xml.etree import ElementTree as ET

from build import assemble


class BlogBuildTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.archive = self.root / "research"
        self.archive.mkdir()
        (self.archive / "index.html").write_text("<h1>Research</h1>", encoding="utf-8")
        # Even a stale render must not bring the removed blog back.
        stale = self.archive / "blog/old-post"
        stale.mkdir(parents=True)
        (stale / "index.html").write_text("Old post", encoding="utf-8")
        self.posts = self.root / "blog"
        self.posts.mkdir()
        self.output = self.root / "published"

    def post(self, slug, entry, content):
        folder = self.posts / slug
        folder.mkdir()
        (folder / entry).write_text(content, encoding="utf-8")
        return folder

    def build(self, output=None):
        assemble(self.archive, output or self.output, self.posts,
                 "https://example.org/socaity/")

    def test_markdown_html_and_accompanying_assets(self):
        markdown = self.post("first-post", "index.md", """# First post

Hello **world**. ![Diagram](./images/diagram.svg)

| Name | Value |
| --- | --- |
| A | 1 |

```python
print('<hello>')
```
""")
        (markdown / "images").mkdir()
        (markdown / "images/diagram.svg").write_text("<svg/>", encoding="utf-8")
        (markdown / "article.yml").write_text(
            "date: 2026-11-19\nsummary: A first article.\n", encoding="utf-8")
        (markdown / ".private").write_text("not public", encoding="utf-8")
        # 'posts' is a normal slug; no legacy front-matter parser may claim it.
        raw = '<!doctype html><html><head><title>Custom page</title></head><body><link rel="stylesheet" href="./custom.css">Hello</body></html>'
        html = self.post("posts", "index.html", raw)
        (html / "custom.css").write_text("body { color: red; }", encoding="utf-8")
        self.build()

        published = self.output / "blog"
        rendered = (published / "first-post/index.html").read_text()
        self.assertIn("<strong>world</strong>", rendered)
        self.assertIn("<table>", rendered)
        self.assertIn("&lt;hello&gt;", rendered)
        self.assertIn('src="./images/diagram.svg"', rendered)
        self.assertIn('href="../../styles.css"', rendered)
        self.assertEqual(rendered.count("<h1>"), 1)
        self.assertEqual((published / "posts/index.html").read_text(), raw)
        for path in ("first-post/images/diagram.svg", "posts/custom.css"):
            self.assertEqual((published / path).read_bytes(), (self.posts / path).read_bytes())
        for path in ("first-post/index.md", "first-post/article.yml", "first-post/.private", "old-post"):
            self.assertFalse((published / path).exists(), path)
        index = (published / "index.html").read_text()
        self.assertIn('href="first-post/"', index)
        self.assertIn('href="posts/"', index)
        self.assertIn("Custom page", index)
        items = ET.parse(published / "feed.xml").findall("./channel/item")
        self.assertEqual([item.findtext("title") for item in items], ["First post", "Custom page"])
        self.assertEqual(items[0].findtext("link"), "https://example.org/socaity/blog/first-post/")
        self.assertEqual(items[0].findtext("description"), "A first article.")
        self.assertEqual((self.output / "research.html").read_text(), "<h1>Research</h1>")

    def test_empty_blog_is_valid(self):
        (self.posts / "README.md").write_text("Authoring instructions", encoding="utf-8")
        self.build()
        self.assertEqual({path.name for path in (self.output / "blog").iterdir()},
                         {"index.html", "feed.xml", "blog.css"})
        self.assertEqual(ET.parse(self.output / "blog/feed.xml").findall("./channel/item"), [])

    def test_invalid_posts_fail_without_partial_output(self):
        for slug, entries in (("both", ("index.md", "index.html")),
                              ("missing", ("notes.md",)),
                              ("Bad Slug", ("index.md",))):
            with self.subTest(slug=slug):
                folder = self.posts / slug
                folder.mkdir()
                for name in entries:
                    (folder / name).write_text("Content", encoding="utf-8")
                with self.assertRaises(ValueError):
                    self.build()
                self.assertFalse(self.output.exists())
                for entry in folder.iterdir():
                    entry.unlink()
                folder.rmdir()

    def test_symlinked_assets_are_rejected(self):
        folder = self.post("example", "index.md", "# Example")
        (folder / "linked.txt").symlink_to(self.archive / "index.html")
        with self.assertRaisesRegex(ValueError, "symbolic links"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_build_is_deterministic(self):
        self.post("example", "index.md", "# Example\n\nAn article.")
        self.build()
        second = self.root / "second"
        self.build(second)
        def files(root):
            return {path.relative_to(root): path.read_bytes()
                    for path in root.rglob("*") if path.is_file()}
        self.assertEqual(files(self.output), files(second))


if __name__ == "__main__":
    unittest.main()
