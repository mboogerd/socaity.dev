#!/usr/bin/env python3
"""DISPUTE-DRIFT cross-check — council/socaity-z61.md.

z61 settled that file state is the only authority: "No dispute state lives
outside graph/ files — if the site shows it, a file says it."  The dispute PR
flips the edge asserted → disputed and carries a structured `dispute_ref`
{kind, repo, number, url}; the resolving PR flips disputed → settled with an
in-file rationale.  The community-builder's scheduled cross-check survives as
the **drift alarm**: it never sets state, it only fails when the tree and the
live disputes have drifted apart.

Five conditions, each exiting non-zero and naming the file and line:

  D0  a credentialed run that cannot read the dispute list at all — a drift
      alarm that cannot see live disputes fails rather than passes quietly.
  D1  an open `graph:dispute` PR or issue older than the first-response SLO
      that no edge in the tree points at — the contestation is invisible on
      the rendered site (z61: "the render can never quietly hide a live
      dispute").
  D2  an edge still `disputed` whose dispute_ref points at a closed PR or
      issue — resolution flips to `settled` with a rationale, never silence.
  D3  a dispute_ref that does not resolve at all (wrong repo, or a number
      that does not exist) — a courtesy pointer that points nowhere.
  D4  local, always checked: a `disputed` edge with no dispute_ref, or a
      `settled` edge with neither rationale nor resolution record.

D1–D3 need the GitHub API.  Without a token the gate runs D4 and says so —
but a *CI* run must never degrade that quietly, so the workflow passes
`--require-api`, which turns a missing token or an unusable response into D0.
Dropping the `GITHUB_TOKEN:` line from the workflow then breaks the build
instead of turning the alarm into a two-check formality.  `--fixture` feeds it
a recorded API payload, which is how it is tested.

Python stdlib only: the gate runs before dependencies are installed.

Usage:
  python3 tools/gates/dispute_drift.py [--root .] [--repo owner/name]
  python3 tools/gates/dispute_drift.py --fixture disputes.json --now 2026-08-13T12:00:00Z
"""

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import miniyaml  # noqa: E402

DISPUTE_LABEL = "graph:dispute"
DEFAULT_REPO = "socaity/socaity.dev"
API = ("https://api.github.com/repos/%s/issues"
       "?state=all&labels=%s&per_page=100&page=%d")


class UnreadableDisputes(Exception):
    """The dispute list could not be obtained or made sense of."""


# --------------------------------------------------------------------------
# the tree
# --------------------------------------------------------------------------
def line_of(path, needle):
    """First 1-based line containing `needle`, for a message that can be opened."""
    try:
        with open(path, encoding="utf-8") as handle:
            for lineno, line in enumerate(handle, 1):
                if needle in line:
                    return lineno
    except OSError:
        pass
    return 0


def load_edges(root):
    """[(relpath, line, node_id, edge)] over every edge in graph/nodes."""
    nodes_dir = os.path.join(root, "graph", "nodes")
    edges = []
    if not os.path.isdir(nodes_dir):
        return edges
    for name in sorted(os.listdir(nodes_dir)):
        if not name.endswith((".yaml", ".yml")):
            continue
        path = os.path.join(nodes_dir, name)
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        try:
            node = miniyaml.load_file(path)
        except miniyaml.YAMLSubsetError as exc:
            raise SystemExit("dispute-drift: %s: %s" % (rel, exc))
        for edge in (node or {}).get("edges") or []:
            edges.append((rel, line_of(path, "id: %s" % edge.get("id")),
                          (node or {}).get("id"), edge))
    return edges


# --------------------------------------------------------------------------
# the live disputes
# --------------------------------------------------------------------------
def fetch_disputes(repo, token):
    """[{number, state, kind, url, created_at, title}] labelled graph:dispute."""
    items, page = [], 1
    while page < 20:
        request = urllib.request.Request(
            API % (repo, DISPUTE_LABEL.replace(":", "%3A"), page),
            headers={"Accept": "application/vnd.github+json",
                     "User-Agent": "socaity-dispute-drift"})
        if token:
            request.add_header("Authorization", "Bearer %s" % token)
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
        if not isinstance(payload, list):
            # A 200 that is not a list is an error document; treating it as
            # "no disputes" would be the exact silent pass D0 exists to stop.
            raise UnreadableDisputes(
                "the API returned %s, not a list of issues: %.120r"
                % (type(payload).__name__, payload))
        items.extend(payload)
        if len(payload) < 100:
            break
        page += 1
    return [normalise_issue(item) for item in items]


def normalise_issue(item):
    return {
        "number": item.get("number"),
        "state": item.get("state"),
        # The API sends `pull_request` as an object on PRs; a recorded fixture
        # may carry `{}`, which is falsy — presence is the signal, not truth.
        "kind": "pr" if "pull_request" in item else "issue",
        "url": item.get("html_url"),
        "created_at": item.get("created_at"),
        "title": item.get("title", ""),
    }


def parse_time(stamp):
    return dt.datetime.fromisoformat((stamp or "").replace("Z", "+00:00"))


