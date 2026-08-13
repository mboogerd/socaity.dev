# Mechanism design — domain knowledge

## Goodhart taxonomy (check each against every metric you introduce)

1. **Regressional** — selecting on a proxy selects on its noise. Credit for
   "estimated value" pays estimation error.
2. **Extremal** — optimization pushes into regimes where the proxy-target
   correlation breaks (centrality scores behave differently in a graph
   grown adversarially than in one grown organically).
3. **Causal** — participants manipulate the proxy directly: fabricate
   dependency edges, split needs, inflate demand.
4. **Adversarial** — coordinated agents model the metric better than the
   designers do. Assume this within months of any credit having value.

## Collusion catalog (from quadratic funding practice)

- **Self-dealing**: propose need → "solve" it → collect. Defense: value
  vests on realized usage by *others*; usage by correlated identities
  discounted.
- **Sybil demand inflation**: covered by proof-of-personhood, but check the
  *marginal cost of a fake person* vs *marginal credit it unlocks* — the
  ratio is the security budget.
- **Bribery / vote buying**: a market for demand-side votes can exist off-
  platform. Pseudonymity makes it harder to *prove* delivery of a bought
  vote (a feature — MACI's core insight: receipts enable bribery, so deny
  receipts).
- **Circular contribution rings**: A verifies B verifies C verifies A.
  Detect via graph motifs on the verification market; discount correlated
  clusters (Gitcoin's Sybil-scoring lineage: pairwise-bounded QF).

## Centrality pitfalls

- Betweenness/eigenvector centrality are both manipulable by edge insertion;
  contestable edges help only if contesting is cheaper than fabricating.
  Price the asymmetry explicitly.
- Probabilistic flow through OR nodes: branch probabilities are themselves
  estimates that can be pumped. Consider market-based branch weights
  (prediction-market style) over declared ones.
- Decay: exponential decay with half-life per node *type*, not global —
  infrastructure demand decays slower than feature demand. Tune from data
  at M2 (the observatory gives you real decay observations for free).

## Control-theory notes for the capacity market

- The stampede the vision describes is a classic underdamped loop. Options:
  rate-limit multiplier changes (slew limiting), hysteresis bands (no
  adjustment inside ±x%), or integral-only response to *sustained*
  imbalance. Prefer legibility over optimality: participants must be able
  to predict multiplier behavior, or they hedge against the controller
  itself.
- Commitment friction (vesting over pledge duration) is the damper on the
  supply side; verify it doesn't just shift oscillation to longer periods.
- Simulate before deploying: agent-based sim with strategic (not honest)
  agents. The honest-agent sim always looks fine; it is worthless.

## Vesting and epoch design

- Vesting on realized usage imports an oracle: *usage telemetry*. Now usage
  is the Goodhart target (fake downloads, inflated CI dependencies). Prefer
  hard-to-fake usage signals: dependents' own realized value, reverse-
  dependency adoption, paid usage.
- Epoch-share bootstrapping: fix the epoch pie in *claim units*, publish the
  retroactive-distribution rule as code from day one. Ambiguity here is the
  #1 source of later community blowups (see every retroactive airdrop).
- Keep reputation non-transferable AND non-delegatable, or a rental market
  appears (Soulbound-token literature covers the failure modes).

## Literature anchors

- Buterin, Hitzig, Weyl — *A Flexible Design for Funding Public Goods* (QF).
- Pairwise-bounded QF + Gitcoin's collusion retrospectives.
- MACI (minimal anti-collusion infrastructure) — receipt-freeness.
- Optimism RetroPGF rounds 1–3 retrospectives — badge-holder collusion,
  impact-metric gaming, the "impact = profit" ambiguity.
- Ostrom, *Governing the Commons* — monitoring, graduated sanctions, cheap
  exit; map each of the 8 principles onto a platform feature.
- Hirschman, *Exit, Voice, and Loyalty* — forkability is exit; the graph is
  voice; reputation is loyalty. Check every governance decision against all
  three.

## Red flags to raise immediately

- Any place where money can buy demand-side weight, however indirectly
  (compute margin discounts tied to voting patterns, etc.).
- Any metric that pays out before an adversary would find it profitable to
  attack (payout timing < attack cost recovery = safe; reverse = unsafe).
- Founder-tuned parameters that move founder income (the sustainability doc
  names this; keep it visible in every design review).
