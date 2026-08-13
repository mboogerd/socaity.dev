# Platform engineering — domain knowledge

## Ledger design (append-only, public, auditable)

- Event-sourced log with content-addressed entries (hash chain) gives
  tamper evidence without consensus machinery. Periodic signed checkpoints
  published somewhere you don't control (git tags in public mirrors is
  enough at M0).
- The ledger records *contributions*; credit balances are a **derived
  view**, recomputable by anyone from the log. Never store balances as
  source of truth — the standing commitment ("future inflows distributed
  retroactively per recorded contribution") is only credible if a stranger
  can recompute it.
- Schema versioning from entry #1: the retroactive distribution at M5 will
  replay events written years earlier. Treat the event schema like a wire
  protocol (additive changes only, explicit version field).
- Separate *observation* (agent-hours metered, PR merged) from
  *valuation* (credit assigned). Valuations change when parameters are
  retuned; observations never do. Retroactive re-valuation is a feature —
  design for replay-with-new-parameters.

## Forkability as an executable property

- A fork needs: full data export (graph + ledger + comments), the mechanism
  code, and *no dependence on privileged identity*. Test it: a CI job that
  stands up a fork from public artifacts and replays state. If the fork job
  is green, the exit-is-cheap claim is true; the day it breaks, capture has
  begun.
- Identity is the hard part of forking: pseudonymous IDs must be portable
  (user-held keys, not platform-issued rows) or forks lose everyone's
  standing. Coordinate with `identity-specialist`.

## Convergence and the graph

- Contestable edges = concurrent assertions about the same edge. Model
  edges as first-class entities with status (asserted/disputed/settled) and
  never delete — settle. This sidesteps most CRDT conflict pain: the data
  is append-mostly claims, not mutable cells.
- Merge/split of need nodes is the genuinely hard concurrent operation:
  merges can race with edits and other merges. Precedent: how Wikidata
  handles entity merges (redirects, not deletion; edits follow redirects).
- Probabilistic value flow is a classic incremental-view problem: value
  scores are a materialized view over graph + demand signals; recompute
  incrementally on deltas. This is exactly ComputeNet's dataflow shape —
  the domain fits the substrate; make sure it stays that way.

## Deterministic simulation

- Same event log + same parameters ⇒ same balances, on any node. This
  demands: no wall-clock reads in mechanism code (timestamps come from
  events), no map-iteration-order dependence, fixed-point or rational
  arithmetic for credit math (floats drift across platforms).
- Strategic-agent simulation harness: pluggable agent policies (honest,
  greedy, colluding ring, Sybil swarm) over the real mechanism code — not a
  reimplementation. If the sim runs a copy of the mechanism, the sim lies.

## Milestone-honesty checklist

- M0–M1 needs: a web app, a database, a signed append-only log. It does
  not need convergence, distribution, or ComputeNet maturity. Do not block
  the market window on substrate work.
- The substrate must be real by: M3 (metered agent capacity), M4 (live
  multi-writer graph at scale), M5 (replay-grade determinism for the
  retroactive distribution).
- Migration path > premature generality: design M1's plain-database schema
  so its event log can be replayed into ComputeNet later. The ledger's
  append-only discipline makes this nearly free — keep it that way.
