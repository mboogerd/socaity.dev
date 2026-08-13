"""A deliberately small Markdown subset, so doc/*.md can be a site page.

Why not a library: the site is a pure function of the merged tree and a fork
has to reproduce it from `pip install -r tools/requirements.txt`. Every
dependency a forker inherits is a cost (council/socaity-z61.md, platform
engineer: "PyYAML + jinja2, nothing else"). doc/manifesto.md and doc/faq.md
use one narrow subset — headings, paragraphs, blockquotes, bullet and ordered
lists, pipe tables, links, bold, italics, code spans, thematic breaks — so the
converter below is smaller than the dependency would be.

Three rules it exists to enforce:

* **HTML comments never reach the page.** The `<!-- vocab-ok: ... -->` waivers
  the banned-wordlist gate reads are authoring metadata; leaking them into a
  public surface would publish our own review notes. A comment that is never
  closed is not a comment: it stays on the page as escaped, visible text, which
  is how you find out you wrote one.
* **Markup in the source is escaped, never executed** — including the href.
  Escaping tags but writing an arbitrary URL into `href=` escapes nothing, so
  only http, https, mailto, fragments and relative paths survive; anything else
  keeps its words and loses its link.
* **Nothing here reads the wall clock, the locale, or the environment.** Output
  is a pure function of the input string, so two renders are byte-identical.

Anything outside the subset (raw inline HTML, nested lists, setext headings,
reference links, images, footnotes, double-backtick code spans, underscore
emphasis) is passed through as escaped text rather
than silently mangled: if a document grows a construct this does not know, it
shows up as visible literal punctuation in review, not as broken markup.
"""

import re

__all__ = ["render_markdown", "strip_comments", "first_heading"]

_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_HR = re.compile(r"^\s{0,3}(?:-{3,}|\*{3,}|_{3,})\s*$")
_BULLET = re.compile(r"^\s{0,3}[-*+]\s+(.*)$")
_ORDERED = re.compile(r"^\s{0,3}(\d+)\.\s+(.*)$")
_TABLE_RULE = re.compile(r"^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$")
_CODE_SPAN = re.compile(r"`([^`]+)`")
# The href allows one level of balanced parentheses, so a Wikipedia-shaped URL
# ("/wiki/Foo_(bar)") does not truncate at the inner ")" and leak a stray one.
_LINK = re.compile(r"\[([^\]\[]+)\]\(((?:[^()\s]|\([^()\s]*\))+)\)")
_STRONG_EM = re.compile(r"\*\*\*(.+?)\*\*\*", re.DOTALL)
_STRONG = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_EM = re.compile(r"(?<![*\w])\*([^*\n]+?)\*(?!\*)")
_SLUG_STRIP = re.compile(r"[^a-z0-9]+")
_SENTINEL = "\x00%d\x00"
_SENTINEL_RE = re.compile(r"\x00(\d+)\x00")


def strip_comments(text):
    """Remove HTML comments (the vocab-ok waivers) before anything else runs."""
    return _COMMENT.sub("", text)


def _escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def _unescape(text):
    """Inverse of _escape. Hrefs are captured out of already-escaped text."""
    return (text.replace("&quot;", '"').replace("&gt;", ">")
                .replace("&lt;", "<").replace("&amp;", "&"))


def _safe_href(href):
    """True unless the URL carries a scheme that can execute or smuggle code.

    A hand-rolled converter that escapes tags but then writes an attacker's
    string straight into href= has not escaped anything: javascript: and data:
    URLs run in the page's origin. Relative links, fragments and the schemes
    below are the whole subset the site needs.
    """
    head = href.strip().lower()
    # Strip control characters browsers ignore when parsing a scheme.
    head = re.sub(r"[\x00-\x20]", "", head)
    match = re.match(r"^([a-z][a-z0-9+.\-]*):", head)
    return not match or match.group(1) in ("http", "https", "mailto")


def _slug(text):
    return _SLUG_STRIP.sub("-", text.lower()).strip("-") or "section"


