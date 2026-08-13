#!/usr/bin/env python3
"""BANNED-WORDLIST gate — doc/standards/vocabulary-and-visual.md §1.6.

The machine half of the vocabulary standard. Consumes
`doc/standards/banned-words.txt` and runs it over the *published surfaces*:
the rendered site (site/ is gitignored, so a gate over tracked files would
never see published copy), the published Markdown sources the site is built
from, and the templates that carry static page chrome.  "The rendered site"
means everything under it that carries words, generator output included: the
pages, the RSS feed, and graph.json / sections.json — those exports are the M1
ingestion seam and they reproduce node titles and body prose verbatim, so a
banned word in one is published just as surely as one on a page.

A page is read the way a reader reads it, not the way a file stores it: text
and attribute copy (alt, title, og:*, placeholder, aria-*), JSON-LD metadata,
tag boundaries closed so `wall<span>et</span>` is one word, lines joined so a
phrase that wraps is one phrase, and NFKC + confusable folding so a Cyrillic
homoglyph or a zero-width space is not a hiding place.  Each of those is a
bypass that worked before tools/gates/test_gates.py existed.

Two jobs, per §1.6:

  1. Banlist.  A bare pattern is FAIL-level: any match fails the build, with
     no waiver path.  A pattern prefixed with `~` is REVIEW-REQUIRED: the hit
     is always reported, and it fails only when the matching line carries no
     inline waiver — `<!-- vocab-ok: reason -->` (Markdown/HTML) or
     `# vocab-ok: reason` (code/config).

     A waiver covers **the line it sits on**, and nothing else: a waiver that
     reached the following line could silently excuse a violation nobody was
     looking at.  Prose that wraps is still waivable, because a phrase that
     straddles two lines is matched by the window view and honours a waiver on
     either side of the join.  A waiver needs a reason a person wrote —
     `vocab-ok:` with nothing after it, or with punctuation after it, waives
     nothing — and in Markdown it must sit in a comment, so that prose merely
     mentioning the marker cannot grant one.  Every waiver that actually
     suppressed a hit is printed: an invisible waiver is an unreviewed one.

     Waivers live in the *source* the copy is authored in, and the Markdown
     renderer drops HTML comments, so a rendered page cannot show its own
     waiver.  The gate therefore resolves a review-required hit on a rendered
     page against a same-line waiver first (which is what happens once the
     renderer preserves the comment) and against the waivers granted in the
     published sources second.  Fail-level hits and the required-string
     assertion have no such fallback: they are checked on the render itself.

  2. Required string.  A banlist cannot assert presence.  Any surface that
     presents the ledger or the mechanism must carry the first-screen string
     "No token. Nothing to trade." verbatim (1ux, xuz).

Scope is §0 of the standard, and it is load-bearing: doc/, council/ and
.claude/skills/ are internal prose and are exempt — internal precision may use
words public copy must not.  The two published documents that happen to live
under doc/ (the manifesto and the FAQ) are named surfaces and are scanned.
Run with --audit to see what the exemption is worth.

Python stdlib only: the gate runs before dependencies are installed.

Usage:
  python3 tools/gates/vocab_gate.py [--root .] [--site site] [--audit]
  python3 tools/gates/vocab_gate.py --list        # resolved surface list
"""

import argparse
import html.parser
import json
import os
import re
import sys
import unicodedata

# --------------------------------------------------------------------------
# §0 scope.  A path is a surface iff it matches SURFACE_* and is not exempt;
# NAMED_SURFACES win over the exemptions (the manifesto and FAQ live in doc/).
# --------------------------------------------------------------------------
NAMED_SURFACES = (
    "README.md",
    "doc/manifesto.md",
    "doc/faq.md",
)

# Globs are matched against the repo-relative path; `**` spans separators and,
# as in gitignore, `a/**/b` also matches `a/b` — otherwise `blog/**/*.md` would
# silently skip every post that is not in a subdirectory, which is most of them.
SURFACE_GLOBS = (
    "blog/**/*.md",
    "blog/**/*.html",
)

