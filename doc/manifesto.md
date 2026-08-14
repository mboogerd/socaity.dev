# socaity.dev

*The place where society self-develops.*

**The system never assigns work. It prices it.**

**No token. Nothing to trade. The ledger is a database, not a blockchain.** <!-- vocab-ok: the mandatory first-screen asset adopted verbatim in socaity-1ux and carried in m0-standing-commitment.md Part I; "blockchain" appears only inside the negation -->

Status: [mechanism designed](vision.md) · [record running](../ledger/) · [rule unwritten](#what-we-do-not-know) · [network of one](#is-this-a-crypto-thing). <!-- vocab-ok: a same-page fragment identifier, slugged from the heading two sections down whose own waiver covers it; the reader-visible words on this line are the four standing clauses, and the section it points at is where "there is currently one contributor" is evidenced -->

- **The record.** [Every entry, with its evidence and its arithmetic.](https://socaity.dev/ledger/)
- **The rule, as code.** [`rule/`](../rule/), and the [validator that refuses an epoch without it](../ledger/validator.py).
- **The needs graph.** [Our own roadmap, in the platform's own conventions.](https://socaity.dev/roadmap/)
- **The build.** [`tools/check.sh`](../tools/check.sh) renders this site twice and fails if the bytes differ.

---

The long answer is the second section of this page.

> **Publication status.** This is the M0 launch text. It publishes together
> with [the Standing Commitment](m0-standing-commitment.md) and not before —
> that instrument goes to a licensed Dutch practitioner first, and the three
> components publish together or not at all.

## Society knows how to want things. It is bad at building the things everyone wants and nobody will pay for.

Every ambitious thing rests on foundations — libraries, protocols,
infrastructure, research — that unlock enormous value downstream and capture
almost none of it. Everybody wants the foundation. Nobody wants to be the one
who pays for it. So it arrives late, or badly, or never, and everything built
on top of it waits. xz. log4j. The list is long and the list is boring, and
the boringness is the problem: quiet load-bearing work is exactly what markets
price worst.

Two things changed. Agentic AI turned software effort into something meterable
and delegable — you can now contribute *capacity*, not only hours. And it
became feasible to hold, in one shared structure, a live map of what people
need and how those needs depend on one another.

Together those make a mechanism practical that was not practical before:

**The system never assigns work. It prices it.**

Demand is expressed by people — one human, one voice, never weighted by money
or machines. Supply is self-directed: you point your own agents at whatever
you care about. Because the whole dependency structure is visible, the places
where underinvestment is structurally predictable — high downstream value, low
direct demand — become computable, and a **subsidy multiplier** rises on
exactly those nodes until someone finds it worth showing up.

Nobody is directed. Nobody contributes to an average. The pricing is what makes
caring about the commons individually rational.

The mechanism in full — the AND/OR needs graph, contestable edges, the
Pigouvian subsidy made computable, the verification market, and the table of
attacks it has to survive — is [doc/vision.md](vision.md). It is a dense
document on purpose. This page is the argument; that one is the design.

---

## Is this a crypto thing? <!-- vocab-ok: quoted reader objection, answered in the negative; never our own description -->

No.

**A public record of contributions. No token. Nothing to trade. This is a
database.**

There is nothing to buy and nothing to sell. Entries are non-transferable and
non-purchasable — you cannot buy this and you cannot sell it, and participation
is not an investment. <!-- vocab-ok: definitional negation, required FAQ copy per vocabulary standard §1.4 -->

That is not a promise about our character; it is a property of the code, and
the code is in this repository. The record is an append-only signed event log
([`ledger/log.py`](../ledger/log.py)), validated at append time against a closed
event catalogue ([`ledger/catalog.py`](../ledger/catalog.py)) by predicates you
can read in an afternoon ([`ledger/validator.py`](../ledger/validator.py)),
serialised as canonical JSON with floats rejected outright
([`ledger/canonical.py`](../ledger/canonical.py)). It is a file with a hash
chain. If we ever betray it, fork it — the record and the rule leave with you.

The obvious objection — that a record started by one person is a *pre-mine* — <!-- vocab-ok: names the objection in the objector's own words, per socaity-xuz; not asserted as our description -->
is a fair one. It is answered where it belongs, on the `/ledger` page that
publishes beside this one, with
the denominator as the headline: there is currently one contributor, so the
first epoch's shares are concentrated *because nobody else is in it yet*. The
same rules, the same validation, and a declared rate apply to the founder as to
anyone — clause 8 of [the Standing Commitment](m0-standing-commitment.md).

---

## What we promise, exactly

> Every contribution is recorded on a public, append-only ledger from day one.
> Records start as provisional and are confirmed through a published validation
> process. If money ever flows out of this project, it is allocated across
> confirmed records by a published rule, not by our mood. Whether, when, and
> how much is never guaranteed — no amount exists until a distribution is <!-- vocab-ok: canonical Part I paragraph, adopted verbatim in socaity-1ux; negates entitlement rather than asserting one -->
> declared. What the rule protects is your recorded place in it: confirmed
> weights can't be quietly rewritten, and the whole ledger is forkable if we
> ever betray that.

We make no promise that money will ever be distributed. We bind ourselves
publicly to the allocation rule if it ever is.

That paragraph is the ceiling, not the floor: no page of ours may claim more
than it says, and none may say it more softly. The operative text behind it —
eleven clauses, the validation policy, the identity terms — is
[doc/m0-standing-commitment.md](m0-standing-commitment.md).

The structural consequence worth naming plainly: a fixed pie per epoch means
the same contribution is a larger fraction of a smaller network. That is
arithmetic about a denominator, not a forecast about money. We will not put a
number, a multiple, or a projection on it, and if you meet us and ask what it
is worth, you will get this same structural answer.

---

## The glass house

Claims are cheap. These are the artifacts:

- **The record and its rules** — [`ledger/`](../ledger/): the append-only log,
  its closed event catalogue, its validator, and their tests. The page that
  renders the record, `/ledger`, publishes with this one; every entry links its
  evidence and every displayed number is computed from a published artifact
  rather than typed in.
- **Our own roadmap as the first needs graph** —
  [`graph/nodes/`](../graph/nodes/) and [`graph/tickets/`](../graph/tickets/),
  checked on every change by
  [`.github/workflows/graph-check.yml`](../.github/workflows/graph-check.yml).
  This project's construction is the first commons problem it has to solve, so
  it is modelled in the platform's own conventions.
- **How decisions were actually made** — [`council/`](../council/). Every
  design question was argued by role-specialists in the open and adopted by
  consent; the raw deliberations are checked in, including the rounds where a
  proposal was overruled or withdrawn.
- **The words we forbid ourselves** —
  [`doc/standards/vocabulary-and-visual.md`](standards/vocabulary-and-visual.md)
  and the machine-checked
  [`banned-words.txt`](standards/banned-words.txt) that gates every public page
  in CI, this one included.
- **The road, in order** — [doc/milestones.md](milestones.md); how the builders
  eat while walking it — [doc/sustainability.md](sustainability.md).

---

## What we do not know

The honesty here is not modesty. These are unsolved, and anyone who tells you
otherwise is selling something.

- **The allocation rule is not written yet.** What exists is the *procedure*:
  the validator refuses to open any epoch after the first without a
  hash-attested, published rule version
  ([`ledger/validator.py`](../ledger/validator.py)). Until that rule ships as
  versioned executable code, an epoch share is a plan, not a number.
- **Proof of personhood.** One human, one voice needs a mechanism that resists
  Sybil attacks without excluding the people we most need to hear. We do not
  have one we like.
- **When money is allowed near this.** The moment a recorded contribution can
  be turned into money, every attack becomes profitable. That door stays shut until the verification
  market has been pointed at us and survived it — deliberately the last
  milestone, not the first.
- **Losing branches.** Exploring an approach that fails still produces
  information. We cannot yet price it.
- **Who tunes the multipliers.** The parameters that decide what the commons is
  worth are set by people whose own income depends on them. Publishing them and
  making exit cheap is a real constraint but not a complete answer; it is the
  sharpest open question in [doc/sustainability.md](sustainability.md).
- **The commitment is unreviewed.** No licensed practitioner has read the
  instrument yet. Until one has, nothing above it publishes.

Summary of our actual position: mechanism designed, record running, rule
unwritten, network of one.

---

## Who this is for

People who have watched something load-bearing rot for want of a maintainer,
and who suspect the problem is not laziness but pricing.

There is no queue to join and no position to hold. Two things are worth doing:
read [vision.md](vision.md) and try to break it — the attack table is a
challenge, not a boast — and [open a challenge against anything in the record
that you think is wrong](https://socaity.dev/all/).

The milestone we care about is not an audience. It is the first entry on that
ledger that was not written by us.
