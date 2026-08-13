"""Shared, dependency-light loading of the needs-graph files.

Schema v1 per council/socaity-sbb.md: one YAML file per node in graph/nodes/,
edges and estimates inline in the asserting node's file, tickets as files.

Nothing here validates; validation lives in tools/validate/validate.py.
Nothing here reads the wall clock: every derived value is a function of the
merged tree only (council/socaity-z61.md: the site is a pure function of the
merged tree).
"""

import os

import yaml

NODES_DIRNAME = os.path.join("graph", "nodes")
TICKETS_DIRNAME = os.path.join("graph", "tickets")

EDGE_TYPES = ("refines", "requires", "equivalent_to")
NODE_STATUSES = ("open", "merged", "withdrawn", "resolved")
EDGE_STATUSES = ("asserted", "disputed", "settled")
ESTIMATE_KINDS = ("effort", "value", "branch_probability")
MAX_REDIRECT_HOPS = 8


def _load_dir(path, prefix):
    """Load every <prefix>*.yaml in path, sorted by filename for determinism."""
    out = []
    if not os.path.isdir(path):
        return out
    for name in sorted(os.listdir(path)):
        if not name.endswith(".yaml") or not name.startswith(prefix):
            continue
        full = os.path.join(path, name)
        with open(full, "r", encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)
        out.append((full, name, doc))
    return out


def load_nodes(root):
    return _load_dir(os.path.join(root, NODES_DIRNAME), "n-")


def load_tickets(root):
    return _load_dir(os.path.join(root, TICKETS_DIRNAME), "t-")


def edges_of(node):
    return list(node.get("edges") or [])


def estimates_of(obj):
    return list(obj.get("estimates") or [])


def all_records(node):
    """(kind, record) for every provenance-bearing record in a node file."""
    yield ("node", node)
    for edge in edges_of(node):
        yield ("edge", edge)
        for est in estimates_of(edge):
            yield ("estimate", est)
    for est in estimates_of(node):
        yield ("estimate", est)


def resolve(node_id, by_id):
    """Follow merged_into redirects to the surviving node id (bounded)."""
    seen = []
    cur = node_id
    for _ in range(MAX_REDIRECT_HOPS):
        node = by_id.get(cur)
        if node is None or not node.get("merged_into"):
            return cur, seen
        seen.append(cur)
        cur = node["merged_into"]
        if cur in seen:
            return cur, seen
    return cur, seen


def index(nodes):
    """Build the read model: id -> node, plus the reverse edge index.

    Returns a dict with:
      by_id    node id -> node document
      out      node id -> list of edges asserted by that node
      inc      node id -> list of edges pointing at that node
    """
    by_id = {}
    out = {}
    inc = {}
    for _, _, node in nodes:
        by_id[node["id"]] = node
    for nid in by_id:
        out.setdefault(nid, [])
        inc.setdefault(nid, [])
    for nid in sorted(by_id):
        for edge in edges_of(by_id[nid]):
            out[nid].append(edge)
            target = edge.get("to")
            if target in inc:
                inc[target].append(edge)
    for nid in inc:
        inc[nid].sort(key=lambda e: e.get("id", ""))
        out[nid].sort(key=lambda e: e.get("id", ""))
    return {"by_id": by_id, "out": out, "inc": inc}


def current_estimates(records):
    """Latest non-withdrawn record per kind; superseded ones stay as history.

    Ordering is by asserted_at then id, so it is stable and clock-free.
    """
    ordered = sorted(
        records,
        key=lambda r: (
            (r.get("provenance") or {}).get("asserted_at", ""),
            r.get("id", ""),
        ),
    )
    current = {}
    history = {}
    for rec in ordered:
        if rec.get("status") == "withdrawn":
            continue
        kind = rec.get("kind")
        history.setdefault(kind, []).append(rec)
        current[kind] = rec
    return current, history


def graph_clock(nodes):
    """The graph's own clock: the newest asserted_at anywhere in the tree.

    Used instead of the wall clock so that freshness/expiry rendering stays a
    pure function of the merged tree and CI output is byte-reproducible.
    """
    newest = ""
    for _, _, node in nodes:
        for _kind, rec in all_records(node):
            stamp = (rec.get("provenance") or {}).get("asserted_at") or ""
            if stamp > newest:
                newest = stamp
    return newest
