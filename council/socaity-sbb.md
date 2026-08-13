# Council: socaity-sbb — Define graph schema and serialization for roadmap-as-graph before M1 tooling

Participants: agent-engineer, platform-engineer, product-designer
Type: decision · Priority: P0 · Blocks: socaity-c1y (node identity across decomposer runs), socaity-8wg (M1 focus+context prototype test)

Issue:
- Context: milestones.md M0 requires the roadmap expressed "in its own conventions (AND/OR nodes, contestable edges)" before any M1 tool exists; vision.md "The needs graph" defines the ontology (problem/solution, OR/AND, contestable edges, aging estimates) but no concrete data model.
- Question: What is the minimal node/edge schema and serialization format (files in the repo? beads? ComputeNet cells?) that M0 uses by hand and the M1 decomposition agent later reads and writes — including stable node identity, edge types (refinement, dependency, equivalence), and estimate fields?
- Why it matters: Every M1 agent task (decompose, dedup, estimate) targets this schema; deciding it after M0 forces a migration of the first public graph and breaks ledger references to nodes.

Adopted context binding this council:
- socaity-7mk: ledger schema v1 has validator-enforced no-free-text and hash-only evidence; ledger entries will reference graph nodes — node IDs must be stable, content-addressable or otherwise permanent.
- socaity-y39 (resolved, platform-engineer): M1 stack is a boring web app + DB + event log; ComputeNet off the critical path until M3.
- socaity-774 (open, related): M0 roadmap-as-graph storage format — this council's decision should resolve or directly constrain it.
- Related agent-engineer resolutions: socaity-0vv (OR-branch generation technique, closed); socaity-c1y has a recommendation comment (proposer-not-authority, match-then-propose with contestable equivalence edges).
- socaity-5u4 (resolved, product-designer): edge contestation at N=1 is edit-with-history, not litigation; dispute ceremony reserved for M4.