# --------------------------------------------------------------------------
# the checks
# --------------------------------------------------------------------------
def local_checks(edges):
    """D4 — the tree alone must be self-consistent."""
    failures = []
    for rel, line, node_id, edge in edges:
        status, eid = edge.get("status"), edge.get("id")
        ref = edge.get("dispute_ref")
        if status == "disputed" and not isinstance(ref, dict):
            failures.append((rel, line, "D4",
                             "edge %s on %s is disputed with no dispute_ref — z61 "
                             "requires the structured {kind, repo, number, url} "
                             "record on the flip" % (eid, node_id)))
        if status == "settled" and not (edge.get("rationale") or edge.get("resolution")):
            failures.append((rel, line, "D4",
                             "edge %s on %s is settled with no in-file rationale — "
                             "z61: the graph file stays self-contained even if the "
                             "PR thread vanishes" % (eid, node_id)))
    return failures


def drift_checks(edges, disputes, repo, slo_hours, now):
    """D1–D3 — the tree against the live disputes."""
    failures = []
    by_number = {d["number"]: d for d in disputes}

    referenced = {}
    for rel, line, node_id, edge in edges:
        ref = edge.get("dispute_ref")
        if not isinstance(ref, dict):
            continue
        number = ref.get("number")
        referenced.setdefault(number, []).append((rel, line, node_id, edge, ref))

        live = by_number.get(number)
        if ref.get("repo") != repo:
            failures.append((rel, line, "D3",
                             "edge %s dispute_ref points at %s, not the platform "
                             "repo %s" % (edge.get("id"), ref.get("repo"), repo)))
        elif live is None:
            failures.append((rel, line, "D3",
                             "edge %s dispute_ref #%s resolves to no %s in %s — a "
                             "courtesy pointer that points nowhere"
                             % (edge.get("id"), number, DISPUTE_LABEL, repo)))
        elif edge.get("status") == "disputed" and live["state"] == "closed":
            failures.append((rel, line, "D2",
                             "edge %s is still disputed but %s #%s is closed — the "
                             "resolving merge must flip it to settled with a "
                             "rationale, never leave the render contested"
                             % (edge.get("id"), live["kind"], number)))

    for dispute in disputes:
        if dispute["state"] != "open":
            continue
        age = (now - parse_time(dispute["created_at"])).total_seconds() / 3600.0
        if age <= slo_hours:
            continue
        holders = referenced.get(dispute["number"], [])
        flipped = [h for h in holders if h[3].get("status") in ("disputed", "settled")]
        if not flipped:
            failures.append(("graph/nodes", 0, "D1",
                             "%s #%s (%s) is an open %s open for %.0fh — past the "
                             "%.0fh first-response SLO — and no edge in graph/nodes "
                             "carries a dispute_ref to it: the site is hiding a live "
                             "dispute" % (dispute["kind"], dispute["number"],
                                          dispute["url"], DISPUTE_LABEL, age,
                                          slo_hours)))
    return failures


def main(argv=None):
    ap = argparse.ArgumentParser(description="dispute-drift cross-check")
    ap.add_argument("--root", default=".")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY") or DEFAULT_REPO)
    ap.add_argument("--slo-hours", type=float, default=24.0,
                    help="z61 first-response SLO before an unflipped dispute is drift")
    ap.add_argument("--fixture", help="a recorded /issues payload, instead of the API")
    ap.add_argument("--now", help="ISO instant to age disputes against (tests)")
    ap.add_argument("--offline", action="store_true", help="run the local checks only")
    ap.add_argument("--require-api", action="store_true",
                    help="CI: D1-D3 must actually run — no token, or an "
                         "unreadable dispute list, is itself a D0 failure")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    edges = load_edges(root)
    now = parse_time(args.now) if args.now else dt.datetime.now(dt.timezone.utc)

    print("== dispute-drift cross-check")
    print("   %d edges in graph/nodes, repo %s, SLO %.0fh"
          % (len(edges), args.repo, args.slo_hours))

    failures = local_checks(edges)

    disputes, source = None, None
    if args.fixture:
        with open(args.fixture, encoding="utf-8") as handle:
            disputes = [normalise_issue(i) for i in json.load(handle)]
        source = args.fixture
    elif not args.offline:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not token and args.require_api:
            failures.append((".github/workflows/dispute-drift.yml", 0, "D0",
                             "--require-api but neither GITHUB_TOKEN nor GH_TOKEN "
                             "is set: D1-D3 would not run, and a drift alarm "
                             "reduced to its local half must say so, not go green"))
        else:
            try:
                disputes = fetch_disputes(args.repo, token)
                source = "the GitHub API"
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
                    UnreadableDisputes, ValueError) as exc:
                # A credentialed run is a CI run: an alarm that cannot read the
                # disputes is not a passing alarm, it is a broken one.
                if token or args.require_api:
                    failures.append(("tools/gates/dispute_drift.py", 0, "D0",
                                     "the %s list for %s could not be read (%s) — "
                                     "a drift alarm that cannot see live disputes "
                                     "must fail, not pass quietly"
                                     % (DISPUTE_LABEL, args.repo, exc)))
                else:
                    print("   NOTE: %s unreachable (%s) — local checks only"
                          % (args.repo, exc))

    if disputes is None:
        print("   NOTE: no dispute list — D1/D2/D3 skipped, D4 ran")
    else:
        print("   %d %s items from %s (%d open)"
              % (len(disputes), DISPUTE_LABEL, source,
                 sum(1 for d in disputes if d["state"] == "open")))
        failures += drift_checks(edges, disputes, args.repo, args.slo_hours, now)

    for rel, line, rule, message in failures:
        print("FAIL %s:%d: DISPUTE-DRIFT %s — %s" % (rel, line, rule, message))

    if failures:
        print("   %d drift failure(s)" % len(failures))
        return 1
    print("== dispute-drift cross-check: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
