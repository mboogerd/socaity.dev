#!/usr/bin/env python3
"""Static-site generator for the needs graph (council/socaity-z61.md).

PyYAML + jinja2, no framework. The site is a pure function of the merged tree:
no wall clock, no network, no database. Two runs over the same tree produce
byte-identical output, so a clone plus one command reproduces CI.

Emits, under --out:
  index.html                       the manifesto, rendered from doc/manifesto.md
  faq/index.html                   doc/faq.md
  roadmap/index.html               root node pages + "what matters now" strip
  n/<id>/index.html                focus+context node pages
  s/<slug>/index.html              slug redirects (IDs stay the durable ref)
  all/index.html                   flat index for auditors
  graph.json                       lossless export / M1 ingestion seam
  sections.json                    node-page sections, for the CI diff bot
  ...plus whatever tools/render/generators/*.py contribute (see HOOK below).

Usage:
  python3 tools/render/render.py [--root .] [--out site]
"""

import argparse
import importlib.util
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jinja2 import Environment, FileSystemLoader, select_autoescape  # noqa: E402

import graphlib as g  # noqa: E402
import markdown_subset as md  # noqa: E402

# The published 1:1 mapping table (CONTRIBUTING.md + the legend on every page).
NODE_CHIPS = {
    "open": ("Open", "open"),
    "resolved": ("Done", "done"),
    "withdrawn": ("Withdrawn", "withdrawn"),
    "merged": ("Merged into →", "merged"),
}
EDGE_CHIPS = {
    "asserted": None,  # quiet default, published in the legend
    "disputed": ("Contested", "contested"),
    "settled": ("Settled", "settled"),
}
LEGEND = [
    # The two provenance kinds, named symmetrically (council/socaity-0hb.md
    # §E). The pair is a closed set of exactly two strings and the html gate
    # holds every .prov object to it. The wording is load-bearing: `written
    # by a person` / `written by a program` differ in one noun and rank
    # neither. `unverified`, `AI-generated`, `automated` and every badge or
    # verification grammar are forbidden here — `unverified` worst of all,
    # because it names an absence and invites the reader to supply the
    # positive term. A human write always carries its mark too: absence of a
    # mark is never the human signal.
    ("written by a person", "provenance kind: a person wrote this assertion"),
    ("written by a program", "provenance kind: a program wrote this assertion"),
    ("Open", "node status open"),
    ("Done", "node status resolved"),
    ("Withdrawn", "node status withdrawn; the page stays reachable"),
    ("Merged into →", "node status merged; links the surviving node"),
    # The legend is the published glossary and it is now the only place on the
    # site that still spoke the pre-§D vocabulary. Two words had to go. `badge`
    # is the object §D removed — there are no badges here, there are chips with
    # a marker, a word and a value — and §E forbids badge grammar anywhere near
    # the provenance kinds two rows above. `dispute` is the microcopy §D
    # replaces with `read the contest`, applied everywhere in node.html and
    # missed here, which left the glossary teaching a word no surface uses.
    ("(no chip)", "edge status asserted"),
    # `disputed` stays: it is the edge's value in the schema, and this table is
    # the published 1:1 mapping from a chip to the graph state behind it. What
    # changes is the reader-facing half of the sentence.
    ("Contested", "edge status disputed; links the contest"),
    ("Settled", "edge status settled; links the resolving record"),
]
ISSUE_URL = "https://github.com/socaity/socaity.dev/issues/new"
REPO_BLOB = "https://github.com/socaity/socaity.dev/blob/main/"
REPO_TREE = "https://github.com/socaity/socaity.dev/tree/main/"
#: This site's own canonical origin.  A link in doc/*.md that names a PAGE of
#: this site rather than a file in the repository is written absolutely, so it
#: resolves for a reader on GitHub, and `doc_link_rewriter` turns it back into
#: a relative path at render time, so the built page — and a fork's build, and
#: a `file://` reading of it — never leaves its own tree.  `../ledger/` still
#: means the ledger's SOURCE: the glass house is a list of artifacts and those
#: links must stay repository links, so the two intents keep two spellings.
SITE = "https://socaity.dev/"

