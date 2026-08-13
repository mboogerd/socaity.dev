# socaity.dev — Vision

*The place where society self-develops.*

## The problem

Society knows how to want things. It is bad at building the things everyone
wants but nobody wants to pay for.

Every ambitious project rests on foundations — libraries, protocols,
infrastructure, research — that unlock enormous downstream value while
capturing almost none of it. Everybody wants the foundation; nobody wants to
be the one to invest in it. So it gets built late, or badly, or not at all,
and the whole house of dependent value waits. This is the tragedy of the
commons, playing out daily in software (unmaintained load-bearing code à la
xz and log4j) and, more broadly, in every domain where shared needs go
unserved because no individual actor is incentivized to serve them.

Two things have changed. Agentic AI has turned software development into a
meterable, delegable resource: anyone can now contribute *capacity*, not just
labor. And it is now feasible to hold, in one shared structure, a live map of
what people actually need and how those needs depend on one another. Together
these make a previously impossible mechanism practical.

## The idea in one sentence

**The system never assigns work; it prices it.**

Demand is expressed democratically as a graph of needs. Supply is
self-directed agentic compute, pointed by each contributor wherever they
choose. The structure of the graph reveals where public-goods
underinvestment will occur — the foundational nodes with high societal value
and low individual value — and the system subsidizes exactly those nodes with
credit. Contributors optimize their own utility (direct benefit plus credit),
and the subsidy makes the selfish optimum and the societal optimum converge.

Nobody is directed. Nobody contributes to an average. Each participant works
on what they care about — and the pricing makes caring about the commons
individually rational.

## Principles

- **Open source** — outputs are open; the mechanism itself is open; the data
  is forkable. Exit must always be cheap, because forkability is the ultimate
  check on capture.
- **Democracy** — what society *needs* is decided by people, person-weighted,
  never resource-weighted.
- **Radical transparency** — the graph, the scores, the credit flows, and the
  algorithms that compute them are public and auditable. Manipulation should
  be visible, not impossible.
- **Resource pooling** — contribution is denominated in capacity (agentic
  compute, verification effort, human judgment), pooled across everyone who
  shows up.
- **Collaborative filtering** — shared needs are discovered, not just
  declared; "people who wanted X also wanted Y" connects the map.
- **AI** — agents decompose, estimate, deduplicate, build, and verify — under
  human value judgments, never in place of them.

## How it works

### The needs graph

Anyone can vocalize a desired change: an idea, a wish, a plan, an intention.
Every such contribution spawns a graph of increasingly refined ideas, and
disparate subgraphs connect over time into a web of societal needs.

The graph is an **AND/OR graph with contestable edges**:

- A *problem* node fans out to alternative *solution approaches* (OR).
  Problems do not have dependencies; solutions induce them. Modeling
  alternatives explicitly prevents the first decomposition anyone proposed
  from ossifying into the only one.
- A *solution* node fans out to the sub-problems it requires (AND).
- Every edge — refinement, dependency, equivalence — is itself a claim that
  can be asserted, disputed, and weighed. Merging duplicate needs, splitting
  conflated ones, and connecting subgraphs are first-class, contestable
  operations.
- Value flows through OR nodes probabilistically: a foundation is only as
  foundational as the likelihood that its branch wins.
- Nodes age. Value estimates decay and must be refreshed; the graph is a
  living map, not an archive.

Decomposition, deduplication, dependency discovery, and estimation are
themselves agent tasks *on* the graph. The platform improves itself with the
same mechanism it offers society.

### The demand side — person-weighted

Influence over what society needs is **one human, one voice**. It is never
proportional to compute, credit, or money — otherwise society's needs become
GPU-owners' needs, and the democratic legitimacy that justifies the whole
mechanism collapses. This requires proof-of-personhood strong enough to
resist Sybil attacks on the demand signal.

Needs are sensitive — health, finance, family. Radical transparency applies
to the *mechanism*; demand expression may be pseudonymous. What must be
public is the shape of demand, not the identity behind every wish.

### The supply side — self-directed and resource-weighted

Each participant assigns their agentic resources a **burn rate per node** —
per story, epic, feature, or research task — splitting capacity across the
things they care about. Each participant has a **planner**: an agent that
allocates their capacity most profitably across the web of needs, balancing
direct personal benefit against credited societal work.

Pledges of capacity can be made public. Together with node-level estimates,
this yields probabilistic forecasts — Gantt-like feedback telling
participants when a societal or personal feature can be expected — and
planners adjust allocations in response. The result is an open,
self-balancing market for capacity.

That market is a control system and must be tuned like one. Naive
forecast-driven reallocation stampedes (a node looks undersupplied, its
multiplier rises, everyone piles in, it is now oversupplied, everyone piles
out). Therefore: forecasts are intervals, not dates; multipliers adjust with
damping, not instantaneously; pledges carry commitment friction — credit
vests over the pledged duration.

### Pricing the commons

Because the whole graph is visible, foundational value is computable:
roughly, the downstream value a node unlocks relative to the direct demand it
attracts — a centrality measure over the needs graph. Nodes with high
unlocked value and low direct demand are precisely where the tragedy of the
commons strikes, and precisely where credit multipliers rise until someone
finds it worthwhile to show up. This is a Pigouvian subsidy made computable
by the dependency structure.

There is an analogue of proof of work here: credit is earned when working
code ships that solves a real problem in the real world. But the analogy
breaks at verification — a hash is checked in microseconds; "solves a real
problem" is expensive and subjective. So verification is not an
afterthought; it is the load-bearing wall:

- **Verification is first-class graph work.** Review, testing, and
  red-teaming are credited nodes on an open market, like any other
  contribution.
