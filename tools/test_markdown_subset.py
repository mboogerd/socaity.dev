"""Tests for the Markdown subset that turns doc/*.md into site pages.

Run: python3 -m unittest discover tools
"""

import unittest

import markdown_subset as md


class TestSubset(unittest.TestCase):
    def test_comments_never_reach_the_page(self):
        out = md.render_markdown("Plain. <!-- vocab-ok: quoted objection -->\n")
        self.assertNotIn("vocab-ok", out)
        self.assertNotIn("<!--", out)

    def test_comment_spanning_lines_is_removed_whole(self):
        out = md.render_markdown("## Head <!-- a\nb -->\n\nBody.\n")
        self.assertNotIn("b -->", out)
        self.assertIn("<h2", out)

    def test_headings_carry_source_derived_ids(self):
        out = md.render_markdown('## 1. "Is this a crypto thing?"\n')
        self.assertIn('id="1-is-this-a-crypto-thing"', out)

    def test_duplicate_headings_get_distinct_ids(self):
        out = md.render_markdown("### The concession\n\n### The concession\n")
        self.assertIn('id="the-concession"', out)
        self.assertIn('id="the-concession-2"', out)

    def test_inline_subset(self):
        out = md.render_markdown("**b** *i* `c*d` [t](x.md)\n")
        self.assertIn("<strong>b</strong>", out)
        self.assertIn("<em>i</em>", out)
        self.assertIn("<code>c*d</code>", out)  # no emphasis inside a code span
        self.assertIn('<a href="x.md">t</a>', out)

    def test_html_in_source_is_escaped_not_executed(self):
        out = md.render_markdown("A <script>alert(1)</script> B\n")
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)

    def test_links_are_rewritten(self):
        out = md.render_markdown("[v](vision.md)\n", lambda href: "https://x/" + href)
        self.assertIn('href="https://x/vision.md"', out)

    def test_blocks(self):
        out = md.render_markdown(
            "> quoted\n\n- one\n  still one\n- two\n\n1. first\n2. second\n\n"
            "| A | B |\n|---|---|\n| 1 | 2 |\n\n---\n")
        self.assertIn("<blockquote>", out)
        self.assertIn("<li>one still one</li>", out)
        self.assertIn("<ol>", out)
        self.assertIn('<th scope="col">A</th>', out)
        self.assertIn("<td>1</td>", out)
        self.assertIn("<hr>", out)

    def test_unsafe_url_schemes_lose_the_link_not_the_words(self):
        for href in ("javascript:alert(1)", "JaVaScRiPt:alert(1)",
                     "java\tscript:alert(1)", "data:text/html;base64,PHNjcmlwdD4=",
                     "vbscript:msgbox(1)"):
            out = md.render_markdown("[click](%s)\n" % href)
            self.assertNotIn("<a ", out, href)
            self.assertIn("click", out, href)

    def test_safe_schemes_and_relative_links_survive(self):
        for href in ("https://example.test/x", "http://example.test/x",
                     "mailto:a@example.test", "../doc/faq.md", "#anchor"):
            self.assertIn('<a href="%s">' % href,
                          md.render_markdown("[t](%s)\n" % href), href)

    def test_href_is_escaped_exactly_once(self):
        out = md.render_markdown("[q](https://x.test/a?b=1&c=2)\n")
        self.assertIn('href="https://x.test/a?b=1&amp;c=2"', out)
        self.assertNotIn("&amp;amp;", out)

    def test_link_keeps_balanced_parentheses_in_the_url(self):
        out = md.render_markdown("[x](https://x.test/wiki/Foo_(bar))\n")
        self.assertIn('href="https://x.test/wiki/Foo_(bar)"', out)
        self.assertNotIn("</a>)", out)  # no stray paren left behind

    def test_bold_italic_nests_validly(self):
        self.assertIn("<strong><em>both</em></strong>",
                      md.render_markdown("***both***\n"))

    def test_source_cannot_forge_a_code_span_placeholder(self):
        out = md.render_markdown("a \x000\x00 b `real`\n")
        self.assertEqual(out.count("<code>"), 1)
        self.assertIn("<code>real</code>", out)

    def test_output_is_a_pure_function_of_the_input(self):
        text = "# T\n\nOne. <!-- c -->\n\n- a\n- b\n"
        self.assertEqual(md.render_markdown(text), md.render_markdown(text))

    def test_first_heading_is_the_title(self):
        self.assertEqual(md.first_heading("\n# socaity.dev\n\n## next\n"), "socaity.dev")


if __name__ == "__main__":
    unittest.main()