# --- the card (council/socaity-0hb.md §G) ---------------------------------
#
# One 1200x630 object per surface, one template, one register sentence. The
# sentence lives here rather than in a generator because §G puts the same card
# on home, /ledger, /claim, /faq, /roadmap, every node and every post: two
# copies of a disclosure are two disclosures.
REGISTER_LINE = ("A public record of contributions. No token. Nothing to "
                 "trade. This is a database.")

# The card box and the type scale card.html declares, restated once so the fit
# check below measures the thing that actually renders. Keep the two in step:
# a size changed in the stylesheet and not here is a card that overflows
# silently, which is the failure §G names.
CARD_BOX = (1200, 630)
CARD_PAD = (72, 64)                       # x, y
#            key           px  line-height  margin-top  em-per-char
CARD_BLOCKS = (("strip",   20, 1.6,  0, 0.55),
               ("title",   54, 1.2, 24, 0.55),
               ("register", 44, 1.3, 28, 0.55),
               ("detail",  32, 1.45, 24, 0.55),
               ("foot",    20, 1.6, 21, 0.55))   # 20px padding + 1px rule


def card_overflow(card):
    """Estimated laid-out height minus the content box, in pixels.

    Deliberately an estimate and deliberately pessimistic. There is no
    renderer in this toolchain, so the alternative to arithmetic is a headless
    browser in CI, and §J refuses screenshot-class checks as required gates.
    `em-per-char` is set above Georgia's own average because §A tunes the
    design against the LAST resolvable entry in the font stack, not the first:
    a card that fits only in Georgia is a card that overflows on a machine
    that has none of the stack.

    The number this returns is what fails the build. It cannot prove a card
    fits; it can prove one does not, which is the direction that matters when
    what falls off the bottom is the disclosure.
    """
    width = CARD_BOX[0] - 2 * CARD_PAD[0]
    height = CARD_BOX[1] - 2 * CARD_PAD[1]
    # The register is measured whether or not the caller has passed it: it is
    # the object §G says must never be the one that falls off, so a check that
    # skipped it when it was still a default would be measuring the card that
    # cannot overflow instead of the card that ships.
    card = dict(card)
    card.setdefault("register", REGISTER_LINE)
    # The strip is one line on every card by construction (wordmark, kind,
    # optional "written by a program", optional date), and the template builds
    # it rather than the caller, so it is measured as its own line here.
    card.setdefault("strip", "socaity.dev")
    used = 0
    for key, size, lh, margin, per_char in CARD_BLOCKS:
        text = str(card.get(key) or "")
        if not text:
            continue
        lines = max(1, -(-int(len(text) * size * per_char) // width))
        used += margin + int(round(lines * size * lh))
    return used - height


def first_sentence(text):
    """The first sentence of a node statement, for its card and its og tags.

    A node body is prose written for the node page, not a summary written for
    a crop. Taking its first sentence is the honest reduction: it is the
    author’s own words, and it is short enough that the card fit check
    below does not have to truncate anything mid-clause.
    """
    flat = " ".join((text or "").split())
    cut = flat.find(". ")
    return flat[:cut + 1] if cut != -1 else flat


def trim_detail(card):
    """Shorten a card’s detail line until the card fits, at a word boundary.

    Only for details taken from prose this renderer does not own — a node
    statement is written for the node page, and failing the build because an
    author wrote a long first sentence would make the card a constraint on the
    graph. Authored card copy (home, /faq, /roadmap, /claim, /ledger, posts)
    gets the hard failure instead, because there the fix is to write a shorter
    sentence and the build is the only thing that will ever say so.

    The register is untouched and stays above the detail, so what an ellipsis
    takes is the tail §G says a fixed box takes anyway.
    """
    words = str(card.get("detail") or "").split()
    while words and card_overflow(card) > 0:
        words.pop()
        card = dict(card, detail=" ".join(words) + "…")
    return card


def card_page(env, **card):
    """Render one card, or fail the build if its disclosure would not fit."""
    card.setdefault("register", REGISTER_LINE)
    card.setdefault("og_type", "website")
    over = card_overflow(card)
    if over > 0:
        raise SystemExit(
            "card for %s overflows its 1200x630 box by ~%dpx: shorten the "
            "headline or the detail sentence. §G: overflow fails the build "
            "rather than shipping a card whose disclosure fell off the bottom."
            % (card.get("url", card.get("title", "?")), over))
    return env.get_template("card.html").render(card=card)


# Markdown documents published as site pages. The .md file in doc/ is the only
# copy of the copy: this renders it, it never restates it. Changing the words
# is a change to the Markdown, in its own PR, under the wordlist gate.
DOC_PAGES = [
    {"source": "doc/manifesto.md", "path": "index.html", "nav": "Home"},
    {"source": "doc/faq.md", "path": "faq/index.html", "nav": "FAQ"},
]

# The card and og copy for the surfaces core renders (§G). Keyed by the page's
# own path, which is the same key `emit` uses, so a surface cannot acquire a
# card without acquiring a page.
#
# `title` is the card HEADLINE, and it is not the page's <h1>: a headline that
# survives a 1200x630 crop with no site around it is a different sentence from
# one read under a masthead. /faq is the case that makes the rule visible — its
# headline is the consent sentence rather than "FAQ", because the asset a
# maintainer meets first should be the commitment, not the furniture
# (socaity-0hb round 2, objection 9).
#
# `card: False` means og tags without a 1200x630 page. /all is a table of every
# node; there is no sentence it could put at 44px that a node's own card would
# not say better, and §G does not list it.
CARD_SURFACES = {
    "index.html": {
        "kind_label": "manifesto",
        "title": "The system never assigns work. It prices it.",
        "detail": "A needs graph anyone can contest, a published rule that "
                  "prices the work, and a record you can replay yourself.",
    },
    "faq/index.html": {
        "kind_label": "questions",
        "title": "Consent precedes contribution.",
        "detail": "A maintainer’s “no” is not a low weight; it is a "
                  "wall. Four predictable objections, answered before they "
                  "are raised.",
    },
    "roadmap/index.html": {
        "kind_label": "roadmap",
        "title": "Our own roadmap, in the platform’s own conventions.",
        "detail": "Every open problem in the needs graph, with what it "
                  "requires and what it competes with.",
    },
    "all/index.html": {
        "card": False,
        "kind_label": "index",
        "title": "All nodes",
        "detail": "Every node in the merged tree, including withdrawn and "
                  "merged ones. Sorted by permanent ID.",
    },
}


def surface_card(path, **extra):
    """The card/og view for one page path. One dict feeds both."""
    spec = dict(CARD_SURFACES.get(path) or {})
    spec.update(extra)
    href = path[:-len("index.html")]
    spec.setdefault("url", SITE + href)
    spec.setdefault("foot", "socaity.dev/" + href)
    return spec


# Every M0 surface, in nav order. `published: False` means the surface is a
# stub today: it gets a page saying so, because a nav entry that 404s is a
# worse answer than one that admits the gap. A generator claims a surface by
# exporting a NAV entry with the same href (see the HOOK block below).
#
# `/claim` is deliberately NOT here (council/socaity-0hb.md §I). It is a
# rendered surface with no nav membership: a nav entry is a routing fact, and
# the routing fact this site wants is that you arrive at /claim FROM A REASON
# TO CLAIM — an unclaimed ticket, a roadmap row, the empty second line of the
# ledger, the comment on your merged pull request — never from a directory
# listing on all 26 pages, where `Ledger · Claim` reads balance → withdraw.
# Re-adding it here (or a NAV export in generators/claim.py, which would
# publish this entry rather than create one) reinstates that reading. The
# orphan BFS in tools/gates/html_gate.py (check E) is what keeps the page
# reachable without it, and it goes red if the in-body link set is broken.
SURFACES = [
    {"label": "Home", "href": "", "order": 10, "published": True},
    {"label": "Roadmap", "href": "roadmap/", "order": 20, "published": True},
    {"label": "Ledger", "href": "ledger/", "order": 30, "published": False,
     "summary": "the contribution record itself — every entry with its evidence, "
                "and every displayed number computed from a published artifact.",
     "path": "ledger/index.html"},
    {"label": "FAQ", "href": "faq/", "order": 50, "published": True},
    {"label": "All nodes", "href": "all/", "order": 60, "published": True},
]

# ---------------------------------------------------------------------------
# HOOK — how /ledger, /claim, the blog, and anything after them add pages
# ---------------------------------------------------------------------------
# Drop a module in tools/render/generators/. Do not edit this file to add a
# page. Modules are loaded in sorted filename order and may export:
#
#   NAV = [{"label": "Blog", "href": "blog/", "order": 70}]      # optional
#       Nav entries, merged into SURFACES above and sorted by "order" (ties
#       break on label). An entry whose "href" equals an existing surface's
#       marks that surface published and replaces its stub page — that is how
#       the ledger generator switches /ledger from "not yet published" to real.
#
#   def generate(ctx):                                            # required
#       return [("ledger/index.html", "<!doctype html>...")]
#       An iterable of (path, html) pairs. `path` is relative to the site root
#       and uses "/" separators; `html` is the complete page text. Returning a
#       dict of the same shape also works. Paths are written in sorted order;
#       two generators claiming one path is an error, not a silent last-wins.
#
# ctx is a dict:
#   root, out       absolute paths to the repo and the output directory
#   env             the Jinja environment; templates live in ../templates, so
#                   {% extends "base.html" %} works and gives you the shared
#                   nav, footer and stylesheet. base.html defines four blocks,
#                   all optional except the two you will always want:
#                     {% block title %}  the <title>, before " · socaity"
#                     {% block main %}   the page body, inside <main>
#                     {% block head %}   extra <head> tags — per-surface og
#                                        tags and the like (ledger.html uses it)
#                     {% block rail %}   the left rail of the two-track grid.
#                                        EMPTY BY DEFAULT: fill only title and
#                                        main and you still get a correct,
#                                        single-column page. Its contents are a
#                                        closed list — provenance, freshness,
#                                        permalinks, breadcrumbs, chip rows,
#                                        publication-status. Consent, refusal
#                                        and reassurance stay in the text
#                                        column (council/socaity-0hb.md §C).
#                   Pass depth=<number of path segments above the file>, e.g.
#                   depth=1 for ledger/index.html.
#   nav             the final nav list, already merged and sorted
#   nodes           the rendered node views, sorted by id (see node_view)
#   tickets_by_node {node id: ticket dict}
#   clock           the graph clock: the newest assertion in the merged tree
#   render_markdown(text, path_of_the_source_file, depth=None) -> HTML fragment,
#                   with the repo-relative links rewritten and the vocab-ok HTML
#                   comments stripped. `depth` is the depth of the page you are
#                   WRITING (same number you pass to the template), because that
#                   is what the "../" in a rewritten link is relative to. It
#                   defaults to the depth of the source path, which is right
#                   only when the two happen to match — pass it explicitly.
#
# Two rules the hook cannot enforce for you, and check.sh will catch:
#   1. Determinism. No wall clock, no os.environ, no network, no set/dict
#      iteration order that depends on hashing. Derive time from ctx["clock"].
#   2. The visual and vocabulary standard (doc/standards/vocabulary-and-visual.md)
#      applies to every page you emit, not only to the ones in this file.
# ---------------------------------------------------------------------------
GENERATORS_DIRNAME = "generators"


def day(stamp):
    return (stamp or "")[:10]


def provenance_line(prov):
    """One line of provenance, for the places a .prov object does not reach.

    Same two words as the object and the legend (council/socaity-0hb.md §E),
    because a second vocabulary is a second claim. What it used to say was
    `human-authored` against `agent-drafted, human-accountable`: asymmetric,
    and rankable in the one channel the geometry cannot cover — a reader
    orders authored above drafted without being told to, and `accountable`
    is the liability grammar the resolution refuses. `written by a person` /
    `written by a program` differ in one noun and rank neither.
    """
    by = (prov or {}).get("asserted_by") or {}
    who = by.get("actor_id", "unknown")
    if by.get("actor_kind") == "agent":
        who = "%s, on behalf of %s" % (who, by.get("on_behalf_of", "unknown"))
        kind = "written by a program"
    else:
        kind = "written by a person"
    return "Asserted by %s · %s · %s" % (who, kind, day(prov.get("asserted_at")))


def provenance_fields(prov):
    """The provenance record as FIELDS, for the .prov object (0hb §E).

    Data in, appearance out: this returns what the record says and nothing
    about how it looks. Which words name a kind, which class carries the
    fill pattern and what a missing model reads as are template decisions,
    because a class picked per value in Python is the presentation logic the
    resolution forbids.

    `kind` is the raw schema value, not a label — the validator already
    constrains actor_kind to human|agent, and a page that guessed would be
    asserting authorship it does not know.
    """
    prov = prov or {}
    by = prov.get("asserted_by") or {}
    return {
        "kind": "agent" if by.get("actor_kind") == "agent" else "human",
        "actor_id": by.get("actor_id") or "unknown",
        "on_behalf_of": by.get("on_behalf_of"),
        "model": by.get("model"),
        "run_id": by.get("run_id"),
        "asserted_at": day(prov.get("asserted_at")),
        "evidence": list(prov.get("evidence") or []),
    }


def estimate_view(rec, clock):
    """One estimate rendered with provenance and a freshness stamp, never bare."""
    kind = rec.get("kind")
    value = rec.get("value")
    if kind == "branch_probability":
        text = "weight recorded"  # no probability decimals at M0
    else:
        text = "%s–%s %s" % (value.get("low"), value.get("high"), rec.get("unit", ""))
    return {
        "id": rec.get("id"),
        "kind": kind,
        "text": text.strip(),
        "low": None if kind == "branch_probability" else value.get("low"),
        "high": None if kind == "branch_probability" else value.get("high"),
        "asserted_at": day((rec.get("provenance") or {}).get("asserted_at")),
        "provenance": provenance_line(rec.get("provenance")),
        "expires_at": day(rec.get("expires_at")),
        "stale": bool(rec.get("expires_at")) and rec["expires_at"] < clock,
    }


def dispute_link(edge):
    ref = edge.get("dispute_ref") or {}
    return ref.get("url")


def node_view(node, idx, tickets_by_node, clock):
    """Focus + context: the node, its parents, its children, its claims."""
    by_id, out, inc = idx["by_id"], idx["out"], idx["inc"]
    nid = node["id"]

    crumbs = []
    cur, hops = nid, 0
    while hops < 16:
        parents = [e for e in out.get(cur, []) if e.get("type") == "refines" and e.get("to") in by_id]
        if not parents:
            break
        cur = parents[0]["to"]
        if any(c["id"] == cur for c in crumbs):
            break
        crumbs.append({"id": cur, "title": by_id[cur]["title"]})
        hops += 1
    crumbs.reverse()

    requires = []
    for edge in out.get(nid, []):
        if edge.get("type") != "requires" or edge.get("to") not in by_id:
            continue
        target = by_id[edge["to"]]
        current, _hist = g.current_estimates(g.estimates_of(target))
        effort = current.get("effort")
        requires.append({
            "id": target["id"], "title": target["title"], "slug": target["slug"],
            "chip": NODE_CHIPS.get(target.get("status")),
            "done": target.get("status") == "resolved",
            "edge_chip": EDGE_CHIPS.get(edge.get("status")),
            "dispute_url": dispute_link(edge),
            "estimate": estimate_view(effort, clock) if effort else None,
        })

    approaches, refined_by, see_also = [], [], []
    for edge in inc.get(nid, []) + out.get(nid, []):
        other_id = edge["from"] if edge["to"] == nid else edge.get("to")
        if other_id not in by_id or other_id == nid:
            continue
        other = by_id[other_id]
        weights, _h = g.current_estimates(g.estimates_of(edge))
        prob = weights.get("branch_probability")
        card = {
            "id": other["id"], "title": other["title"], "slug": other["slug"],
            "body": other.get("body", "").strip(),
            "chip": NODE_CHIPS.get(other.get("status")),
            "edge_chip": EDGE_CHIPS.get(edge.get("status")),
            "dispute_url": dispute_link(edge),
            "rationale": edge.get("rationale"),
            "weight": prob.get("value") if prob else None,
            "weight_provenance": provenance_line(prob.get("provenance")) if prob else None,
            "weight_stamp": estimate_view(prob, clock)["asserted_at"] if prob else None,
        }
        if edge.get("type") == "equivalent_to":
            see_also.append(card)
        elif edge.get("type") == "refines" and edge["to"] == nid:
            (approaches if other["type"] == "solution" else refined_by).append(card)

    top = max([c["weight"] for c in approaches if c["weight"] is not None], default=None)
    for card in approaches:
        card["weight_label"] = ("currently favored" if card["weight"] == top and top is not None
                                else "open") if card["weight"] is not None else None
    approaches.sort(key=lambda c: c["id"])
    refined_by.sort(key=lambda c: c["id"])
    see_also.sort(key=lambda c: c["id"])

    current, history = g.current_estimates(g.estimates_of(node))
    estimates = []
    for kind in sorted(current):
        view = estimate_view(current[kind], clock)
        view["revisions"] = len(history.get(kind, []))
        view["history"] = [estimate_view(r, clock) for r in history.get(kind, [])]
        estimates.append(view)

    contested = sorted(
        [e for e in out.get(nid, []) + inc.get(nid, []) if e.get("status") == "disputed"],
        key=lambda e: e.get("id", ""))
    merged_into = by_id.get(node.get("merged_into"))
    ticket = tickets_by_node.get(nid)
    return {
        "id": nid, "slug": node["slug"], "type": node["type"], "title": node["title"],
        "body": node.get("body", "").strip(), "status": node.get("status"),
        "chip": NODE_CHIPS.get(node.get("status")),
        "merged_into": {"id": merged_into["id"], "title": merged_into["title"]} if merged_into else None,
        "external_ref": node.get("external_ref"),
        "provenance": provenance_line(node.get("provenance")),
        "prov": provenance_fields(node.get("provenance")),
        "crumbs": crumbs, "requires": requires, "approaches": approaches,
        "refined_by": refined_by, "see_also": see_also, "estimates": estimates,
        "contested_count": len(contested),
        "contested_links": [dispute_link(e) for e in contested if dispute_link(e)],
        "ticket": ticket,
        "issue_url": "%s?title=Contest+%s&body=Node%%3A+%s" % (ISSUE_URL, node["slug"], nid),
    }


def sections_of(view):
    """Flat, diffable text per page section — what the CI comment bot compares."""
    return {
        "title": view["title"],
        "status": "%s / %s" % (view["status"], view["chip"][0] if view["chip"] else "-"),
        "body": view["body"],
        "provenance": view["provenance"],
        "breadcrumbs": " > ".join(c["title"] for c in view["crumbs"]),
        "requires": [
            "%s [%s]%s" % (r["title"], r["chip"][0] if r["chip"] else "-",
                           " " + r["estimate"]["text"] if r["estimate"] else "")
            for r in view["requires"]],
        "approaches": [
            "%s%s%s" % (a["title"],
                        " (" + a["weight_label"] + ")" if a.get("weight_label") else "",
                        " [" + a["edge_chip"][0] + "]" if a["edge_chip"] else "")
            for a in view["approaches"]],
        "refined_by": [
            "%s%s" % (r["title"], " [" + r["edge_chip"][0] + "]" if r["edge_chip"] else "")
            for r in view["refined_by"]],
        "see_also": [
            "%s%s" % (s["title"], " [" + s["edge_chip"][0] + "]" if s["edge_chip"] else "")
            for s in view["see_also"]],
        # An edge flipping to disputed is the contest workflow's whole event: it
        # has to show up in the PR comment, not only in the HTML.
        "contested": ["%d contested edge(s)" % view["contested_count"]] + view["contested_links"],
        "estimates": ["%s: %s (asserted %s, %d revision(s)%s)"
                      % (e["kind"], e["text"], e["asserted_at"], e["revisions"],
                         ", stale" if e["stale"] else "")
                      for e in view["estimates"]],
    }


def what_matters_now(views, idx, tickets_by_node):
    """accepted (in the merged tree, open) AND unblocked AND unclaimed."""
    strip = []
    for view in views:
        ticket = tickets_by_node.get(view["id"])
        if view["status"] != "open" or not ticket:
            continue
        if ticket.get("status") != "open" or ticket.get("claimed_by"):
            continue
        if any(not r["done"] for r in view["requires"]):
            continue
        strip.append({"id": view["id"], "title": view["title"], "slug": view["slug"],
                      "type": view["type"], "tier": ticket.get("tier"), "ticket": ticket["id"],
                      # The node's own status chip and its contest address, so
                      # /roadmap can render a row that acts (A6) instead of a
                      # bullet that names. Both are already on the view; this
                      # carries them across, and decides nothing.
                      "chip": view["chip"], "issue_url": view["issue_url"]})
    strip.sort(key=lambda s: s["id"])
    return strip


def doc_link_rewriter(source, depth):
    """Rewrite a Markdown link so it still resolves once the page is on the web.

    A link in doc/*.md is written relative to the repository. On the site it
    has to point either at the sibling page we also publish, or at the file
    itself in the repository — the manifesto's "glass house" section is a list
    of artifacts, and a dead link there is the claim failing in public.
    """
    published = {p["source"]: p for p in DOC_PAGES}
    base = os.path.dirname(source)
    up = "../" * depth

    def rewrite(href):
        # Our own origin, made relative. Routing, not presentation: the
        # surface's address is read off the URL and nothing is decided here.
        if href.startswith(SITE):
            return (up + href[len(SITE):]) or "./"
        if href.startswith(("http://", "https://", "mailto:", "#", "/")):
            return href
        target, _, fragment = href.partition("#")
        fragment = ("#" + fragment) if fragment else ""
        if not target:
            return fragment
        repo_path = os.path.normpath(os.path.join(base, target)).replace(os.sep, "/")
        page = published.get(repo_path)
        if page:
            surface = os.path.dirname(page["path"])
            return "%s%s%s" % (up, surface + "/" if surface else "", fragment)
        # A link written at a directory stays a directory listing, not a blob.
        base_url = REPO_TREE if target.endswith("/") else REPO_BLOB
        return base_url + repo_path + fragment

    return rewrite


def doc_page(root, spec):
    """One Markdown document as a page view. The Markdown is the only source."""
    depth = spec["path"].count("/")
    with open(os.path.join(root, spec["source"]), encoding="utf-8") as fh:
        text = fh.read()
    return {
        "title": md.first_heading(text),
        "html": md.render_markdown(text, doc_link_rewriter(spec["source"], depth)),
        "source": spec["source"],
        "source_url": REPO_BLOB + spec["source"],
        "depth": depth,
        # The surface this document IS, in the same form the nav uses, so the
        # masthead can mark it aria-current (A3). Routing, not presentation:
        # it is the page's own address, restated once instead of guessed.
        "href": (os.path.dirname(spec["path"]) + "/") if os.path.dirname(spec["path"]) else "",
    }


def load_generators(here):
    """Import tools/render/generators/*.py in sorted order. See the HOOK block."""
    directory = os.path.join(here, GENERATORS_DIRNAME)
    modules = []
    if not os.path.isdir(directory):
        return modules
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".py") or name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(
            "socaity_generator_" + name[:-3], os.path.join(directory, name))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "generate"):
            raise SystemExit("generator %s exports no generate(ctx)" % name)
        modules.append((name, module))
    return modules