# Markup surfaces: parsed for visible text, attribute copy and waiver comments.
MARKUP_EXT = (".html", ".htm", ".xml", ".xhtml", ".svg", ".atom", ".rss")
# Data surfaces: the renderer publishes graph.json and sections.json next to the
# pages, they carry node titles and body prose verbatim, and they are the M1
# ingestion seam — public copy by any reading. Every string in them is scanned.
DATA_EXT = (".json", ".txt", ".webmanifest")

# Static page chrome lives here; the fixture graph does not exercise every
# branch of it, so the templates are scanned as source alongside the render.
TEMPLATE_GLOBS = (
    "tools/render/templates/*.html",
)

# §0: "Not a surface, and deliberately exempt".
EXEMPT_PREFIXES = (
    "doc/",
    "council/",
    ".claude/",
    ".codex/",
    ".agents/",
    ".beads/",
    ".github/",
    "graph/",
    "ledger/",
    "rule/",
    "tools/",
    "AGENTS.md",
    "CLAUDE.md",
)

REQUIRED_STRING = "No token. Nothing to trade."

# A surface "presenting the ledger or the mechanism" — narrow on purpose, the
# same editing rule the wordlist is under.
REQUIRED_TRIGGER = re.compile(
    r"\b(the ledger|the contribution ledger|epoch shares?|valuation units?|"
    r"subsidy multiplier|earliness premium)\b",
    re.IGNORECASE,
)

WAIVER = re.compile(r"vocab-ok\s*:\s*(\S.*?)(?:-->|$)", re.IGNORECASE)
# A waiver is a decision someone signed; an empty or punctuation-only reason is
# a decision nobody made, so it does not waive.
MIN_REASON = 4

FAIL, REVIEW = "FAIL", "REVIEW"