def _inline(text, link_rewriter):
    """Escape, then apply the inline subset. Code spans are protected first."""
    spans = []

    def stash(match):
        spans.append("<code>%s</code>" % _escape(match.group(1)))
        return _SENTINEL % (len(spans) - 1)

    text = _CODE_SPAN.sub(stash, text)
    text = _escape(text)

    def link(match):
        # The href was captured out of already-escaped text; undo that before
        # the rewriter sees it, or a query string's "&" ends up as "&amp;amp;".
        label, href = match.group(1), _unescape(match.group(2))
        href = link_rewriter(href)
        if not _safe_href(href):
            return label  # an unsafe scheme loses its link, never its words
        return '<a href="%s">%s</a>' % (_escape(href), label)

    text = _LINK.sub(link, text)
    text = _STRONG_EM.sub(lambda m: "<strong><em>%s</em></strong>" % m.group(1), text)
    text = _STRONG.sub(lambda m: "<strong>%s</strong>" % m.group(1), text)
    text = _EM.sub(lambda m: "<em>%s</em>" % m.group(1), text)
    text = _SENTINEL_RE.sub(lambda m: spans[int(m.group(1))], text)
    return text.strip()


def _row_cells(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def _is_block_start(line):
    return bool(_HEADING.match(line) or _HR.match(line) or _BULLET.match(line)
                or _ORDERED.match(line) or line.startswith(">") or not line.strip())


def render_markdown(text, link_rewriter=None, heading_shift=0):
    """Convert a Markdown subset to an HTML fragment.

    link_rewriter maps a Markdown href to the href written into the page (the
    site rewrites repo-relative links to their published address).
    heading_shift adds to every heading level, so a document whose H1 is the
    page title can be nested under a page chrome that already owns <h1>.
    """
    rewrite = link_rewriter or (lambda href: href)
    # NUL is the code-span placeholder; a source file containing one could
    # otherwise address a stashed span it did not write.
    lines = strip_comments(text).replace("\x00", "").replace("\r\n", "\n").split("\n")
    out, seen_ids, i = [], {}, 0

    def heading_id(raw):
        # Slugged from the Markdown source, not from the rendered HTML: the
        # escaped form would put "quot" in the anchor of any quoted question,
        # and these anchors are how people link to a specific answer.
        plain = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", raw)
        base = _slug(re.sub(r"[*`_]", "", plain))
        seen_ids[base] = seen_ids.get(base, 0) + 1
        return base if seen_ids[base] == 1 else "%s-%d" % (base, seen_ids[base])

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        match = _HEADING.match(line)
        if match:
            level = min(6, len(match.group(1)) + heading_shift)
            body = _inline(match.group(2), rewrite)
            if body:
                out.append('<h%d id="%s">%s</h%d>'
                           % (level, heading_id(match.group(2)), body, level))
            i += 1
            continue

        if _HR.match(line):
            out.append("<hr>")
            i += 1
            continue

        if line.lstrip().startswith(">"):
            block = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                block.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>")
            out.append(render_markdown("\n".join(block), rewrite, heading_shift))
            out.append("</blockquote>")
            continue

        if "|" in line and i + 1 < len(lines) and _TABLE_RULE.match(lines[i + 1]):
            header = _row_cells(line)
            i += 2
            body = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                body.append(_row_cells(lines[i]))
                i += 1
            out.append("<table>")
            out.append("<thead><tr>%s</tr></thead>" % "".join(
                '<th scope="col">%s</th>' % _inline(c, rewrite) for c in header))
            out.append("<tbody>")
            for row in body:
                out.append("<tr>%s</tr>" % "".join(
                    "<td>%s</td>" % _inline(c, rewrite) for c in row))
            out.append("</tbody></table>")
            continue

        if _BULLET.match(line) or _ORDERED.match(line):
            ordered = bool(_ORDERED.match(line))
            pattern = _ORDERED if ordered else _BULLET
            items = []
            while i < len(lines):
                match = pattern.match(lines[i])
                if not match:
                    # A lazy continuation line belongs to the item above it.
                    if items and lines[i].strip() and not _is_block_start(lines[i]):
                        items[-1].append(lines[i].strip())
                        i += 1
                        continue
                    break
                items.append([(match.group(2) if ordered else match.group(1)).strip()])
                i += 1
            tag = "ol" if ordered else "ul"
            out.append("<%s>" % tag)
            for item in items:
                out.append("<li>%s</li>" % _inline(" ".join(item), rewrite))
            out.append("</%s>" % tag)
            continue

        para = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not _is_block_start(lines[i]):
            para.append(lines[i].strip())
            i += 1
        out.append("<p>%s</p>" % _inline(" ".join(para), rewrite))

    return "\n".join(out) + "\n"


def first_heading(text):
    """The document's first ATX heading, as plain text — the page title."""
    for line in strip_comments(text).split("\n"):
        match = _HEADING.match(line)
        if match:
            return re.sub(r"[*`]", "", match.group(2)).strip()
    return ""
