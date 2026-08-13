# socaity.dev — FAQ

**Status: PRE-LAUNCH DRAFT.** This page is written to publish at M0, *with*
the M0 instrument — the Standing Commitment, the Ledger Validation Policy and
the identity terms ([m0-standing-commitment.md](m0-standing-commitment.md)).
That instrument does not publish until a licensed Dutch practitioner has
reviewed it, and this page does not publish before it. Nothing here may be
quoted as live copy until then.

This page is bound by [standards/vocabulary-and-visual.md](standards/vocabulary-and-visual.md).
Where a sentence here and the instrument could be read differently, the
instrument governs, and the divergence is a shipping blocker rather than an
editing note.

> A public record of contributions. No token. Nothing to trade.
> This is a database.

Four objections are predictable, so they are answered here before they are
raised, including the parts we cannot answer yet.

---

## 1. "Is this another crypto thing?" <!-- vocab-ok: names the objection in the objector's own words in order to answer it; never our own description of the project -->

No, and the refusal is structural rather than tonal.

**There is no token and there never will be one.** No issuance is planned,
deferred, or held in reserve; refusing it is listed as a revenue refusal, not
only a design preference ([sustainability.md](sustainability.md),
*Anti-commitments*). There is nothing to buy and nothing to sell.

**A ledger entry is not an instrument.** Clause 3 of the Standing Commitment
states what an entry is not: not a debt, not a deposit, not repayable funds,
not electronic money, not a security, not a participation right, not a unit in
a collective fund, not a claim of any kind against us or anyone else. Entries
are **non-transferable and non-purchasable** — you cannot buy this and you
cannot sell it, now or by later amendment. An entry carries no monetary value
unless and until a distribution is declared, and no interest or time-based
accrual attaches to anything undeclared.

**The ledger is a database, not a blockchain.** <!-- vocab-ok: the mandatory first-screen asset adopted verbatim in socaity-1ux and carried in m0-standing-commitment.md Part I; "blockchain" appears only inside the negation --> It is a git-backed, append-only
public record with a hash chain over its entries. There is no consensus
protocol, no fee market, no validator class, no network to join by running
hardware. The whole record, together with the executable allocation rule, is
exportable at all times — the point of that is exit, not distribution.

**We promise nothing about money.** The governing framing is: *we make no
promise that money will ever be distributed; we bind ourselves publicly to the
allocation rule if it ever is.* Whether, when and how much are entirely at our
discretion. What is surrendered is discretion over *allocation*: if a
distribution is ever declared, it is computed by versioned, deterministic,
published code, and the code governs over any prose describing it.

### The concession

We do take one idea from proof-of-work systems, and hiding it would be worse
than naming it. Contribution is scored per epoch as a share of a fixed pie, so
the same amount of work recorded into a small network records a larger fraction
of that epoch than the same work recorded into a large one. That is an
earliness premium, and it is real. It is explained structurally — fixed pie per
epoch, smaller network, larger share — and never as a percentage, a multiple,
or a projection of what an early record might one day be worth. There is no
number, because there is no amount until a distribution is declared, and none
is promised.

The sharper version of the objection is: *this is a pre-mine — the founder <!-- vocab-ok: quotes the pre-mine objection verbatim as the objection being answered, per socaity-xuz's requirement that we name it in the objector's words -->
records the early epochs and everyone else arrives late.* Today the founder is
the only contributor, so the founder's share of recorded contribution is all of
it. We publish that with the denominator as the headline —
the share is that large because there is one contributor, and it falls
mechanically as others appear. Founder labour runs through the identical rule,
at a publicly declared rate, under the same validation and the same challenge
exposure; there is no founder carve-out, and any value flowing to insiders in
respect of contribution flows exclusively through the published rule.

Money is deliberately the **last** thing built, not the first
([milestones.md](milestones.md), M5). The moment a record can turn into money,
every attack on the record becomes profitable, so the verification market has
to exist and be red-teamed first.

---

## 2. "So you're going to flood open source with AI slop PRs?"

That failure mode is the single most likely way this project destroys its own
constituency, so the answer has two halves: consent, and a public bar.

### Consent first

The rule is **consent precedes contribution**. Agents are pointed only at the
platform's own repositories or at projects that have opted in. This is not a
guideline we hold internally; it is adopted policy from
[council/socaity-15b.md](../council/socaity-15b.md), which makes consent a
**hard tier and structurally impossible to outweigh**:

- **consented** — targetable;
- **not yet asked** — facts about the project are visible in the public index,
  and the project is rendered as *a candidate for outreach*, never as a target
  for anyone's agent;
- **declined, or an existing AI-PR ban detected** — no targeting affordance is
  displayed at all.