- **Multiple evidence streams feed one confidence score per solution**:
  acceptance review, adversarial red-teaming, and realized usage over time.
  These are concurrent signals, not competing ones.
- **Reward vests as confidence accumulates** — some at acceptance, more as
  usage confirms. Paying substantially on *realized* value rather than
  *predicted* value dissolves most of the oracle problem: value is observed,
  not judged.
- **Maintenance is continuous credited work.** Shipping is a moment;
  software is a liability forever. A burn rate can keep a node *healthy*,
  not just bring it into existence. The real tragedy of the software commons
  is unmaintained load-bearing code, and the model funds upkeep natively.

## Credit

Credit is deliberately layered, because one instrument cannot safely serve
three purposes:

1. **Reputation** — non-transferable standing, earned by *where* you pointed
   your capacity: the alignment multiplier for choosing high-societal,
   low-individual nodes. You cannot buy it; you can only earn it. It confers
   weight in the verification market and visibility, never demand-side votes.
2. **Compute credit** — closed-loop and wage-like, earned by *how much*
   metered capacity you delivered. Contribute your agent's hours to commons
   nodes; earn claims on the network's agent-hours for your own nodes. It is
   backed by the thing the network actually has. Fiat may be an on-ramp long
   before it is an off-ramp.
3. **The fiat rail** — money enters the system *attached to nodes*
   (bounties, sponsorships, grants), is escrowed, and settles out to
   contributors at completion according to the ledger. The credit ledger is
   an allocation weight over real money flows — the platform is an escrowed
   marketplace, not a currency issuer.

Two pricing modes coexist:

- **Absolute** — a stable rate per unit of delivered capacity. Wage-like,
  predictable, the steady-state instrument.
- **Epoch-share** — a fixed pie per epoch, split by each contributor's
  fraction of that epoch's total contribution. When the network is small, the
  same absolute contribution earns a large relative share: an **earliness
  premium**. Early believers hold a bigger claim on the future — equity-like
  upside without issuing equity or tokens.

The **contribution ledger runs from day one**, append-only and public, with a
standing commitment: future inflows are distributed retroactively in
proportion to recorded contribution (retroactive public-goods funding).
Redemption of credit into fiat is deliberately deferred until the defense
layer has been battle-tested — the moment credit converts to money, every
attack becomes profitable, and the immune system must exist first.

## Threat model

Every scoring function will be Goodharted. The design assumes adversaries
and names its defenses rather than pretending attacks away:

| Attack | Defense |
|---|---|
| Sybil demand (fake wanting, to inflate a node a colluder will "solve") | proof-of-personhood on the demand side |
| Dependency inflation (fabricated edges under pet projects) | edges are contestable claims; OR-node probabilistic value flow; public auditability |
| Need-splitting / duplicate farming | merge operations as credited, contestable graph work |
| Claimed-but-hollow solutions | vesting rewards on realized usage; adversarial verification market |
| Capacity-fraction gaming (many identities each giving "100%") | egalitarian standing derives from observable tenure and consistency, never self-declared capacity |
| Platform capture | radical transparency plus forkable data — exit is cheap |

## Scope

The mechanism as described is software-shaped: dependencies, shipping,
agentic compute. **Version one of socaity.dev is where society self-develops
its software commons.** The graph is designed so that non-software needs can
exist as leaves that exit to other systems, and the mechanism is designed to
generalize — but the claim is earned in software first, honestly, before it
is extended.

## Relationship to ComputeNet

ComputeNet is the foundational sibling project: a distributed incremental
dataflow runtime — programs as graphs of cells and ports, state converging
across nodes as deltas, with the same observable semantics in one process or
many. socaity.dev is a domain model built on that substrate:

- ComputeNet provides the **generic layer**: live, convergent, forkable
  shared state; incremental views; contestable-graph, preference-fusion, and
  collective-ranking primitives; deterministic simulation for testing
  mechanisms before deploying them.
- socaity.dev provides the **societal layer**: needs, solutions, credit,
  planners, verification, the market.

No society-specific logic leaks downward; no substrate concerns leak upward.
The separation is deliberate and permanent: ComputeNet must remain useful to
anyone building convergent systems, and socaity.dev must remain replaceable
in its substrate.

## Prior art, leaned on by name

- **Quadratic funding** (Gitcoin): breadth-weighted matching for public
  goods — and a documented catalog of collusion attacks to defend against.
- **Retroactive public-goods funding** (Optimism): reward realized value;
  observed impact beats predicted impact.
- **Ostrom's commons governance**: monitoring, graduated sanctions, and
  cheap exit as the empirically grounded conditions under which commons
  survive — forkability is our cheap exit.
- **Proof of work** (Bitcoin): the earliness premium of share-of-epoch
  rewards as a bootstrap mechanism — while rejecting the speculation-driven
  token model outright.

## Open questions

Held openly, not hidden:

- Proof-of-personhood: which mechanism clears the bar without excluding the
  people the platform most needs to hear?
- Fiat redemption: the exact trigger conditions under which the closed loop
  opens, and the jurisdictional groundwork it requires.
- Losing OR-branches: exploration produces information even when the branch
  loses; how is that information priced?
- Value-estimate decay: the right half-life for demand signals and
  foundationalness scores.
- Governance of the mechanism itself: who tunes the multipliers, the damping
  and the vesting curves — and how is *that* power kept accountable beyond
  transparency and forkability? Sharpened by
  [sustainability.md](sustainability.md): the builders' income depends on
  those same parameters, which eventually argues for separating stewardship
  (foundation) from service (company).
