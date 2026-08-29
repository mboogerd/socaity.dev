# Why the invariants exist

Compressed from ~2 months of computenet's unattended-work history. Each rule is
the cheap form of a lesson that was paid for once. The skill states intent
rather than procedure on purpose: computenet's 13k-line original showed that
spelling out the *how* breeds rules, which breed exception rules — while an
agent given the *why* routes around novel situations correctly.

**Main checkout clean, work in worktrees.** Sessions overrun their slot and
become concurrent with the next; a dirty main checkout makes every concurrent
session's premises false (stashes, half-staged files, wrong HEAD). Worktrees
branch off `origin/main` and cannot interfere with each other or with the
anchor. This is also what makes parallel subagents safe: one worktree each, no
shared mutable checkout.

**Land through PRs.** Main advances only by merges, so concurrent sessions
never race a direct push; history stays reviewable per-change; a bad landing is
one revert. Merge-your-own is fine exactly when gate-green + clean scope +
easy-revert all hold — the same three-part confidence test computenet uses for
`gh pr ready`. When one fails, the open PR with a named doubt *is* the
deliverable.

**Pull before push (beads).** The pull is what makes a claim a lock instead of
a private note. Skipping it is how two machines both claim one item or mint the
same id (computenet, 2026-08). A round-trip costs seconds; a clobber costs a
session.

**No `bd create --parent=` under shared epics.** Child ids come from a
per-database counter reconciled only at sync. Two machines filing under one
parent between syncs mint the same id for different beads; conflict resolution
destroys one of each pair (measured on computenet, 2026-08-14). Unparented
creates draw hash ids and cannot collide.

**Premise verification.** A session that builds on a false premise produces
work whose every step is unsatisfiable — discovered at review time, wasting the
slot. A parked `QUESTION:` costs one paragraph and routes the decision to a
human (computenet-egl, 2026-08-19: an epic correctly parked rather than broken
down on a machine that could not build its deliverable).

**The 24h stale-claim window.** Crash leftovers must be recoverable or the
queue deadlocks; fresh claims must be safe or two machines double-implement.
24h with a takeover comment is slow enough to never race a live session,
traceable for the crashed one.

**One claim, many subagents.** The claim is the unit of accountability and
crash-recovery, so there is exactly one per session. Parallelism happens
*under* it — subagents in their own worktrees — and the session reads every
diff, because a subagent's work lands on the session's claim and the session's
name.

**Honest close comments.** An unattended session's summary is the only reviewer
present. A "done" without a passed gate poisons the premises of every later
session that reads the bead as landed truth.
