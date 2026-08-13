#!/usr/bin/env python3
"""Static-site generator for the needs graph (council/socaity-z61.md).

PyYAML + jinja2, no framework. The site is a pure function of the merged tree:
no wall clock, no network, no database. Two runs over the same tree produce
byte-identical output, so a clone plus one command reproduces CI.

Emits, under --out:
  index.html, roadmap/index.html   root node page + "what matters now" strip
  n/<id>/index.html                focus+context node pages
  s/<slug>/index.html              slug redirects (IDs stay the durable ref)
  all/index.html                   flat index for auditors
  graph.json                       lossless export / M1 ingestion seam
  sections.json                    node-page sections, for the CI diff bot

Usage:
  python3 tools/render/render.py [--root .] [--out site]
"""

import argparse
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jinja2 import Environment, FileSystemLoader, select_autoescape  # noqa: E402

import graphlib as g  # noqa: E402

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
    ("Open", "node status open"),
    ("Done", "node status resolved"),
    ("Withdrawn", "node status withdrawn; the page stays reachable"),
    ("Merged into →", "node status merged; links the surviving node"),
    ("(no badge)", "edge status asserted"),
    ("Contested", "edge status disputed; links the dispute"),
    ("Settled", "edge status settled; links the resolving record"),
]
ISSUE_URL = "https://github.com/socaity/socaity.dev/issues/new"


def day(stamp):
    return (stamp or "")[:10]


def provenance_line(prov):
    """The provenance line as a designed object; agent content always labelled."""
    by = (prov or {}).get("asserted_by") or {}
    who = by.get("actor_id", "unknown")
    if by.get("actor_kind") == "agent":
        who = "%s (agent, on behalf of %s)" % (who, by.get("on_behalf_of", "unknown"))
        label = "agent-drafted, human-accountable"
    else:
        who = "%s (human)" % who
        label = "human-authored"
    return "Asserted by %s · %s · %s" % (who, label, day(prov.get("asserted_at")))


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
                      "type": view["type"], "tier": ticket.get("tier"), "ticket": ticket["id"]})
    strip.sort(key=lambda s: s["id"])
    return strip


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

    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")),
        autoescape=select_autoescape(["html"]), keep_trailing_newline=True, trim_blocks=True,
        lstrip_blocks=True)
    env.globals.update(legend=LEGEND, clock=clock[:10], issue_url=ISSUE_URL)

    if os.path.isdir(out):
        shutil.rmtree(out)
    for view in views:
        write(os.path.join(out, "n", view["id"], "index.html"),
              env.get_template("node.html").render(node=view, depth=2))
        write(os.path.join(out, "s", view["slug"], "index.html"),
              env.get_template("redirect.html").render(target="../../n/%s/" % view["id"]))
    roadmap = env.get_template("roadmap.html").render(
        roots=roots, strip=what_matters_now(views, idx, tickets_by_node), depth=1)
    write(os.path.join(out, "roadmap", "index.html"), roadmap)
    write(os.path.join(out, "index.html"),
          env.get_template("redirect.html").render(target="roadmap/"))
    write(os.path.join(out, "all", "index.html"),
          env.get_template("all.html").render(nodes=views, tickets=tickets_by_node, depth=1))
    write(os.path.join(out, "style.css"),
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "style.css"),
               encoding="utf-8").read())

    export = {"schema": 1, "clock": clock,
              "nodes": [n for _p, _nm, n in sorted(nodes, key=lambda t: t[2]["id"])],
              "tickets": [t for _p, _nm, t in sorted(tickets, key=lambda t: t[2]["id"])]}
    write(os.path.join(out, "graph.json"), json.dumps(export, sort_keys=True, indent=2) + "\n")
    write(os.path.join(out, "sections.json"),
          json.dumps({v["id"]: sections_of(v) for v in views}, sort_keys=True, indent=2) + "\n")
    print("rendered %d node page(s) to %s (graph clock %s)" % (len(views), out, clock[:10]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
