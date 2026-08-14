#!/usr/bin/env python3
"""HTML gate — council/socaity-0hb.md §J, over the rendered site.

The render is the only artefact the public actually loads, so the properties
the council fixed about it are asserted against `site/**` rather than against
the templates that produce it.  Two of them are structural and hold today; the
rest arrive with the markup that satisfies them.

Checks that run:

  A   **No off-origin subresource.**  Every URL the browser fetches *on its
      own* while rendering a page must resolve to this origin: `src`,
      `srcset`, `<link>` with a subresource `rel` (stylesheet, icon, preload,
      manifest …), `<object data>`, `poster`, `@import`, and every `url()` in
      a stylesheet, a `<style>` block or a `style=` attribute.  That is the
      "zero external requests by construction" property platform-engineer
      traded the webfont for.

      Also flagged, because the reader does not choose them either: the
      `ping` list on an anchor (POSTed on click whatever the href says), a
      `<meta http-equiv=refresh>` to another origin, a form `action`, the
      legacy `background` attribute, `xlink:href` on SVG `<use>`/`<image>`/
      `<feImage>`, and anything inside an `<iframe srcdoc>`.  URLs are read
      the way the URL parser reads them — ASCII tab and newline removed, CSS
      escapes resolved — because a scheme test run over the raw attribute
      sees no scheme in `ht&#10;tps://…` and waves it through.

      `<a href>` is **not** a subresource and is never flagged.  The dispute
      links, the edit links and the whole provenance apparatus are outbound
      GitHub links; a gate that failed them would be turned off within a day.
      Navigation is a choice the reader makes; a subresource is not.

  E   **No orphan page.**  Breadth-first from `site/index.html` over
      same-origin `<a href>`/`<area href>`, every emitted HTML page must be
      reachable.  This is the check that makes deleting `Claim` from the
      global navigation a decidable change rather than a hopeful one (§I): the
      in-body link set either keeps the page reachable or this gate goes red.
      A directory link works with or without its trailing slash, and a query
      string does not hide the target, because the host resolves both.  A
      `<meta refresh>` redirect stub is excused from needing inbound links
      only while it is *nothing but* a stub — no headings or other structure,
      a sentence of text at most, no link that goes anywhere but its own
      target — so an unreachable page cannot buy an exemption with one
      `<meta refresh>` to the homepage.

  C   **No `.chip` without a text node.**  A chip's marker is a CSS `::before`
      and its colour is a token; both are gone with images off, in a text
      browser, in a feed reader that strips styles, and in any greyscale
      capture where the ink family collapses.  What survives all of those is
      the WORD, so the word is mandatory and this gate is what makes it so.
      The council's phrasing: three redundant channels — marker shape, word,
      value — and a chip that lost its text would be shape-only signalling,
      which is colour-only signalling with a different alibi (§D).

      The text may be nested (`<span class="chip">ticket <code>x</code></span>`
      counts) and whitespace does not count.  An element that carries the
      class and is written self-closing can never have text and is reported
      at its start tag.

  B   **No `figure` without a `figure__derivation`** (§F, §J·b).  The
      component is three lines — fraction, percentage, derivation — and the
      third is the only one a reader can check.  A figure with it removed is
      an assertion wearing a figure's clothes.

  G   **No `%` at heading or display size without its denominator** (§F's
      paramount, §J·f).  The size is resolved out of the stylesheets the page
      loads rather than guessed from the tag, because what makes a percentage
      dangerous is how big it is set: a 50px number is what a screenshot
      crops and a timeline reposts.  At or above the `--t-h2` rung — or
      inside an `<h1>`/`<h2>` at any size — a percentage must sit in a
      `figure` that carries BOTH a derivation and a `.figure__frac` stating
      the fraction it came from.

      The second requirement is the check, and B is not a substitute for it.
      /ledger shipped a second display figure whose derivation named the rule
      and the chain the number was computed over — real provenance, no
      denominator — which would pass "is there a derivation?" while breaking
      the paramount that question exists to serve.  A derivation that names
      where a number came from is not a statement of what it is a fraction
      OF.

  P   **Every `.prov` object names its kind**, from a closed set of exactly
      two strings — `written by a person` / `written by a program` (§E).
      Two failures, one check.  A `.prov` with no kind cannot ship, so
      *absence of a mark can never become the human signal* and "the founder
      carries the identical object" is enforced rather than promised.  And a
      kind whose word disagrees with the fill on the rule — `.prov--agent`
      saying `written by a person`, or the reverse — is the one way the mark
      and the word could drift apart, after which the pattern would be
      encoding something nobody wrote down.  The set is closed on purpose:
      `unverified`, `AI-generated`, `automated` and every badge or
      verification grammar are forbidden, and a closed set is how a gate
      forbids a word it has not been told to expect.

  F1  **Every `font-family` declaration ends in a generic family** (§A, the
      greppable half).  The stack is tuned against its *last resolvable*
      entry, so a stack with no generic end has no defined last entry.  A
      `font-family: var(--x)` is resolved against the custom properties
      declared in the same file before it is judged.

  S1  **The positional style couplings still hold** (§H).  The manifesto's
      first screen and the /faq register strip are styled by ordinal —
      `.doc--manifesto > p:nth-of-type(1..4)`, `.doc--faq > blockquote` —
      because the Markdown subset has no attribute syntax and the alternative
      was presentation logic in `render.py`.  This asserts that the paragraph
      standing in each styled position still opens with the sentence the rule
      was written for, so inserting a paragraph at the top of doc/manifesto.md
      fails the build instead of silently restyling the first screen.

Deferred, by the rule platform-engineer generalised in round 3 — "a check may
not land in a commit where it is red", because "a gate that ships failing gets
commented out within a week, and then we have neither the check nor the
honesty of not claiming one".  Each lands in the ticket that ships the markup
satisfying it, as a new entry in CHECKS:

  D   freshness stamp without `<time>`.
  H   the prose-percentage inventory diffed against
      `tools/gates/percent_inventory.txt` — an inventory, never a verdict.
  I   `blog_card.html` palette drift: every colour literal also in `:root`.

Python stdlib only — `html.parser`, no dependency: the gate runs on a cold
checkout before anything is installed, exactly like the other gates here.

Usage:
  python3 tools/gates/html_gate.py [--root .] [--site site]
  python3 tools/gates/html_gate.py --list          # pages the gate sees
  python3 tools/gates/html_gate.py --only A,E      # run a subset
"""

import argparse
import html.parser
import os
import re
import sys

# The canonical origin.  An absolute URL naming it is this site, spelled the
# long way, and is not an external request.
SITE_ORIGINS = (
    "https://socaity.dev",
    "http://socaity.dev",
    "https://www.socaity.dev",
    "http://www.socaity.dev",
)

# Schemes that never produce a network request: the bytes are already in the
# document, or the URL is not a fetch at all.
INERT_SCHEMES = ("data:", "about:", "blob:", "javascript:", "mailto:", "tel:")

# The URL parser strips these before it looks for a scheme; so do we.
URL_NOISE = {ord(c): None for c in "\t\n\r\f"}

