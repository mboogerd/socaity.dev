# Council: socaity-15b + socaity-3jq (consolidated) — The M2→M1 seam: how an index entry becomes an agent-actionable needs-graph node

Participants: data-analyst, agent-engineer, platform-engineer
Type: research · Priority: P1 · Consolidates socaity-3jq ("agent-actionable" filter; same owner, participant subset)

Issue (merged):
- 15b: Nothing yet says how an M2 index entry becomes an M1 needs-graph node an agent and the ledger can target — exactly where the traction hack must convert into the product.
- 3jq: "Actionability" is the index's stated differentiator vs Libraries.io/criticality-score — every under-supported node must be something an agent can actually be pointed at. Define it operationally, as a filter/annotation the pipeline computes.

Adopted context:
- socaity-155: the package graph IS a needs-graph instance (problem/solution nodes, project-level identity, requires edges, equivalence classes); shared module consumes the sbb schema; the M2 pipeline is ETL + params.
- socaity-sbb: schema v1 (permanent n- IDs, provenance mandatory, external_ref field on nodes).
- socaity-v9o: M1 = BYO-agent skill + render/validate/ingest web app; context packs are the M3 product surface (t46 specifies them).
- Agent quality bar (AE knowledge): consent precedes contribution; issue-first; M3 targets come from consenting projects only (3o2 consent registry).
- Remaining scope: (a) the materialization rule — which index entries become platform graph nodes, when, and with what provenance (crawled facts are not contestable claims — how is an ingested node marked?); (b) the operational definition of agent-actionable (what signals: build reproducibility? test suite present? maintainer responsiveness? issue clarity?) computed as an annotation; (c) the dedup/identity seam (an index project node vs a user's M1 node for the same project); (d) what stays OUT (the index does not auto-spawn work items; consent gates M3 targeting).