# --------------------------------------------------------------------------
# wordlist
# --------------------------------------------------------------------------
def load_wordlist(path):
    """Return [(tier, source_line_no, raw_pattern, compiled)]."""
    out = []
    with open(path, encoding="utf-8") as handle:
        for lineno, raw in enumerate(handle, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            tier = FAIL
            if line.startswith("~"):
                tier, line = REVIEW, line[1:].strip()
            try:
                compiled = re.compile(line, re.IGNORECASE)
            except re.error as exc:
                die("%s:%d: unusable pattern %r (%s)" % (path, lineno, line, exc))
            out.append((tier, lineno, line, compiled))
    if not out:
        die("%s: no patterns loaded" % path)
    return out


# --------------------------------------------------------------------------
# text extraction
# --------------------------------------------------------------------------
class _Extract(html.parser.HTMLParser):
    """Visible text and alt/title copy, per source line; comments kept apart."""

    # <script type="application/ld+json"> is published metadata, not code: it
    # is what a search result and a social card actually show.
    SKIP = {"script", "style"}
    LD_JSON = "application/ld+json"
    TEXT_ATTRS = {"alt", "title", "content", "aria-label", "aria-description",
                  "aria-placeholder", "aria-roledescription", "aria-valuetext",
                  "placeholder", "label", "value", "summary", "abbr", "download",
                  "data-label", "data-title", "data-tooltip", "data-text"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = {}      # line -> visible text, word-separated
        self.glued = {}     # line -> the same text with tag boundaries closed
        self.comments = {}  # line -> comment text
        self._skip = 0
        self._ld = 0

    def _add(self, store, line, chunk):
        for offset, part in enumerate(chunk.split("\n")):
            if part.strip():
                store[line + offset] = (store.get(line + offset, "") + " " + part).strip()

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self._skip += 1
            if tag == "script" and any(
                    n == "type" and (v or "").strip().lower() == self.LD_JSON
                    for n, v in attrs):
                self._ld += 1
        line = self.getpos()[0]
        for name, value in attrs:
            if name in self.TEXT_ATTRS and value:
                self._add(self.text, line, value)
                self._add(self.glued, line, value)

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag):
        if tag in self.SKIP and self._skip:
            self._skip -= 1
            if tag == "script" and self._ld:
                self._ld -= 1

    def handle_data(self, data):
        if not self._skip:
            self._add(self.text, self.getpos()[0], data)
            # `wall<span>et</span>` is one word to a reader and two data chunks
            # to the parser. `glued` re-joins them with nothing in between, so a
            # banned word split across a tag boundary still matches.
            self._add_glued(self.getpos()[0], data)
        elif self._ld:
            # JSON-LD: scan the strings, not the punctuation.
            self._add(self.text, self.getpos()[0], " ".join(json_strings(data)))

    def _add_glued(self, line, chunk):
        # Whitespace inside a chunk is kept and whitespace *between* chunks is
        # not invented: `wall` + `et` becomes `wallet`, while `a</p><p>b` stays
        # two words only if the markup actually put space between them.
        for offset, part in enumerate(chunk.split("\n")):
            if part:
                self.glued[line + offset] = self.glued.get(line + offset, "") + part

    def handle_comment(self, data):
        self._add(self.comments, self.getpos()[0], data)


# Homoglyphs: a Cyrillic `а` reads as `a` and matches nothing.  This is the
# short list of Latin lookalikes in the Cyrillic and Greek blocks plus the
# fullwidth forms; NFKC handles the rest.  Zero-width characters are deleted
# outright — they exist only to break a word for a machine while leaving it
# whole for a reader.
_CONFUSABLES = str.maketrans({
    "\u0430": "a", "\u0435": "e", "\u043e": "o", "\u0440": "p", "\u0441": "c",
    "\u0443": "y", "\u0445": "x", "\u0455": "s", "\u0456": "i", "\u0458": "j",
    "\u04bb": "h", "\u0501": "d", "\u051b": "q", "\u051d": "w",
    "\u0410": "A", "\u0412": "B", "\u0415": "E", "\u041a": "K", "\u041c": "M",
    "\u041d": "H", "\u041e": "O", "\u0420": "P", "\u0421": "C", "\u0422": "T",
    "\u0425": "X", "\u0405": "S", "\u0406": "I", "\u0408": "J",
    "\u03b1": "a", "\u03bf": "o", "\u03c1": "p", "\u03bd": "v", "\u03c5": "u",
    "\u0391": "A", "\u0392": "B", "\u0395": "E", "\u0396": "Z", "\u0397": "H",
    "\u0399": "I", "\u039a": "K", "\u039c": "M", "\u039d": "N", "\u039f": "O",
    "\u03a1": "P", "\u03a4": "T", "\u03a7": "X", "\u0392": "B",
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-",
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u00a0": " ", "\u2007": " ", "\u202f": " ", "\u2009": " ",
    # deleted, not replaced: invisible word-breakers
    "\u200b": "", "\u200c": "", "\u200d": "", "\u2060": "", "\ufeff": "",
    "\u00ad": "", "\u034f": "",
})


def fold(text):
    """Normalise published copy to the form the wordlist is written against."""
    return unicodedata.normalize("NFKC", text).translate(_CONFUSABLES)


def json_strings(raw):
    """Every string in a JSON document — keys excluded, values and lists in."""
    def walk(node, out):
        if isinstance(node, str):
            out.append(node)
        elif isinstance(node, dict):
            for value in node.values():
                walk(value, out)
        elif isinstance(node, list):
            for value in node:
                walk(value, out)
    found = []
    try:
        walk(json.loads(raw), found)
    except (ValueError, TypeError):
        # Not JSON after all: scan it as flat text rather than skipping it.
        return [raw]
    return found


def waiver_reason(comment):
    found = WAIVER.search(comment)
    return re.sub(r"\s+", " ", found.group(1).strip().rstrip("->").strip()) if found else ""


def valid_waiver(comment):
    """A waiver needs a reason a human wrote. `vocab-ok: -->` is not one."""
    found = WAIVER.search(comment)
    if not found:
        return False
    reason = found.group(1).strip().rstrip("->").strip()
    return len(reason) >= MIN_REASON and re.search(r"[A-Za-z]{3}", reason) is not None


def read_surface(path):
    """(text_by_line, glued_by_line, waiver_lines) for one surface file."""
    with open(path, encoding="utf-8", errors="replace") as handle:
        raw = fold(handle.read())

    waivers = {}
    if path.endswith(DATA_EXT):
        # A data export has no lines a reader sees and no comment syntax to
        # carry a waiver: every string in it is checked, unwaivable.
        text = {i: value for i, value in enumerate(json_strings(raw), 1)}
        return text, dict(text), waivers

    if path.endswith(MARKUP_EXT):
        parser = _Extract()
        parser.feed(raw)
        parser.close()
        text, glued = parser.text, parser.glued
        for line, comment in parser.comments.items():
            if valid_waiver(comment):
                waivers[line] = waiver_reason(comment)
    else:
        text, glued = {}, {}
        for lineno, line in enumerate(raw.split("\n"), 1):
            if line.strip():
                text[lineno] = line
                glued[lineno] = line
            # In Markdown the waiver must sit in a comment or a `#` line, so
            # that prose merely mentioning the marker cannot grant one.
            stripped = line.strip()
            if ("<!--" in line or stripped.startswith("#")) and valid_waiver(line):
                waivers[lineno] = waiver_reason(line)
    return text, glued, waivers


def normalise(text_by_line):
    """One whitespace-collapsed blob, for presence assertions across wrapping."""
    joined = " ".join(text_by_line[k] for k in sorted(text_by_line))
    joined = joined.replace(" ", " ").replace("’", "'")
    return re.sub(r"\s+", " ", joined)


# --------------------------------------------------------------------------
# path selection
# --------------------------------------------------------------------------
def glob_match(pattern, path):
    """fnmatch with a `**` that spans separators — and collapses.

    `blog/**/*.md` must match `blog/post.md` as well as `blog/2026/post.md`.
    The naive translation makes the separators around `**` mandatory, so the
    flat case — which is most posts — silently falls outside the gate.
    """
    def literal(chunk):
        return re.escape(chunk).replace(r"\*", "[^/]*").replace(r"\?", "[^/]")

    rx, rest = "", pattern
    while rest:
        cut = rest.find("**")
        if cut < 0:
            rx += literal(rest)
            break
        prefix, after = rest[:cut], rest[cut + 2:]
        if after.startswith("/"):
            # `a/**/b`: the whole middle, separators included, is optional, so
            # that `blog/**/*.md` still covers `blog/post.md`.
            head = literal(prefix.rstrip("/"))
            rx += (head + "/(?:.*/)?") if head else "(?:.*/)?"
            rest = after[1:]
        else:
            # `a/**`: the separator before it is real; `blogx/` is not `blog/`.
            rx += literal(prefix) + ".*"
            rest = after
    return re.fullmatch(rx, path) is not None


def is_exempt(rel):
    return rel.startswith(EXEMPT_PREFIXES)


def walk(root, rel_dir):
    base = os.path.join(root, rel_dir)
    if not os.path.isdir(base):
        return
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in {".git", "__pycache__"})
        for name in sorted(filenames):
            yield os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")