# `rel` values that make the browser fetch the href without being asked.
# `canonical`, `alternate`, `author`, `license`, `me` and friends are pointers
# a human or a crawler follows, not subresources, and stay legal off-origin.
SUBRESOURCE_RELS = {
    "stylesheet", "icon", "shortcut", "apple-touch-icon",
    "apple-touch-icon-precomposed", "mask-icon", "manifest",
    "preload", "modulepreload", "prefetch", "preconnect", "dns-prefetch",
    "prerender", "import",
}

# Attributes the browser fetches on its own.  `href` is deliberately absent:
# it is handled per-element, so that `<a href>` stays legal (see check A).
SRC_ATTRS = {"src", "poster", "data", "formaction"}
SRCSET_ATTRS = {"srcset", "imagesrcset"}

# Elements whose plain `href` is a fetch rather than a navigation.  `<base>`
# retargets every relative URL on the page; the rest are SVG.
HREF_FETCH_TAGS = ("base", "use", "image", "feimage", "script")

# The legacy `background` attribute is still fetched by every browser.
BACKGROUND_TAGS = {"body", "table", "td", "th", "tr", "tbody", "thead", "tfoot"}

# CSS generic families and the global keywords, per §A.  A stack ending in one
# of these has a defined last resolvable entry; one that does not, does not.
GENERIC_FAMILIES = {
    "serif", "sans-serif", "monospace", "cursive", "fantasy",
    "system-ui", "ui-serif", "ui-sans-serif", "ui-monospace", "ui-rounded",
    "math", "emoji", "fangsong",
}
GLOBAL_KEYWORDS = {"inherit", "initial", "unset", "revert", "revert-layer"}

# The most visible text a `<meta refresh>` page may carry and still count as
# a redirect stub rather than a page (render.py's stub carries ~100 chars),
# and the elements whose presence says the page is not a stub at all.
STUB_MAX_TEXT = 300
STRUCTURE_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "img", "table", "figure",
                  "section", "article", "nav", "form", "ul", "ol", "dl",
                  "blockquote", "pre", "details", "video", "audio", "svg",
                  "iframe", "main", "header", "footer"}

# Elements with no end tag. One of these carrying `class="chip"` can never
# hold a text node, so it fails check C at its start tag rather than waiting
# for a close that is not coming.
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}

# The closed set of provenance kinds (§E), and the fill each one is drawn
# with.  Exactly two strings, named symmetrically: they differ in one noun and
# rank neither.  The set is closed rather than open because that is how a gate
# forbids a word nobody told it about — `unverified` above all, which names an
# absence and invites the reader to supply the positive term.
PROV_KINDS = {
    "written by a person": "human",
    "written by a program": "agent",
}

PAGE_EXT = (".html", ".htm")
CSS_EXT = (".css",)

CSS_URL = re.compile(r"""url\(\s*(?P<q>['"]?)(?P<url>[^'")]*)(?P=q)\s*\)""",
                     re.IGNORECASE)
CSS_IMPORT = re.compile(
    r"""@import\s+(?:url\(\s*(?P<q1>['"]?)(?P<u1>[^'")]*)(?P=q1)\s*\)"""
    r"""|(?P<q2>['"])(?P<u2>[^'"]*)(?P=q2))""",
    re.IGNORECASE)
CSS_FONT_FAMILY = re.compile(r"font-family\s*:\s*([^;}]*)", re.IGNORECASE)
# The `font:` shorthand sets font-family too, so a stack can enter the
# stylesheet without the word `font-family` appearing anywhere near it.
CSS_FONT_SHORTHAND = re.compile(r"(?<![-\w])font\s*:\s*([^;}]*)", re.IGNORECASE)
# An @font-face block's `font-family` names the face being defined; it is not
# a stack and has no generic end by construction.
CSS_FONT_FACE = re.compile(r"@font-face\s*\{[^}]*\}", re.IGNORECASE | re.DOTALL)
CSS_IMPORTANT = re.compile(r"!\s*important\s*$", re.IGNORECASE)
# `font: menu` and friends take the whole shorthand from the platform.
SYSTEM_FONT_KEYWORDS = {"caption", "icon", "menu", "message-box",
                        "small-caption", "status-bar"}
CSS_CUSTOM_PROP = re.compile(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;}]*)")
CSS_VAR = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)\s*(?:,\s*(.*?)\s*)?\)$",
                     re.IGNORECASE | re.DOTALL)


