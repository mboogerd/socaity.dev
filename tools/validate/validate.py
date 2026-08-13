#!/usr/bin/env python3
"""Offline validator for the needs graph (council/socaity-sbb.md, socaity-z61.md).

Gates, all of them offline and file-only:
  schema:1                 every file declares schema: 1
  ID discipline            n-/e-/est-/t- + 26 base32 chars, unique, filename = id
  slug pinning             kebab, globally unique, references are IDs only,
                           to_slug (when present) matches the target's slug
  referential integrity    edges resolve, from = own id, redirects terminate,
                           no refines/requires cycles
  provenance completeness  every node/edge/estimate/ticket, humans included
  estimates append-only    merged records are never edited or removed (--base)

Exit status is non-zero on any error, so it can be a required PR check.

Usage:
  python3 tools/validate/validate.py [--root .] [--base origin/main]
"""

import argparse
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml  # noqa: E402

import graphlib as g  # noqa: E402

B32 = "[a-z2-7]{26}"
ID_RE = {
    "node": re.compile(r"^n-%s$" % B32),
    "edge": re.compile(r"^e-%s$" % B32),
    "estimate": re.compile(r"^est-%s$" % B32),
    "ticket": re.compile(r"^t-%s$" % B32),
}
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
STAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
AGENT_FIELDS = ("on_behalf_of", "model", "prompt_hash", "run_id")
# Only forward moves are legal; a record is never edited back to a quieter state.
EDGE_TRANSITIONS = {"asserted": {"disputed", "settled"}, "disputed": {"settled"}, "settled": set()}
# Fields the contest workflow appends to an already-merged edge record. They may
# be ADDED once (the dispute PR, then the resolving PR); they may never be
# rewritten or removed afterwards.
EDGE_ADDITIVE = ("dispute_ref", "resolution")
DISPUTE_REF_KINDS = ("pr", "issue")


class Errors:
    def __init__(self):
        self.items = []

    def add(self, where, msg):
        self.items.append("%s: %s" % (where, msg))

    def __bool__(self):
        return bool(self.items)


def check_provenance(err, where, prov):
    if not isinstance(prov, dict):
        err.add(where, "provenance block missing (required for human writes too)")
        return
    by = prov.get("asserted_by")
    if not isinstance(by, dict):
        err.add(where, "provenance.asserted_by missing")
        return
    if not by.get("actor_id"):
        err.add(where, "provenance.asserted_by.actor_id missing")
    kind = by.get("actor_kind")
    if kind not in ("human", "agent"):
        err.add(where, "provenance.asserted_by.actor_kind must be human|agent")
    if kind == "agent":
        for field in AGENT_FIELDS:
            if not by.get(field):
                err.add(where, "agent write is missing provenance.asserted_by.%s" % field)
    stamp = prov.get("asserted_at")
    if not isinstance(stamp, str) or not STAMP_RE.match(stamp):
        err.add(where, "provenance.asserted_at must be an ISO-8601 UTC stamp, e.g. 2026-08-01T09:00:00Z")
    ev = prov.get("evidence")
    if not isinstance(ev, list):
        err.add(where, "provenance.evidence must be a list of hashes (may be empty)")
    else:
        for item in ev:
            if not isinstance(item, str) or not HASH_RE.match(item):
                err.add(where, "evidence entry %r is not sha256:<64 hex>" % (item,))


def check_estimate(err, where, est):
    kind = est.get("kind")
    if kind not in g.ESTIMATE_KINDS:
        err.add(where, "estimate kind must be one of %s" % (g.ESTIMATE_KINDS,))
    value = est.get("value")
    if kind in ("effort", "value"):
        if not isinstance(value, dict) or set(value) != {"low", "high"}:
            err.add(where, "%s estimate value must be an interval {low, high}" % kind)
        elif not isinstance(value["low"], (int, float)) or not isinstance(value["high"], (int, float)):
            err.add(where, "interval bounds must be numbers")
        elif value["low"] > value["high"]:
            err.add(where, "interval requires low <= high")
        if not est.get("unit"):
            err.add(where, "%s estimate needs a unit" % kind)
    elif kind == "branch_probability":
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
            err.add(where, "branch_probability value must be a scalar in [0, 1]")
    if "confidence" in est:
        err.add(where, "no confidence field exists in schema 1 (interval width encodes it)")
    if not est.get("expires_at"):
        err.add(where, "estimate needs expires_at")
    check_provenance(err, where, est.get("provenance"))


