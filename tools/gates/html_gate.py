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

  F1  **Every `font-family` declaration ends in a generic family** (§A, the
      greppable half).  The stack is tuned against its *last resolvable*
      entry, so a stack with no generic end has no defined last entry.  A
      `font-family: var(--x)` is resolved against the custom properties
      declared in the same file before it is judged.

Deferred, by the rule platform-engineer generalised in round 3 — "a check may
not land in a commit where it is red", because "a gate that ships failing gets
commented out within a week, and then we have neither the check nor the
honesty of not claiming one".  Each lands in the ticket that ships the markup
satisfying it, as a new entry in CHECKS:

  B   `figure` without a `figure__derivation`.
  C   `.chip` with no text.
  D   freshness stamp without `<time>`.
  G   any `%` at heading or display size outside a `figure` with a derivation.
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
    """What the two live checks need out of a page, with source lines.

    Deliberately shallow: a list of references and a list of CSS fragments.
    The deferred checks need element nesting, so they will grow a tree here
    rather than reparse — the parse stays single-pass either way.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.subresources = []   # (line, kind, url) — fetched without asking
        self.navigations = []    # (line, url) — <a>/<area>, reader-initiated
        self.css = []            # (line, css_text) — <style> blocks, style=""
        self.refresh = None      # meta http-equiv=refresh target, if any
        self.text_len = 0        # visible text, less <style>/<script>
        self.structure = 0       # elements a redirect stub never carries
        self._style = None
        self._quiet = 0          # inside <script>: text is not page text

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        attr = {}
        for name, value in attrs:
            # A repeated attribute: the browser keeps the first. So do we.
            attr.setdefault(name.lower(), value or "")

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
        if tag == "script":
            self._quiet = max(0, self._quiet - 1)
        if tag == "style":
            self._style = None

    def handle_endtag(self, tag):
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

    def close(self):
        super().close()
        if self._style is not None:          # unclosed <style>
            line, chunks = self._style
            self.css.append((line, "".join(chunks)))
            self._style = None


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


# The registry the deferred checks slot into: one entry per §J check, in the
# order the resolution lists them.  Adding (b)–(f), the percent inventory and
# the palette drift check is a new line here plus its function — no rework.
CHECKS = (
    ("A", "no off-origin subresource", check_off_origin),
    ("E", "no orphan page", check_orphans),
    ("F1", "every font-family ends in a generic family", check_font_generic),
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
