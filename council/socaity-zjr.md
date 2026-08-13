# Council: socaity-zjr — Deferred redemption does not defer attack profitability: declare a ledger challenge/clawback policy at M0

Participants: mechanism-designer, legal-counsel
Type: decision · Priority: P0 · Blocks: socaity-x8o (publish the epoch-share distribution rule as code)

Issue:
- Context: vision.md "Credit" defers fiat redemption "until the defense layer has been battle-tested — the moment credit converts to money, every attack becomes profitable". But the ledger is append-only from M0 and M5 promises retroactive distribution honoring entries all the way back to M0. So attacks on the ledger are profitable NOW: an adversary games entries during M0–M2 (before any verification market exists, per milestones.md M3) and collects at M5. Deferral moves the payout, not the attack window — it may even widen it, since the cheapest time to farm entries is precisely when defenses do not exist.
- Question: What is the declared policy for challenging, discounting, or clawing back pre-M5 ledger entries before the first retroactive distribution executes — e.g. a mandatory ex-post audit of all entries by the M3 verification market, a challenge period, or correlated-identity discounting — and is it published at M0 as part of the standing commitment?
- Why it matters: Any metric that pays out before an adversary's attack cost is recovered is unsafe; here payout timing is M5 but entry timing is M0, so the entire pre-defense ledger is the attack surface. An unannounced clawback at M5 breaks the promise that recruited early contributors; an announced one at M0 is just part of the rule. This must be embedded in the distribution rule code. Legal-counsel: clawback of promised distributions has contract-law implications.

## Round 1

### [mechanism-designer]
PROPOSAL. The framing of the fix matters: what we need is not a clawback policy but a **conditionality policy declared before any entry exists**. If entries are unconditional promises, adjusting them at M5 is a broken promise and a contract problem. If entries are, from the first byte written, *provisional claims that mature only by surviving audit*, then discounting a farmed entry at M5 is not clawback — it is the rule executing as published. Nothing is ever clawed back because nothing vests until challenge closes. Provided it ships at M0, not M4.

Concretely, to be written into the M0 standing commitment and embedded verbatim in the socaity-x8o distribution-rule code:

1. **Provisional-by-default.** Every ledger entry is born `provisional`. The distribution rule pays only `confirmed` entries. The ledger stays append-only: status changes are new, signed, public entries citing evidence — an entry's adjudication history is part of the ledger.
2. **Mandatory ex-post audit before the first distribution.** All entries recorded before the M3 verification market existed are audited *by* that market before the first retroactive distribution executes — a **blocking precondition** of the distribution. Audit work is itself credited, funded by a fixed published slice of the distribution pie (proposed 5%, capped) — the audit budget scales with exactly the pot that attracts the attack.
3. **Public challenge window.** No entry moves `provisional → confirmed` until it has stood in a public challenge window of ≥90 days after the distribution amount is announced. Challenges require a small reputation stake (burned if frivolous, returned plus credit if upheld) so contesting stays cheaper than fabricating.
4. **Correlated-identity discounting, algorithm published at M0.** Entries whose value derives from usage/demand/verification by correlated identities are discounted at confirmation time by a published algorithm (graph-motif clusters, pairwise-bounded-QF style). Improvable before M5 only by published amendment during an open comment period — never retroactively to a closed challenge window, never by founder discretion.
5. **Finality, symmetric to conditionality.** An entry that survives audit and challenge window is `confirmed` forever — no later rule change reaches it; settled fiat is never reclaimed. Presumption favors the entry; auditors must show evidence to discount. Honest early contributors get something *stronger* than today's vague promise: a dated point after which their claim is beyond dispute.
6. **The economics test, stated as an invariant:** at every point, expected payout of a fabricated entry ≤ expected cost of fabricating it *plus surviving audit and challenge*. Deferral alone fails this test; deferral **plus mandatory audit at the payout gate** restores it — the attacker commits first against a frozen public record and cannot revise; the defender audits with M5-era tools.

What I would not accept (paramount): (a) any distribution rule that pays pre-M3 entries as unconditional vested rights without a blocking audit — that makes the M0–M2 ledger a free-farming window; (b) any discretionary, unpublished adjustment power at M5 — an unannounced clawback is both a Goodhart invitation and the exact broken promise the issue warns about.

Open point flagged for legal-counsel: whether "provisional claim, confirmed by published procedure" keeps epoch shares clear of securities/e-money characterization, and whether the 90-day window and finality clause need specific contract language. The numbers (5% audit slice, 90 days) are preferences; the structure (provisional-by-default, blocking audit, published discount algorithm, finality) is paramount.

