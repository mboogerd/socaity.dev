#!/usr/bin/env python3
"""Score decomposition runs against small, reviewable golden fixtures.

The harness deliberately scores structure, not generated prose.  A prediction
is JSON with ``nodes`` (each having a stable ``id`` and ``kind``),
``alternatives`` (lists of node ids), and ``dependencies`` (``from``/``to``).
Use ``--write-judge-prompt`` to hand the same case to an LLM judge; judge
scores are optional annotations, never a source of truth for graph structure.
"""

import argparse
import json
import math
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _pairs(values):
    return {tuple(sorted(pair)) for pair in values}


def _deps(values):
    return {(item["from"], item["to"]) for item in values}


def _node_ids(case):
    return {node["id"] for node in case.get("nodes", [])}


def score_case(golden, prediction):
    expected_alts = _pairs(golden.get("alternatives", []))
    actual_alts = _pairs(prediction.get("alternatives", []))
    expected_deps = _deps(golden.get("dependencies", []))
    actual_deps = _deps(prediction.get("dependencies", []))
    alt_hits = expected_alts & actual_alts
    phantom = actual_deps - expected_deps
    expected_count = len(golden.get("nodes", []))
    actual_count = len(prediction.get("nodes", []))
    return {
        "alternative_coverage": len(alt_hits) / len(expected_alts) if expected_alts else 1.0,
        "alternative_precision": len(alt_hits) / len(actual_alts) if actual_alts else 1.0,
        "granularity": (1.0 - abs(actual_count - expected_count) / max(expected_count, 1)),
        "phantom_dependencies": len(phantom) / len(actual_deps) if actual_deps else 0.0,
        "expected_alternatives": len(expected_alts),
        "matched_alternatives": len(alt_hits),
        "phantom_dependency_edges": sorted("%s->%s" % edge for edge in phantom),
        "expected_nodes": expected_count,
        "actual_nodes": actual_count,
        "unknown_node_ids": sorted(_node_ids(prediction) - _node_ids(golden)),
    }


def signature(prediction):
    nodes = sorted((n.get("id"), n.get("kind")) for n in prediction.get("nodes", []))
    alternatives = sorted(sorted(pair) for pair in prediction.get("alternatives", []))
    dependencies = sorted((d.get("from"), d.get("to")) for d in prediction.get("dependencies", []))
    return {"nodes": nodes, "alternatives": alternatives, "dependencies": dependencies}


def _jaccard(left, right):
    left = set(json.dumps(item, sort_keys=True) for item in left)
    right = set(json.dumps(item, sort_keys=True) for item in right)
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def variance(predictions):
    """Return mean pairwise structural disagreement across repeated runs."""
    signatures = [signature(prediction) for prediction in predictions]
    distances = []
    for index, left in enumerate(signatures):
        for right in signatures[index + 1 :]:
            similarities = [_jaccard(left[key], right[key]) for key in left]
            distances.append(1.0 - sum(similarities) / len(similarities))
    mean = sum(distances) / len(distances) if distances else 0.0
    spread = math.sqrt(sum((value - mean) ** 2 for value in distances) / len(distances)) if distances else 0.0
    return {"runs": len(predictions), "pairwise_disagreement": mean, "disagreement_stddev": spread}


def judge_prompt(golden, prediction):
    return """You are judging an AI decomposition, not its writing style.
Score each dimension 0 (missed), 1 (partial), or 2 (clear and justified).
Return JSON only: {\"alternative_coverage\": 0, \"granularity\": 0,
\"phantom_dependencies\": 0, \"notes\": \"...\"}.

Golden case:
%s

Candidate decomposition:
%s

Rubric:
- alternative_coverage: all materially competing approaches are represented as
  alternatives, including a viable null/no-change branch when appropriate.
- granularity: each node is independently actionable; do not reward ceremony
  or punish a concise node that preserves the important edges.
- phantom_dependencies: dependency edges are supported by the golden evidence;
  invented blockers score 0, and uncertain edges must be called out.
""" % (json.dumps(golden, indent=2, sort_keys=True), json.dumps(prediction, indent=2, sort_keys=True))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden-dir", type=Path, default=Path("evals/decomposition/golden"))
    parser.add_argument("--predictions", type=Path, help="JSON object keyed by case name, or a single case JSON")
    parser.add_argument("--runs", type=Path, help="JSON list of repeated prediction maps for variance")
    parser.add_argument("--write-judge-prompt", type=Path)
    args = parser.parse_args(argv)
    goldens = {path.stem: load_json(path) for path in sorted(args.golden_dir.glob("*.json"))}
    predictions = load_json(args.predictions) if args.predictions else {}
    if args.predictions and "nodes" in predictions:
        predictions = {next(iter(goldens)): predictions}
    report = {name: score_case(golden, predictions.get(name, {})) for name, golden in goldens.items()}
    if args.runs:
        repeated = load_json(args.runs)
        report["variance"] = {name: variance([run[name] for run in repeated if name in run]) for name in goldens}
    if args.write_judge_prompt:
        name = next(iter(goldens))
        args.write_judge_prompt.write_text(judge_prompt(goldens[name], predictions.get(name, {})), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
