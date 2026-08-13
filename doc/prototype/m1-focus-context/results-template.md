# Results — M1 focus+context usability test (socaity-8wg)

**THIS TEMPLATE IS EMPTY ON PURPOSE. NO SESSIONS HAVE BEEN RUN.**
Every row below is a blank to be filled by a human facilitator who watched a
real person use `prototype.html`. Do not fill any cell from inference,
simulation, or an agent's guess about how a developer would behave. A cell
filled without a witnessed session invalidates the whole test.

- Test run by: `____________________`
- Dates: `____________________`
- Prototype version (git hash of prototype.html): `____________________`
- Protocol version: `PROTOCOL.md` as of `____________________`

## 0. Participants

| | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| Role (maintainer / team dev / triage-non-dev) | | | | | |
| Years shipping code | | | | | |
| Open issues in their own repo (>50 required) | | | | | |
| Stranger to founder? (y/n — need ≥3 y) | | | | | |
| Recruited via | | | | | |
| Compensated? | | | | | |
| Date / duration | | | | | |

## 1. First impression (before any click)

Verbatim answer to "tell me what you are looking at".

| | Verbatim |
|---|---|
| P1 | |
| P2 | |
| P3 | |
| P4 | |
| P5 | |

Did they use the words problem/solution/approach/blocker unprompted? Which?

| | Words used | Words that confused them |
|---|---|---|
| P1 | | |
| P2 | | |
| P3 | | |
| P4 | | |
| P5 | | |

## 2. Task A — find what is blocking "Harden the existing single-node engine"

| | Time | Direct reqs named (of 5) | 2nd-level req named? | Prompts given | Used breadcrumbs? | Asked for whole-graph view? | Pass / Partial / Fail |
|---|---|---|---|---|---|---|---|
| P1 | | | | | | | |
| P2 | | | | | | | |
| P3 | | | | | | | |
| P4 | | | | | | | |
| P5 | | | | | | | |

Observations (hesitations >5s, what was on screen, wrong turns):

- P1:
- P2:
- P3:
- P4:
- P5:

## 3. Task B — dispute one edge

| | Time | Found "Dispute this link" unprompted? | Edge disputed | Reason about relationship or node? | Expected deletion? | Noticed history entry? | Pass / Partial / Fail |
|---|---|---|---|---|---|---|---|
| P1 | | | | | | | |
| P2 | | | | | | | |
| P3 | | | | | | | |
| P4 | | | | | | | |
| P5 | | | | | | | |

What did they look for first (delete / edit / comment / flag / other)?

- P1:
- P2:
- P3:
- P4:
- P5:

## 4. Task C — add one need

| | Time | What they added | Where they attached it | Justified placement? | Noticed it was unweighted? | Read that as honest or broken? | Pass / Partial / Fail |
|---|---|---|---|---|---|---|---|
| P1 | | | | | | | |
| P2 | | | | | | | |
| P3 | | | | | | | |
| P4 | | | | | | | |
| P5 | | | | | | | |

## 5. Task D — OR-branch prediction (asked BEFORE demonstrating)

Verbatim prediction:

| | Verbatim answer to "what happens to everything listed under it?" |
|---|---|
| P1 | |
| P2 | |
| P3 | |
| P4 | |
| P5 | |

Scoring — predicted (P) / not predicted (N) / contradicted (C):

| Behaviour | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| 1. Nothing deleted; losing branch kept, greyed | | | | | |
| 2. Exclusive requirements flagged "no live approach requires this" | | | | | |
| 3. Shared requirement survives untouched (benchmark suite) | | | | | |
| 4. Surviving branches' weights are NOT repriced | | | | | |

What surprised them after they ran it (verbatim):

- P1:
- P2:
- P3:
- P4:
- P5:

## 6. Post-task questions

| | Q1 would you use it / instead of what | Q2 where do "favored/contested" come from + trust | Q3 what does "unweighted" mean | Q4 wanted a whole map? what for | Q5 person or machine? what told you |
|---|---|---|---|---|---|
| P1 | | | | | |
| P2 | | | | | |
| P3 | | | | | |
| P4 | | | | | |
| P5 | | | | | |

**Q2 red-flag check** — did any participant read the buckets as a vote, market,
measurement, or team consensus? (Any single yes = absolute fail of the bar.)

| | Yes/No | Exact words |
|---|---|---|
| P1 | | |
| P2 | | |
| P3 | | |
| P4 | | |
| P5 | | |

## 7. Session logs

Paste the output of "Copy session log" per participant.

<details><summary>P1</summary>

```
```
</details>

<details><summary>P2</summary>

```
```
</details>

<details><summary>P3</summary>

```
```
</details>

<details><summary>P4</summary>

```
```
</details>

<details><summary>P5</summary>

```
```
</details>

## 8. Verdict against the pre-declared bar

| Bar | Required | Observed | Met? |
|---|---|---|---|
| Task A pass, no help, ≤2 min | 4 of 5 | | |
| Task B pass, dispute found unprompted | 4 of 5 | | |
| Task C pass, placement justified | 4 of 5 | | |
| OR-branch points 1 and 2 predicted | 3 of 5 | | |
| OR-branch point 3 (shared requirement) predicted | 2 of 5 | | |
| Nobody expects automatic repricing of survivors | 0 of 5 expect it | | |
| Buckets read as vote/market/measurement/consensus | 0 of 5 | | |
| Needed a whole-graph map to finish tasks | ≤1 of 5 | | |

**Overall: PASS / FAIL** `__________`

If FAIL, which specific bar failed and what class of remedy it implies
(affordance fix / copy fix / model change / schema change):

-

If the remedy is a model or schema change, name the council decision it
reopens (`socaity-sbb` schema, `socaity-6kb` weight display, or neither):

-

## 9. Decisions taken from this test

| # | Finding | Evidence (participant + quote) | Decision | Beads issue filed |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |
