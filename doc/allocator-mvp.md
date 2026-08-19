# The personal planner at N=1 — multi-project budget allocator MVP

A slider of sorts: one human declares how their agentic compute budget divides
across their projects, and a fleet of worker machines makes the long-run spend
approximate that declaration. This is socaity.dev's core gesture — the system
never assigns work, it allocates resources toward expressed needs — at its
smallest possible scale: one user, three projects (socaity.dev, glass-factory,
computenet), a handful of machines.

Sited in socaity.dev because the multi-human generalization of this MVP —
many people's declarations aggregating into collective burn rates — is the
platform itself. ComputeNet remains the execution substrate underneath;
Glass Factory (later) is where consumption gets recorded and the
declared-vs-enacted diff becomes observable.

## Context: what exists

- Each project manages tasks in its **own beads repository** (bd + dolt sync).
- ComputeNet has a wave-based plan-orchestrator (Docker workers over git
  worktrees) and a multi-machine shared-backlog setup — single-project today.
- The MVP adds the meta-layer: machines decide *which project* to serve
  before they pick *which item*.

## Requirements

### R1 — Project registry

A small config listing the participating projects. Each entry points at the
project's **task source** — today, that project's own beads repo — plus its
code repo and runner invocation. Task storage location is a per-project detail
behind one interface: "give me your most important ready task." The invariant
is only that every worker machine can reach and sync the task repositories of
every project it might draw. Adding a project is editing this file.

### R2 — Declared allocation

A versioned weights artifact (`allocation.yaml`) holding:

- **Ratios**: fractions per project summing to 1.
- **Monthly spend ceiling**: "at most 10% of my budget this month" —
  concretely `monthly_cap: {hours: H}`, a self-declared session-hours number
  standing proxy for subscription capacity (the actually scarce resource).
- The rolling window the ratios apply over.

Hand-edited in the MVP; git history is the change log. Schema shaped so a
slider UI can write it later and so each change can be emitted as a ledger
event (`allocation.declared`).

Ratios are **soft**: any moment may violate 60/40; the month should
approximate it. The cap is **hard**: spend never exceeds it.

### R3 — Metering

Every worker session appends one record to a shared append-only spend log:

```
{project, machine, work_item, started, ended}
```

Unit is session wall-clock (the subscription-capacity proxy). JSONL, synced
between machines over the same channel as beads/dolt. No token scraping.

With lottery scheduling the spend log is not needed to enforce ratios — only
to enforce the monthly cap and to generate the report. Ratio enforcement is
stateless.

### R4 — Scheduling by weighted lottery

When a machine is free:

1. **Check the cap**: if this month's total enacted hours ≥ ceiling, no draw —
   machines go quiet until the month rolls over.
2. **Restrict the draw to projects with ready work** (spillover): renormalize
   the declared weights over that set. 60/40 with the 60 starved → the 40
   draws at 100%. Spillover redistributes spend but never creates it — the
   cap remains the hard guarantee.
3. **Draw a project at random**, weighted by the renormalized ratios.
4. Ask that project's task source for its most important ready task; run it
   to completion (no preemption).

A machine idles only when the cap is hit or no project has ready work.
Long-run convergence to the ratios comes from the law of large numbers, which
matches the soft-ratio requirement exactly.

### R5 — Starvation is visible, not enforced

Each draw where a project was excluded for having no ready work is recorded.
Ratio distortion from spillover must be explainable from the log: "GF
received 78% enacted vs 40% declared because ComputeNet was starved for 11 of
30 days." Reserved-but-unspendable budget means the bottleneck is
decomposition, not compute — that project needs its backlog refilled or
unblocked. Keeping backlogs decomposed is part of operating the system.

### R6 — Report

A generated digest per window, derived purely from the weights history and
spend log (replayable from the founding — the law-1 discipline from day one):

- Declared vs enacted share per project, with starvation-driven drift
  explained (R5).
- Cap tracking: hours spent vs ceiling, projected month-end burn.

## Accepted trade-offs

- **Draw-count vs time convergence.** The lottery converges on draw counts,
  but the unit is time; systematically different task durations across
  projects will drift time-shares from the ratios even as draw-shares
  converge. Accepted for the MVP; R6 reveals whether it matters. Upgrade path
  if it does: sample weighted by remaining deficit instead of raw weights —
  keeps the randomness, self-corrects for duration.
- **Approximate enforcement.** Per-machine independent draws, no central
  allocator; convergence comes from many small work items.
- **Spillover distorts ratios.** Chosen knowingly (work-conserving beats
  strict reservation at this scale); acceptable because the cap is respected
  and the distortion is explainable from the log.

## Non-goals

Multi-user weight aggregation, credits/pricing, preemption of running
sessions, token-level caps, cross-project dependency awareness, the slider UI
itself (fast follow writing R2's artifact).

## Acceptance test

Two machines, three projects, one week. Change the weights mid-week: enacted
shares converge toward the new declaration within the window. Empty one
project's backlog: its share spills over and the report explains the drift as
starvation. Drive spend to the ceiling: all machines stop drawing until the
month rolls over.