def merge_nav(modules):
    """SURFACES plus generator NAV entries; a matching href marks it published."""
    nav = {s["href"]: dict(s) for s in SURFACES}
    for name, module in modules:
        for entry in getattr(module, "NAV", []):
            merged = dict(nav.get(entry["href"], {}))
            merged.update(entry)
            merged["published"] = True
            merged.setdefault("order", 100)
            merged["generator"] = name
            nav[entry["href"]] = merged
    return sorted(nav.values(), key=lambda s: (s["order"], s["label"]))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="site")
    args = ap.parse_args(argv)
    root, out = os.path.abspath(args.root), os.path.abspath(args.out)

    nodes = g.load_nodes(root)
    tickets = g.load_tickets(root)
    idx = g.index(nodes)
    clock = g.graph_clock(nodes)
    tickets_by_node = {}
    for _p, _n, ticket in tickets:
        tickets_by_node.setdefault(ticket["node"], ticket)

    views = [node_view(n, idx, tickets_by_node, clock) for _p, _n, n in nodes]
    views.sort(key=lambda v: v["id"])
    roots = [v for v in views
             if v["type"] == "problem" and v["status"] == "open"
             and not any(e.get("type") == "refines" for e in idx["out"].get(v["id"], []))]

    here = os.path.dirname(os.path.abspath(__file__))
    env = Environment(
        loader=FileSystemLoader(os.path.join(here, "templates")),
        autoescape=select_autoescape(["html"]), keep_trailing_newline=True, trim_blocks=True,
        lstrip_blocks=True)
    generators = load_generators(here)
    nav = merge_nav(generators)
    env.globals.update(legend=LEGEND, clock=clock[:10], issue_url=ISSUE_URL, nav=nav)

    pages = {}

    def emit(path, html, who):
        if path in pages:
            raise SystemExit("two page sources claim %s: %s and %s"
                             % (path, pages[path][1], who))
        pages[path] = (html, who)

    # Every surface §G names gets a card, and every surface that gets a card
    # gets the og tags that point at it, from the same dict. The card page and
    # the <head> that advertises it cannot drift apart because there is only
    # one of them.
    for view in views:
        card = surface_card("n/%s/index.html" % view["id"],
                            kind_label="node",
                            title=view["title"],
                            detail=first_sentence(view["body"]) or view["title"],
                            machine=view["prov"]["kind"] == "agent",
                            og_type="article")
        card = trim_detail(card)
        emit("n/%s/index.html" % view["id"],
             env.get_template("node.html").render(node=view, og=card, depth=2), "core")
        emit("n/%s/card/index.html" % view["id"], card_page(env, **card), "core")
        emit("s/%s/index.html" % view["slug"],
             env.get_template("redirect.html").render(target="../../n/%s/" % view["id"]), "core")
    roadmap_card = surface_card("roadmap/index.html")
    emit("roadmap/index.html", env.get_template("roadmap.html").render(
        roots=roots, strip=what_matters_now(views, idx, tickets_by_node),
        og=roadmap_card, depth=1), "core")
    emit("roadmap/card/index.html", card_page(env, **roadmap_card), "core")
    emit("all/index.html",
         env.get_template("all.html").render(nodes=views, tickets=tickets_by_node,
                                             og=surface_card("all/index.html"), depth=1), "core")
    for spec in DOC_PAGES:
        page = doc_page(root, spec)
        card = surface_card(spec["path"])
        emit(spec["path"],
             env.get_template("doc.html").render(page=page, og=card, depth=page["depth"]),
             spec["source"])
        if card.get("card", True):
            emit(spec["path"].replace("index.html", "card/index.html"),
                 card_page(env, **card), spec["source"])

    ctx = {
        "root": root, "out": out, "env": env, "nav": nav, "nodes": views,
        "tickets_by_node": tickets_by_node, "clock": clock,
        "card_page": card_page, "surface_card": surface_card,
        "render_markdown": lambda text, source, depth=None: md.render_markdown(
            text, doc_link_rewriter(source, source.count("/") if depth is None else depth)),
    }
    for name, module in generators:
        produced = module.generate(ctx)
        for path, html in (produced.items() if isinstance(produced, dict) else produced):
            emit(path, html, "generators/" + name)

    # A nav entry nobody built still gets a page: "not yet published" is an
    # answer; a 404 from our own navigation is not.
    for surface in nav:
        if surface.get("published") or surface.get("path") in pages:
            continue
        emit(surface["path"], env.get_template("placeholder.html").render(
            surface=surface, depth=surface["path"].count("/")), "core placeholder")

    # A generator that declares a NAV entry and then does not emit the page has
    # put a 404 in our own navigation — the exact failure the placeholder above
    # exists to prevent. Fail the build instead of shipping the dead link.
    for surface in nav:
        href = surface["href"]
        if href.startswith(("http://", "https://", "/")):
            continue
        if (href + "index.html") not in pages:
            raise SystemExit(
                "nav entry %r (%s) has no page: %s claimed the surface but "
                "emitted nothing at %sindex.html"
                % (surface["label"], href or "/", surface.get("generator", "core"), href))

    if os.path.isdir(out):
        shutil.rmtree(out)
    for path in sorted(pages):
        write(os.path.join(out, *path.split("/")), pages[path][0])
    write(os.path.join(out, "style.css"),
          open(os.path.join(here, "templates", "style.css"), encoding="utf-8").read())
    # The custom domain, emitted by the renderer rather than bolted onto the
    # Pages artifact in CI, so the deployed tree stays exactly the tree
    # tools/check.sh proved reproducible. GitHub drops the custom domain from a
    # workflow-published site if CNAME is missing from the artifact.
    write(os.path.join(out, "CNAME"), "socaity.dev\n")

    export = {"schema": 1, "clock": clock,
              "nodes": [n for _p, _nm, n in sorted(nodes, key=lambda t: t[2]["id"])],
              "tickets": [t for _p, _nm, t in sorted(tickets, key=lambda t: t[2]["id"])]}
    write(os.path.join(out, "graph.json"), json.dumps(export, sort_keys=True, indent=2) + "\n")
    write(os.path.join(out, "sections.json"),
          json.dumps({v["id"]: sections_of(v) for v in views}, sort_keys=True, indent=2) + "\n")
    print("rendered %d page(s) (%d node page(s), %d generator(s)) to %s (graph clock %s)"
          % (len(pages), len(views), len(generators), out, clock[:10]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
