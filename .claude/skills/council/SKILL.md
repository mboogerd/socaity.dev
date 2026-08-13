---
name: council
description: Convene the expertise roles on a cooperative beads issue — each role speaks, perspectives are recorded as comments, consensus is found or trade-offs escalated to the founder. Use when the user invokes /council, asks to resolve a cooperative issue, or asks to run the deliberation workflow.
---

# Council

You convene a deliberation between socaity.dev's expertise roles on a
cooperative issue. Protocol:
[expertise-protocol.md](../../../doc/expertise-protocol.md). The
deliberation is public and auditable — all substance goes into beads
comments, not just the chat.

## Selecting issues

- `/council <issue-id>` — deliberate that issue.
- `/council` or `/council all` — list open issues having any `needs:`
  label (`bd list --status open` + inspect labels), order by priority and
  by how many other issues depend on them (`bd dep`), then deliberate
  them one at a time, most-blocking first.

## Procedure per issue

1. **Convene.** `bd show <id>`. Participants = the `role:` owner plus
   every `needs:` role. Read each participant's charter
   (`.claude/skills/<role>/SKILL.md`); read a role's `knowledge.md` when
   its domain is central to the question. Read any doc sections the issue
   cites. Mark in progress: `bd update <id> --status in_progress`.
2. **Round 1 — positions.** Each role in turn states, *from its own
   charter and incentives*: its answer or proposal, its reasoning, and
   its red lines (what it would not accept). Post each as
   `bd comment <id> "[<role>] ..."`. Roles must genuinely differ where
   their charters differ — a round of polite agreement is a failed round;
   redo it with each role explicitly attacking the emerging default.
3. **Rounds 2–3 — convergence.** Each role responds to the others:
   concessions, syntheses, remaining objections. New facts beat
   restatement; a role with nothing new says "no change" and is skipped
   in later rounds. If deliberation surfaces a genuinely separate
   question, file it as a new issue (per protocol conventions) and link
   it (`bd link` / `bd dep`) rather than widening this one.
4. **Close out — consensus** (all roles accept, red lines respected):
   post a final comment `[council] RESOLUTION: ...` summarizing the
   decision, the reasoning, and any follow-up issues filed; then
   `bd label add <id> consensus` and `bd close <id>`.
5. **Close out — no consensus after round 3**: post
   `[council] ESCALATION:` comment containing: the options (2–4), which
   roles back each and why, the trade-offs stated symmetrically, and
   each option's reversibility. Then `bd label add <id> escalated` and
   leave it open — only the founder closes escalated issues. Escalate
   only genuine trade-offs; "we didn't try hard enough" is not an
   escalation.

## After a batch

Report to the founder in chat: issues resolved (with one-line
resolutions), issues escalated (with the options table), new issues
spawned, and whether the open set is shrinking toward all-`task` — the
protocol's definition of "ready to build". Then `bd dolt push`.

## Ground rules

- Fidelity over harmony: each role argues its charter honestly, citing
  its knowledge layer where it applies. The founder's known preferences
  are context, never a trump card.
- The docs are the spec; proposals to change the vision get filed as
  `decision` issues, never smuggled into a resolution.
- Keep comments substantive and self-contained — the beads thread must be
  readable by someone who never saw the chat session.
