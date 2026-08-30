#!/usr/bin/env python3
"""The blog: the broadcast surface, rendered from the repository.

council/socaity-ue3: the canonical build-in-public surface is a blog living in
this repository and rendered by the z61 generator. A post is a commit -- there
is no editor, no draft database and no publish button; a post exists when a
Markdown file exists in the merged tree, and its edit history is its file
history. That is what makes the archive checkable: the register on /blog links
every post to its own commit log, so a silently rewritten post is a visible
force-push and nothing else.

Emitted pages, all under blog/ (no other generator may claim these paths):

  blog/index.html               the archival register: every post, newest
                                first, with its source file and its commits
  blog/<slug>/index.html        one post
  blog/<slug>/card/index.html   the 1200x630 card that social previews crop to
                                -- authored as the disclosure (xuz, V10), not
                                as a headline
  blog/feed.xml                 RSS 2.0

Post sources are blog/posts/<slug>.md with a small `---` delimited header of
`key: value` lines. The header is deliberately not YAML: tools/blog/digest.py
writes these files with the standard library alone, and one format both halves
can read without a dependency is worth more than nesting nobody needs.

  title       the post title
  date        YYYY-MM-DD, the day the post was written
  kind        note | letter | digest
  authorship  human | machine   (machine is a label, never a disclaimer: V8)
  summary     one sentence, reused verbatim as the feed description
  card        the disclosure text the preview card carries, authored
  generator   digest posts only: the command that produced the file
  window      digest posts only: the history window the post was derived from

DETERMINISM. This module reads files and nothing else. It never shells out to
git, never reads the environment and never asks the operating system what time
it is -- including in the feed, where `pubDate` comes from the post's own
header and the channel carries no `lastBuildDate` at all (see feed_xml). The
weekly digest IS derived from git history, but that derivation happens in
tools/blog/digest.py, whose output is a committed file. A renderer that read
git would make the site a function of how deep you cloned.
"""

import os
import re
import xml.etree.ElementTree as ET

# The public origin. Feed items need absolute URLs; a relative guid is not one.
SITE = "https://socaity.dev/"
SITE_HOST = "socaity.dev"
REPO_BLOB = "https://github.com/socaity/socaity.dev/blob/main/"
REPO_COMMITS = "https://github.com/socaity/socaity.dev/commits/main/"

POSTS_DIR = ("blog", "posts")
DISCUSSIONS = ("blog", "discussions.json")

# The register line every surface that presents the record opens with (1ux)
# now lives in render.py as REGISTER_LINE and reaches every card through
# ctx["card_page"] (§G). A second copy here would be a second disclosure.

# Which posts have to carry it, decided by the post's own words rather than by
# an author remembering. Same trigger the standard's gate applies
# (doc/standards/vocabulary-and-visual.md 1.6, tools/gates/vocab_gate.py).
#
# The renderer refuses to build such a post when its source is missing the line,
# rather than adding the line to the page itself. A renderer that supplied the
# required copy would make the source file and the published surface say
# different things, and the source is the surface people fork.
REGISTER_TRIGGER = re.compile(
    r"\b(the ledger|the contribution ledger|epoch shares?|valuation units?|"
    r"subsidy multiplier|earliness premium)\b", re.IGNORECASE)
REQUIRED_STRING = "No token. Nothing to trade."

KINDS = {
    "note": ("Note", "a short written record of something that changed"),
    "letter": ("Founder letter", "the monthly human post: decisions, open "
                                 "questions, and what was missed"),
    "digest": ("Weekly digest", "written by a program from the commit history "
                                "and the record, on a schedule"),
}

NAV = [{"label": "Blog", "href": "blog/", "order": 70}]

# RFC 822 wants English abbreviations regardless of the machine's locale, so
# they are spelled out here: strftime("%a") would make the feed depend on LC_TIME.
DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


# ---------------------------------------------------------------------------
# post sources
# ---------------------------------------------------------------------------
def parse_header(text, path):
    """Split the `---` header from the body. Returns (dict, body)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise SystemExit("blog: %s has no --- header" % path)
    header, body_at = {}, None
    for number, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body_at = number + 1
            break
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise SystemExit("blog: %s header line %d is not key: value"
                             % (path, number))
        header[key.strip()] = value.strip()
    if body_at is None:
        raise SystemExit("blog: %s header is never closed" % path)
    return header, "\n".join(lines[body_at:])


def rfc822(date, offset="+0000"):
    """A calendar day as an RFC 822 date-time, without touching the clock."""
    year, month, day = (int(part) for part in date.split("-"))
    # Zeller-free: the standard library's date object does the calendar, and
    # weekday() is a pure function of the three integers above.
    import datetime
    weekday = datetime.date(year, month, day).weekday()
    return "%s, %02d %s %04d 00:00:00 %s" % (
        DAYS[weekday], day, MONTHS[month - 1], year, offset)


def load_posts(root):
    """Every post in blog/posts, newest first. Ties break on slug, always."""
    directory = os.path.join(root, *POSTS_DIR)
    posts = []
    if not os.path.isdir(directory):
        return posts
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(directory, name)
        with open(path, encoding="utf-8") as handle:
            header, body = parse_header(handle.read(), name)
        for required in ("title", "date", "kind", "authorship", "summary", "card"):
            if not header.get(required):
                raise SystemExit("blog: %s is missing `%s:`" % (name, required))
        if header["kind"] not in KINDS:
            raise SystemExit("blog: %s has unknown kind %r" % (name, header["kind"]))
        if header["authorship"] not in ("human", "machine"):
            raise SystemExit("blog: %s has unknown authorship %r"
                             % (name, header["authorship"]))
        slug = name[:-3]
        source = "/".join(POSTS_DIR) + "/" + name
        posts.append({
            "slug": slug,
            "title": header["title"],
            "date": header["date"],
            "kind": header["kind"],
            "kind_label": KINDS[header["kind"]][0],
            "kind_meaning": KINDS[header["kind"]][1],
            "authorship": header["authorship"],
            "machine": header["authorship"] == "machine",
            "summary": header["summary"],
            "card": header["card"],
            "generator": header.get("generator"),
            "window": header.get("window"),
            "body": body,
            "source": source,
            "source_url": REPO_BLOB + source,
            "history_url": REPO_COMMITS + source,
            "url": SITE + "blog/" + slug + "/",
            "pubdate": rfc822(header["date"]),
        })
    posts.sort(key=lambda post: (post["date"], post["slug"]), reverse=True)
    return posts


def load_discussions(root):
    """slug -> discussion URL, written back by the announce step after it runs.

    A missing or empty file is the honest state before the first digest is
    announced; the register simply carries no discussion link for that row.
    Nothing here invents a thread that does not exist (V12).
    """
    import json
    path = os.path.join(root, *DISCUSSIONS)
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    return {str(k): str(v) for k, v in sorted(data.items())}


# ---------------------------------------------------------------------------
# links
# ---------------------------------------------------------------------------
# A root-absolute link (`/blog/feed.xml`) is the natural thing to write in a
# post and the wrong thing to publish. It assumes the site is served from the
# root of a domain, and this one is not necessarily: .github/workflows/graph-
# check.yml deploys with actions/deploy-pages from a repository named
# `socaity.dev` rather than `<owner>.github.io`, which GitHub serves as a
# PROJECT site under a path prefix (`https://<owner>.github.io/socaity.dev/`).
# `/blog/` under that deploy resolves to `<owner>.github.io/blog/` — a 404 —
# and under a `file://` preview of site/ it resolves to the filesystem root.
# The workflow deliberately refuses to feed configure-pages' base_path into the
# renderer (that would make the site a function of CI rather than of the tree),
# so the only base-independent form is a relative one, which is correct under
# every base at once: domain root, path prefix, and file://.
ROOT_RELATIVE_ATTR = re.compile(r'\b(href|src)="/(?!/)')


def site_relative(html, depth):
    """Root-absolute site links -> page-relative ones. `//host` is left alone."""
    return ROOT_RELATIVE_ATTR.sub(lambda m: '%s="%s' % (m.group(1), "../" * depth),
                                  html)


# ---------------------------------------------------------------------------
# feed
# ---------------------------------------------------------------------------
def feed_xml(posts):
    """RSS 2.0, serialised by a real XML writer rather than string formatting.

    The determinism trap in every feed generator is the pair of timestamps RSS
    invites you to stamp with the wall clock: `lastBuildDate` (when this file
    was built) and a `pubDate` defaulted to "now" for undated items. Both are
    optional in RSS 2.0, and both would make two builds of one tree differ.
    So: no `lastBuildDate` at all, and the channel's `pubDate` is the newest
    item's own date. Every item date comes from the post header, which for the
    weekly digest is itself derived from the commit history it summarises.
    """
    ET.register_namespace("atom", "http://www.w3.org/2005/Atom")
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")

    def text(parent, tag, value, attrib=None):
        node = ET.SubElement(parent, tag, attrib or {})
        node.text = value
        return node

    text(channel, "title", "socaity.dev")
    text(channel, "link", SITE + "blog/")
    text(channel, "description",
         "Build-in-public posts from the socaity.dev repository. Every post is "
         "a commit; the weekly digest is written by a program from the commit "
         "history and the record.")
    text(channel, "language", "en")
    text(channel, "docs", "https://www.rssboard.org/rss-specification")
    text(channel, "generator", "tools/render/generators/blog.py")
    # Qualified name, not the literal string "atom:link": only the {uri}tag form
    # makes the writer declare the prefix, and an undeclared prefix is a feed
    # that no XML parser will open.
    ET.SubElement(channel, "{http://www.w3.org/2005/Atom}link", {
        "href": SITE + "blog/feed.xml", "rel": "self",
        "type": "application/rss+xml"})
    if posts:
        text(channel, "pubDate", posts[0]["pubdate"])

    for post in posts:
        item = ET.SubElement(channel, "item")
        text(item, "title", post["title"])
        text(item, "link", post["url"])
        text(item, "guid", post["url"], {"isPermaLink": "true"})
        text(item, "pubDate", post["pubdate"])
        text(item, "category", post["kind_label"])
        text(item, "description", post["summary"])

    body = ET.tostring(rss, encoding="unicode")
    return '<?xml version="1.0" encoding="utf-8"?>\n' + body + "\n"


# ---------------------------------------------------------------------------
# pages
# ---------------------------------------------------------------------------
def generate(ctx):
    env, root = ctx["env"], ctx["root"]
    posts = load_posts(root)
    threads = load_discussions(root)
    pages = {}

    index = env.get_template("blog_index.html")
    post_template = env.get_template("blog_post.html")

    kinds = [{"key": key, "label": label, "meaning": meaning}
             for key, (label, meaning) in sorted(KINDS.items())]

    pages["blog/index.html"] = index.render(
        posts=posts, kinds=kinds, threads=threads, depth=1, feed_url="feed.xml")
    pages["blog/feed.xml"] = feed_xml(posts)

    for post in posts:
        # Whitespace-collapsed, because the required string is a sentence and a
        # sentence wraps across lines in a Markdown source. The gate normalises
        # the same way before asserting its presence.
        whole = " ".join(" ".join(
            [post["title"], post["summary"], post["card"], post["body"]]).split())
        if REGISTER_TRIGGER.search(whole) and REQUIRED_STRING not in whole:
            raise SystemExit(
                "blog: %s presents the record (%r) but its source is missing "
                "the first-screen string %r — see "
                "doc/standards/vocabulary-and-visual.md V14"
                % (post["source"], REGISTER_TRIGGER.search(whole).group(0),
                   REQUIRED_STRING))
        view = dict(post)
        view["html"] = site_relative(
            ctx["render_markdown"](post["body"], post["source"], 2), 2)
        view["thread"] = threads.get(post["slug"])
        pages["blog/%s/index.html" % post["slug"]] = post_template.render(
            post=view, depth=2)
        # The same card object as every other surface (§G). blog_card.html was
        # its ancestor; it is now card.html and this generator is one caller of
        # it, so a change to the card is a change in one file rather than two
        # that agree by hand.
        pages["blog/%s/card/index.html" % post["slug"]] = ctx["card_page"](
            env,
            kind_label=view["kind_label"], machine=view["machine"],
            date=view["date"], title=view["title"], detail=view["card"],
            url=view["url"], foot=SITE_HOST + "/blog/" + post["slug"] + "/",
            og_type="article")

    return pages