# --------------------------------------------------------------------------
# document model
# --------------------------------------------------------------------------
class _Doc(html.parser.HTMLParser):
    """What the live checks need out of a page, with source lines.

    Deliberately shallow: lists of references and CSS fragments, plus the one
    piece of nesting check C actually needs — an open-element stack, so the
    text inside a `.chip` can be attributed to it however deeply it is
    wrapped. The remaining deferred checks grow this stack into a tree rather
    than reparse; the parse stays single-pass either way.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.subresources = []   # (line, kind, url) — fetched without asking
        self.navigations = []    # (line, url) — <a>/<area>, reader-initiated
        self.css = []            # (line, css_text) — <style> blocks, style=""
        self.refresh = None      # meta http-equiv=refresh target, if any
        self.text_len = 0        # visible text, less <style>/<script>
        self.structure = 0       # elements a redirect stub never carries
        self.chips = []          # (line, text) — one per element carrying .chip
        self._style = None
        self._quiet = 0          # inside <script>: text is not page text
        self._open = []          # (tag, chip_frame or None) — open elements
        self._chips = []         # the frames of the chips currently open
        # The element tree checks B and G need (W2c). It grows out of the
        # same single pass and the same open-element stack check C keeps:
        # `self._nodes` is pushed and popped in lockstep with `self._open`,
        # so unbalanced markup closes both the same way the browser does.
        self.root = _element(None, {}, 0, None)
        self._nodes = []

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        attr = {}
        for name, value in attrs:
            # A repeated attribute: the browser keeps the first. So do we.
            attr.setdefault(name.lower(), value or "")

        chip = None
        if "chip" in attr.get("class", "").split():
            chip = [line, []]
            self.chips.append(chip)
        parent = self._nodes[-1] if self._nodes else self.root
        node = _element(tag, attr, line, parent)
        parent["children"].append(node)

        if tag in VOID_TAGS:
            chip = None          # no end tag, so no text can ever arrive
        else:
            self._open.append((tag, chip))
            self._nodes.append(node)
            if chip is not None:
                self._chips.append(chip)

        if tag == "style":
            self._style = (line, [])
        if tag == "script":
            self._quiet += 1
        if tag in STRUCTURE_TAGS:
            self.structure += 1
        if tag == "meta" and attr.get("http-equiv", "").strip().lower() == "refresh":
            found = re.search(r"url\s*=\s*(.*)$", attr.get("content", ""),
                              re.IGNORECASE)
            if found:
                self.refresh = (line, found.group(1).strip().strip("'\""))
        if "style" in attr and attr["style"].strip():
            self.css.append((line, attr["style"]))

        for name, value in attr.items():
            if name in SRC_ATTRS and value.strip():
                self.subresources.append((line, "<%s %s>" % (tag, name), value.strip()))
            elif name in SRCSET_ATTRS and value.strip():
                for candidate in split_srcset(value):
                    self.subresources.append((line, "<%s %s>" % (tag, name), candidate))
            elif name == "background" and tag in BACKGROUND_TAGS and value.strip():
                # Legacy, still fetched.
                self.subresources.append((line, "<%s background>" % tag, value.strip()))
            elif name == "ping" and tag in ("a", "area") and value.strip():
                # The one place an <a> really does cause a fetch: every URL
                # here is POSTed when the reader clicks, whatever the href.
                for target in value.split():
                    self.subresources.append((line, "<%s ping>" % tag, target))
            elif name == "action" and tag == "form" and value.strip():
                # Not a load-time fetch, but a request the reader cannot see
                # the destination of — the same property `formaction` is
                # already held to two lines up.
                self.subresources.append((line, "<form action>", value.strip()))
            elif name.endswith(":href") and tag != "a" and value.strip():
                # `xlink:href` — deprecated, universally supported, and the
                # form <use>/<image>/<feImage> sprites are actually written in.
                self.subresources.append((line, "<%s %s>" % (tag, name), value.strip()))

        if tag == "iframe" and attr.get("srcdoc", "").strip():
            # A whole document in an attribute; its subresources are ours.
            nested = parse_page(attr["srcdoc"])
            for _nline, kind, url in nested.subresources:
                self.subresources.append((line, "<iframe srcdoc> %s" % kind, url))
            for _nline, chunk in nested.css:
                self.css.append((line, chunk))

        href = attr.get("href", "").strip()
        if href:
            if tag in ("a", "area"):
                # Navigation, not a fetch. Off-origin here is legal and load
                # bearing: dispute, edit and provenance links all point out.
                self.navigations.append((line, href))
            elif tag == "link":
                rels = {r.strip().lower() for r in attr.get("rel", "").split()}
                if rels & SUBRESOURCE_RELS:
                    kind = "<link rel=\"%s\">" % " ".join(sorted(rels & SUBRESOURCE_RELS))
                    self.subresources.append((line, kind, href))
            elif tag in HREF_FETCH_TAGS:
                # <base href> retargets every relative URL on the page, and
                # SVG <use>/<image>/<feImage>/<script href> are fetches.
                self.subresources.append((line, "<%s href>" % tag, href))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self._pop(tag)
        if tag == "script":
            self._quiet = max(0, self._quiet - 1)
        if tag == "style":
            self._style = None

    def _pop(self, tag):
        """Close `tag` and every element left open inside it.

        Unbalanced markup is the browser's problem too, and it resolves it the
        same way: an end tag closes the nearest matching open element and
        whatever was still open below it. An end tag matching nothing is
        ignored.
        """
        for depth in range(len(self._open) - 1, -1, -1):
            if self._open[depth][0] == tag:
                del self._open[depth:]
                del self._nodes[depth:]
                # Rebuilt rather than spliced: two chips opened on the same
                # line hold equal-valued frames, and removing "an equal one"
                # is not the same as removing this one.
                self._chips = [c for _name, c in self._open if c is not None]
                return

    def handle_endtag(self, tag):
        self._pop(tag)
        if tag == "script":
            self._quiet = max(0, self._quiet - 1)
        if tag == "style" and self._style is not None:
            line, chunks = self._style
            self.css.append((line, "".join(chunks)))
            self._style = None

    def handle_data(self, data):
        if self._style is not None:
            self._style[1].append(data)
        elif not self._quiet:
            self.text_len += len(data.strip())
            for chip in self._chips:
                chip[1].append(data)
            (self._nodes[-1] if self._nodes else self.root)["text"].append(data)

    def close(self):
        super().close()
        if self._style is not None:          # unclosed <style>
            line, chunks = self._style
            self.css.append((line, "".join(chunks)))
            self._style = None


def _element(tag, attr, line, parent):
    """One node of the page tree: what a selector can be matched against."""
    return {"tag": tag,
            "classes": frozenset(attr.get("class", "").split()),
            "id": attr.get("id", ""),
            "attrs": attr,
            "line": line,
            "parent": parent,
            "children": [],
            "text": []}


def walk(node):
    """Every element under `node`, document order, `node` excluded."""
    for child in node["children"]:
        yield child
        for deeper in walk(child):
            yield deeper


def node_text(node):
    """All text in the subtree, whitespace collapsed."""
    parts = list(node["text"])
    for child in walk(node):
        parts.extend(child["text"])
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def has_class(node, name):
    return name in node["classes"]


def find_class(node, name):
    """The first descendant carrying `name`, or None."""
    for child in walk(node):
        if has_class(child, name):
            return child
    return None


def split_srcset(value):
    """The URLs out of a srcset, descriptors dropped."""
    out = []
    for part in value.split(","):
        part = part.strip()
        if part:
            out.append(part.split()[0])
    return out


# --------------------------------------------------------------------------
# origin
# --------------------------------------------------------------------------
def clean_url(url):
    """The URL as the browser's parser sees it.

    The URL parser removes every ASCII tab and newline before it does
    anything else, so `ht&#10;tps://evil.example/x.js` is a fetch of
    `https://evil.example/x.js` — and a scheme test run over the raw
    attribute value sees no scheme at all and waves it through.
    """
    return url.translate(URL_NOISE).strip()


CSS_ESCAPE = re.compile(r"\\(?:([0-9A-Fa-f]{1,6})[ \t\n]?|(.))", re.DOTALL)


def css_unescape(text):
    """Resolve CSS escapes, so `url(https\\3a //host/x)` reads as a scheme."""
    def one(match):
        if match.group(1) is not None:
            point = int(match.group(1), 16)
            return chr(point) if 0 < point < 0x110000 else ""
        return match.group(2)
    return CSS_ESCAPE.sub(one, text)


def is_off_origin(url):
    """True iff fetching this URL would leave this origin.

    Relative and root-relative URLs are this origin by construction.  A URL
    with an authority is off-origin unless the authority is ours — including
    the protocol-relative `//cdn.example/x.js`, which is the form that looks
    harmless in a diff.
    """
    url = clean_url(url)
    if not url or url.startswith("#"):
        return False
    lowered = url.lower()
    if lowered.startswith(INERT_SCHEMES):
        return False
    if lowered.startswith("//"):
        return not any(lowered.startswith(o.split(":", 1)[1] + "/")
                       or lowered == o.split(":", 1)[1]
                       for o in SITE_ORIGINS)
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", url):
        for origin in SITE_ORIGINS:
            if lowered == origin or lowered.startswith(origin + "/"):
                return False
        return True
    return False


def strip_origin(url):
    """A same-origin URL as a site-root path, or None if it is not one."""
    url = clean_url(url)
    lowered = url.lower()
    for origin in SITE_ORIGINS:
        if lowered == origin:
            return "/"
        if lowered.startswith(origin + "/"):
            return url[len(origin):]
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", url) or url.startswith("//"):
        return None
    return url


# --------------------------------------------------------------------------
# page graph
# --------------------------------------------------------------------------
def resolve(from_path, href, pages=None):
    """Resolve `href` on the page at site-relative `from_path` to a page path.

    Returns a site-relative file path (`blog/index.html`), or None when the
    link does not designate a page in this site.  A directory URL means its
    `index.html`, which is how the renderer emits every page — with or
    without the trailing slash, because that is what the host does: a
    directory request without the slash is redirected to the slash, so
    `href="/ledger"` reaches `/ledger/index.html` and the gate must not call
    the page an orphan for the sake of one character.
    """
    target = strip_origin(href)
    if target is None:
        return None
    target = clean_url(target).split("#", 1)[0].split("?", 1)[0]
    if not target:
        return from_path                       # bare "#frag" — this page
    if target.startswith("/"):
        path = target.lstrip("/")
    else:
        path = os.path.normpath(os.path.join(os.path.dirname(from_path), target))
        if path == ".":
            path = ""
        if path.startswith(".."):
            return None                        # escapes the site root
    path = path.replace(os.sep, "/")
    if target.endswith("/") or path == "":
        path = (path.rstrip("/") + "/index.html").lstrip("/")
    elif not path.lower().endswith(PAGE_EXT):
        directory = path + "/index.html"
        if pages is not None and directory in pages:
            return directory                   # a directory, slash omitted
        return None                            # an asset, not a page
    return path


# --------------------------------------------------------------------------
# CSS
# --------------------------------------------------------------------------
def css_references(css_text, base_line=1):
    """[(line, kind, url)] for every fetch a stylesheet fragment triggers."""
    out = []
    for match in CSS_IMPORT.finditer(css_text):
        url = match.group("u1") if match.group("u1") is not None else match.group("u2")
        out.append((base_line + css_text[:match.start()].count("\n"), "@import",
                    css_unescape(url)))
    for match in CSS_URL.finditer(css_text):
        # An @import written as url() is already reported above.
        head = css_text[:match.start()]
        if re.search(r"@import\s*$", head, re.IGNORECASE):
            continue
        out.append((base_line + head.count("\n"), "url()",
                    css_unescape(match.group("url"))))
    return out


def blank_font_faces(css_text):
    """@font-face bodies blanked out, line numbers preserved."""
    return CSS_FONT_FACE.sub(
        lambda m: re.sub(r"[^\n]", " ", m.group(0)), css_text)


def font_family_values(css_text, base_line=1):
    """[(line, raw_value, shorthand?)] for every declaration that sets a stack."""
    css_text = blank_font_faces(css_text)
    out = []
    for regex, shorthand in ((CSS_FONT_FAMILY, False), (CSS_FONT_SHORTHAND, True)):
        for m in regex.finditer(css_text):
            value = CSS_IMPORTANT.sub("", m.group(1).strip()).strip()
            out.append((base_line + css_text[:m.start()].count("\n"), value,
                        shorthand))
    return sorted(out)


def custom_properties(css_text):
    """{--name: value} — last declaration wins, as the cascade would."""
    props = {}
    for match in CSS_CUSTOM_PROP.finditer(css_text):
        props[match.group(1)] = match.group(2).strip()
    return props


def resolve_font_stack(value, props, seen=None):
    """Follow a trailing `var(--x)` to the stack it names.

    Returns (resolved_value, None) or (value, reason_it_is_unresolvable).  An
    unresolvable stack is a failure, not a pass: the design is tuned against
    the last resolvable entry, and a stack whose tail cannot be read here has
    no last entry anyone has checked.
    """
    seen = seen or set()
    value = value.strip()
    match = CSS_VAR.search(value)
    if not match:
        return value, None
    name, fallback = match.group(1), match.group(2)
    if name in seen:
        return value, "circular custom property %s" % name
    seen.add(name)
    if name in props:
        head = value[:match.start()].strip().rstrip(",").strip()
        tail, why = resolve_font_stack(props[name], props, seen)
        return ((head + ", " + tail).strip(", ") if head else tail), why
    if fallback:
        return resolve_font_stack(fallback, props, seen)
    return value, "%s is not declared in this file" % name


def ends_in_generic(value, shorthand=False):
    """True iff the last family in the stack is a generic family keyword.

    In a `font:` shorthand the family list is the tail of the value, after
    the size — so the candidate is the last whitespace-separated word of the
    last comma-separated segment rather than the segment itself.
    """
    value = value.strip().rstrip(";").strip()
    if not value:
        return False
    if value.lower() in GLOBAL_KEYWORDS:
        return True                            # not a stack at all
    if shorthand and value.lower() in SYSTEM_FONT_KEYWORDS:
        return True                            # the platform picks the stack
    last = value.split(",")[-1].strip().strip("'\"").strip().lower()
    if shorthand:
        words = last.split()
        last = words[-1].strip("'\"") if words else ""
    return re.sub(r"\s+", " ", last) in GENERIC_FAMILIES


# --------------------------------------------------------------------------
# collection
# --------------------------------------------------------------------------
def walk_site(site_root):
    """Site-relative paths of every file the render emitted, sorted."""
    found = []
    for dirpath, dirnames, filenames in os.walk(site_root):
        dirnames[:] = sorted(d for d in dirnames if d not in {".git", "__pycache__"})
        for name in sorted(filenames):
            rel = os.path.relpath(os.path.join(dirpath, name), site_root)
            found.append(rel.replace(os.sep, "/"))
    return sorted(found)


def read(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def parse_page(text):
    doc = _Doc()
    doc.feed(text)
    doc.close()
    return doc


def load(site_root):
    """{page_path: _Doc} and {css_path: text} for the whole render."""
    pages, sheets = {}, {}
    for rel in walk_site(site_root):
        if rel.lower().endswith(PAGE_EXT):
            pages[rel] = parse_page(read(os.path.join(site_root, rel)))
        elif rel.lower().endswith(CSS_EXT):
            sheets[rel] = read(os.path.join(site_root, rel))
    return pages, sheets


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------
def check_off_origin(pages, sheets, _site_root):
    """A — no off-origin subresource. `<a href>` is untouched, on purpose."""
    failures = []
    for rel, doc in sorted(pages.items()):
        for line, kind, url in doc.subresources:
            if is_off_origin(url):
                failures.append((rel, line, "%s fetches %s" % (kind, url)))
        for line, css_text in doc.css:
            for css_line, kind, url in css_references(css_text, line):
                if is_off_origin(url):
                    failures.append((rel, css_line, "CSS %s fetches %s" % (kind, url)))
        if doc.refresh is not None and is_off_origin(doc.refresh[1]):
            # Not a subresource, but not a choice either: the reader is sent
            # off-origin without touching anything.
            failures.append((rel, doc.refresh[0],
                             "<meta http-equiv=refresh> sends the reader to %s"
                             % doc.refresh[1]))
    for rel, css_text in sorted(sheets.items()):
        for line, kind, url in css_references(css_text):
            if is_off_origin(url):
                failures.append((rel, line, "CSS %s fetches %s" % (kind, url)))
    return [(rel, line, "OFF-ORIGIN-SUBRESOURCE", what +
             " — the render makes zero external requests by construction "
             "(0hb §A/§J·a); an <a href> may leave this origin, a subresource "
             "may not")
            for rel, line, what in failures]


def redirect_target(rel, doc, pages=None):
    """Where a redirect stub sends the reader, or None if it is a real page.

    `s/<slug>/index.html` is an *alias*: display sugar over a node's permanent
    `n/<id>/` address (render.py:450).  An alias is an entry point, not a
    destination — nothing links to it because the durable ID is what pages
    link to — so requiring inbound links to it would make check E red on a
    render the council never objected to.  It is excused from reachability and
    its target is required to be reachable instead, so an orphan cannot be
    laundered by putting a stub in front of it.

    The excuse is only available to a page that is *nothing but* the stub.
    Otherwise the rule launders in the other direction: any unreachable page
    could keep its content and buy an exemption with one `<meta refresh>` to
    the homepage.  So a stub must carry no more than a sentence of text
    (STUB_MAX_TEXT) and must not link anywhere except its own target.  A page
    with something to say has to be reachable like every other page.
    """
    if doc.refresh is None:
        return None
    target = resolve(rel, doc.refresh[1], pages)
    if target is None or target == rel:
        return None
    if doc.text_len > STUB_MAX_TEXT:
        return None                            # a page, wearing a redirect
    if doc.structure:
        return None                            # headings, figures, tables: a
                                               # page with something in it
    for _line, href in doc.navigations:
        if resolve(rel, href, pages) != target:
            return None                        # goes somewhere of its own
    return target


def check_orphans(pages, _sheets, _site_root):
    """E — every emitted page reachable from index.html by <a href>."""
    entry = "index.html"
    if entry not in pages:
        return [(entry, 0, "ORPHAN-BFS",
                 "no %s to start from — render the site first" % entry)]

    aliases = {}
    for rel, doc in pages.items():
        if doc.refresh is not None:
            target = redirect_target(rel, doc, pages)
            if target is not None:
                aliases[rel] = target

    seen, queue = {entry}, [entry]
    while queue:
        current = queue.pop(0)
        links = [href for _line, href in pages[current].navigations]
        if pages[current].refresh is not None:
            # A refresh on a page the reader can already get to really does
            # take them onward, stub or not, so it is an edge of the graph.
            links.append(pages[current].refresh[1])
        for href in links:
            target = resolve(current, href, pages)
            if target in pages and target not in seen:
                seen.add(target)
                queue.append(target)

    failures = []
    for rel in sorted(set(pages) - seen):
        if rel in aliases:
            target = aliases[rel]
            if target in pages and target in seen:
                continue                       # an alias for a reachable page
            failures.append((rel, pages[rel].refresh[0], "ORPHAN-BFS",
                             "redirect stub whose target %r is itself "
                             "unreachable — a stub in front of an orphan is "
                             "still an orphan (0hb §J·e)" % (target or
                                                             pages[rel].refresh[1])))
            continue
        failures.append((rel, 0, "ORPHAN-BFS",
                         "unreachable from %s by any chain of same-origin "
                         "<a href> — an emitted page nobody can navigate to is "
                         "published and invisible (0hb §J·e)" % entry))
    return failures


def check_chip_text(pages, _sheets, _site_root):
    """C — no `.chip` without a text node (§D, §J·c).

    The marker is a `::before` and the state is a colour token; strip the
    stylesheet and only the word is left. So the word is the load-bearing
    channel, not the decoration, and a chip without one is not a quieter chip
    — it is an unreadable one.
    """
    failures = []
    for rel, doc in sorted(pages.items()):
        for line, parts in doc.chips:
            if not "".join(parts).strip():
                failures.append((rel, line, "CHIP-WITHOUT-TEXT",
                                 "a .chip with no text node — the marker is a "
                                 "CSS ::before and the state is a colour "
                                 "token, so with the stylesheet gone this "
                                 "chip says nothing at all; every chip carries "
                                 "its own word (0hb \u00a7D/\u00a7J\u00b7c)"))
    return failures


def check_prov_kind(pages, _sheets, _site_root):
    """P — every .prov names its kind, from the closed two-string set (§E).

    Read off the page tree rather than the class attribute alone, because the
    property being checked is what a reader is told, and a reader is told by
    the words.  Three ways to fail:

      · a `.prov` with no `.prov__kind` at all.  This is the failure the
        check exists for: it is what makes "absence of a mark is never the
        human signal" and "the founder's entries carry the same object as
        everyone else's" enforceable rather than promised.
      · a kind outside the closed set.  `unverified`, `AI-generated`,
        `automated` and every badge or verification grammar land here, along
        with any well-meant rewording that reintroduces a ranking.
      · a kind whose word contradicts the fill on its rule.  The mark and
        the word are two channels for one fact; if they can drift apart, the
        hatch starts meaning something nobody wrote down.
    """
    failures = []
    for rel, doc in sorted(pages.items()):
        for node in walk(doc.root):
            if not has_class(node, "prov"):
                continue
            kind_node = find_class(node, "prov__kind")
            kind = node_text(kind_node) if kind_node is not None else ""
            drawn = "agent" if has_class(node, "prov--agent") else "human"
            if kind not in PROV_KINDS:
                failures.append((
                    rel, node["line"], "PROV-KIND",
                    ".prov carries %s, which is not one of %s — a provenance "
                    "object always names its kind, in words, in one of "
                    "exactly two strings (0hb §E)"
                    % ("no .prov__kind" if kind_node is None else repr(kind),
                       sorted(PROV_KINDS))))
            elif PROV_KINDS[kind] != drawn:
                failures.append((
                    rel, node["line"], "PROV-KIND-DISAGREES",
                    ".prov is drawn as the %s kind and reads %r — the fill "
                    "and the word carry one fact between them and may not "
                    "say different things (0hb §E)" % (drawn, kind)))
    return failures


def check_font_generic(pages, sheets, _site_root):
    """F1 — every font-family declaration ends in a generic family (§A)."""
    failures = []

    def judge(rel, line, value, props, shorthand=False):
        prop = "font" if shorthand else "font-family"
        resolved, why = resolve_font_stack(value, props)
        if why:
            failures.append((rel, line, "FONT-STACK-UNRESOLVABLE",
                             "%s: %s — %s, so the stack has no last "
                             "resolvable entry to design against (0hb §A)"
                             % (prop, value, why)))
        elif not ends_in_generic(resolved, shorthand):
            failures.append((rel, line, "FONT-STACK-NO-GENERIC",
                             "%s: %s does not end in a generic family "
                             "%s — the design is tuned against the last "
                             "resolvable entry in the stack (0hb §A)"
                             % (prop, resolved, sorted(GENERIC_FAMILIES))))

    for rel, css_text in sorted(sheets.items()):
        props = custom_properties(css_text)
        for line, value, shorthand in font_family_values(css_text):
            judge(rel, line, value, props, shorthand)

    for rel, doc in sorted(pages.items()):
        # A page's own <style> blocks and style="" attributes, plus the custom
        # properties of every stylesheet it loads — a page may legitimately
        # write `font-family: var(--font-text)` against style.css.
        page_css = "\n".join(chunk for _line, chunk in doc.css)
        props = dict(custom_properties(page_css))
        for sheet_text in sheets.values():
            for name, value in custom_properties(sheet_text).items():
                props.setdefault(name, value)
        for line, chunk in doc.css:
            for css_line, value, shorthand in font_family_values(chunk, line):
                judge(rel, css_line, value, props, shorthand)
    return failures


# --------------------------------------------------------------------------
# type size — what the reader actually sees (checks B and G, W2c)
# --------------------------------------------------------------------------
# A percentage's danger is a function of how big it is set, not of which tag
# it is in: a 50px number is what a screenshot crops and a timeline reposts.
# So check G resolves the font size the page actually renders, out of the
# stylesheets the page loads, rather than trusting a tag name.
#
# The resolution is deliberately partial and deliberately conservative:
#   · only selectors this file can evaluate exactly are honoured — tag,
#     class, id, attribute presence, and the structural pseudo-classes
#     (`:nth-of-type`, `:first-child` …). A selector with `:has()`, `:not()`
#     or a sibling combinator is IGNORED, because a wrong match here would
#     be a wrong verdict;
#   · every matching declaration counts, `@media` context included, and the
#     LARGEST wins. A rule that only applies on a phone is still a size this
#     page renders somewhere, and the check would rather ask about a figure
#     that turned out to be small than miss one that was not.
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
CSS_RULE = re.compile(r"(?P<sel>[^{}]+)\{(?P<body>[^{}]*)\}", re.DOTALL)
CSS_FONT_SIZE = re.compile(r"(?<![-\w])font-size\s*:\s*([^;}]+)", re.IGNORECASE)
CSS_LENGTH = re.compile(r"(-?[\d.]+)\s*(px|rem|em|pt|%)", re.IGNORECASE)
# The compound-selector reader. Anything it cannot name, it refuses.
SEL_TOKEN = re.compile(r"""
    (?P<tag>^[A-Za-z][\w-]*|^\*)
  | \.(?P<cls>[\w-]+)
  | \#(?P<id>[\w-]+)
  | \[(?P<attr>[^\]]*)\]
  | ::?(?P<pseudo>[\w-]+)(?P<args>\([^)]*\))?
