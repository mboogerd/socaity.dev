# Routing: demand levels and operating points

What a ticket demands of its executor, and which model+effort pair to write it
for. The skill cites this file; only this file changes when models rev.

- [Demand levels](#demand-levels)
- [Operating points](#operating-points)
- [Rules](#rules)
- [Provenance and calibration](#provenance-and-calibration)

## Demand levels

Assign each work child the **lowest** level it can honestly carry, and write it
to that level's profile. Padding a D2 with detail does not make it a D0 — the
level is set by how much judgment the ticket still requires, not by word count.

| Level | The executor must | The ticket must supply |
|---|---|---|
| **D0** mechanical | Follow instructions | Exact files by path, the convention cited by path, the verbatim test/gate command, zero open design choices, acceptance fully machine-checkable |
| **D1** local design | Choose an implementation within fixed constraints | The *what* and the constraints, the proof method, pointers to nearby prior art; acceptance mostly machine-checkable |
| **D2** open design | Decide approach or trade-offs | The problem, the boundaries, what must be proven; acceptance may need review judgment |
| **D3** judgment | Decide what the problem even is | Only the outcome and the constraints — this is breakdown's own altitude |

**The cheaper the intended executor, the more executable the acceptance
criterion must be.** A ticket whose acceptance needs taste ("idiomatic",
"well-factored") cannot be D0 at any level of description detail. Routing down
and strengthening the oracle are the same move: trust shifts from the executor
to the gate.

So decide, per work child, **what must be proven and how**. If the repo already
has the method (a gate script, a golden-vector suite, a lint rule), cite it by
path. If it does not, emit a **harness child** — "introduce proof method X" —
at D2, blocking the implementation children it unlocks. One harness ticket
subsidises N cheap ones.

## Operating points

The routing target is a **(model, effort) pair**, not a model. Effort moves
capability further than model choice does, and every point below is on the
cost/capability Pareto frontier — anything omitted is dominated.

| Point | Agentic | Terminal-Bench | GDPval | $/task | out tok/task | min/task |
|---|---|---|---|---|---|---|
| Luna medium | 31.8 | 53.2 | 38.5 | $0.01 | 3,940 | 0.6 |
| Luna high | 41.0 | 69.7 | 47.8 | $0.02 | 8,727 | 1.2 |
| Luna xhigh | 44.4 | 77.9 | 50.7 | $0.03 | 13,336 | 1.8 |
| Luna max | 46.9 | 80.9 | 53.5 | $0.05 | 20,046 | 2.6 |
| Sol medium | 47.9 | 86.1 | 52.2 | $0.29 | 4,758 | 1.1 |
| Sol high | 50.6 | 87.3 | 55.8 | $0.43 | 7,545 | 1.7 |
| Sol xhigh | 53.6 | **89.5** | 58.6 | $0.63 | 11,098 | 2.3 |
| Sol max | 57.8 | 88.0 | 60.5 | $0.95 | 16,879 | 3.6 |
| Opus 5 xhigh | 58.4 | 88.0 | 64.9 | $1.80 | 31,185 | 6.2 |
| Opus 5 max | **59.2** | 89.1 | **66.2** | $2.34 | 40,249 | 7.4 |

Default mapping:

| Level | Coding-hard | Judgment-hard |
|---|---|---|
| D0 | Luna high/xhigh | — |
| D1 | Sol medium/high | Sol high |
| D2 | Sol xhigh | Opus 5 xhigh |
| D3 | Sol xhigh + Opus review | Opus 5 max |

**Say which kind of hard it is.** The frontier differs per axis: Sol xhigh is
the best terminal/coding executor available *at any price* (89.5 beats Opus 5
max's 89.1 for a quarter of the cost), while Opus 5 max leads messy
real-world work by 5.7 GDPval points that no OpenAI point reaches. A
coding-hard D2 and a judgment-hard D2 route to different providers.

## Rules

- **Escalate by changing model, not by cranking effort.** More effort is not
  monotonically better: on tool-use benchmarks Opus 5 peaks at *high* (44.7)
  and declines at xhigh (43.3) and max (42.1). A bounced ticket goes sideways
  to the other provider or up a model, not up an effort notch.
- **Never route on per-token price.** Verbosity erases it. Sonnet 5 at max
  effort burns 72,342 output tokens per task, which lands it at $1.72/task and
  8.9 min/task — dominated outright by Opus 5 medium. Route on cost-per-task
  and tokens-per-task.
- **Verify one tier above where you implement.** When acceptance is not fully
  machine-checkable, review costs far less than generating at the higher tier
  would, and cross-provider review catches more than same-model review.
- **A bounce is a routing signal, not a failure.** An executor that finds the
  ticket underdetermined mid-flight labels it and stops rather than guessing.
- Known-dominated, do not route to: Fable 5 (agentic 56.6 at $3.14 — a
  reasoning model, not an agentic executor), Sonnet 5 max, Sonnet 4.6 max,
  Opus 4.7/4.8 max, every GPT-5.5 tier, most Terra tiers.

## Provenance and calibration

Figures: Artificial Analysis, read 2026-08-30 — Agentic Index (GDPval-AA v2 +
τ³-Banking), Terminal-Bench v2.1, and their weighted cost/tokens/time per
Intelligence Index task. **These are their task mix, not this repo.** Treat the
table as a prior and correct it from local evidence: bounce rate and gate-failure
rate per level, filed as friction beads.

Two coverage gaps to keep in mind. APEX-Agents (long-horizon agentic work) is
measured for only a handful of these points — the multi-hour unattended session,
which is exactly what `/work` does, is the least-benchmarked capability there
is. And under a flat-rate subscription the `$/task` column governs only overflow
decisions; **out tok/task and min/task are the real currency**, because weekly
limits are consumed in tokens and clock, not dollars.
