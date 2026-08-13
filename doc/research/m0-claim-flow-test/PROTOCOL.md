# M0 Claim-Flow Pre-Launch Test — Protocol

**Status: NOT YET RUN.** This document is the instrument, not a result. No
participant has been recruited, no session has been conducted, and no timing
data exists. `results-template.md` is empty by design and must stay empty until
real sessions produce real answers.

**Ticket:** socaity-4qy · **Feeds:** socaity-bxo (M0 launch sequencing) ·
**Source:** [council/socaity-ipg.md](../../../council/socaity-ipg.md),
clause 7 — the four tests the resolution names as pre-launch gates.

**Under test:** [`/claim`](../../../tools/render/templates/claim.html) ·
[`/claim/reserved`](../../../tools/render/templates/claim_reserved.html) ·
[the merge comment](../../templates/merge-comment.md)

---

## 1. What is being gated

M0's done-condition runs through this flow: a stranger's contribution is
merged, and they attach it to a key only they hold. Everything before the merge
has been designed to need no key concepts at all; this is the one place a
contributor pays a real cost, and it is paid at the moment of highest
motivation. If it does not convert, the milestone does not complete.

The four tests below are the ipg resolution's clause 7, verbatim in substance:

| | Test | Passes when |
|---|---|---|
| (a) | Five developers complete `/claim` starting from the merge comment alone | 5 of 5 finish; median under 3 minutes; no participant needs the facilitator |
| (b) | Those five can say, unprompted, what the private key is for and what losing it would mean | 5 of 5 state both, in their own words, without seeing the page again |
| (c) | A stranger reads a **claimed** entry permalink | states whose it is, what it records, and how they would check it — inside 30 seconds |
| (d) | A stranger reads an **unclaimed** entry permalink | states who it belongs to and why — inside 30 seconds |

Failure of any one of them blocks the launch post. The standing instruction on
failure is the same one socaity-xuz gave the comprehension test: **redesign the
step that failed; do not add copy on top of it.**

---

## 2. What is already automated, and what it does not prove

`tools/claim/test_claim_flow.sh` runs the three published copy-paste blocks in
a clean `HOME`, exactly as they are rendered — the script reads them out of
`tools/render/generators/claim.py` rather than keeping a second copy — and then
checks the resulting attestation with stock `ssh-keygen -Y verify` and with
`tools/claim/verify_claim.py`, including four rejection cases (a tampered link line, a
mismatched account, a stripped signature, and a genuine signature made in a
different namespace).

Run it before every session, and record its output in the results file:

```
tools/claim/test_claim_flow.sh
```

What it proves: the commands run, in that order, on a machine with nothing set
up, and produce an attestation that verifies. What it cannot prove: any part of
test (a) except the machine time, which is negligible and was never the
question — and nothing at all about (b), (c) or (d). **The script passing is
not a result for this protocol.** Do not report it as one.

---

## 3. Participants

**Five for (a) and (b).** Five for (c) and (d), who must be *different people*:
a participant who has just walked the claim flow cannot read the permalink as a
stranger.

Required for (a)/(b):

- comfortable in a terminal (M0 contributors are developers; this is not a
  test of non-developer accessibility, which is an M1 in-browser-keygen
  question and out of scope here);
- has **not** read the manifesto, the FAQ, or any council record;
- has **not** used `ssh-keygen -Y sign` before, or does not remember doing so.

Required for (c)/(d):

- has never seen this project;
- no requirement to be a developer — the 30-second read is a claim about the
  page, not about the reader.

Disqualifying for all four: anyone who has contributed to socaity, anyone the
facilitator has discussed the mechanism with, and the founder.

---

## 4. Session — tests (a) and (b)

Setup: a real merged pull request on a scratch repository, a real merge comment
posted from `doc/templates/merge-comment.md` with both placeholders filled, and
a machine the participant has not prepared. Screen recording with consent, or
no recording.

1. **Hand them the merge comment and nothing else.** Say: "You made this
   change. This comment appeared. Do whatever you would do." Then stop talking.
2. **Start the clock** when they open the comment. **Stop it** when they post
   the attestation comment, or when they say they are done, or when they give
   up. Record which of the three it was.
3. **Do not help.** If they ask a question, write it down verbatim and say "I
   can't help with that during the session — do whatever you'd do if I weren't
   here." An answered question is a lost data point about the page.
4. **Record every hesitation over five seconds**, with what was on screen.
5. When they finish, **close the page**, then ask, in this order, and write the
   answers verbatim:
   - "In your own words, what was that for?"
   - "What is the file it made?"
   - "What happens if you lose it?"
   - "Is there a deadline?" *(there is not; a participant who thinks there is
     has found a copy failure and it is a finding, not a mistake)*
   - "Who can see what you just published, and what does it prove?"

Test (b) passes only on answers given **after the page is closed**, unprompted
by the wording of the question. "It's a key" is not a pass for the first
question. "I'd be locked out" is a pass for the third; "I'd ask you to fix it"
is a fail and an important one — the whole point of the no-administrator design
is that nobody can.

---

## 5. Session — tests (c) and (d)

Two permalinks: one entry whose attribution is **reserved**, one that has been
**claimed**. Randomise which the participant sees first, so ordering does not
flatter either.

1. Show the permalink. Say: "Read this. Tell me what it is when you're ready."
2. **Stop the clock at their first substantive sentence**, not when they finish
   talking.
3. Then ask: "Whose is it?" and "How would you check that?"

Pass for (c): they say whose it is and what work it records, inside 30 seconds.
Pass for (d): they say it belongs to whoever made the merged change and has not
attached their name yet, inside 30 seconds — **without using the words
"anonymous", "unknown", "nobody" or "unassigned"**. Those four words are the
failure this state was designed to avoid; if participants reach for them, the
rendering is wrong regardless of what they say next.

---

## 6. Recording rules

- A cell in `results-template.md` holds a verbatim quote, a measured number, or
  nothing. Never an expectation, a paraphrase that improves the answer, or a
  plausible placeholder.
- Report raw counts (`4 of 5`). Five people is not a sample for percentages.
- Report the failures first in any summary. If a session is discarded, the
  reason goes in the file before the data does.
- The facilitator does not score their own copy. If the founder wrote the page
  under test, someone else runs the session.

---

## 7. What happens on a fail

| Fails | The change is |
|---|---|
| (a) on time | Cut a step or a decision, not words. Three blocks is already the budget; a fourth is a redesign, not a fix |
| (a) on completion | Find the exact line they stopped at and rewrite that command, then re-run the automated flow test — a block that confuses is usually also a block that is doing too much |
| (b) | The key explanation moves up the page or into the step it belongs to. It does not get longer |
| (c) or (d) | The entry rendering changes. Adding a caption to rescue a permalink fails the crop test by construction — a permalink is read without its page |

None of these is a launch-schedule decision. The resolution's paramount stands:
no milestone announcement while the first entry's contributor is null, and no
schedule-pressure exceptions.