def collect_surfaces(root, site_dir, with_templates=True):
    """Repo-relative surface paths, deduplicated and ordered."""
    found, seen = [], set()

    def add(rel):
        if rel in seen:
            return
        if os.path.isfile(os.path.join(root, rel)):
            seen.add(rel)
            found.append(rel)

    for rel in NAMED_SURFACES:
        add(rel)

    for rel in walk(root, site_dir):
        # Everything the renderer publishes that carries words: pages, feeds,
        # and the JSON exports that sit next to them.
        if rel.endswith(MARKUP_EXT) or rel.endswith(DATA_EXT):
            add(rel)

    for pattern in SURFACE_GLOBS:
        top = pattern.split("/", 1)[0]
        for rel in walk(root, top):
            if glob_match(pattern, rel) and not (is_exempt(rel) and rel not in NAMED_SURFACES):
                add(rel)

    if with_templates:
        for pattern in TEMPLATE_GLOBS:
            top = pattern.rsplit("/", 1)[0]
            for rel in walk(root, top):
                if glob_match(pattern, rel):
                    add(rel)

    return found


def exempt_paths(root):
    """Every tracked-looking file the §0 boundary keeps out of the gate."""
    out = []
    for prefix in ("doc", "council", ".claude"):
        for rel in walk(root, prefix):
            if rel.endswith((".md", ".txt", ".html")) and rel not in NAMED_SURFACES:
                out.append(rel)
    return out