The same resolution forbids any composite "actionability score" that could let
technical quality outrank consent, forbids the index from auto-spawning work
items, and forbids any sorting or list that puts a non-consenting project one
click away from being targeted. A maintainer's "no" is not a low weight; it is
a wall.

### The public quality bar

These are the rules an agent contribution must satisfy. They are published so
that a maintainer can hold us to them. Only rule 1 rests on an adopted council
resolution; the rest carry the marker below and say so on their face:

1. **Consent precedes contribution.** Only opted-in projects or our own repos.
2. `[UNRATIFIED — needs agent-engineer]` **Issue-first, PR-second.** The agent engages the project's existing issue,
   or files one, and waits for a maintainer signal before writing code. A pull
   request nobody asked for is spam even when it is correct.
3. `[UNRATIFIED — needs agent-engineer]` **Small, tested, styled.** Repo conventions matched, tests included, diffs
   minimal. One reverted agent PR costs more trust than ten merged ones earn.
4. `[UNRATIFIED — needs agent-engineer]` **Human-accountable.** Every PR names the human owner of the agent. "The
   agent did it" never launders responsibility.
5. `[UNRATIFIED — needs agent-engineer]` **Disclosed.** Every PR states that it was agent-authored and links the
   graph node that priced the work — the same link is the audit trail.

Rule 1 and the consent tiers are council-adopted (socaity-15b). Rules 2–5 are
committed in the repository as the role's standing quality bar and are
published here as binding on us, but they have not themselves been through a
council resolution; treat the wording as fixable, the substance as committed.

### What is not decided, and we will not pretend it is

- **How a project records, scopes and revokes consent** — the machine-readable
  consent record, per-repo policies and revocation are an open decision
  (bead `socaity-3o2`), and it has to be answered at M2 outreach time rather
  than at M3, because asking twice burns the relationship.
- **The etiquette specification** — how an agent discovers a project's
  contribution etiquette, the exact disclosure format in the PR body, how a
  stop signal propagates, and what happens when a rule is violated, are all
  open (bead `socaity-4bt`).
- **Evidence that our agents clear the bar** — there is none yet. The adopted
  calibration loop logs, for every targeted node, what the pipeline predicted
  and what actually happened (merged, revised, rejected, ignored), and
  prediction quality is the eval. No results exist because no PR exists.

The parts below are the drafter's proposals, written because a maintainer will
ask and silence is worse than a marked answer. They are **not** policy:

- `[UNRATIFIED — needs agent-engineer]` A maintainer-visible stop signal that
  halts targeting of their project immediately, without a conversation, and
  without us asking for a reason.
- `[UNRATIFIED — needs agent-engineer]` A published outcome record for agent
  contributions — merged, revised, rejected, ignored — including the ones that
  went badly. The logging is adopted; publishing it is not.
- `[UNRATIFIED — needs agent-engineer]` Any consequence attaching to an agent
  owner who breaks the bar. No enforcement mechanism has been designed.

Two limits are worth stating plainly. Agent verification can attest that
something compiles, that tests pass, and — partially, with rubrics and
adversarial checks — that a change matches its stated acceptance criteria. It
cannot attest that a change *solves a real problem in the real world*; only
realized usage over time does that, which is why recognition vests as
confidence accumulates rather than at merge. And a rule about not wasting
maintainer time is only as good as the humans running the agents, which is why
rule 4 exists.

---

## 3. "Isn't this just another bounty platform?"

A bounty prices a **task** that somebody already wants done and is already
willing to fund. That mechanism works, and where it works it needs no help
from us. It does nothing at all about the problem this project exists for:
the foundational work that unlocks enormous value downstream while capturing
almost none of it, which is therefore worth very little to any single actor
and stays unfunded.

The difference is where the price comes from. A bounty's price is set by the
person posting it, and it reflects their private benefit. Here the price is
computed from the **structure of the needs graph**: roughly, how much
downstream value a node unlocks relative to the direct demand it attracts.
Nodes with high unlocked value and low direct demand are exactly where the
tragedy of the commons strikes, and those are the nodes whose **subsidy
multiplier** rises until working on them is individually rational. It is a
Pigouvian subsidy made computable by the dependency structure — pricing the
externality, not the errand.

Three practical consequences:

- **The system never assigns work.** Nobody is directed, nobody contributes to
  an average, and there is no queue. Contributors point their own capacity
  wherever they choose; the subsidy changes what "wherever they choose" is
  worth.
- **Maintenance is first-class.** A bounty is a moment; software is a liability
  forever. Keeping a load-bearing node healthy is recognised continuously, and
  unmaintained load-bearing code is the actual tragedy of the software commons.
- **Verification is priced work too.** Review and red-teaming are graph nodes
  that carry recognition, not unpaid favours attached to somebody else's
  contribution.

### The concession