def check_dispute_ref(err, where, edge):
    """A contested edge must carry the machine-readable pointer the chip links.

    council/socaity-z61.md: dispute = flip to disputed + a structured
    dispute_ref {kind: pr|issue, repo, number, url}; resolution = flip to
    settled carrying an in-file rationale, so the file survives the PR thread.
    """
    ref = edge.get("dispute_ref")
    status = edge.get("status")
    if status == "settled" and not (edge.get("rationale") or "").strip():
        err.add(where, "a settled edge needs an in-file rationale: the graph file stays "
                       "self-contained even if the PR thread vanishes")
    if ref is None:
        if status == "disputed":
            err.add(where, "a disputed edge needs a dispute_ref {kind, repo, number, url}; "
                           "the Contested chip and its link derive from file state only")
        return
    if not isinstance(ref, dict):
        err.add(where, "dispute_ref must be a structured record, not a bare URL")
        return
    if ref.get("kind") not in DISPUTE_REF_KINDS:
        err.add(where, "dispute_ref.kind must be one of %s" % (DISPUTE_REF_KINDS,))
    if not isinstance(ref.get("repo"), str) or "/" not in (ref.get("repo") or ""):
        err.add(where, "dispute_ref.repo must be <owner>/<repo>")
    if not isinstance(ref.get("number"), int) or isinstance(ref.get("number"), bool):
        err.add(where, "dispute_ref.number must be an integer")
    url = ref.get("url")
    if not isinstance(url, str) or not url.startswith("https://"):
        err.add(where, "dispute_ref.url must be an https URL (a courtesy pointer, never load-bearing)")


def collect_ids(err, ids, kind, value, where):
    if not isinstance(value, str) or not ID_RE[kind].match(value):
        err.add(where, "%s id %r must match %s-<26 base32 chars>" % (kind, value, {"estimate": "est"}.get(kind, kind[0])))
        return
    if value in ids:
        err.add(where, "duplicate id %s (also in %s)" % (value, ids[value]))
    else:
        ids[value] = where