# --------------------------------------------------------------------------
# scanning
# --------------------------------------------------------------------------
def scan_file(root, rel, patterns):
    """[(tier, lineno, pattern, matched_text, waiver_reason_or_None)].

    Each line is examined in three views, because a banned phrase can hide in
    the seams between them:

      `text`    the visible copy, words separated as a reader sees them.
      `glued`   the same line with tag boundaries closed, so `wall<span>et`
                is the word it renders as.
      `window`  the line joined to the one after it, with a trailing hyphen
                eaten, so a phrase that wraps — `earn` / `credits`, `token-` /
                `omics` — is still one phrase.  A window hit counts only if the
                match actually crosses the join; otherwise it is the next
                line's own hit, and the next line reports it.

    Each (line, pattern) pair is reported once, so widening the search does not
    multiply the failure list.  A boundary hit is waived by a waiver on either
    of the two lines it spans.
    """
    text, glued, waivers = read_surface(os.path.join(root, rel))
    order = sorted(text)
    following = {line: order[i + 1] for i, line in enumerate(order[:-1])}
    hits, seen = [], set()
    for lineno in order:
        nxt = following.get(lineno)
        window, boundary = None, 0
        if nxt is not None:
            head = re.sub(r"(\w)-$", lambda m: m.group(1) + "\x00",
                          text[lineno].rstrip())
            window = (head + " " + text[nxt]).replace("\x00 ", "")
            boundary = len(window) - len(text[nxt])
        for tier, _src, pattern, compiled in patterns:
            if (lineno, pattern) in seen:
                continue
            waived = waivers.get(lineno)
            found = compiled.search(text[lineno]) or compiled.search(
                glued.get(lineno, ""))
            if not found and window is not None:
                spanning = compiled.search(window)
                if spanning and spanning.start() < boundary < spanning.end():
                    found = spanning
                    waived = waived or waivers.get(nxt)
            if not found:
                continue
            seen.add((lineno, pattern))
            hits.append((tier, lineno, pattern, found.group(0), waived))
    return hits, text


def required_string_failures(rel, text):
    """§1.6 job two: assert presence, which a banlist cannot express."""
    blob = normalise(text)
    trigger = REQUIRED_TRIGGER.search(blob)
    if trigger and REQUIRED_STRING not in blob:
        return [(rel, trigger.group(0))]
    return []


def die(message):
    sys.stderr.write("vocab-gate: %s\n" % message)
    raise SystemExit(2)


