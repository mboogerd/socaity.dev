---
name: work-unsupervised
description: Runs the `work` skill in autonomous mode — no human is available. Use when a cron job, scheduled task, or routine starts an unattended work slot, or the user says "/work-unsupervised".
disable-model-invocation: true
---

You are running **unsupervised**. Read the `work` skill and follow it (use the Skill
tool when available; otherwise read its SKILL.md directly).

This file adds only the conditions the run happens under. Everything about *what* the
work is and *how* to do it — selection, claiming, worktrees, the gate, PRs, closing —
lives in `work` and its references. Don't restate it here, and don't second-guess it.

## No human is available

This session was started by a scheduled task, not by a person. Nobody is reading your
output while it runs, and nobody will answer a question you ask.

- **Do not ask clarifying questions.** A question in your output is not a question — it
  is a dropped task. Decide it, or park it the way `work` step 5 does.
- **Do not wait or block on anything.** No approvals, no confirmations, no "let me know
  if you'd like me to continue."
- **Anything you want a human to see must be written somewhere durable** — a bead
  comment, a commit message, a PR body. Your transcript is not durable.
- **That includes complaints about the process itself.** `work`'s friction bead is the
  only channel you have for "this skill told me to do something that didn't work".
  Unsupervised, it is also the only way the skill ever improves — nobody was watching
  to notice. Use it, including for your own misreadings.

`work` step 1 must pass before claiming. A sandbox network failure gets one retry
through the approved network route when available; a denial or failed retry ends the
slot. Never claim or push an unsynced backlog.

## Where the bar sits when nobody is listening

An answer arrives on human time, not session time. A `QUESTION:` comment sits until
someone next looks, so parking is genuinely expensive — but so is a wrong guess on an
interface or a rule's semantics.

Record every assumption you *do* make in the PR body or a bead comment. That is the only
place a human will ever see it.

## Merging is a decision, not a question

`work` step 8 sets the merge bar; running unsupervised does not raise it. Leaving a
green, finished PR open for a human to click is a dropped task, same as asking a
question nobody reads.

## Ending the run

`work` ends with a session summary — follow that rather than inventing an ending. Two
failure modes to hold yourself to, since nobody is watching for them:

- **Padding.** If `bd ready` is genuinely empty or everything left is blocked, claimed
  or parked, stop early and say so. Inventing work to fill the budget is worse than
  finishing the slot early.
- **Stopping mid-flight.** Whatever state you leave behind is what a human finds — hold
  yourself to `work`'s invariants with no one there to check.
