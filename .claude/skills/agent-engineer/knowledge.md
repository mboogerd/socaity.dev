# Agent engineering — domain knowledge

## The M3 PR quality bar (non-negotiable, in order)

1. **Consent precedes contribution.** Only target projects that opted in
   (via the M2 index outreach) or the platform's own repos. Unsolicited AI
   PRs are how curl and others ended up publicly banning them.
2. **Issue-first, PR-second.** The agent engages the project's existing
   issue (or files one) and waits for maintainer signal before code. A PR
   nobody asked for is spam even when correct.
3. **Small, tested, styled.** Match repo conventions, include tests, keep
   diffs minimal. One reverted agent PR costs more trust than ten merged
   ones earn.
4. **Human-accountable.** Every PR names the human owner of the agent;
   the platform never lets "the agent did it" launder responsibility.
5. **Disclosure.** PRs disclose agent authorship and link the graph node
   that priced the work — that link is the marketing (see
   `launch-strategist`) and the audit trail.

## Decomposition quality

- AND/OR decomposition failure modes: solution bias (decomposing into the
  first approach rather than surfacing alternatives — the vision explicitly
  guards against this; the agent must generate *competing* OR branches),
  wrong granularity (nodes too big to estimate or too small to matter),
  phantom dependencies (plausible-sounding edges that don't hold).
- Eval approach: golden decompositions on known projects (take a shipped
  project's real retrospective structure as ground truth), LLM-judge with
  rubrics for alternative coverage, human spot-checks on a sample. Track
  inter-run variance — an unstable decomposer can't be trusted to merge
  duplicate needs.
- Estimation: agents are systematically overconfident on effort. Calibrate
  against realized effort from merged work (the platform generates its own
  calibration data — close the loop by M3).

## Verification agents — what they can attest

| Signal | Agent-verifiable? |
|---|---|
| Compiles, tests pass, coverage delta | Yes, cheaply — table stakes, not "verification" |
| Matches declared need / acceptance criteria | Partially — LLM judgment, needs rubric + adversarial check |
| No regressions / security issues introduced | Partially — static analysis + red-team probes; false-negative-prone |
| "Solves a real problem in the real world" | **No.** Only realized usage over time attests this — which is why vesting exists |

- Red-team agents: give them a *budget and a target* (break this change,
  find the injection, produce a failing test), pay per confirmed find
  (their finds are ledger-credited graph work per the vision). Watch the
  collusion vector: red-teamer and author splitting rewards on planted
  bugs — randomize assignment, never let authors pick their reviewers
  (coordinate with `mechanism-designer`).
- Layer signals: cheap automated gates → agent review → human maintainer
  acceptance → usage over time. Each layer only sees what passed the
  previous one; price each layer's cost honestly.

## Metering

- Meter what's verifiable: tokens and wall-clock are auditable; "effort" is
  not. Burn rate per node = token budget per epoch, hard-capped.
- Log every agent run (prompt hash, model, tokens, output hash) to the
  ledger as observations — this is the metered capacity that compute
  credit is backed by, so it must be as auditable as money.

## Tooling posture

- Build on the user's own agents (Claude Code et al.) per the milestones —
  the platform provides targets, context packs, and verification, not a
  captive agent runtime. A "context pack" per graph node (need, acceptance
  criteria, repo conventions, entry points) is the M3 product surface.
- Keep the platform's own agent needs (decomposition, dedup, estimation)
  runnable as ordinary graph work so capacity contributors can run them —
  dogfooding the supply side.
