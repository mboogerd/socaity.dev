# Expertise protocol

How the role skills in `.claude/skills/` collaborate through beads to
recursively resolve open questions until development can start. Companion to
[vision.md](vision.md), [sustainability.md](sustainability.md),
[milestones.md](milestones.md).

## The roles

| Skill | Expertise |
|---|---|
| `mechanism-designer` | Incentive design, credit system, market mechanics |
| `platform-engineer` | Distributed systems, ComputeNet substrate, forkability |
| `data-analyst` | OSS ecosystem data, the M2 observatory index |
| `agent-engineer` | Agentic decomposition, contribution loop, verification agents |
| `identity-specialist` | Proof-of-personhood, pseudonymity, Sybil resistance |
| `legal-counsel` | Financial regulation, entity structure, compliance |
| `community-builder` | OSS community, maintainer relations, cohort recruitment |
| `grant-writer` | Public-goods funding, NGI/NLnet/STF pipeline |
| `launch-strategist` | Positioning, launch events, build-in-public marketing |
| `product-designer` | Graph UX, trust design, progressive complexity |

Each skill has two layers: the **charter** (SKILL.md — role, responsibilities,
workflow) and the **knowledge layer** (knowledge.md — domain checklists and
best practices, read only when doing deep work in that role).

## Issue conventions

All findings, research questions, and decisions live in beads. Labels:

- `role:<skill-name>` — the role that owns the issue.
- `needs:<skill-name>` — each additional role whose input is required.
  An issue with one or more `needs:` labels is **cooperative**.
- `research` | `decision` | `task` — what kind of issue it is.
  - `research`: an open question needing investigation.
  - `decision`: a choice between alternatives that must be settled.
  - `task`: concrete work, ready once its dependencies close.
- `consensus` — cooperative issue resolved by council; resolution recorded
  in comments before closing.
- `escalated` — council could not converge; a trade-off report for the
  founder exists in the comments. Only the founder closes these.

Issue description format (keep it short):

```
Context: <one or two sentences; link doc sections>
Question: <the actual question or claim>
Why it matters: <what is blocked or at risk>
```

Use `bd link` / `bd dep` to record when one question blocks another. Use
`bd find-duplicates` before filing — roles will independently discover the
same questions, and merging duplicates is part of the job.

## The workflow

1. **Analysis pass** — invoke a role skill ("analyze the docs"). The role
   reads `doc/*.md`, lists unbiased findings, then files issues: things it
   can resolve alone (`role:` only) and things needing other expertise
   (`needs:` labels). It resolves what it can immediately.
2. **Council** — `/council <issue-id>` convenes every role named on a
   cooperative issue. Each role speaks from its charter (and knowledge layer
   when depth is needed); perspectives are recorded as `bd comment` entries
   under a `[role-name]` prefix, so the deliberation is public and auditable
   — the glass house applies to the platform's own construction.
3. **Convergence** — up to three rounds. Consensus → record the resolution
   as a final comment, label `consensus`, close. No consensus → label
   `escalated` and write a comment with the options, each option's
   supporters, and the trade-offs; the founder decides.
4. **Recursion** — resolutions typically spawn new, more concrete issues.
   Repeat until the open set is only `task` issues: that is the signal that
   development of the initial product can start.

## Ground rules

- Roles disagree openly. A council where every role politely agrees in
  round one is a smell — each role must state what it would *not* accept.
- The docs are the spec. Claims about the vision cite the doc section;
  proposed changes to the vision are `decision` issues, never silent edits.
- Founder time is the scarcest resource: escalate only with a genuine
  trade-off report, never with "what do you think?".
