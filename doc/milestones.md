# socaity.dev — Milestones

The road from one contributor to a self-sustaining commons. Companion to
[vision.md](vision.md); how the builders eat along the way is
[sustainability.md](sustainability.md).

## Constraints

- One founder, finite resources. The binding goal is the **earliest possible
  moment at which other people's resources compound toward the shared goal**.
- ComputeNet exists as a research-grade substrate, not a product.
- The market window is now: agentic coding capacity is exploding while OSS
  sustainability is a mainstream crisis. Speed toward the intersection of
  those two beats polish everywhere else.

## Principles

1. **Single-player value first.** Every network-dependent feature is
   worthless at N=1. Each milestone must be useful to its first user alone,
   while quietly laying network structure. Come for the tool, stay for the
   network.
2. **Each milestone recruits the cohort the next milestone needs.** Traction
   is not one audience; it is a sequence of audiences, each of which is the
   supply or demand the next stage requires.
3. **Value first, economy last, ledger always.** The contribution ledger is
   append-only and public from day zero, with a standing commitment that
   future inflows are distributed retroactively in proportion to recorded
   contribution. Monetization waits until the defense layer has been
   battle-tested; early contributors are paid in epoch shares — claims on the
   future — which is exactly the earliness premium a bootstrap needs.

## The sequence

### M0 — The manifesto and the glass house

**Goal:** attract the first aligned contributors; start the ledger.

- Publish the vision document on socaity.dev; repo public from day zero.
- socaity.dev's own roadmap becomes **the first needs graph**, expressed in
  its own conventions (AND/OR nodes, contestable edges). The platform's own
  construction is the first tragedy-of-the-commons instance it must solve —
  dogfooding is both proof and recruitment.
- Radical transparency from the first commit: decisions, trade-offs, and the
  contribution ledger all in the open.

**Recruits:** the handful of people who read a manifesto and feel it was
written for them. Manifestos are traction artifacts — the Bitcoin whitepaper
shipped before the network did.

**Done when:** the vision is public, the roadmap-as-graph is public, and the
ledger has recorded its first external contribution.

### M1 — The graph as a single-player tool

**Goal:** make the needs graph useful to one person with no network.

- An AI-native needs and decomposition tool: capture a desired change,
  agents decompose it into the AND/OR graph, estimate nodes, surface
  dependencies and alternatives.
- Point it at any GitHub repository and it ingests the issue tracker into a
  needs graph — instant utility as agentic backlog triage and roadmap
  planning.
- ComputeNet's backlog-triage (collective ranking, agent API) and agora
  (contestable-edge graph) demos are the direct ancestors.

**Recruits:** individual developers and small teams, who begin populating
real graphs with real needs.

**Done when:** a stranger uses it on their own repo because it is the best
triage tool available to them, network aside.

### M2 — The commons observatory

**Goal:** demonstrate the core insight — find the under-loved foundational
node — publicly, on real data, with zero users required. *This is the
traction hack; run it in parallel with M1 where possible.*

- Ingest the public dependency graphs (npm, PyPI, Maven, GitHub) plus
  funding signals (GitHub Sponsors, Open Collective, OpenSSF criticality).
  The existing package ecosystems already *are* an empirical web of software
  needs.
- Publish the index of **the most foundational, least-supported software in
  the world** — foundationalness versus support, the vision's subsidy signal
  computed on reality.
- Differentiator versus prior art (Libraries.io, CHAOSS): actionability.
  Every under-supported node is a target you can point an agent at.

**Recruits:** the OSS-sustainability community — maintainers, foundations,
and funders — which is simultaneously the platform's moral constituency and
its first fiat source. Inherently press-worthy.

**Done when:** the index is cited by people we did not contact.

### M3 — The first contribution loop

**Goal:** the proof-of-work moment — merged PRs that exist because the graph
priced them.

- A user points their own agent (Claude Code or similar) at a graph node and
  ships a real pull request.
- Minimal verification market: maintainer acceptance plus red-team agents,
  both credited on the ledger as first-class graph work.
- Run it on socaity's and ComputeNet's own backlogs plus a few consenting
  OSS projects surfaced by the M2 index.
- Rewards vest with confidence: part at acceptance, more as usage confirms.

**Recruits:** agent-owners with idle capacity looking for meaningful,
credited targets.

**Done when:** an external agent-owner's PR, targeted via the graph, is
merged into a project its owner does not maintain — and the verification
work around it was itself credited.

### M4 — Multi-player demand

**Goal:** switch on the democratic demand side and the market mechanics, on
a graph that already has real supply and real content.

- Personhood-lite identity; person-weighted need expression and voting.
- Collaborative filtering connects subgraphs and surfaces latent shared
  needs; merge/split operations as credited, contestable graph work.
- Personal planners allocate burn rates across nodes; pledges are public;
  forecasts are probabilistic intervals with damped multiplier adjustment
  (the market is a control system — tune it like one).

**Recruits:** need-havers — people who want things built and now have a
place to say so with consequences.

**Done when:** a node rises to the top of the priority signal through
person-weighted demand alone and subsequently gets built by self-directed
supply.

### M5 — The economy

**Goal:** open the loop between credit and money — last, deliberately.

- Fiat attaches to nodes (bounties, sponsorships, grants), is escrowed, and
  settles to contributors per the ledger: the platform as escrowed
  marketplace, never currency issuer.
- **First retroactive distribution honoring epoch shares all the way back to
  M0** — the promise that paid the early believers, kept.
- Compute credits open if ComputeNet's pooling has matured: closed-loop
  claims on network agent-hours, fiat as on-ramp before it is an off-ramp.
- Fiat redemption decisions are made only now, after the defense layer has
  been red-teamed — by the M3 verification market, pointed at the platform
  itself.

**Recruits:** funders — the constituency M2 introduced, now with a
mechanism they can route real money through.

**Done when:** external money has entered attached to a node, settled to
contributors according to the ledger, and the retroactive distribution has
executed.

## The recruitment chain, end to end

> manifesto → aligned builders → tool users → OSS-sustainability world →
> agent-owners → need-havers → funders

Each arrow is the point: every cohort is the supply or the demand that the
next milestone cannot function without. Skipping ahead breaks the chain —
M4's demand democracy is theater without M3's supply, M5's money is an
attack surface without M3's verification, and everything before M2 is
invisible without its index.
