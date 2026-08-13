#!/usr/bin/env python3
"""Adversarial tests for the CI gates — socaity-ddi.

A gate is only worth its green tick if someone has tried to get past it. Every
case here is a bypass that worked at some point, kept as a test so it cannot
come back:

  * miniyaml against PyYAML.  A hand-rolled parser that reads the graph
    differently than the renderer does is worse than no gate; the tab-indent
    case silently emptied `edges:` and disarmed the whole dispute check.
  * vocab_gate against a banned word hidden in markup.  Split across a tag,
    wrapped over a line, spelled with a Cyrillic homoglyph, padded with a
    zero-width space, or sitting in the JSON export instead of the page.
  * the waiver mechanism, which is the gate's only unlocked door.

PyYAML is optional: the differential cases skip without it, so this file still
runs on the cold checkout the gates are designed for.

Usage:  python3 tools/gates/test_gates.py
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import miniyaml            # noqa: E402
import vocab_gate          # noqa: E402

try:
    import yaml
except ImportError:
    yaml = None

WORDLIST = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "doc", "standards", "banned-words.txt")


# ---------------------------------------------------------------------------
# miniyaml
# ---------------------------------------------------------------------------
AGREE = [
    "id: n-1\ntitle: hello\n",
    "a:\n  b: 1\n  c: two\n",
    "xs:\n  - a\n  - b\n",
    "xs:\n- a\n- b\n",
    "edges:\n  - id: e1\n    status: asserted\n  - id: e2\n    status: disputed\n",
    'title: "a: b"\n',
    "title: 'a: b'\n",
    "url: https://example.com/x\n",
    "hashes:\n  - sha256:abcd\n",
    "text: |\n  line one\n  line two\n",
    "text: |-\n  one\n  two\n",
    "text: >\n  one\n  two\n",
    "xs: []\n",
    "xs: {}\n",
    "x:\n",
    "x: null\n",
    "x: ~\n",
    "a: true\nb: false\n",
    "a: yes\nb: no\n",
    "a: on\nb: off\n",
    "a: 42\nb: -3.5\n",
    "a: 1  # note\n",
    "a: red#blue\n",
    'a: "red # blue"\n',
    "title: naïve — ünïcode ✓\n",
    "edges:\n  - id: e1\n    tags:\n      - x\n      - y\n",
    "a:\n  b:\n    c:\n      d: 1\n",
    "---\na: 1\n",
    "some-key: 1\n",
    'a: ""\n',
    "a: 1\n\n\nb: 2\n",
    "xs:\n  - a\nys: 1\n",
    "a:\n    b: 1\n",
    "t: |\n  one\n\n  two\n",
    "t: |\n  one\n  # two\n  three\n",
    "a: 50%\n",
    "a: --flag\n",
    "e:\n  - id: 1\n    m:\n      k: v\n  - id: 2\n",
    "id: n-x\nedges:\n  - id: e1\n    status: disputed\n    dispute_ref:\n"
    "      kind: pr\n      repo: o/r\n      number: 12\n      url: https://x/1\n",
    "id: n-x\nnote: |\n  edges:\n    - id: fake\n      status: settled\n"
    "edges:\n  - id: real\n    status: disputed\n",
]

# Outside the subset. Each must raise — never be parsed into something the
# renderer would read differently.
LOUD = [
    ("tab indentation", "a:\n\tb: 1\n"),
    ("tab-indented edge block", "id: n\nedges:\n\t- id: e1\n\t  status: disputed\n"),
    ("anchor", "base: &b\n  x: 1\nother: *b\n"),
    ("alias", "a: *ref\n"),
    ("multi-line plain scalar", "a: one\n  two\n"),
    ("flow sequence", "xs: [a, b]\n"),
    ("flow mapping", "xs: {a: 1}\n"),
    ("flow edges", "edges: [ {id: e1, status: disputed} ]\n"),
    ("nested flow sequence", "a:\n  - - x\n    - y\n"),
    ("multi-document", "a: 1\n---\nb: 2\n"),
    ("leading-zero integer", "a: 0012\n"),
]


class MiniYAMLDifferential(unittest.TestCase):
    """The gate and the renderer must read the same tree, or agree to stop."""

    @unittest.skipIf(yaml is None, "PyYAML not installed")
    def test_agrees_with_pyyaml(self):
        for source in AGREE:
            with self.subTest(source=source):
                self.assertEqual(miniyaml.loads(source), yaml.safe_load(source))

    def test_outside_the_subset_raises(self):
        for name, source in LOUD:
            with self.subTest(name=name):
                with self.assertRaises(miniyaml.YAMLSubsetError):
                    miniyaml.loads(source)

    def test_tab_indent_does_not_empty_a_disputed_edge(self):
        # The regression that matters: this used to parse as
        # {'edges': [{'id': 'e1'}], 'status': 'disputed'} — a disputed edge with
        # no status, which D2/D3/D4 all skip.
        with self.assertRaises(miniyaml.YAMLSubsetError) as caught:
            miniyaml.loads("id: n\nedges:\n\t- id: e1\n\t  status: disputed\n")
        self.assertIn("TAB", str(caught.exception))

    def test_block_scalar_keeps_blank_and_hash_lines(self):
        parsed = miniyaml.loads("t: |\n  one\n\n  # two\n  three\n")
        self.assertEqual(parsed["t"], "one\n\n# two\nthree\n")

    @unittest.skipIf(yaml is None, "PyYAML not installed")
    def test_every_real_graph_file_matches_pyyaml(self):
        root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
        graph = os.path.join(root, "graph")
        seen = 0
        for dirpath, _dirs, names in os.walk(graph):
            for name in sorted(names):
                if not name.endswith((".yaml", ".yml")):
                    continue
                path = os.path.join(dirpath, name)
                with self.subTest(path=path):
                    with open(path, encoding="utf-8") as handle:
                        raw = handle.read()
                    self.assertEqual(miniyaml.loads(raw), yaml.safe_load(raw))
                seen += 1
        self.assertGreater(seen, 0, "no graph files were compared")


# ---------------------------------------------------------------------------
# vocab gate
# ---------------------------------------------------------------------------
class VocabBypass(unittest.TestCase):
    """Every one of these hid a banned word from the gate at some point."""

    def setUp(self):
        self.patterns = vocab_gate.load_wordlist(WORDLIST)
        self.root = tempfile.mkdtemp()

    def scan(self, rel, body):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(body)
        hits, _text = vocab_gate.scan_file(self.root, rel, self.patterns)
        return {(h[3].lower(), bool(h[4])) for h in hits}

    def assertCaught(self, rel, body, word):
        found = {matched for matched, _waived in self.scan(rel, body)}
        self.assertTrue(any(word in matched for matched in found),
                        "%s did not catch %r; saw %s" % (rel, word, sorted(found)))

    def test_split_across_a_tag_boundary(self):
        self.assertCaught("site/a.html", "<p>wall<span>et</span> here</p>\n", "wallet")

    def test_wrapped_across_a_line(self):
        self.assertCaught("site/b.html", "<p>you can earn\ncredits today</p>\n",
                          "earn credit")

    def test_hyphenated_across_a_line(self):
        self.assertCaught("site/c.html", "<p>token-\nomics explained</p>\n", "tokenomics")

    def test_cyrillic_homoglyph(self):
        self.assertCaught("site/d.html", "<p>your w\u0430llet</p>\n", "wallet")

    def test_zero_width_space(self):
        self.assertCaught("site/e.html", "<p>wal\u200blet</p>\n", "wallet")

    def test_alt_text(self):
        self.assertCaught("site/f.html", '<img alt="buy our token now">\n', "our token")

    def test_title_element(self):
        self.assertCaught("site/g.html", "<head><title>airdrop</title></head>\n",
                          "airdrop")

    def test_open_graph_meta(self):
        self.assertCaught("site/h.html",
                          '<meta property="og:description" content="tokenomics">\n',
                          "tokenomics")

    def test_placeholder_attribute(self):
        self.assertCaught("site/i.html", '<input placeholder="your wallet">\n', "wallet")

    def test_json_ld_metadata(self):
        self.assertCaught(
            "site/j.html",
            '<script type="application/ld+json">{"description":"airdrop"}</script>\n',
            "airdrop")

    def test_code_block(self):
        self.assertCaught("site/k.html", "<pre><code>airdrop</code></pre>\n", "airdrop")

    def test_rss_feed(self):
        self.assertCaught("site/feed.xml",
                          "<rss><channel><item><title>tokenomics</title>"
                          "</item></channel></rss>\n", "tokenomics")

    def test_graph_json_export(self):
        self.assertCaught("site/graph.json",
                          '{"nodes":[{"title":"the wallet problem"}]}\n', "wallet")

    def test_a_clean_page_is_clean(self):
        self.assertEqual(self.scan("site/ok.html",
                                   "<p>The record is a database.</p>\n"), set())

    def test_window_does_not_borrow_the_next_lines_hit(self):
        # Line 1 is clean; only line 2 may be reported, for its own word.
        lines = self.scan("site/w.html", "<p>a clean line</p>\n<p>airdrop</p>\n")
        self.assertEqual({m for m, _ in lines}, {"airdrop"})


class VocabWaiver(unittest.TestCase):
    """The waiver is the only unlocked door in the gate; it must need a key."""

    setUp = VocabBypass.setUp
    scan = VocabBypass.scan

    def waived(self, rel, body):
        return {matched for matched, is_waived in self.scan(rel, body) if is_waived}

    def test_empty_reason_waives_nothing(self):
        self.assertEqual(self.waived("blog/a.md", "the token <!-- vocab-ok: -->\n"),
                         set())

    def test_punctuation_reason_waives_nothing(self):
        self.assertEqual(self.waived("blog/b.md", "the token <!-- vocab-ok: - -->\n"),
                         set())

    def test_prose_mentioning_the_marker_waives_nothing(self):
        self.assertEqual(
            self.waived("blog/c.md",
                        "see vocab-ok: notes for why we avoid the token\n"), set())

    def test_a_real_reason_waives_its_own_line(self):
        self.assertEqual(
            self.waived("blog/d.md",
                        "the token <!-- vocab-ok: quoted objection, answered below -->\n"),
            {"the token"})

    def test_a_waiver_does_not_reach_an_unrelated_next_line(self):
        body = ("clean <!-- vocab-ok: quoted objection, answered below -->\n"
                "an unrelated sentence about investors\n")
        self.assertEqual(self.waived("blog/e.md", body), set())

    def test_a_waiver_still_covers_a_phrase_that_wraps(self):
        body = ('<p>you can earn <!-- vocab-ok: quoted objection, answered below -->\n'
                'credits today</p>\n')
        self.assertIn("earn credit",
                      " ".join(self.waived("site/f.html", body)) or "")

    def test_json_export_cannot_be_waived(self):
        self.assertEqual(
            self.waived("site/graph.json",
                        '{"a":"the token","b":"vocab-ok: nice try indeed"}\n'), set())


if __name__ == "__main__":
    unittest.main(verbosity=2)