def main(argv=None):
    ap = argparse.ArgumentParser(description="banned-wordlist gate")
    ap.add_argument("--root", default=".")
    ap.add_argument("--site", default="site",
                    help="rendered site directory (default: site)")
    ap.add_argument("--wordlist", default="doc/standards/banned-words.txt")
    ap.add_argument("--no-templates", action="store_true",
                    help="scan only the render output and published Markdown")
    ap.add_argument("--list", action="store_true", help="print the surfaces and exit")
    ap.add_argument("--audit", action="store_true",
                    help="also report what the §0 exemption suppresses, and exit 0 on it")
    ap.add_argument("--require-site", action="store_true",
                    help="fail if the rendered site is missing (CI renders first)")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    patterns = load_wordlist(os.path.join(root, args.wordlist))
    surfaces = collect_surfaces(root, args.site, not args.no_templates)

    if args.list:
        for rel in surfaces:
            print(rel)
        return 0

    site_pages = [s for s in surfaces if s.startswith(args.site + "/")]
    if args.require_site and not site_pages:
        die("no rendered pages under %s/ — render the site before the gate" % args.site)

    print("== banned-wordlist gate")
    print("   %d patterns (%d fail-level, %d review-required) over %d surfaces"
          % (len(patterns),
             sum(1 for p in patterns if p[0] == FAIL),
             sum(1 for p in patterns if p[0] == REVIEW),
             len(surfaces)))
    if not site_pages:
        print("   NOTE: no rendered pages under %s/ — source surfaces only" % args.site)

    sources = [s for s in surfaces if s not in site_pages]
    failures, missing, granted, allowed = [], [], {}, []

    # Pass 1: the authored sources, where waivers live.
    for rel in sources:
        hits, text = scan_file(root, rel, patterns)
        for tier, lineno, pattern, matched, is_waived in hits:
            if tier == FAIL:
                failures.append((rel, lineno, "BANNED", pattern, matched, None))
            elif is_waived:
                allowed.append((rel, lineno, pattern, matched, is_waived))
                granted.setdefault((pattern, matched.lower()), (rel, lineno, is_waived))
            else:
                failures.append((rel, lineno, "REVIEW-REQUIRED", pattern, matched, None))
        missing.extend(required_string_failures(rel, text))

    # Pass 2: the render, which is what the public actually reads.
    for rel in site_pages:
        hits, text = scan_file(root, rel, patterns)
        for tier, lineno, pattern, matched, is_waived in hits:
            if tier == FAIL:
                failures.append((rel, lineno, "BANNED", pattern, matched, None))
            elif is_waived or (pattern, matched.lower()) in granted:
                if is_waived:
                    allowed.append((rel, lineno, pattern, matched, is_waived))
                else:
                    src_rel, src_line, reason = granted[(pattern, matched.lower())]
                    allowed.append((rel, lineno, pattern, matched,
                                    "via %s:%d — %s" % (src_rel, src_line, reason)))
            else:
                failures.append((rel, lineno, "REVIEW-REQUIRED", pattern, matched, "render"))
        missing.extend(required_string_failures(rel, text))

    for rel, lineno, rule, pattern, matched, where in failures:
        if rule == "BANNED":
            why = "banned outright — no waiver path"
        elif where == "render":
            why = ("review-required — published copy with no <!-- vocab-ok: reason -->"
                   " on this line and no waiver for it in any published source")
        else:
            why = ("review-required — needs an inline <!-- vocab-ok: reason -->"
                   " on this line")
        print("FAIL %s:%d: %s %s (pattern %s) — %s"
              % (rel, lineno, rule, repr(matched), pattern, why))
    for rel, trigger in missing:
        print("FAIL %s:0: REQUIRED-STRING %r absent — the surface presents the "
              "mechanism (matched %r), so it must carry the first-screen string "
              "verbatim (vocabulary-and-visual.md §1.6)"
              % (rel, REQUIRED_STRING, trigger))

    # A waiver nobody sees is a waiver nobody reviewed, and the source-to-render
    # fallback in particular grants site-wide permission from one authored line.
    for rel, lineno, pattern, matched, reason in allowed:
        print("WAIVED %s:%d: %s (pattern %s) — %s" % (rel, lineno, repr(matched),
                                                      pattern, reason))
    print("   %d waived review-required hits, %d failures"
          % (len(allowed), len(failures) + len(missing)))

    if args.audit:
        skipped = exempt_paths(root)
        counts = {FAIL: 0, REVIEW: 0}
        for rel in skipped:
            for tier, _l, _p, _m, _w in scan_file(root, rel, patterns)[0]:
                counts[tier] += 1
        print("== §0 audit: %d exempt files hold %d fail-level and %d "
              "review-required hits that the scope boundary suppresses"
              % (len(skipped), counts[FAIL], counts[REVIEW]))

    if failures or missing:
        return 1
    print("== banned-wordlist gate: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
