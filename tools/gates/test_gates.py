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
  * html_gate against an off-origin subresource — script, CDN stylesheet,
    @import, url(), srcset candidate, protocol-relative host — and against
    the opposite error, flagging the outbound GitHub <a href> the dispute and
    provenance links depend on; plus an orphan page, and an orphan hidden
    behind a redirect stub.

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
import html_gate           # noqa: E402
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


# ---------------------------------------------------------------------------
# html gate
# ---------------------------------------------------------------------------
class HtmlGateSubresources(unittest.TestCase):
    """Check A: every off-origin fetch caught, every outbound link left alone.

    The second half matters as much as the first. `<a href>` to GitHub is how
    a dispute, an edit and a provenance record are reached; a gate that failed
    those would be switched off in a week and check A would be gone with it.
    """

    def scan(self, body, css=None):
        root = tempfile.mkdtemp()
        os.makedirs(os.path.join(root, "site"))
        with open(os.path.join(root, "site", "index.html"), "w",
                  encoding="utf-8") as handle:
            handle.write(body)
        if css is not None:
            with open(os.path.join(root, "site", "style.css"), "w",
                      encoding="utf-8") as handle:
                handle.write(css)
        pages, sheets = html_gate.load(os.path.join(root, "site"))
        return [why for _rel, _line, _rule, why
                in html_gate.check_off_origin(pages, sheets, root)]

    def assertFlagged(self, body, css=None):
        found = self.scan(body, css)
        self.assertTrue(found, "off-origin subresource not caught")

    def assertClean(self, body, css=None):
        self.assertEqual(self.scan(body, css), [])

    def test_off_origin_script(self):
        self.assertFlagged('<script src="https://cdn.example/a.js"></script>')

    def test_protocol_relative_script(self):
        self.assertFlagged('<script src="//cdn.example/a.js"></script>')

    def test_cdn_stylesheet(self):
        self.assertFlagged('<link rel="stylesheet" href="https://cdn.example/a.css">')

    def test_css_import(self):
        self.assertFlagged('<style>@import "https://fonts.example/f.css";</style>')

    def test_css_url_in_a_stylesheet(self):
        self.assertFlagged("<p>x</p>", css="body{background:url(https://i.example/b.png)}")

    def test_css_url_in_a_style_attribute(self):
        self.assertFlagged('<p style="background:url(\'https://i.example/b.png\')">x</p>')

    def test_srcset_candidate(self):
        self.assertFlagged('<img srcset="a.png 1x, https://i.example/b.png 2x" alt="">')

    def test_github_anchor_is_legal(self):
        self.assertClean('<a href="https://github.com/socaity/socaity.dev/pull/1">'
                         'the contest</a>')

    def test_off_origin_canonical_is_not_a_subresource(self):
        self.assertClean('<link rel="canonical" href="https://socaity.dev/x/">')

    def test_data_uri_is_not_a_request(self):
        self.assertClean('<img src="data:image/gif;base64,R0lGOD" alt="">')

    def test_the_sites_own_absolute_url_is_this_origin(self):
        self.assertClean('<link rel="stylesheet" href="https://socaity.dev/style.css">')

    # Bypasses found by attacking the gate after it was written (socaity-3hv).
    # Each of these got a fetch past check A once.

    def test_xlink_href_is_the_form_sprites_are_written_in(self):
        self.assertFlagged('<svg><use xlink:href="https://i.example/s.svg#a"/></svg>')
        self.assertFlagged('<svg><image xlink:href="https://i.example/a.png"/></svg>')

    def test_svg_feimage_href(self):
        self.assertFlagged('<svg><filter><feImage href="https://i.example/f.png"/>'
                           '</filter></svg>')

    def test_meta_refresh_to_another_origin(self):
        self.assertFlagged('<meta http-equiv="refresh" '
                           'content="0;url=https://elsewhere.example/">')

    def test_anchor_ping_is_a_fetch_even_though_href_is_not(self):
        self.assertFlagged('<a href="/ledger/" ping="https://track.example/p">x</a>')

    def test_legacy_background_attribute(self):
        self.assertFlagged('<body background="https://i.example/bg.png">')

    def test_off_origin_form_action(self):
        self.assertFlagged('<form action="https://collect.example/f" method="post">'
                           '<input name="a"></form>')

    def test_a_url_split_by_a_newline_the_url_parser_removes(self):
        # The URL parser strips tab/newline before it looks for a scheme.
        self.assertFlagged('<img src="ht&#10;tps://i.example/a.png" alt="">')
        self.assertFlagged('<img src="https:&#9;//i.example/b.png" alt="">')

    def test_a_css_escaped_scheme(self):
        self.assertFlagged("<p>x</p>",
                           css="body{background:url(https\\3a //i.example/c.png)}")

    def test_import_with_a_media_query(self):
        self.assertFlagged('<style>@import "https://f.example/a.css" '
                           'screen and (min-width:0);</style>')
        self.assertFlagged('<style>@import url(https://f.example/b.css) print;</style>')

    def test_preloaded_font(self):
        self.assertFlagged('<link rel="preload" as="font" crossorigin '
                           'href="https://f.example/f.woff2">')

    def test_a_host_that_only_looks_like_this_one(self):
        self.assertFlagged('<img src="https://socaity.dev.evil.example/a.png" alt="">')
        self.assertFlagged('<img src="https://socaity.dev@evil.example/a.png" alt="">')

    def test_a_document_hidden_in_an_iframe_srcdoc(self):
        self.assertFlagged('<iframe srcdoc="&lt;img src=https://i.example/a.png&gt;">'
                           '</iframe>')

    def test_media_elements(self):
        for markup in ('<iframe src="https://x.example/f"></iframe>',
                       '<embed src="https://x.example/e">',
                       '<video src="https://x.example/v.mp4"></video>',
                       '<audio src="https://x.example/a.mp3"></audio>',
                       '<video><track src="https://x.example/t.vtt"></video>',
                       '<video><source src="https://x.example/s.mp4"></video>',
                       '<object data="https://x.example/o.bin"></object>'):
            with self.subTest(markup=markup):
                self.assertFlagged(markup)


