---
name: resolve-friction
description: Drains socaity.dev friction beads at the cheapest total cost — fix the cause, fail loudly, disclose progressively, rarely add skill prose, often close as won't-fix. Use when a work slot or the user asks to resolve frictions, drain the friction log, or improve the work skill.
---

# /resolve-friction

The goal is a lean, cost-effective work orchestrator — not a complete one.
Every sentence in the work skill taxes every future session, whether or not it
ever meets the problem; a lesson left unwritten costs only the sessions that
hit it, at re-derivation price. Resolve each friction at the cheapest total
cost — which is often writing nothing.

## When to act on a bead

Take beads labeled `friction`. Act when one has **recurred** (a second logged
incident, as comments on the bead) or a single incident was **severe** (an
hour lost, a wrong result shipped). One incident at moderate cost: leave it
open and move on. The log is the experiment; recurrence is the data.

## The resolution ladder — stop at the first rung that holds

1. **Fix the world.** Remove the cause: repair the script, config, doc, or
   tool invocation that generated the friction. Zero ongoing cost.
2. **Fail loudly.** Make the trap announce itself where it happens — a check,
   an error message, a gate — so the lesson arrives just-in-time, only to
   sessions that actually hit it.
3. **Progressive disclosure.** One paragraph in a reference file
   (`work/references/`), read only by sessions that go there.
4. **Skill prose** — the most expensive rung, for something every session
   meets. One sentence stating the fact or intent, never the procedure: facts
   prevent the behavior; prohibitions get argued with. The work SKILL.md has a
   hard budget of 90 lines — to add a line, name the line it displaces, or the
   addition is refused.
5. **Won't-fix.** Recurrence × re-derivation cost is below the standing tax of
   every rung above. Close the bead saying so. This outcome is normal, not a
   failure.

## Discipline

- Close every resolved bead naming the rung and the reasoning.
- Land changes like any work item: worktree, branch, PR (the work skill's
  invariants apply here too).
- If a resolution itself needs a rule to explain it, you picked the wrong rung.