def validate_tree(root):
    err = Errors()
    nodes = g.load_nodes(root)
    tickets = g.load_tickets(root)
    ids = {}
    slugs = {}

    for path, name, node in nodes:
        where = os.path.relpath(path, root)
        if not isinstance(node, dict):
            err.add(where, "file is not a YAML mapping")
            continue
        if node.get("schema") != 1:
            err.add(where, "schema must be exactly 1 (unknown versions are rejected)")
        collect_ids(err, ids, "node", node.get("id"), where)
        if name != "%s.yaml" % node.get("id"):
            err.add(where, "filename must be <id>.yaml")
        slug = node.get("slug")
        if not isinstance(slug, str) or not SLUG_RE.match(slug or ""):
            err.add(where, "slug %r must be kebab-case" % (slug,))
        elif slug in slugs:
            err.add(where, "slug %r is already used by %s" % (slug, slugs[slug]))
        else:
            slugs[slug] = where
        if node.get("type") not in ("problem", "solution"):
            err.add(where, "type must be problem|solution")
        title = node.get("title")
        if not isinstance(title, str) or not title.strip():
            err.add(where, "title is required")
        elif len(title) > 70:
            err.add(where, "title is %d chars, limit is 70" % len(title))
        if not (node.get("body") or "").strip():
            err.add(where, "body is required")
        status = node.get("status")
        if status not in g.NODE_STATUSES:
            err.add(where, "status must be one of %s" % (g.NODE_STATUSES,))
        if status == "merged" and not node.get("merged_into"):
            err.add(where, "merged node needs merged_into (merge is a redirect, never a deletion)")
        if node.get("merged_into") and status != "merged":
            err.add(where, "merged_into is only valid with status: merged")
        check_provenance(err, where, node.get("provenance"))
        for est in g.estimates_of(node):
            collect_ids(err, ids, "estimate", est.get("id"), "%s [%s]" % (where, est.get("id")))
            check_estimate(err, "%s [%s]" % (where, est.get("id")), est)
        for edge in g.edges_of(node):
            eid = edge.get("id")
            ewhere = "%s [%s]" % (where, eid)
            collect_ids(err, ids, "edge", eid, ewhere)
            if edge.get("from") != node.get("id"):
                err.add(ewhere, "edge is misfiled: from must be the asserting node %s" % node.get("id"))
            if edge.get("type") not in g.EDGE_TYPES:
                err.add(ewhere, "edge type must be one of %s" % (g.EDGE_TYPES,))
            if edge.get("status") not in g.EDGE_STATUSES:
                err.add(ewhere, "edge status must be one of %s" % (g.EDGE_STATUSES,))
            to = edge.get("to")
            if not isinstance(to, str) or not ID_RE["node"].match(to or ""):
                err.add(ewhere, "edge target %r must be a permanent node ID, never a slug" % (to,))
            elif to == node.get("id"):
                err.add(ewhere, "self-edge")
            check_dispute_ref(err, ewhere, edge)
            check_provenance(err, ewhere, edge.get("provenance"))
            for est in g.estimates_of(edge):
                collect_ids(err, ids, "estimate", est.get("id"), "%s [%s]" % (ewhere, est.get("id")))
                check_estimate(err, "%s [%s]" % (ewhere, est.get("id")), est)
                if est.get("kind") != "branch_probability":
                    err.add(ewhere, "only branch_probability estimates live inside an edge record")

    idx = g.index(nodes)
    by_id = idx["by_id"]

    # Referential integrity, slug pinning against the resolved tree.
    for path, _name, node in nodes:
        where = os.path.relpath(path, root)
        if not isinstance(node, dict):
            continue
        target = node.get("merged_into")
        if target:
            if target not in by_id:
                err.add(where, "merged_into %s does not exist" % target)
            else:
                final, _chain = g.resolve(node["id"], by_id)
                # Terminating means the last hop is a node that redirects nowhere.
                # A loop (A -> B -> A) or an over-long chain leaves us on a node
                # that still carries merged_into.
                if final not in by_id or by_id[final].get("merged_into"):
                    err.add(where, "redirect chain from %s does not terminate (loop or too long)"
                            % node["id"])
        for edge in g.edges_of(node):
            ewhere = "%s [%s]" % (where, edge.get("id"))
            to = edge.get("to")
            if to not in by_id:
                err.add(ewhere, "edge target %s does not exist" % to)
                continue
            final, _chain = g.resolve(to, by_id)
            if final not in by_id or by_id[final].get("merged_into"):
                err.add(ewhere, "edge target %s does not redirect to a surviving node" % to)
            if "to_slug" in edge and edge["to_slug"] != by_id[to].get("slug"):
                err.add(ewhere, "to_slug %r does not match target slug %r (ID wins; fix the annotation)"
                        % (edge["to_slug"], by_id[to].get("slug")))
            etype = edge.get("type")
            if etype == "equivalent_to" and by_id[to].get("type") != node.get("type"):
                err.add(ewhere, "equivalent_to must connect two nodes of the same type")
            if etype in ("refines", "requires") and by_id[to].get("type") != "problem":
                err.add(ewhere, "%s must point at a problem (edges point child -> parent)" % etype)

    err_cycle = find_cycle(by_id)
    if err_cycle:
        err.add("graph", "refines/requires cycle: %s" % " -> ".join(err_cycle))

    ticket_ids = {}
    for path, name, ticket in tickets:
        where = os.path.relpath(path, root)
        if not isinstance(ticket, dict):
            err.add(where, "file is not a YAML mapping")
            continue
        if ticket.get("schema") != 1:
            err.add(where, "schema must be exactly 1")
        collect_ids(err, ticket_ids, "ticket", ticket.get("id"), where)
        if name != "%s.yaml" % ticket.get("id"):
            err.add(where, "filename must be <id>.yaml")
        if ticket.get("node") not in by_id:
            err.add(where, "ticket node %r does not exist" % ticket.get("node"))
        if ticket.get("status") not in ("open", "claimed", "done"):
            err.add(where, "ticket status must be open|claimed|done")
        if ticket.get("status") == "claimed" and not ticket.get("claimed_by"):
            err.add(where, "claimed ticket needs claimed_by (claim state is file-derived)")
        check_provenance(err, where, ticket.get("provenance"))

    return err, nodes