Bounties are not the enemy and are not excluded. When money eventually enters
the system it enters **attached to nodes** — bounties, sponsorships and grants
are the three named inflows — held in escrow and settled to contributors
according to the record. The platform is an escrowed marketplace at that point,
never an issuer of anything. So a fair reading of the finished system is "a
bounty board plus a subsidy layer on top", and the honest claim is narrower
than the slogan: **the subsidy layer is the new part, and it is the part that
is unproven.**

Two further honest notes. First, none of this money exists yet: through M0–M2
the only inflows are public-goods grants and they are recorded on the same
ledger as everything else, distributed or explicitly reserved under the same
rule. Second, the subsidy is only ever as good as the graph it is computed
over, and a sparse or manipulated graph produces confident nonsense. Which is
why the graph's own defences are the next question.

---

## 4. "One human, one voice is naive — you'll be swamped by fake accounts."

Correct, if the mechanism is left undefended. The design assumes adversaries
rather than pretending them away, and the defences are published as a table in
[vision.md](vision.md) under *Threat model*:

| Attack | Defence |
|---|---|
| Sybil demand — fake wanting, to inflate a node a colluder will "solve" | proof-of-personhood on the demand side |
| Dependency inflation — fabricated edges under pet projects | edges are contestable claims; probabilistic value flow through alternatives; public auditability |
| Need-splitting / duplicate farming | merge operations are themselves recognised, contestable graph work |
| Claimed-but-hollow solutions | recognition vests on realized usage; adversarial verification market |
| Capacity-fraction gaming — many identities each pledging "100%" | standing derives from observable tenure and consistency, never from self-declared capacity |
| Platform capture | the mechanism is public and auditable, and the data is forkable — exit is cheap |

Two design decisions do most of the work. Influence over what society needs is
**never** proportional to compute, money, or recorded contribution — if it
were, society's needs would become the needs of whoever owns the most hardware,
and the legitimacy the whole mechanism rests on would be gone. And the
democratic demand side is switched on **late** (M4), on a graph that already
carries real supply and real content, precisely because it is the part with no
proven defence.

### What is genuinely open

These are open questions, not answers we are withholding:

- **Which personhood mechanism.** vision.md holds this open by name: which
  mechanism clears the Sybil bar *without excluding the people the platform
  most needs to hear*. Every candidate we know of trades one of those against
  the other. Undecided; we are also tracking eIDAS 2.0 / EUDI as a candidate
  attestation for the M4–M5 window (bead `socaity-q6g`), which is a
  jurisdiction-shaped answer and therefore only a partial one.
- **The gap between M0 and M4.** The record runs from day one and personhood
  arrives at M4, so identity-splitting attacks are possible before any
  personhood mechanism exists. The question being worked is which quantities
  are strictly capacity-weighted (splitting yourself across several keys gains
  nothing) and which are per-identity (splitting pays). The design rule we are
  aiming at is *nothing per-identity carries recognition before personhood
  exists* — but it is not ratified, it is bead `socaity-3la`, and until it is
  settled this is a real hole and not a hypothetical one.
- **Private demand versus a public record.** Needs are sensitive — health,
  finance, family. The mechanism is public; demand expression may be
  pseudonymous. Whether the substrate can carry state that is
  aggregated-public but individually-private, with no per-user receipt, is
  undecided (bead `socaity-8j4`). It matters beyond privacy: someone who can
  prove how they voted can sell that vote.
- **Erasure against an append-only record.** Reconciling a permanent public
  record with the right to erasure is open (beads `socaity-m2i`,
  `socaity-9g1`).
- **Who tunes the mechanism.** The multipliers, the damping and the vesting
  curves are set by someone, and that someone's income depends on them. The
  eventual answer is likely a split between a foundation that owns the
  mechanism and a company that sells service, but it is named as an open
  question in both [vision.md](vision.md) and
  [sustainability.md](sustainability.md), and the trigger condition for the
  split is not defined.

The honest summary: one human, one voice is a **requirement** the project has
committed to and a **problem** it has not solved. The commitments that survive
the gap are that influence is never bought, that the demand side does not ship
before it can be defended, and that if we get it wrong, the record and the rule
leave with you.

---

## Where to check us

- [vision.md](vision.md) — the mechanism, the threat model, the open questions.
- [milestones.md](milestones.md) — what is built when, and what each stage has
  to prove before the next one is allowed to start.
- [sustainability.md](sustainability.md) — how the builders make a living, and
  the four things we refuse to do for money.
- [m0-standing-commitment.md](m0-standing-commitment.md) — the operative text,
  its annexes, and its own register of unresolved items.
- [standards/vocabulary-and-visual.md](standards/vocabulary-and-visual.md) —
  the words and visual patterns we are not allowed to use, and why.

If an answer above is softer, bolder, or simply different from the instrument,
the instrument wins and this page is wrong. Say so publicly; corrections are
published rather than quietly edited.