""", re.VERBOSE)
STRUCTURAL_PSEUDO = {"first-child", "last-child", "only-child", "only-of-type",
                     "first-of-type", "last-of-type", "nth-child",
                     "nth-of-type"}
#: The rung the resolution calls a heading (--t-h2, 29.41px at a 17px root),
#: less a hair for rounding. At or above this a number is a headline.
HEADING_PX = 29.0
#: …and these tags are headings whatever the stylesheet sets them to.
HEADING_TAGS = {"h1", "h2"}
PERCENT = re.compile(r"\d\s*%")
#: A denominator, stated: two numbers with a division word between them.
DENOMINATOR = re.compile(r"\d[\d.,]*\s*(?:of|/|÷|out of|per)\s+\d", re.IGNORECASE)


def parse_compound(text):
    """A compound selector as {tag, classes, ids, ok}. `ok` is False if this
    file cannot evaluate it exactly, in which case the whole rule is dropped."""
    out = {"tag": None, "classes": set(), "ids": set(), "pseudo": [], "ok": True}
    pos = 0
    while pos < len(text):
        found = SEL_TOKEN.match(text, pos)
        if not found or found.end() == pos:
            return {"ok": False}
        if found.group("tag"):
            out["tag"] = found.group("tag").lower()
        elif found.group("cls"):
            out["classes"].add(found.group("cls"))
        elif found.group("id"):
            out["ids"].add(found.group("id"))
        elif found.group("attr") is not None:
            name = re.split(r"[~|^$*]?=", found.group("attr"), maxsplit=1)[0].strip()
            out["pseudo"].append(("attr", name.lower(), None))
        elif found.group("pseudo"):
            name = found.group("pseudo").lower()
            if text[found.start():found.start() + 2] == "::":
                return {"ok": False}       # a pseudo-element, not this element
            if name not in STRUCTURAL_PSEUDO:
                return {"ok": False}
            args = (found.group("args") or "()")[1:-1].strip().lower()
            out["pseudo"].append(("pseudo", name, args))
        pos = found.end()
    return out


def nth_matches(index, spec):
    """`index` is 1-based. Only literal integers, `odd` and `even`."""
    if spec == "odd":
        return index % 2 == 1
    if spec == "even":
        return index % 2 == 0
    try:
        return index == int(spec)
    except ValueError:
        return False


def compound_matches(node, compound):
    if node["tag"] is None:
        return False
    if compound.get("tag") not in (None, "*", node["tag"]):
        return False
    if not compound["classes"] <= node["classes"]:
        return False
    if compound["ids"] and node["id"] not in compound["ids"]:
        return False
    for kind, name, args in compound["pseudo"]:
        if kind == "attr":
            if name not in node["attrs"]:
                return False
            continue
        siblings = node["parent"]["children"] if node["parent"] else [node]
        same_type = [s for s in siblings if s["tag"] == node["tag"]]
        if name == "first-child" and siblings.index(node) != 0:
            return False
        if name == "last-child" and siblings.index(node) != len(siblings) - 1:
            return False
        if name == "only-child" and len(siblings) != 1:
            return False
        if name == "first-of-type" and same_type.index(node) != 0:
            return False
        if name == "last-of-type" and same_type.index(node) != len(same_type) - 1:
            return False
        if name == "only-of-type" and len(same_type) != 1:
            return False
        if name == "nth-child" and not nth_matches(siblings.index(node) + 1, args):
            return False
        if name == "nth-of-type" and not nth_matches(same_type.index(node) + 1, args):
            return False
    return True


def parse_selector(text):
    """A selector as a right-to-left list of (combinator, compound), or None
    if any part of it is one this file will not claim to understand."""
    parts = re.split(r"\s*([>])\s*|\s+", text.strip())
    parts = [p for p in parts if p]
    if not parts or any(p in ("+", "~") for p in parts):
        return None
    chain = []
    combinator = " "
    for part in reversed(parts):
        if part == ">":
            combinator = ">"
            continue
        compound = parse_compound(part)
        if not compound.get("ok"):
            return None
        chain.append((combinator, compound))
        combinator = " "
    return chain


def selector_matches(node, chain):
    if not compound_matches(node, chain[0][1]):
        return False
    current = node
    for combinator, compound in chain[1:]:
        if combinator == ">":
            current = current["parent"]
            if current is None or not compound_matches(current, compound):
                return False
        else:
            current = current["parent"]
            while current is not None and not compound_matches(current, compound):
                current = current["parent"]
            if current is None:
                return False
    return True


def font_size_rules(sheets):
    """[(chain, value)] for every font-size this file can place, plus the root
    size the page's `rem` are counted in."""
    rules, root_px = [], 16.0
    for text in sheets.values():
        clean = CSS_COMMENT.sub(" ", text)
        props = custom_properties(text)
        for block in CSS_RULE.finditer(clean):
            values = CSS_FONT_SIZE.findall(block.group("body"))
            for shorthand in CSS_FONT_SHORTHAND.findall(block.group("body")):
                found = CSS_LENGTH.search(shorthand.split("/")[0])
                if found:
                    values.append(found.group(0))
            if not values:
                continue
            for raw in values:
                value = raw.strip()
                var = CSS_VAR.search(value)
                if var:
                    value = props.get(var.group(1), var.group(2) or "").strip()
                for selector in block.group("sel").split(","):
                    chain = parse_selector(selector)
                    if chain is None:
                        continue
                    if (selector.strip() == "html"
                            and value.lower().endswith("px")):
                        root_px = float(CSS_LENGTH.match(value).group(1))
                    rules.append((chain, value))
    return rules, root_px