class HtmlGateOrphans(unittest.TestCase):
    """Check E: the check that makes deleting a nav item decidable (§I)."""

    def orphans(self, files):
        root = tempfile.mkdtemp()
        for rel, body in files.items():
            path = os.path.join(root, "site", rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(body)
        pages, sheets = html_gate.load(os.path.join(root, "site"))
        return sorted(rel for rel, _l, _r, _w
                      in html_gate.check_orphans(pages, sheets, root))

    def test_an_unlinked_page_is_an_orphan(self):
        self.assertEqual(
            self.orphans({"index.html": "<a href='a/'>a</a>",
                          "a/index.html": "<p>a</p>",
                          "b/index.html": "<p>nobody links here</p>"}),
            ["b/index.html"])

    def test_reachable_through_a_chain(self):
        self.assertEqual(
            self.orphans({"index.html": "<a href='a/'>a</a>",
                          "a/index.html": "<a href='../b/'>b</a>",
                          "b/index.html": "<p>b</p>"}), [])

    def test_an_off_origin_link_does_not_reach_anything(self):
        self.assertEqual(
            self.orphans({"index.html": "<a href='https://github.com/x/b/'>b</a>",
                          "b/index.html": "<p>b</p>"}), ["b/index.html"])

    def test_a_slug_alias_stub_is_not_an_orphan(self):
        self.assertEqual(
            self.orphans({"index.html": "<a href='n/x/'>node</a>",
                          "n/x/index.html": "<p>node</p>",
                          "s/name/index.html":
                              "<meta http-equiv='refresh' content='0; url=../../n/x/'>"}),
            [])

    def test_a_stub_in_front_of_an_orphan_is_still_an_orphan(self):
        self.assertEqual(
            self.orphans({"index.html": "<p>home</p>",
                          "hidden/index.html": "<p>hidden</p>",
                          "s/name/index.html":
                              "<meta http-equiv='refresh' content='0; url=../../hidden/'>"}),
            ["hidden/index.html", "s/name/index.html"])

    # The stub excuse, attacked from the other side (socaity-3hv): it must not
    # become a licence any unreachable page can buy with one <meta refresh>.

    def test_a_page_with_content_cannot_buy_the_stub_excuse(self):
        self.assertEqual(
            self.orphans({"index.html": "<a href='a/'>a</a>",
                          "a/index.html": "<p>a</p>",
                          "secret/index.html":
                              "<meta http-equiv='refresh' content='0; url=/'>"
                              "<h1>a page nobody links to</h1>"}),
            ["secret/index.html"])

    def test_a_stub_pointing_at_itself_is_not_a_stub(self):
        self.assertEqual(
            self.orphans({"index.html": "<p>home</p>",
                          "secret/index.html":
                              "<meta http-equiv='refresh' content='0; url=/secret/'>"}),
            ["secret/index.html"])

    def test_a_stub_that_also_goes_somewhere_of_its_own_is_a_page(self):
        self.assertEqual(
            self.orphans({"index.html": "<a href='n/x/'>node</a>",
                          "n/x/index.html": "<p>node</p>",
                          "s/name/index.html":
                              "<meta http-equiv='refresh' content='0; url=../../n/x/'>"
                              "<p>also see <a href='/elsewhere/'>elsewhere</a></p>",
                          "elsewhere/index.html": "<p>e</p>"}),
            ["elsewhere/index.html", "s/name/index.html"])

    def test_a_directory_link_without_its_trailing_slash_still_reaches(self):
        # The host redirects /ledger to /ledger/; the gate must not call the
        # page an orphan over one character.
        self.assertEqual(
            self.orphans({"index.html": "<a href='/ledger'>l</a>",
                          "ledger/index.html": "<p>l</p>"}), [])

    def test_a_link_carrying_a_query_string_still_reaches(self):
        self.assertEqual(
            self.orphans({"index.html": "<a href='/p/?from=home'>p</a>",
                          "p/index.html": "<p>p</p>"}), [])

    def test_a_fragment_only_link_reaches_nothing_new(self):
        self.assertEqual(
            self.orphans({"index.html": "<a href='#top'>top</a>",
                          "b/index.html": "<p>b</p>"}), ["b/index.html"])

    def test_a_page_reachable_only_from_an_orphan_is_an_orphan(self):
        self.assertEqual(
            self.orphans({"index.html": "<p>home</p>",
                          "orphan/index.html": "<a href='/child/'>c</a>",
                          "child/index.html": "<p>c</p>"}),
            ["child/index.html", "orphan/index.html"])


class HtmlGateFontStacks(unittest.TestCase):
    """F1: the greppable half of §A — every stack has a last resolvable entry."""

    def failures(self, css):
        root = tempfile.mkdtemp()
        os.makedirs(os.path.join(root, "site"))
        with open(os.path.join(root, "site", "index.html"), "w",
                  encoding="utf-8") as handle:
            handle.write("<p>x</p>")
        with open(os.path.join(root, "site", "style.css"), "w",
                  encoding="utf-8") as handle:
            handle.write(css)
        pages, sheets = html_gate.load(os.path.join(root, "site"))
        return [rule for _rel, _line, rule, _why
                in html_gate.check_font_generic(pages, sheets, root)]

    def test_a_stack_without_a_generic_end_fails(self):
        self.assertEqual(self.failures("body{font-family: Charter, Georgia}"),
                         ["FONT-STACK-NO-GENERIC"])

    def test_a_stack_ending_in_a_generic_passes(self):
        self.assertEqual(self.failures('body{font-family: Charter, "Noto Serif", serif}'),
                         [])

    def test_a_var_is_resolved_before_it_is_judged(self):
        self.assertEqual(self.failures(":root{--f: Charter, Georgia}"
                                       "body{font-family: var(--f)}"),
                         ["FONT-STACK-NO-GENERIC"])
        self.assertEqual(self.failures(":root{--f: Charter, serif}"
                                       "body{font-family: var(--f)}"), [])

    def test_an_unresolvable_var_is_a_failure_not_a_pass(self):
        self.assertEqual(self.failures("body{font-family: var(--nowhere)}"),
                         ["FONT-STACK-UNRESOLVABLE"])

    def test_inherit_is_not_a_stack(self):
        self.assertEqual(self.failures("body{font-family: inherit}"), [])

    # socaity-3hv: three ways a stack got past F1, and one way a legal stack
    # was failed by it.

    def test_the_font_shorthand_sets_a_stack_too(self):
        self.assertEqual(self.failures("h1{font: 700 1.2rem/1.4 Georgia}"),
                         ["FONT-STACK-NO-GENERIC"])
        self.assertEqual(self.failures("h1{font: 700 1.2rem/1.4 Georgia, serif}"), [])
        self.assertEqual(self.failures("h1{font: menu}"), [])

    def test_important_does_not_hide_the_generic_end(self):
        self.assertEqual(self.failures("body{font-family: Charter, serif !important}"),
                         [])
        self.assertEqual(self.failures("body{font-family: Charter !important}"),
                         ["FONT-STACK-NO-GENERIC"])

    def test_a_font_face_family_is_a_name_not_a_stack(self):
        self.assertEqual(self.failures("@font-face{font-family: Charter;"
                                       "src: url(/f/charter.woff2)}"), [])

    def test_a_stack_inside_a_media_query_is_judged(self):
        self.assertEqual(self.failures("@media print{body{font-family: Georgia}}"),
                         ["FONT-STACK-NO-GENERIC"])

    def test_a_var_in_the_middle_of_a_stack(self):
        self.assertEqual(self.failures(":root{--f: Georgia}"
                                       "body{font-family: Charter, var(--f)}"),
                         ["FONT-STACK-NO-GENERIC"])
        self.assertEqual(self.failures(":root{--f: Georgia}"
                                       "body{font-family: var(--f), serif}"), [])

    def test_a_var_fallback_is_judged_when_the_property_is_missing(self):
        self.assertEqual(self.failures("body{font-family: var(--nowhere, Georgia)}"),
                         ["FONT-STACK-NO-GENERIC"])
        self.assertEqual(self.failures("body{font-family: var(--nowhere, Georgia, serif)}"),
                         [])

    def test_a_circular_var_is_a_failure(self):
        self.assertEqual(self.failures(":root{--a: var(--b); --b: var(--a)}"
                                       "body{font-family: var(--a)}"),
                         ["FONT-STACK-UNRESOLVABLE"])


class HtmlGateProvenance(unittest.TestCase):
    """Check P — a .prov object always names its kind (0hb §E).

    The check is what keeps the provenance mark honest in the one direction
    the CSS cannot: the fill on the rule says which kind at thumbnail size,
    and the word says it everywhere else. A .prov with no word would make
    absence-of-a-mark the human signal, which is the thing the whole design
    refuses; a word outside the closed pair is how `unverified` or a badge
    grammar would arrive; a word that contradicts its own fill is the two
    channels drifting apart.
    """

    HUMAN = ('<div class="prov"><p class="prov__kind">written by a person</p>'
             '<dl class="prov__grid"><dt>asserted by</dt><dd>founder</dd></dl></div>')
    AGENT = ('<div class="prov prov--agent">'
             '<p class="prov__kind">written by a program</p>'
             '<dl class="prov__grid"><dt>asserted by</dt><dd>a</dd></dl></div>')

    def rules(self, body):
        root = tempfile.mkdtemp()
        os.makedirs(os.path.join(root, "site"))
        with open(os.path.join(root, "site", "index.html"), "w",
                  encoding="utf-8") as handle:
            handle.write(body)
        pages, sheets = html_gate.load(os.path.join(root, "site"))
        return [rule for _rel, _line, rule, _why
                in html_gate.check_prov_kind(pages, sheets, root)]

    def test_both_kinds_pass(self):
        self.assertEqual(self.rules(self.HUMAN + self.AGENT), [])

    def test_the_two_kinds_are_a_closed_set_of_two(self):
        self.assertEqual(sorted(html_gate.PROV_KINDS),
                         ["written by a person", "written by a program"])

    def test_a_prov_with_no_kind_is_flagged(self):
        self.assertEqual(self.rules('<div class="prov"><dl><dt>asserted by</dt>'
                                    '<dd>founder</dd></dl></div>'),
                         ["PROV-KIND"])

    def test_verification_grammar_is_flagged(self):
        for word in ("unverified", "AI-generated", "automated", "verified"):
            self.assertEqual(
                self.rules('<div class="prov"><p class="prov__kind">%s</p></div>' % word),
                ["PROV-KIND"], word)

    def test_a_word_that_contradicts_its_own_fill_is_flagged(self):
        self.assertEqual(
            self.rules('<div class="prov prov--agent">'
                       '<p class="prov__kind">written by a person</p></div>'),
            ["PROV-KIND-DISAGREES"])
        self.assertEqual(
            self.rules('<div class="prov">'
                       '<p class="prov__kind">written by a program</p></div>'),
            ["PROV-KIND-DISAGREES"])

    def test_the_kind_may_be_nested_and_wrapped(self):
        self.assertEqual(
            self.rules('<div class="prov"><p class="prov__kind">\n  written by\n'
                       '  <span>a person</span>\n</p></div>'), [])

    def test_a_modifier_without_the_object_class_is_not_a_prov(self):
        # `.prov--agent` alone carries no rule of its own: the object is
        # `.prov`, and a page that wrote only the modifier would render an
        # unmarked block. The gate sees nothing here, and the CSS renders
        # nothing either, so the two agree.
        self.assertEqual(self.rules('<div class="prov--agent">x</div>'), [])


class HtmlGateFigures(unittest.TestCase):
    """Checks B and G: a figure without its working, and a percentage set at
    heading size without its denominator (0hb §F, §J·b and §J·f).

    The case that matters most here is the one that PASSES B and FAILS G: a
    figure whose derivation is real — it names the rule and the chain the
    number was computed over — but states no denominator. That is the shape
    /ledger shipped at line 129, and a gate that only asked "is there a
    derivation?" would have certified it.
    """

    SHEET = (""":root { --t-display: 2.99rem; --t-h2: 1.73rem; }
               html { font-size: 17px }
               .figure__frac { font-size: var(--t-display) }
               .figure__pct { font-size: var(--t-h2) }
               .big { font-size: 2.2rem }""")

    def rules(self, body, css=None):
        root = tempfile.mkdtemp()
        os.makedirs(os.path.join(root, "site"))
        with open(os.path.join(root, "site", "index.html"), "w",
                  encoding="utf-8") as handle:
            handle.write(body)
        with open(os.path.join(root, "site", "style.css"), "w",
                  encoding="utf-8") as handle:
            handle.write(self.SHEET if css is None else css)
        pages, sheets = html_gate.load(os.path.join(root, "site"))
        found = html_gate.check_figure_derivation(pages, sheets, root)
        found += html_gate.check_percent_size(pages, sheets, root)
        return sorted(rule for _rel, _line, rule, _why in found)

    FIGURE = ('<figure class="figure">'
              '<p class="figure__frac">%s</p>'
              '<p class="figure__pct">= 100%% founder share of epoch 0</p>'
              '%s</figure>')
    DERIVATION = ('<figcaption class="figure__derivation">because the '
                  'denominator D is 50 vu and all of it is his.</figcaption>')

    def test_the_shipped_figure_is_clean(self):
        self.assertEqual(self.rules(self.FIGURE % ("50 of 50 vu", self.DERIVATION)), [])

    def test_a_figure_without_a_derivation(self):
        self.assertEqual(self.rules(self.FIGURE % ("50 of 50 vu", "")),
                         ["FIGURE-WITHOUT-DERIVATION", "PERCENT-WITHOUT-DENOMINATOR"])

    def test_a_derivation_that_names_provenance_but_no_denominator(self):
        # Passes B. Fails G. This is the whole point of G existing.
        provenance = ('<figcaption class="figure__derivation">Computed by the '
                      'published rule over the example chain.</figcaption>')
        self.assertEqual(self.rules(self.FIGURE % ("Your epoch", provenance)),
                         ["PERCENT-WITHOUT-DENOMINATOR"])
        self.assertEqual(self.rules(self.FIGURE % ("0 of 1 vu", provenance)), [])

    def test_a_display_percentage_outside_any_figure(self):
        self.assertEqual(self.rules('<p class="big">Epoch 0: 100% founder</p>'),
                         ["PERCENT-WITHOUT-DENOMINATOR"])

    def test_a_percentage_in_a_heading(self):
        self.assertEqual(self.rules("<h2>Epoch 0: 100% founder</h2>"),
                         ["PERCENT-WITHOUT-DENOMINATOR"])

    def test_a_percentage_in_prose_is_not_this_check(self):
        # The prose inventory (§J·h) is where a body-size percentage is
        # answered; G is about the size a crop takes.
        self.assertEqual(self.rules("<p>the founder share is 100% of the "
                                    "epoch</p>"), [])

    def test_the_size_is_read_from_the_stylesheet_not_the_tag(self):
        # Same markup, one rem smaller: below the heading rung, so not G's.
        small = self.SHEET.replace(".big { font-size: 2.2rem }",
                                   ".big { font-size: 1.2rem }")
        self.assertEqual(self.rules('<p class="big">100% founder</p>', small), [])


# ---------------------------------------------------------------------------
# html gate — check C (W2a)
# ---------------------------------------------------------------------------
class HtmlGateChipText(unittest.TestCase):
    """Check C: no `.chip` without a text node.

    The chip's marker is a CSS `::before` and its state is a colour token, so
    the WORD is the only channel that survives images-off, a text browser, a
    feed reader that strips styles, and a greyscale capture. Every case below
    is a way of shipping a wordless chip that a naive `>...<` test would wave
    through — and the mirror cases, where the word is present but nested or
    entity-escaped, which must NOT be flagged.
    """

    def rules(self, body):
        root = tempfile.mkdtemp()
        os.makedirs(os.path.join(root, "site"))
        with open(os.path.join(root, "site", "index.html"), "w",
                  encoding="utf-8") as handle:
            handle.write(body)
        pages, sheets = html_gate.load(os.path.join(root, "site"))
        return [rule for _rel, _line, rule, _why
                in html_gate.check_chip_text(pages, sheets, root)]

    def test_a_chip_with_a_word_is_clean(self):
        self.assertEqual(self.rules('<span class="chip chip-open">Open</span>'), [])

    def test_an_empty_chip_is_flagged(self):
        self.assertEqual(self.rules('<span class="chip chip-open"></span>'),
                         ["CHIP-WITHOUT-TEXT"])

    def test_whitespace_is_not_a_word(self):
        self.assertEqual(self.rules('<span class="chip">\n   \t </span>'),
                         ["CHIP-WITHOUT-TEXT"])

    def test_a_marker_only_chip_is_flagged(self):
        # The exact regression this check exists for: the state moved into a
        # class and the word was dropped, so the chip says nothing without CSS.
        self.assertEqual(self.rules('<span class="chip chip-contested">'
                                    '<span class="marker"></span></span>'),
                         ["CHIP-WITHOUT-TEXT"])

    def test_nested_text_counts(self):
        self.assertEqual(self.rules('<span class="chip">ticket '
                                    '<code>open</code></span>'), [])

    def test_an_entity_counts(self):
        self.assertEqual(self.rules('<span class="chip">&#79;pen</span>'), [])

    def test_script_inside_a_chip_is_not_text(self):
        self.assertEqual(self.rules('<span class="chip">'
                                    '<script>var x = "Open";</script></span>'),
                         ["CHIP-WITHOUT-TEXT"])

    def test_a_void_element_carrying_the_class_is_flagged(self):
        # No end tag, so no text can ever arrive; alt text is not a text node.
        self.assertEqual(self.rules('<img class="chip" alt="Open">'),
                         ["CHIP-WITHOUT-TEXT"])

    def test_the_container_is_not_a_chip(self):
        self.assertEqual(self.rules('<p class="chips"></p>'), [])

    def test_a_class_that_merely_starts_with_chip_is_not_a_chip(self):
        self.assertEqual(self.rules('<span class="chipmunk"></span>'), [])

    def test_text_after_the_chip_closes_does_not_rescue_it(self):
        self.assertEqual(self.rules('<span class="chip"></span> Open'),
                         ["CHIP-WITHOUT-TEXT"])

    def test_two_chips_on_one_line_are_judged_separately(self):
        self.assertEqual(self.rules('<span class="chip">Open</span>'
                                    '<span class="chip"></span>'),
                         ["CHIP-WITHOUT-TEXT"])

    def test_unbalanced_markup_still_attributes_the_text(self):
        # An end tag closes the nearest match and everything open inside it,
        # which is what the browser does too.
        self.assertEqual(self.rules('<div><span class="chip">Open</div>'), [])

    def test_a_chip_nested_in_a_chip(self):
        self.assertEqual(self.rules('<span class="chip"><span class="chip">'
                                    'Open</span></span>'), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
