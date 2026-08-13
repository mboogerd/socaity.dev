# Product design — domain knowledge

## Graph UX — why node canvases fail, what survives

- Free-form node canvases (the Miro/graphviz view) fail beyond ~50 nodes:
  spatial memory breaks, layout thrash destroys orientation, and users
  can't answer "what matters now?". They demo well and retain terribly.
- What survives in practice: **focus + context** patterns. One node in
  focus with its immediate neighborhood (parents, alternatives, children),
  breadcrumbs up, ranked lists down. Gmail-thread depth, not subway map.
  The full-graph view exists as an overview/minimap moment, never the
  working surface.
- Proven analogues to steal from: issue trackers with dependency views
  (Linear's blocking/blocked-by), package-dependency explorers (deps.dev's
  focused drill-down), argument-mapping tools (Kialo's one-claim-at-a-time
  navigation — the closest existing thing to contestable edges at scale).
- AND/OR rendering: do not teach the vocabulary. Render OR as "N competing
  approaches" (tabs/cards with probability weights) and AND as "requires"
  checklists. Test whether users predict correctly what happens when a
  branch loses — that's the comprehension test that matters.
- Contesting an edge must feel like commenting, not litigation: inline
  "dispute this" → structured claim form → visible status chip
  (asserted/disputed/settled). The court-case ceremony appears only when
  a dispute escalates.

## The ledger (30-second auditability)

- Three questions a stranger must answer unaided, fast: Who contributed
  what? What rule converts contribution to claim? What would *my*
  contribution be worth? — the last one via a small interactive
  calculator; it doubles as the recruiting hook.
- Running totals + per-entry drill-down + "recompute this yourself" link
  (the export + script). Verifiability communicated by *offering* the
  audit path visibly, even though few will take it.
- Epoch-share display: show shares as % of epoch, never as numbers that
  pattern-match token balances. Vocabulary check every screen: anything
  that reads as "wallet", "airdrop", "token" gets renamed.

## Progressive complexity map (who sees what, when)

| Cohort | Sees | Never sees (yet) |
|---|---|---|
| M0 visitor | Manifesto, roadmap graph (read-only), ledger | Any mechanism math |
| M1 tool user | Their own needs graph, decompositions, estimates | Credit, multipliers, epochs |
| M3 agent-owner | Node prices, burn rates, vesting status | Demand-side internals |
| M4 need-haver | Wishes, votes, forecasts ("expect this in Q3±1") | Centrality scores, damping parameters |

Rule: every mechanism concept ships with the cohort that needs it, wrapped
in that cohort's language. Forecasts render as intervals, never dates
(vision requirement — design the interval as the primary object: a bar,
not a point with error).

## Trust aesthetics

- The anti-crypto signal is visual before it is verbal: editorial/document
  aesthetic (think government-report-meets-modern-docs: readable serifs or
  quiet sans, generous whitespace, real diagrams), not glassmorphism/neon/
  3D coins. The manifesto is a *document*, presented like one that expects
  to be cited.
- Radical transparency as UI pattern: every number links to its
  derivation; every decision links to its record. "Why?" affordance
  everywhere beats an explanations page nobody finds.
- Show the machinery honestly: agent-generated content is labeled as such,
  always (this is also `agent-engineer`'s disclosure rule — make the
  label a designed object, not a disclaimer).

## M0/M1 test plan (cheap, decisive)

- M0 before launch: 5-user comprehension test on the site — "what is
  this? who is it for? what's the catch?" in their words. The catch
  question surfaces whether the no-token/ledger framing lands or reads
  as scheme.
- M1 graph model: paper/Figma prototype of focus+context navigation on a
  real repo's issues; task = "find what's blocking X, dispute one edge,
  add one need". Five developers, think-aloud. Run *before* frontend
  investment hardens the model.
- Accessibility floor from day one: keyboard-navigable graph (focus+
  context makes this tractable where canvases make it impossible), WCAG
  AA contrast, screen-reader-sensible structure (the graph is lists and
  relationships underneath — expose that, it's naturally accessible).
