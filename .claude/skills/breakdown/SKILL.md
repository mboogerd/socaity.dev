---
name: breakdown
description: Decomposes one socaity.dev beads epic or feature into bd-ready child tasks with dependencies, using collision-safe creation. Use when /work meets an epic without ready children, or the user asks to break down or decompose a beads item.
---

# /breakdown — one parent, sized children

1. Read the parent bead fully and every doc it cites. Verify its premises on disk
   first; a false premise gets a `QUESTION:` comment on the parent and stops the
   breakdown — children would inherit the falsehood.
2. Check for an existing breakdown before creating anything: children
   (`bd dep list <parent>`) and the parent's comments. A prior session may have
   half-finished — extend it, never duplicate it.
3. Cut 3–10 child tasks. Each: completable in one unattended session,
   self-contained (title; description with file pointers; explicit acceptance
   criterion), decomposing only decided scope — a council resolution, a milestone
   criterion, or the parent's own text. No invented scope.
4. Create collision-safe: `bd create` UNPARENTED (hash ids), then
   `bd dep add <child> <parent> --type parent-child`, then `blocks` edges
   task↔task where order genuinely matters (bd refuses blocks on epics).
   Priorities: inherit the parent's unless ordering dictates otherwise.
5. Leave a breakdown comment on the parent listing the child ids. Bracket the
   whole write set: `bd dolt pull` before, `bd dolt push` after.

Why unparented-then-reparent and the pull/push bracket are load-bearing:
[../work/references/why.md](../work/references/why.md).
