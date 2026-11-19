---
name: breakdown
description: Recursively decomposes one socaity.dev beads item — however abstract — into bd-ready children, typed as work or decision, until every leaf is implementable in one session. Use when /work meets an epic without ready children, or the user asks to break down or decompose a beads item.
---

# /breakdown — one parent, typed children, recursive

There is no epic/story/task taxonomy to satisfy. Only two things are defined:
the **leaf test** (base case) and the **split** (inductive step). Depth is an
outcome: a simple wish is a leaf immediately; a vague concept may take several
rounds. Levels are just distance from a leaf.

**Leaf test** — the item is a work task, stop splitting, when all hold:

- completable in one unattended session at the demand level it declares
  ([references/routing.md](references/routing.md));
- no unresolved decision that needs information not yet in hand;
- acceptance criterion falsifiable by that executor, and executable to the
  degree its demand level requires;
- blast radius bounded (a wrong result is a revert, not a migration).

## Before splitting

1. **Run the leaf test on the parent itself.** If it passes, it *is* the task —
   comment so and stop. The heavy path costs nothing when it isn't needed.
2. **Check for an existing breakdown**: children (`bd dep list <parent>`) and
   the parent's comments — including a prior fog list (below). A prior session
   may have half-finished: extend, never duplicate.
3. **Verify premises** — environmental (a tool, a service, a file the item
   assumes exists: check with a concrete command) *and* semantic ("test X
   proves P", "the spec already decides this": read it). These are the unknown
   knowns — the things the item believes that are false — and every child
   inherits them. A false premise: `QUESTION:` comment on the parent, stop.

## The split

Classify what the parent actually contains, then cut accordingly:

- **Decided scope** (a council resolution, a milestone criterion, the parent's
  own text, verified premises) → **work children**. Cut along one axis —
  workflow step, interface, data variation, business rule, or thinnest
  end-to-end slice first — not by architectural layer.
- **A question an agent can answer** (an external fact, a feasibility check,
  "how should this look") → a **decision child**: label `research` or
  `prototype`. Its acceptance criterion is *the question answered, with
  rationale recorded on the bead* — never product code. A prototype's artifact
  is throwaway evidence, linked, not merged.
- **A question only humans can settle** (values, scope, anything
  founder-gated) → a **decision child** with a `needs:` label, routed to
  /council. `/work` already skips these; the rest of the tree keeps moving.
- **Identifiable but not yet phraseable** → the **fog list**: name it in the
  breakdown comment under `Not yet specified`, don't cut it. If a would-be
  work child depends on an open decision's answer, it is fog, not a child —
  cutting it now just bakes in a guess.

Each child self-contained: title; description with file/doc pointers (the next
session starts fresh and knows the repo only through what you cite); explicit
acceptance criterion. No invented scope. 3–10 children; fewer if the rest is
fog — a small honest frontier beats a complete fiction.

**Check the cut** before creating: every parent acceptance criterion is
carried by some child (a criterion with no child means the split isn't
finished; a child serving none is scope creep); every quality the parent
requires proven maps to a named proof method in some child; every child is strictly
smaller in scope *or* uncertainty (a spike counts via uncertainty); and the
split decides no more than this level requires — record decisions made here
vs. deferred in the breakdown comment, so a premature commitment is visible.

## Route

Give each work child the **lowest demand level it can honestly carry**, say
whether it is coding-hard or judgment-hard, and write it to that level's
profile — [references/routing.md](references/routing.md). Decide there what
must be proven and how: cite the repo's existing proof method by path, or emit
a harness child that introduces one and blocks the children it unlocks. If a
child only carries at D2, split once more or accept the cost — never pad a D2
with detail and label it D0.

## Create

4. Collision-safe: `bd create` UNPARENTED (hash ids), then
   `bd dep add <child> <parent> --type parent-child`, then `blocks` edges
   task↔task where order genuinely matters (bd refuses blocks on epics).
   Priorities: inherit the parent's unless ordering dictates otherwise.
5. Leave a breakdown comment on the parent: child ids by type, decisions
   made-here vs. deferred, and the `Not yet specified` fog list. Bracket the
   whole write set: `bd dolt pull` before, `bd dolt push` after.

## Recurse lazily

Don't pre-expand the tree. Children get their own breakdown only when /work
reaches them and they fail the leaf test. When a decision child closes, its
answer may unfreeze fog or invalidate siblings — the next breakdown on this
parent (step 2 reads the fog list) graduates fog into children, re-scopes in
place, and says so in a comment. Breakdown is re-entrant per node, not
once-per-node.

Why unparented-then-reparent and the pull/push bracket are load-bearing:
[../work/references/why.md](../work/references/why.md).