def length_px(value, root_px, parent_px):
    found = CSS_LENGTH.match(value.strip())
    if not found:
        return None
    number, unit = float(found.group(1)), found.group(2).lower()
    if unit == "px":
        return number
    if unit == "pt":
        return number * 4.0 / 3.0
    if unit == "rem":
        return number * root_px
    if unit == "em":
        return number * parent_px
    return parent_px * number / 100.0


def font_size_of(node, rules, root_px, cache):
    """The largest size any honoured rule sets on this element, else the
    size it inherits."""
    key = id(node)
    if key in cache:
        return cache[key]
    parent_px = (root_px if node["parent"] is None
                 else font_size_of(node["parent"], rules, root_px, cache))
    size = parent_px
    best = None
    for chain, value in rules:
        if selector_matches(node, chain):
            resolved = length_px(value, root_px, parent_px)
            if resolved is not None and (best is None or resolved > best):
                best = resolved
    if best is not None:
        size = best
    cache[key] = size
    return size


def ancestors(node):
    current = node["parent"]
    while current is not None:
        yield current
        current = current["parent"]


def enclosing_figure(node):
    for parent in ancestors(node):
        if parent["tag"] == "figure":
            return parent
    return None


def check_figure_derivation(pages, _sheets, _site_root):
    """B — no `figure` without a `figure__derivation` (§F, §J·b).

    The component is three lines and the third one is not optional: a figure
    is a number plus the working that produced it, and a number with the
    working removed is an assertion wearing a figure's clothes.
    """
    failures = []
    for rel, doc in sorted(pages.items()):
        for node in walk(doc.root):
            if node["tag"] != "figure":
                continue
            if find_class(node, "figure__derivation") is None:
                failures.append((rel, node["line"], "FIGURE-WITHOUT-DERIVATION",
                                 "a <figure> with no .figure__derivation in it "
                                 "— the derivation is the third line of the "
                                 "component and the only part of it a reader "
                                 "can check (0hb §F/§J·b)"))
    return failures


