# socaity.dev — Sustainability

How the people who build the platform make a living without betraying it.
Companion to [vision.md](vision.md) and [milestones.md](milestones.md).

## The alignment test

Every revenue model must pass one question: **would it survive a fork?**

If income depends on something a fork could take away — lock-in, proprietary
data, captive users — it violates the principles *and* it is fragile. If it
depends on something a fork cannot cheaply replicate — trust, freshness,
service, a recorded position on the ledger — it is both aligned and durable.
Forkability is the vision's ultimate check on capture; it is therefore also
the audit standard for every euro the platform's builders earn.

For this project, *how* the builders get paid is a product feature. Every
aligned revenue stream demonstrates that the mechanism works; every
misaligned one is a counterexample the manifesto hands its critics. The
platform's whole thesis is that commons work can be individually rational —
the founder's livelihood is its first test case.

## The backbone: paid by the mechanism itself

**Founder labor is recorded on the contribution ledger from day zero, at a
publicly declared rate.** No special founder privilege exists or is needed:
the ledger's standing commitment — future inflows distributed retroactively
in proportion to recorded contribution, with epoch-share earliness premium —
already gives the earliest and largest contributor the earliest and largest
claim. The founder is paid by the exact same rule as everyone else, and
anyone can audit why the numbers are what they are.

This is radical transparency applied to compensation, and it is dogfooding:
sustaining the platform's own construction is the first
tragedy-of-the-commons instance the platform must solve.

The backbone pays at M5. Everything below is either the bridge that feeds
the work until then, or the steady state that follows.

## Aligned revenue models

### 1. Take rate on the fiat rail *(M5, steady state)*

The platform is an escrowed marketplace: money enters attached to nodes and
settles to contributors per the ledger. A percentage on those flows funds
operations — under three conditions:

- **Visible** in every transaction, never buried.
- **Contestable**: platform operations are themselves a node on the graph;
  the rate is public and arguable like any other claim.
- **Disciplined by exit**: if the rate ever exceeds the value of the
  service, someone forks — and that is the check working as intended, not a
  failure mode.

### 2. Compute margin *(M3+)*

Fiat is an on-ramp for compute credit before it is an off-ramp. Someone must
operate that on-ramp: buy agentic capacity wholesale, meter it, resell it to
participants who would rather pay money than run their own agents. A
transparent margin on metered compute is wage-like and scales with real
network activity. It sells convenience, never influence — it does not touch
the demand side, so one-human-one-voice stays intact.

### 3. The observatory, sponsored and serviced *(M2, earliest revenue)*

The index of the most foundational, least-supported software stays public —
that is the point. Two adjacent things institutions pay for without any
lock-in:

- **Sponsorship** — foundations and companies co-fund the observatory's
  operation (the Blender Development Fund pattern): visible support for
  infrastructure everyone uses.
- **Service** — fresh API access and dependency-risk reports for corporate
  open-source program offices: *which of your load-bearing dependencies is
  about to become the next xz.* The data is forkable; the freshness,
  curation, and accountability are not.

### 4. Hosted convenience *(M1+)*

Everything open source, self-hostable, forkable — and a hosted version for
people who would rather pay a small subscription than run it themselves. The
Ghost model proves hosting alone sustains a livelihood with zero proprietary
code. One caution: never feature-gate the M1 tool itself — its job is
recruiting graph-populators, and friction there starves every later
milestone.

### 5. Public-goods grants *(M0–M2, the bridge)*

socaity.dev is itself foundational, high-societal-value, low-individual-
capture software — the exact profile the vision says goes unfunded. The
institutions built to correct that failure are its natural funders, and
taking their money is philosophically load-bearing: the old mechanism
funding its own replacement. Concretely (EU-based): NLnet / NGI Zero,
Sovereign Tech Fund, Prototype Fund; later Optimism RetroPGF and Gitcoin
rounds. The M2 observatory is nearly a purpose-built application: *we
computed the subsidy signal for the world's software commons.*

Grants are recorded on the ledger like any other inflow — attached to
nodes, distributed per contribution. Grant income is not outside the
mechanism; it is the mechanism's first fiat.

## Anti-commitments

Named early because refusing them is a trust asset. Each would pay faster
than every model above; each converts the platform into the thing it exists
to replace.

- **No token issuance.** Already rejected in the vision; restated here as a
  revenue refusal, not just a design choice.
- **No selling demand-side influence.** No promoted nodes, no sponsored
  priority, no mechanism by which money touches one-human-one-voice — in
  any form, at any price.
- **No proprietary data moat.** The graph and the ledger stay exportable
  even when that is commercially inconvenient. Especially then.
- **No ads.** Attention is not the platform's to sell.

## Sequencing

Revenue stages the same way the milestones stage audiences:

| Phase | Feeds the work |
|---|---|
| M0–M1 | Grants (apply early — lead times are months) + founder labor accruing on the ledger |
| M2 | Observatory sponsorships and institutional reports — first recurring revenue, same motion as the press strategy |
| M3–M4 | Hosted tool + compute margin — revenue scales with network activity |
| M5 | Take rate on the fiat rail + the first retroactive distribution honoring epoch shares back to M0 — the mechanism becomes the livelihood |

## Open question: separating stewardship from service

The vision's governance question — who tunes the multipliers, and how is
that power kept accountable — eventually collides with a fact this document
creates: the founder's income depends on the multipliers. The standard
resolution (Ghost, Blender, Signal) is a split: a **foundation** owns the
mechanism, the ledger, and the tuning power; a **service company** sells
hosting, compute, and reports on ordinary commercial terms. Premature to
build now; wrong to leave unnamed. The trigger condition for the split is
itself a node for the graph to price.
