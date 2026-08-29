# Why the non-negotiables exist

Compressed from ~2 months of computenet's unattended-work history. Each rule paid
for itself in a real incident; the rule is the cheap form of the lesson.

**Pull before push.** The pull is what makes a claim a lock instead of a private
note. Skipping it is how two machines both claim one item or mint the same id
(computenet, 2026-08). A round-trip costs seconds; a clobber costs a session.

**No `bd create --parent=` under shared epics.** Child ids come from a
per-database counter reconciled only at sync. Two machines filing under the same
parent between syncs read the same counter and mint the same id for different
beads; conflict resolution then destroys one of each pair (measured on
computenet, 2026-08-14). Unparented creates draw hash ids and cannot collide;
re-parenting afterwards keeps the id.

**Premise verification before implementing.** A session that builds on a false
premise produces a task tree whose every step is unsatisfiable — discovered only
at review time, wasting the whole slot. A parked `QUESTION:` comment costs one
paragraph and routes the decision to a human (computenet-egl, 2026-08-19: an
epic was correctly parked rather than broken down on a machine that could not
build its deliverable).

**The 24h stale-claim window.** Crash leftovers must be recoverable or the queue
deadlocks under any scheduled use; fresh claims must be safe or two machines
double-implement. 24h with a takeover comment is the compromise: slow enough to
never race a live session, traceable for the crashed one.

**One claim per session.** Parallel claims in one context balloon it and drift
the work. computenet's 13k-line skill solves this with dispatched subagents and
an orchestrator; this skill deliberately does not — if items here outgrow
single-session size, split them in `breakdown` instead of importing that
machinery.

**Honest close comments.** An unattended session's summary is the only reviewer
present. A "done" without a passed gate poisons the premises of every later
session that reads the bead as landed truth.