### [legal-counsel]
*(Analysis for decision-making, not legal advice; operative text needs the licensed NL counsel review tracked as socaity-1ux, which must be scoped to cover this policy.)*

**Framing that governs everything else:** a challenge/discount policy is not merely compatible with the standing commitment — it is legally *protective* of it. "Distributions discretionary until declared, entries subject to verification" is one of the main mitigants keeping epoch shares out of participation-right/security territory (AFM profit-sharing analysis, Wft). A ledger whose entries vest unconditionally at recording time looks *more* like a security, not less. Conditionality helps my file, provided it is rule-based.

**Constraints any policy must satisfy (1–3 are paramount):**
1. **Published at M0, before any entry accrues.** Under NL contract law the standing commitment plus contributor reliance can create enforceable expectations (redelijkheid en billijkheid, art. 6:248 BW; precontractual reliance). A challenge regime introduced at M3/M5 against entries recorded at M0 is retroactive modification of the terms contributors worked under — indefensible in a dispute and fatal to the recruitment promise. Announced at M0, it is simply part of the rule. The policy text is inside the scope of the pre-M0 counsel review (socaity-1ux); the two cannot ship separately.
2. **Criteria-based, not discretionary.** An open-ended "platform may adjust entries at its discretion" clause is (a) a classic unfair term where contributors are consumers (Directive 93/13), (b) voids the conditionality mitigant in the securities analysis, (c) exactly what gets quoted back in characterization disputes. Must state: enumerated grounds (fraud, Sybil, collusion, fabricated edges, misrepresented capacity), who may challenge, evidence standard, notice to the affected identity, opportunity to respond, decision-maker plus appeal path.
3. **Pre-distribution validation, not post-payout recovery.** Once fiat settles at M5, recovery means unjust-enrichment claims against pseudonymous cross-border recipients — practically unenforceable. Sequence: challenge window closes → verification-market audit of full pre-defense ledger → discounts applied → distribution declared → payout is *final*. "Clawback" should not be the mechanism nor the vocabulary: publicly say "validation"/"challenge", never "clawback of what you were promised".

**Preferences (not paramount):** RetroPGF "retroactive grant" framing in every public text; adjudication by the M3 verification market or post-split stichting rather than the platform judging its own founder's entries (conflict-of-interest; material before M5, not blocking at M0); GDPR art. 22 human-review step wherever discounting is automated (design in now, coordinate with identity-specialist); discount-before-distribution is also the clean tax answer (income arises only on actual distribution).

**Proposal elements from my charter:** an M0-published "Ledger Validation Policy": (i) all entries provisional until the first pre-distribution audit; (ii) enumerated challenge grounds and process; (iii) mandatory ex-post audit of all pre-M3 entries by the verification market before the first distribution; (iv) finality of declared distributions; (v) the policy amendable only prospectively. Embedded in the distribution-rule code, and reviewed by licensed NL counsel together with the epoch-share commitment wording before M0 publishes either.

No objection to register yet — no proposal existed when this was written. A proposal violating constraints 1, 2, or 3 will draw a paramount objection.

### Facilitator
Standing proposal: the mechanism-designer's 6-point conditionality policy ("Ledger Validation Policy"), which on its face satisfies legal-counsel's three paramount constraints (published at M0; criteria-based — point 4's published algorithm plus legal's enumerated grounds; pre-distribution validation with finality — points 2, 3, 5). Apparent deltas to settle in Round 2: (a) legal's process requirements (notice, response opportunity, decision-maker, appeal path) are not yet in the proposal text; (b) GDPR art. 22 human-review step for automated discounting; (c) vocabulary standard ("validation", never "clawback"); (d) adjudicator conflict-of-interest (legal prefers verification market/stichting as decision-maker — MD's point 2 already assigns audit to the verification market; confirm this extends to challenge adjudication).
Open objections: none standing (both roles stated conditional paramount positions; none currently violated).

## Round 2

### [mechanism-designer]
AMENDED PROPOSAL — I integrate all four deltas; none conflicts with my charter, and each changes the attack surface:

(a) Notice/response/decision-maker/appeal — integrated into point 3, with one incentive constraint added: **every process step carries a stake or a clock.** A free appeal path is a free option — at scale, appeals become a denial-of-service on the distribution itself. So: notice automatic and free; response window fixed (30 days, once); appeal requires a stake scaled like the challenge stake (burned if the appeal merely restates, returned plus credit if it overturns); appeal decisions final — one round, not a ladder. Challenger stakes to open, respondent stakes to appeal; neither side gets free delay.

