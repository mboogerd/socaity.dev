# Council: socaity-155 — M2 index and the platform subsidy signal must be one computation

Participants: data-analyst, mechanism-designer
Type: research · Priority: P0

Issue:
- Context: vision.md "Pricing the commons" defines foundational value as a centrality measure over the needs graph (downstream value unlocked vs direct demand); milestones.md M2 computes "the vision's subsidy signal on reality" from dependency graphs. These are currently two different computations: a damped reverse-dependency measure over package graphs vs a demand-weighted centrality over AND/OR needs graphs with probabilistic OR flow.
- Question: What is the shared mathematical core (and shared codebase) such that the M2 index genuinely IS the subsidy signal, not merely analogous to it — and which differences (no demand weights, no OR nodes in package data) are acknowledged as approximations?
- Why it matters: "we computed the subsidy signal for the world's software commons" is the grant pitch and the dogfooding claim; if the index is a different formula, that claim is false and critics will notice.

Adopted context:
- socaity-sbb: the needs-graph schema (problem/solution nodes, refines/requires/equivalent_to edges, branch_probability estimates on refines edges).
- socaity-chk (open, related): formal specification + Goodhart analysis of the foundationalness measure — this council should define the shared core; chk carries the full formal spec and Goodhart pass.
- data-analyst's resolved positions: project-level identity with package-level ingestion (socaity-is4); ternary support classification (socaity-l7f).