def check_percent_size(pages, sheets, _site_root):
    """G — no `%` at heading or display size without its denominator beside it
    (§F paramount, §J·f).

    The check that a derivation EXISTS (B) is not the check the paramount
    needs, and the ledger's second display figure is why: its derivation names
    the rule and the chain it was computed over — real provenance, no
    denominator — so it would pass B while breaking the rule B exists to
    serve.  So G asks the harder question: is the fraction stated, in this
    figure, in a `.figure__frac`?  A percentage set at 50px travels alone —
    into a screenshot, a slide, a quote-tweet — and 100% with nothing else in
    the crop is a different claim from `50 of 50 vu`.
    """
    rules, root_px = font_size_rules(sheets)
    failures = []
    for rel, doc in sorted(pages.items()):
        cache = {}
        for node in walk(doc.root):
            own_text = re.sub(r"\s+", " ", "".join(node["text"]))
            if not PERCENT.search(own_text):
                continue
            size = font_size_of(node, rules, root_px, cache)
            heading = (node["tag"] in HEADING_TAGS
                       or any(a["tag"] in HEADING_TAGS for a in ancestors(node)))
            if size < HEADING_PX and not heading:
                continue
            how = ("%.1fpx" % size) if size >= HEADING_PX else "a heading"
            figure = enclosing_figure(node)
            if figure is None:
                failures.append((rel, node["line"], "PERCENT-WITHOUT-DENOMINATOR",
                                 "%r set at %s and not inside a <figure> — a "
                                 "percentage this size is what a crop takes, "
                                 "and it may not appear on any surface without "
                                 "its denominator in the same visual object "
                                 "(0hb §F paramount / §J·f)"
                                 % (own_text.strip()[:60], how)))
                continue
            if find_class(figure, "figure__derivation") is None:
                failures.append((rel, figure["line"], "PERCENT-WITHOUT-DENOMINATOR",
                                 "%r set at %s in a <figure> with no "
                                 "derivation (0hb §F/§J·f)"
                                 % (own_text.strip()[:60], how)))
                continue
            frac = find_class(figure, "figure__frac")
            if frac is None or not DENOMINATOR.search(node_text(frac)):
                failures.append((rel, figure["line"], "PERCENT-WITHOUT-DENOMINATOR",
                                 "%r set at %s in a <figure> whose "
                                 ".figure__frac does not state a fraction%s — a "
                                 "derivation that names provenance is not a "
                                 "denominator, and this is the check that "
                                 "difference is for (0hb §F paramount / "
                                 "§J·f)"
                                 % (own_text.strip()[:60], how,
                                    "" if frac is not None else " (there is none)"))) 
    return failures