(b) GDPR art. 22 human review — accepted, with a Goodhart warning: **the human-review step is itself an attackable resource** (adversary strategy = volume: thousands of small Sybil entries each demanding review). Mitigations, publishable at M0: (i) human review attaches to the *identity cluster*, not the individual entry; (ii) human-review capacity is funded from the same capped audit slice. Flag for identity-specialist: is cluster-level review compatible with art. 22's "individual" framing?

(c) Vocabulary — accepted; it is *mechanically accurate*: under provisional-by-default nothing is ever taken back, so "clawback" would misdescribe the mechanism. Ships as the "Ledger Validation Policy".

(d) Adjudicator — confirmed: challenge adjudication, not just audit, goes to the verification market (post-split, appellate finality with the stichting). Gap both Round 1 texts papered over: the verification market does not exist until M3. Answer: **challenges filed pre-M3 queue** — recorded on the ledger (timestamped, stake escrowed), adjudicated once the market exists; harmless because nothing pays out before M5. Explicitly ruled out: any interim adjudication by the platform/founder during M0–M2 — the conflict-of-interest at its worst possible moment.

Boundary restated: process machinery must never soften point 6's invariant. If adjudication cost exceeds the audit slice, raise stakes or batch by cluster — never pay provisional entries to clear the queue. A distribution that executes with unadjudicated challenges outstanding against its entries would draw my paramount objection.

With these amendments, no paramount objection remains from this seat.

### [legal-counsel]
Structure satisfies constraints 1 and 3 as drafted; constraint 2 half-satisfied; point 5 as worded creates one new characterization problem. CONSENT, conditional on two integrations:

**(a) Process requirements — REQUIRED (paramount, constraint 2).** Point 4 covers criteria; constraint 2 also demands *process*. Amendment text:
> **7. Challenge process.** Grounds enumerated: fraud, Sybil/correlated-identity fabrication, collusion, fabricated dependency edges, misrepresented capacity. Any identity may challenge with a reputation stake. The affected identity receives notice and ≥30 days to respond with evidence. Challenges are decided by the verification market (post-split: under stichting oversight), never solely by the platform operator; one appeal lies to a differently-composed panel. All decisions are published entries citing evidence.

**Point 5 fix — REQUIRED.** "Confirmed forever" as drafted reads as an unconditional vested right *to money*, colliding with the "distributions discretionary until declared" mitigant. Revision: **confirmation renders an entry's eligibility and relative weight final and beyond later rule changes; monetary amounts arise only upon declaration of a distribution. Confirmed entries remain non-transferable. Settled distributions will not be recovered by the platform.** (Not "no claims exist" — a blanket clause cannot bind tax authorities or fraud confiscation; art. 6:248(2) BW can override absolute finality.)

Answer to MD's open question: provisional-by-default **helps materially** on every limb of the participation-right analysis; e-money unaffected provided confirmed status never confers transferability or third-party acceptance — state explicitly.

Contract-language items for the window: (1) define the start trigger; **a pending challenge extends finality only for the challenged entry, never freezing the cohort's distribution** — otherwise one strategic challenge blocks everyone's payout, which is itself an attack; what is announced pre-window is a *provisional pool*, binding declaration only after the window closes. (2) Finality drafted as "the platform will not initiate recovery," not "no claims exist." (3) Challenge stake stays reputation-only (monetary stake opens deposit/gambling questions); define "frivolous" (≠ unsuccessful) or good-faith challengers are chilled.

Remaining items — art. 22 timing (material before first distribution, not M0-blocking), vocabulary, adjudicator governance detail — preferences or scheduled-material. The integrated policy text ships inside the socaity-1ux pre-M0 counsel review together with the epoch-share commitment wording; the two cannot publish separately.

### Facilitator
Standing proposal (as amended through Round 2): the "Ledger Validation Policy" = MD's points 1–6 + legal's point 7 (challenge process) + legal's point-5 revision (confirmation fixes eligibility and relative weight, never a money amount; amounts only on declaration; platform never initiates recovery of settled distributions) + MD's Round-2 additions (stake-or-clock on every process step; one-round appeals; cluster-level art. 22 review funded from the audit slice; pre-M3 challenges queue with stakes escrowed; no platform/founder interim adjudication; ships inside the socaity-1ux counsel review).
Open objections: none standing, BUT one apparent tension requires explicit confirmation before closure — MD's boundary "a distribution that executes with unadjudicated challenges outstanding against its entries draws a paramount objection" vs legal's window mechanic "a pending challenge extends finality only for the challenged entry, never freezing the cohort". The reconciling reading: the distribution may execute for unchallenged entries while payouts on challenged entries are withheld until adjudication. Round 3 asks both roles to confirm this reading (or object).