def find_cycle(by_id):
    """Depth-first cycle search over refines/requires edges, deterministic order."""
    color = {}
    stack = []

    def walk(nid):
        color[nid] = 1
        stack.append(nid)
        for edge in sorted(g.edges_of(by_id[nid]), key=lambda e: e.get("id", "")):
            if edge.get("type") not in ("refines", "requires"):
                continue
            to = edge.get("to")
            if to not in by_id:
                continue
            if color.get(to) == 1:
                return stack[stack.index(to):] + [to]
            if color.get(to, 0) == 0:
                found = walk(to)
                if found:
                    return found
        stack.pop()
        color[nid] = 2
        return None

    for nid in sorted(by_id):
        if color.get(nid, 0) == 0:
            found = walk(nid)
            if found:
                return found
    return None


def git_show(root, ref, relpath):
    proc = subprocess.run(["git", "-C", root, "show", "%s:%s" % (ref, relpath)],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return yaml.safe_load(proc.stdout)


def git_files(root, ref, prefix):
    proc = subprocess.run(["git", "-C", root, "ls-tree", "-r", "--name-only", ref, prefix],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return [line for line in proc.stdout.splitlines() if line.endswith(".yaml")]


def check_append_only(root, base, err):
    """Merged records are append-only: never edited, never removed (offline, via git)."""
    base_files = git_files(root, base, g.NODES_DIRNAME)
    if base_files is None:
        err.add("append-only", "cannot read base ref %r (fetch it before validating)" % base)
        return
    for relpath in sorted(base_files):
        old = git_show(root, base, relpath)
        if not isinstance(old, dict):
            continue
        new_path = os.path.join(root, relpath)
        if not os.path.exists(new_path):
            err.add(relpath, "node file was deleted; nodes are tombstoned, never removed")
            continue
        with open(new_path, "r", encoding="utf-8") as fh:
            new = yaml.safe_load(fh)
        for field in ("id", "type"):
            if old.get(field) != new.get(field):
                err.add(relpath, "%s is immutable (%r -> %r)" % (field, old.get(field), new.get(field)))
        old_edges = {e.get("id"): e for e in g.edges_of(old)}
        new_edges = {e.get("id"): e for e in g.edges_of(new)}
        for eid, old_edge in sorted(old_edges.items()):
            new_edge = new_edges.get(eid)
            if new_edge is None:
                err.add(relpath, "edge %s was removed; edges are status-transitioned, never deleted" % eid)
                continue
            diff_record(err, relpath, "edge %s" % eid, old_edge, new_edge,
                        mutable={"status"}, transitions=EDGE_TRANSITIONS, nested="estimates",
                        additive=EDGE_ADDITIVE)
        old_ests = {e.get("id"): e for e in g.estimates_of(old)}
        new_ests = {e.get("id"): e for e in g.estimates_of(new)}
        compare_estimates(err, relpath, old_ests, new_ests)


def compare_estimates(err, relpath, old_ests, new_ests):
    for eid, old_est in sorted(old_ests.items()):
        new_est = new_ests.get(eid)
        if new_est is None:
            err.add(relpath, "estimate %s was removed; estimates are append-only" % eid)
            continue
        diff_record(err, relpath, "estimate %s" % eid, old_est, new_est,
                    mutable={"status"}, transitions={None: {"withdrawn"}, "withdrawn": set()})


def diff_record(err, relpath, label, old, new, mutable, transitions, nested=None, additive=()):
    keys = set(old) | set(new)
    for key in sorted(keys):
        if key == nested:
            compare_estimates(err, relpath,
                              {e.get("id"): e for e in (old.get(nested) or [])},
                              {e.get("id"): e for e in (new.get(nested) or [])})
            continue
        if old.get(key) == new.get(key):
            continue
        if key in additive and key not in old:
            # Append-only means fields may be ADDED to a record, never rewritten:
            # the dispute PR adds dispute_ref, the resolving PR adds resolution.
            continue
        if key not in mutable:
            err.add(relpath, "%s: field %r changed; merged records are append-only" % (label, key))
            continue
        allowed = transitions.get(old.get(key), set())
        if new.get(key) not in allowed:
            err.add(relpath, "%s: illegal %s transition %r -> %r" % (label, key, old.get(key), new.get(key)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="repository root (default: .)")
    ap.add_argument("--base", help="git ref to check append-only rules against, e.g. origin/main")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    err, nodes = validate_tree(root)
    if args.base:
        check_append_only(root, args.base, err)
    else:
        print("note: --base not given; append-only history check skipped", file=sys.stderr)

    if err:
        print("FAIL: %d problem(s)" % len(err.items))
        for item in err.items:
            print("  " + item)
        return 1
    print("OK: %d node file(s) valid" % len(nodes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
