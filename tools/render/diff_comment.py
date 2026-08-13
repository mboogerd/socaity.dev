#!/usr/bin/env python3
"""CI diff-render bot: before/after of the affected node-page sections.

Reads two sections.json files (produced by render.py for the base tree and the
PR tree) and writes one markdown comment showing, per affected node, what the
rendered page gains, loses or changes. Diffing the rendered sections rather
than the YAML is the point: reviewers see the page a reader would see.

Usage:
  python3 tools/render/diff_comment.py BEFORE.json AFTER.json [--out comment.md]
"""

import argparse
import difflib
import json
import sys

MARKER = "<!-- graph-diff-render -->"
SECTION_ORDER = ["title", "status", "contested", "provenance", "breadcrumbs", "body",
                 "requires", "approaches", "refined_by", "see_also", "estimates"]


def as_lines(value):
    if isinstance(value, list):
        return [str(v) for v in value]
    return str(value).splitlines() or [""]


def section_diff(before, after):
    """Unified diff of one section, or None when it is unchanged."""
    if before == after:
        return None
    lines = list(difflib.unified_diff(as_lines(before), as_lines(after),
                                      lineterm="", n=1))
    return "\n".join(lines[2:]) if lines else None


def node_report(nid, before, after):
    if before is None:
        title = (after or {}).get("title", nid)
        return "### New node: %s\n\n`%s` — page added.\n" % (title, nid)
    if after is None:
        title = before.get("title", nid)
        return "### Removed node: %s\n\n`%s` — page gone. Nodes are tombstoned, never deleted.\n" % (title, nid)
    chunks = []
    for key in SECTION_ORDER:
        diff = section_diff(before.get(key), after.get(key))
        if diff:
            chunks.append("**%s**\n\n```diff\n%s\n```" % (key, diff))
    if not chunks:
        return None
    return "### %s\n\n`%s`\n\n%s\n" % (after.get("title", nid), nid, "\n\n".join(chunks))


def build_comment(before, after):
    reports = []
    for nid in sorted(set(before) | set(after)):
        report = node_report(nid, before.get(nid), after.get(nid))
        if report:
            reports.append(report)
    if not reports:
        return "%s\n**Rendered graph pages: no visible change.**\n" % MARKER
    return "%s\n## Rendered node pages: %d affected\n\nBefore → after of the page sections a reader sees.\n\n%s" % (
        MARKER, len(reports), "\n".join(reports))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--out", help="write the comment here instead of stdout")
    args = ap.parse_args(argv)

    with open(args.before, encoding="utf-8") as fh:
        before = json.load(fh)
    with open(args.after, encoding="utf-8") as fh:
        after = json.load(fh)
    comment = build_comment(before, after)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(comment)
    else:
        sys.stdout.write(comment)
    return 0


if __name__ == "__main__":
    sys.exit(main())