# --------------------------------------------------------------------------
# S1 — the positional style couplings still hold (W2d, for §H)
# --------------------------------------------------------------------------
# style.css styles the manifesto's first screen BY POSITION —
# `.doc--manifesto > p:nth-of-type(1..4)` are the kicker, the thesis, the
# register strip and the standing line — and it reaches the /faq copy of the
# register sentence the same way, as that page's first blockquote.  It has to:
# doc/*.md is the only copy of that copy, and tools/markdown_subset.py has no
# attribute syntax to hang a class on a paragraph with.  The alternative was
# presentation logic in render.py, which the resolution forbids.
#
# Until this check the coupling was documented in the stylesheet and enforced
# by nothing.  Insert one paragraph at the top of doc/manifesto.md and the
# thesis renders as the kicker, the register strip renders as the standing
# line, the first screen §H specifies is gone, and every check on this site
# stays green.  So: the stylesheet says which position, and the table below
# says what has to be standing in it.
#
# Deliberately DATA, not appearance.  The gate never judges the sentence and
# never looks at a computed style; it asserts only that the known opening is
# still where the rule aims.  Rewording the manifesto is a copy change under
# the wordlist gate, and if it touches one of these openings it touches this
# table in the same commit — which is the review the coupling never got.
POSITIONAL_STYLE_COUPLINGS = (
    ("index.html", "doc--manifesto", "p", 1,
     "The place where society self-develops",
     "the kicker — --t-lede, italic, --ink-2"),
    ("index.html", "doc--manifesto", "p", 2,
     "The system never assigns work. It prices it.",
     "the thesis — one of exactly two --t-display uses on the site"),
    ("index.html", "doc--manifesto", "p", 3,
     "No token. Nothing to trade.",
     "the register strip — the one shared .register object"),
    ("index.html", "doc--manifesto", "p", 4,
     "Status:",
     "the standing line — --font-ui at the --t-micro floor"),
    ("faq/index.html", "doc--faq", "blockquote", 1,
     "A public record of contributions. No token. Nothing to trade.",
     "the register strip — the one shared .register object"),
)


class _Children(html.parser.HTMLParser):
    """The direct children of the element carrying `class`, with their text.

    Shallow on purpose, like `_Doc`: `nth-of-type` counts among siblings of
    one type under one parent, so (tag, line, text) for the direct children of
    the container is exactly and only what the check needs.
    """

    def __init__(self, container_class):
        super().__init__(convert_charrefs=True)
        self.want = container_class
        self.children = []          # (tag, line, [text chunks])
        self._depth = None          # None until the container opens
        self._open = None           # the child currently collecting text

    def handle_starttag(self, tag, attrs):
        attr = {}
        for name, value in attrs:
            attr.setdefault(name.lower(), value or "")
        if self._depth is None:
            if self.want in attr.get("class", "").split():
                self._depth = 0
            return
        self._depth += 1
        if self._depth == 1:
            self.children.append((tag, self.getpos()[0], []))
            self._open = self.children[-1][2]

    def handle_startendtag(self, tag, attrs):
        if self._depth is None:
            return                      # a void element cannot be the container
        if self._depth == 0:
            self.children.append((tag, self.getpos()[0], []))

    def handle_endtag(self, tag):
        if self._depth is None:
            return
        if self._depth == 0:
            self._depth = None          # the container closed
            self._open = None
            return
        self._depth -= 1
        if self._depth == 0:
            self._open = None

    def handle_data(self, data):
        if self._open is not None:
            self._open.append(data)


def visible_text(chunks):
    """The child's text as a reader meets it: tags gone, whitespace collapsed."""
    return re.sub(r"\s+", " ", "".join(chunks)).strip()


def check_positional(pages, _sheets, site_root):
    """S1 — every position style.css styles by ordinal still holds its text."""
    failures = []
    wanted = {}
    for rel, container, tag, nth, opening, what in POSITIONAL_STYLE_COUPLINGS:
        wanted.setdefault((rel, container), []).append((tag, nth, opening, what))

    for (rel, container), rows in sorted(wanted.items()):
        if rel not in pages:
            failures.append((rel, 0, "POSITIONAL-PAGE-MISSING",
                             "style.css styles this page by position and the "
                             "render does not emit it (0hb §H)"))
            continue
        parser = _Children(container)
        parser.feed(read(os.path.join(site_root, rel)))
        parser.close()
        if not parser.children:
            failures.append((rel, 0, "POSITIONAL-CONTAINER-MISSING",
                             "no .%s element with children on this page — the "
                             "first-screen rules in style.css select through it "
                             "(0hb §H)" % container))
            continue
        for tag, nth, opening, what in rows:
            same = [child for child in parser.children if child[0] == tag]
            if len(same) < nth:
                failures.append((rel, 0, "POSITIONAL-STYLE-COUPLING",
                                 ".%s > %s:nth-of-type(%d) is %s, and this page "
                                 "has %d <%s> child(ren) — the rule now styles "
                                 "nothing (0hb §H)"
                                 % (container, tag, nth, what, len(same), tag)))
                continue
            _tag, line, chunks = same[nth - 1]
            text = visible_text(chunks)
            if not text.startswith(opening):
                failures.append((rel, line, "POSITIONAL-STYLE-COUPLING",
                                 ".%s > %s:nth-of-type(%d) is styled as %s, so "
                                 "it must still open %r — it opens %r. Either "
                                 "the source moved under the rule or the rule "
                                 "moved under the source, and the stylesheet has "
                                 "no class to fall back on (0hb §H)"
                                 % (container, tag, nth, what, opening,
                                    text[:60])))
    return failures


# The registry the deferred checks slot into: one entry per §J check, in the
# order the resolution lists them.  Adding (b)–(f), the percent inventory and
# the palette drift check is a new line here plus its function — no rework.
# S1 is not a §J check: it is the machine half of §H's first screen, and it
# lives here rather than in a gate of its own because the property it holds
# is a property of the RENDER, which is what this gate is over.
CHECKS = (
    ("A", "no off-origin subresource", check_off_origin),
    ("B", "no figure without a derivation", check_figure_derivation),
    ("C", "no .chip without a text node", check_chip_text),
    ("E", "no orphan page", check_orphans),
    ("G", "no % at heading size without its denominator", check_percent_size),
    ("F1", "every font-family ends in a generic family", check_font_generic),
    ("P", "every .prov names its kind", check_prov_kind),
    ("S1", "positional style couplings still hold", check_positional),
)


def main(argv=None):
    ap = argparse.ArgumentParser(description="rendered-HTML gate (0hb §J)")
    ap.add_argument("--root", default=".")
    ap.add_argument("--site", default="site",
                    help="rendered site directory (default: site)")
    ap.add_argument("--only", default="",
                    help="comma-separated check ids to run (default: all)")
    ap.add_argument("--list", action="store_true",
                    help="print the pages and stylesheets the gate sees, and exit")
    args = ap.parse_args(argv)

    site_root = os.path.join(os.path.abspath(args.root), args.site)
    if not os.path.isdir(site_root):
        sys.stderr.write("html-gate: no rendered site at %s — render it first\n"
                         % site_root)
        return 2

    pages, sheets = load(site_root)

    if args.list:
        for rel in sorted(pages):
            print(rel)
        for rel in sorted(sheets):
            print(rel)
        return 0

    wanted = {c.strip().upper() for c in args.only.split(",") if c.strip()}
    selected = [c for c in CHECKS if not wanted or c[0].upper() in wanted]
    unknown = wanted - {c[0].upper() for c in CHECKS}
    if unknown:
        sys.stderr.write("html-gate: no such check(s): %s\n" % ", ".join(sorted(unknown)))
        return 2

    print("== html gate")
    print("   %d checks over %d pages and %d stylesheets under %s/"
          % (len(selected), len(pages), len(sheets), args.site))
    if not pages:
        sys.stderr.write("html-gate: no pages under %s/ — render the site first\n"
                         % site_root)
        return 2

    failures = []
    for check_id, title, run in selected:
        found = run(pages, sheets, site_root)
        print("   %-3s %-46s %s" % (check_id, title,
                                    "clean" if not found else
                                    "%d failure(s)" % len(found)))
        failures.extend((check_id, rel, line, rule, why) for rel, line, rule, why in found)

    for check_id, rel, line, rule, why in failures:
        print("FAIL %s/%s:%d: %s (%s) — %s"
              % (args.site, rel, line, rule, check_id, why))

    if failures:
        print("   %d failure(s)" % len(failures))
        return 1
    print("== html gate: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
