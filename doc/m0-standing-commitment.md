# The M0 Standing Commitment

**Status: DRAFT FOR COUNSEL REVIEW — NOT FOR PUBLICATION.**
Nothing in this document may be published, quoted in marketing copy, or relied
upon by any contributor until a licensed Dutch practitioner has reviewed the
whole instrument (socaity-7kv). The three components below publish together or
not at all.

---

## 0. What this document is, and where it comes from

This is an **assembly** of decisions already adopted by consent in council. It
introduces no new policy. Where an adopted resolution left something
unspecified, the gap is marked inline as `[OPEN — for counsel: …]` and listed
again in Appendix 2 rather than filled in by the drafter. Any change to the
*structure* below goes back to council, not to redrafting.

### Provenance

| Part | Content | Source resolution |
|---|---|---|
| Part I | Canonical plain paragraph (plain register) | socaity-1ux (launch-strategist Round 2, confirmed by legal-counsel Round 3) |
| Part II, clauses 1–11 | The Standing Commitment (operative register) | socaity-1ux (legal-counsel Round-1 skeleton, as amended Rounds 2–3) |
| Annex A | Ledger Validation Policy | socaity-zjr |
| Annex B | Identity and pseudonymity terms | socaity-7mk |
| Annex C | Conversion Schedule V and the attestation statement | socaity-19p |
| Annex D | Publisher, entity staging and the uitkeringsverbod gate | socaity-gp2 |
| Appendix 1 | Vocabulary standard (banned / required wordlist) | socaity-1ux clause 10 (merged legal-counsel + launch-strategist lists) |
| Appendix 2 | Open items register | this assembly |

### The two registers

Per socaity-1ux, this instrument publishes in **two registers, both at M0**:

- the **plain register** — Part I, one canonical paragraph, reused *verbatim*,
  never paraphrased. It is the **ceiling** for every future claim about credit
  or distribution: no other copy may be bolder, and none may be softer.
- the **operative register** — Part II and its annexes, the counsel-reviewed
  text the plain register links to.

The registers may differ in tone but never in content. A divergence between
them is a shipping blocker, not an editing note.

### The governing framing (socaity-1ux)

> We make no promise that money will ever be distributed. We bind ourselves
> publicly to the allocation rule if it ever is.

Discretion over **whether, when, and how much** is given away entirely.
Discretion over **how a declared distribution is allocated** is surrendered
entirely. Ledger entries are **records of fact, not instruments**.

---

## Part I — Canonical plain paragraph (plain register)

*Adopted verbatim, socaity-1ux Round 2 (launch-strategist), confirmed by
legal-counsel Round 3. This is the single phrasing. It is reused word for word
on the site, in the manifesto, in press, and in grant text.*

> Every contribution is recorded on a public, append-only ledger from day one.
> Records start as provisional and are confirmed through a published validation
> process. If money ever flows out of this project, it is allocated across
> confirmed records by a published rule, not by our mood. Whether, when, and
> how much is never guaranteed — no amount exists until a distribution is
> declared. What the rule protects is your recorded place in it: confirmed
> weights can't be quietly rewritten, and the whole ledger is forkable if we
> ever betray that.

**Drafting note carried from socaity-1ux Round 3 (legal-counsel):** the plain
register may keep the punchier "can't be quietly rewritten"; the operative
register (clause 4.5) says *"cannot be rewritten except through the published
validation and challenge process."*

**Mandatory first-screen assets (socaity-1ux, launch-strategist Round 1):**

> No token. Nothing to trade. The ledger is a database, not a blockchain.

**Copy discipline addendum (socaity-1ux Round 2):** the words *fixed* and
*locked* may only ever modify **the rule**, **epoch parameters**, or **a
confirmed weight**. Never a share of money. Never "what you'll get."

---

## Part II — The Standing Commitment (operative register)

### Clause 1 — What the ledger is

The contribution ledger is a public, append-only record of contributions to
this project, running from the first entry. Contributor identity on the ledger
is the keypair primitive set out in Annex B. Every entry and every status
change is a signed public entry.

### Clause 2 — What recording means

A recorded entry is **provisional** when made. Confirmation under the Ledger
Validation Policy (Annex A) fixes only two things: the entry's **eligibility**
to participate in a distribution, and its **relative weight**. Confirmation
never fixes, creates, or implies a **monetary amount**.

### Clause 3 — What recording does not create

A ledger entry, whether provisional or confirmed, is **not**: a debt, a
deposit, repayable funds, electronic money, a token, a security, a
participation right, a unit in a collective investment scheme, or a claim of
any kind against us or against any third party.

Entries are **non-transferable and non-purchasable**. They cannot be bought,
sold, assigned, or pledged, now or by later amendment.
They carry **no monetary value unless and until a distribution is declared**
under clause 5. No interest, indexation, or time-based accrual attaches to any
undeclared amount. Participation is not an investment.

`[OPEN — for counsel: succession on death or incapacity. No adopted resolution
addresses whether a ledger entry passes to an estate; socaity-7mk does provide
key.successor_designated / key.rotated / key.rebound as forward-only lifecycle
events (Annex B.4), which is a key-continuity mechanism, not an entitlement
transfer. Non-transferability as adopted covers purchase, sale, assignment and
pledge; the drafter has deliberately not extended it to succession, which would
be new policy.]`

Confirmed status confers **no transferability and no third-party acceptance**
(socaity-zjr, legal-counsel Round 2 — the limb on which the e-money analysis
turns).

### Clause 4 — The allocation rule (the binding part)

**4.1** If a distribution is declared, the declared pool is allocated across
**confirmed** entries in proportion to recorded contribution, applying the
published epoch-share computation, including the earliness premium arising
structurally from a fixed pie per epoch.

**4.2 Rule as code, authoritative.** The allocation rule — epoch boundaries,
pie in claim units, share computation, premium formula — and the
correlated-identity discounting algorithm are published at M0 as **versioned,
deterministic, executable code**. Anyone may recompute any distribution. **In
any divergence between the executable rule and prose describing it, the
executable rule governs** (socaity-1ux, mechanism-designer Round 2, condition
of consent).

**4.3 Epoch parameters are fixed before the epoch opens.** The parameters
governing an epoch cannot be amended once that epoch is open. This is a
constraint on our rule-making procedure. It vests no right in any contributor.

**4.4 Amendment, prospective only.** The **structure** of the formula (fixed
pie per epoch, share computation, the functional form of the premium curve) is
final at M0 for every epoch opened under it. **Parameter values** may be
amended only: version-tagged; applying solely to **epochs not yet opened**
(never merely "not yet closed"); after an open public comment period; and via
the amendment meta-rule itself published at M0 as part of the rule.

**4.5 Confirmed weights.** A confirmed entry's recorded weight cannot be
reduced or rewritten except through the published validation and challenge
process in Annex A.

`[OPEN — for counsel: the M0 values of epoch length, pie size in claim units,
premium-curve parameters, and the open-comment period length are not fixed by
any adopted resolution. They are council/mechanism content (socaity-x8o), not
counsel content, but counsel should confirm that publishing clause 4 with these
values present does not itself create a representation of value.]`

`[OPEN — for counsel: is "the executable code governs over the prose" a safe and
enforceable drafting choice under NL law, and how should the code version be
incorporated by reference into the operative text?]`

### Clause 5 — Declaration is discretionary

Whether a distribution occurs, when it occurs, and its size are at our **sole
discretion**. No distribution is promised, scheduled, or owed. Until a
distribution is declared, **no amount exists**.

Upon declaration, the declared pool becomes payable **only** as clause 4
allocates it. Entries under challenge at declaration have their pro-rata share
**escrowed at declared weight** — never redistributed to the unchallenged
cohort — and join a later declaration upon confirmation. A binding declaration
covers only the **confirmed set**; finality attaches per declaration, not per
cohort (socaity-zjr Round 3).

### Clause 6 — Ledger Validation Policy incorporated

The Ledger Validation Policy at **Annex A** forms part of this instrument, of
equal rank, published in the same document and reviewed in the same counsel
engagement. The two cannot publish separately.

### Clause 7 — Identity terms incorporated

The identity and pseudonymity terms at **Annex B** form part of this
instrument: entry permanence, the scope of erasure, pseudonymous earning, and
identity binding at fiat claim time.

`[OPEN — for counsel: socaity-1ux's adopted clause-7 skeleton also lists
**annual statements** among the incorporated identity terms. socaity-7mk, which
supplies Annex B, defines no such artifact — no cadence, content, recipient or
delivery channel exists in any adopted resolution. Flagged rather than invented;
if an annual statement is required, its content is council content and its
wording is counsel content.]`

### Clause 8 — No special founder position

The founder holds **no special position**: the same ledger, the same identity
primitive, the same valuation schedule (Annex C), the same validation process,
the same challenge exposure — at a publicly declared rate benchmarked as
Annex C requires.

**8.1 Uniformity covenant.** Any value flowing to the founder or to any insider
in respect of contribution flows exclusively through the published rule.

**8.2 Precedence over clause 9.2.** Where clause 9.2's carve-outs could touch a
person holding ledger entries, **clause 8 controls**: contracted compensation to
a ledger participant must be publicly declared and arm's-length, so the
carve-out can never become a quiet channel (socaity-1ux, mechanism-designer
Round 3).

### Clause 9 — Non-bypass, scoped; and no third-party rights

**9.1 Non-bypass.** *"We may never pay; we will never pay differently."* Any
**discretionary distribution to contributors** is made exclusively under the
published rule.

**9.2 Carve-out (socaity-1ux, legal-counsel Round 2, amendment (a)).** Ordinary
operating expenditure, contracted compensation, and grant-mandated spending are
**not distributions** and fall outside clause 9.1 — subject to clause 8.2.

**9.3 No third-party rights (amendment (b)).** This commitment creates **no
stipulation for the benefit of third parties** within the meaning of art. 6:253
BW (*derdenbeding*) and **no cause of action**. It is a public self-binding
statement of procedure, not a promise of payment.

**9.4 Enforcement is transparency and exit.** The **ledger and the rule-code
together are exportable at all times**, irrevocably. If we abuse the
discretion clause 5 reserves, the community leaves with the complete record and
the complete rule. That, and public scrutiny, are the sole enforcement.

`[OPEN — for counsel: reconcile clause 9.3 with socaity-zjr's own observation
that the standing commitment plus contributor reliance may create enforceable
expectations under art. 6:248 BW (redelijkheid en billijkheid) and precontractual
reliance. A no-derdenbeding clause does not by itself displace that. Counsel to
draft the reconciling language — the council fixed the intent (procedure, not
promise), not the wording.]`

`[OPEN — for counsel: whether contributors qualify as consumers, and what
follows for unfair-terms review (Directive 93/13 / afdeling 6.5.3 BW) of the
discretion in clause 5 and of the process terms in Annex A. socaity-zjr raised
this as a constraint on discretion; no clause was drafted.]`

### Clause 10 — Vocabulary and consistency

**10.1** The vocabulary standard at **Appendix 1** binds all owned surfaces —
site, repository, manifesto, posts, press material, grant text — permanently.

**10.2 Enforcement, three layers (socaity-1ux Round 2/3):**

1. **Pre-publication gate** — a grep-able banned wordlist held in the
   repository and run in CI over site and manifesto content. The canonical
   paragraph (Part I) is reused verbatim, never paraphrased.
2. **The briefing card** — a one-page card carrying the canonical paragraph
   plus prepared answers to the five predictable traps: *"so it's like
   equity?"*, *"what's it worth?"*, *"when do I get paid?"*, *"is this a
   token?"*, *"how early is early enough?"*. Valuation questions always receive
   the structural answer, never a number.
3. **Correction protocol** — where a spoken statement departs from this
   instrument, a public correction is published linking the operative text. The
   correction log is retained and doubles as a tripwire: the same trap twice
   triggers a re-brief.

**10.3** Clause 10 binds the publication pipeline and imposes a briefing and
correction duty. It is not drafted as an absolute over live speech, which is
not mechanically enforceable.

**10.4** vision.md's phrase *"equity-like upside without issuing equity or
tokens"* must not appear in this instrument, in M0 marketing, or in any public
copy. The earliness premium is explained **structurally only** — fixed pie per
epoch, smaller network, larger share — never as a percentage, multiple, or
projection.

`[OPEN — for counsel: doc/vision.md line ~178 currently contains the banned
"equity-like upside" phrasing. Clause 10.4 forbids it in public copy, and
socaity-1ux calls it "the single most quotable sentence for an AFM
characterization argument", but no adopted resolution instructs an edit to
vision.md. Confirm whether vision.md as published at M0 falls inside clause 10.1's
"owned surfaces" — the drafter reads it as yes, which would require an edit
outside this assembly's scope.]`

### Clause 11 — Track record

*Numbering note: socaity-1ux names a **10-clause** Standing Commitment, and its
facilitator folded mechanism-designer's track-record device into the skeleton
without assigning it a clause number. This assembly renders it as a separate
clause 11 for legibility. The content is adopted; only the numbering is the
drafter's. Renumbering or folding it into clause 4 or 9 is a structural change
and would go back to council.*

Every inflow from M0 onward, **grants explicitly**, is recorded on the ledger
and is either distributed under the rule or explicitly ledger-reserved under
it. This is stated as **the rule operating**, not as goodwill.

---

## Annex A — Ledger Validation Policy

*Source: socaity-zjr, adopted by consent Round 3. Published at M0 as part of
this instrument; embedded in the distribution-rule code (socaity-x8o); reviewed
in this same counsel engagement. Vocabulary: "validation" and "challenge" —
**never "clawback"**, in any public text.*

**A.1 Provisional by default.** Every ledger entry is born `provisional`. The
distribution rule pays only `confirmed` entries. The ledger remains
append-only: status changes are new, signed, public entries citing evidence. An
entry's adjudication history is part of the ledger. Nothing is ever taken back,
because nothing vests until challenge closes.

**A.2 Mandatory ex-post audit.** All entries recorded before the M3
verification market existed are audited **by** that market before the first
retroactive distribution executes. This audit is a **blocking precondition** of
that distribution. Audit and human-review work is itself credited, funded from
a fixed, capped, published slice of the distribution pie — placeholder **5%**.

**A.3 Public challenge window.** Between announcement of a **provisional pool**
and binding declaration there is a public challenge window — placeholder
**≥90 days**. Binding declaration covers only the confirmed set. A pending
challenge extends finality **only for the challenged entry** and never freezes
the cohort's distribution. Challenged entries' shares are escrowed at declared
weight, never redistributed to the cohort, and join a later declaration upon
confirmation.

**A.4 Correlated-identity discounting.** Entries whose value derives from
usage, demand, or verification by correlated identities are discounted at
confirmation time by an algorithm **published at M0**. It is amendable only
prospectively, via an open comment period, never retroactively to a closed
challenge window and never by founder discretion. Automated discounts are
**proposals confirmed by a named human reviewer**, reviewing at **identity-cluster
level** (GDPR art. 22); human-review capacity is funded from the same capped
audit slice as A.2.

**A.5 Finality, symmetric to conditionality.** Confirmation renders an entry's
**eligibility and relative weight** final and beyond later rule changes.
**Monetary amounts arise only upon declaration of a distribution.** Confirmed
entries remain **non-transferable**. **The platform will not initiate recovery
of settled distributions.** (Drafted deliberately as "will not initiate
recovery", not as "no claims exist": a blanket clause cannot bind tax
authorities or fraud confiscation, and art. 6:248(2) BW can override absolute
finality.)

**A.6 The economic invariant.** At every point: the expected payout of a
fabricated entry ≤ the expected cost of fabricating it **plus** surviving audit
and challenge. If adjudication cost exceeds the audit slice, the response is to
raise stakes or batch by cluster — **never** to pay provisional entries in
order to clear the queue. Presumption favours the entry; auditors must show
evidence to discount.

**A.7 Challenge process.**

- **Grounds, enumerated:** fraud; Sybil or correlated-identity fabrication;
  collusion; fabricated dependency edges; misrepresented capacity.
- **Standing:** any identity may challenge, on a **reputation-only stake**
  (never a monetary stake). A stake is burned only for **bad-faith** challenges
  — not for merely unsuccessful ones.
- **Notice and response:** the affected identity receives notice and **≥30
  days**, once, to respond with evidence. Notice is automatic and free.
- **Decision-maker:** the verification market (post-split, under stichting
  oversight) — **never solely the platform operator**.
- **Appeal:** one staked appeal to a differently-composed panel. The stake is
  burned if the appeal merely restates; returned plus credit if it overturns.
  Appeal decisions are final — one round, not a ladder.
- **Publication:** all decisions are published entries citing evidence.
- **Every process step carries a stake or a clock.** A free appeal path is a
  free option and becomes a denial-of-service on the distribution itself.
- **Pre-M3 challenges queue** on-ledger, timestamped, stakes escrowed,
  adjudicated once the verification market exists. **No platform or founder
  interim adjudication during M0–M2**, at any point.

`[OPEN — for counsel: define "frivolous" / "bad faith" operationally. socaity-zjr
requires that it mean bad faith and not merely unsuccessful, or good-faith
challengers are chilled — but no definition was drafted.]`

`[OPEN — for counsel: confirm that a reputation-only stake, burnable, carries no
deposit, gambling, or consumer-payment characterization; and confirm the
regulatory treatment of the escrowed share of a challenged entry between
declaration and adjudication (A.3) — who holds it, in what capacity.]`

`[OPEN — for counsel / identity-specialist: cluster-level art. 22 human review
against art. 22's individual framing. socaity-zjr classes this as material
before the first distribution, not M0-blocking; it remains unanswered.]`

`[OPEN — for counsel: the placeholders — 5% audit slice, ≥90-day challenge
window, ≥30-day response window — are stated as placeholders in the adopted
text. Confirm whether any minimum period is legally constrained (notice periods,
unfair-terms review) before the numbers are frozen.]`

---

## Annex B — Identity and pseudonymity terms

*Source: socaity-7mk, adopted by consent Round 3. Schema v1, effective from
entry #1.*

**B.1 The primitive.** Contributor identity is a **self-generated Ed25519
keypair held by the contributor**. Canonical on-ledger form: the multibase
string `z6Mk…` (multicodec ed25519-pub + base58btc), without the `did:key:` URI
prefix. A versioned `sig_alg` field (`ed25519-v1`) is additive-only.
Verification is prefix-strip plus Ed25519 verify; the forkability CI job fails
if verification ever requires a DID library or network resolution.

**B.2 On-ledger, permanent.** `actor_key`; a structured payload of typed
references only, with **no free text anywhere**, enforced by the schema
validator, not by review; evidence as **content hashes or structured artifact
references only** (a bare commit SHA is acceptable) and **never resolvable
URLs**; timestamp; signature over the canonical serialization; signed
status-change entries per Annex A.

**B.3 Off-ledger, mutable, erasable.** The profile (display name, avatar,
links) keyed by public key — its deletion is the art. 17 erasure mechanism; the
verified-link table (bidirectional signed GitHub attestation, revocable); the
evidence table (entry → resolvable URLs). Forks inherit the ledger, not these
tables: evidence stays **verifiable** post-fork even where it is no longer
**discoverable**.

**B.4 Key lifecycle, forward-only ledger events.**
`key.successor_designated` (repeatable, latest wins at replay);
`key.rotated` (signed by the old key or the designated successor);
`key.rebound` (only via the Annex A adjudication process, carrying an
`adjudication_ref`). No privileged mutation exists; replay resolves continuity
deterministically.

**B.5 No custody.** The platform never holds a contributor's private key. (A
later milestone may offer platform-stored **encrypted** blobs the platform
cannot use.) The founder uses the same primitive — there is no platform-god
identity.

**B.6 Contributor-facing terms, stated plainly at M0.**

- Ledger entries are **permanent and public**. They cannot be deleted.
- **Erasure covers off-ledger data only** — the profile, the verified-link
  table, the evidence table. Contribution facts persist pseudonymously.
- **Earning is pseudonymous, forever.** **Fiat payout is not.** At claim time,
  identity binds via proof of key control to a KYC flow run by the licensed PSP
  partner. DAC7 due-diligence data, tax and sanctions data live with the PSP or
  in a segregated retention-bound store, **never on the ledger**, and are
  retained for as long as tax and AML law requires — art. 17(3)(b) GDPR
  overrides erasure there, and the privacy notice says so from day one.
- No public statement may promise pseudonymous payout, or that the ledger is
  GDPR-exempt.
- **Warning at signing time:** anything a contributor cites is permanent.
  Pseudonymous contributors cite artifact hashes.
- Personhood verification is **never** a precondition for recording work.

**B.7 M4 hook (socaity-7mk item 7).** An **optional opaque attestation field**
(a hash) exists on entries. Personhood credentials bind to the contributor key
at a later milestone. **Nothing recorded at M0 changes** as a result.

`[OPEN — for counsel: identify the data controller for the M0 period, when the
publisher is a natural person and no stichting exists yet (Annex D), and how
controllership transfers on incorporation. Not addressed by any resolution.]`

`[OPEN — for counsel: the privacy notice itself is referenced by socaity-7mk as
carrying the retention/erasure statements from day one, but no notice text has
been drafted or scoped. Confirm whether it belongs inside this instrument or
alongside it, and whether the DPIA (material before M4) needs any M0 hook here.]`

---

## Annex C — Conversion Schedule V, v1, and the attestation statement

*Source: socaity-19p, adopted by consent Round 3. V is the M0 valuation rule; it
publishes as versioned code alongside the allocation rule.*

**C.1 Flat rate.** **1 attested hour = 1 vu**, for every contribution class. A
category enum (code / docs / design / outreach / ops) exists on entries for
legibility and audit routing **only**. There is one rate row. Adding a
multiplier column is a rate-card change requiring the meta-rule: unopened
epochs, ≥14-day public comment, and an attestation re-check. No impact-based
pricing before a market exists.

**C.2 Timed work.** Attested by a public worklog — timestamped, with a
corroborating trace. Hard cap **40 vu per person per week**. All entries
provisional under Annex A.

**C.3 Artifact work.** Prospective tickets only: the ticket is opened **before**
the work, in the versioned repository, with the tier declared at opening —
**T1 ≤ 2 vu, T2 ≤ 8 vu, T3 ≤ 40 vu**; the bounds are epoch-fixed V content and
tier assignment is challengeable under Annex A. Acceptance is the public
merge/accept event: **binary, and identical to any maintainer's gate**.
Rejection leaves no ledger residue. The founder gates **inclusion**, never
**value**.

**C.4 Accrual formula.** `accrual = max(0.5, min(attested_hours, budget))` for
an accepted contribution — an explicit uniform formula in V's versioned code,
never a discretion to round up.

**C.5 Minimum-entry floor.** **0.5 vu**, available ticket-free for trivial
accepted contributions: *the ledger records participation before it records
magnitude*. It applies once per contributor per accepted artifact. Artifacts are
non-splittable for floor purposes — splitting is misrepresented capacity under
Annex A.7. The floor is an entry gate, not a pricing lane. The floor value is
epoch-fixed V content and applies uniformly, including to the founder's trivial
entries.

**C.6 Founder rate.** V applies to founder hours from the same table,
benchmarked to a **published grant-funder referent** (NLnet / NGI Zero cost
bases preferred; Sovereign Tech Fund or Horizon acceptable), set **at or below
the referent, at median**. Source, version, and date are pinned in V's code. The
role-mapping is published and challengeable.

`[OPEN — for counsel: the specific referent figure is inserted when the first
NLnet budget is written (grant-writer execution per socaity-19p / socaity-bgl).
The instrument publishes the rule, not the number. Confirm this is acceptable —
i.e. that V may publish with the referent named and the figure pending.]`

**C.7 Founder-conflict devices.** A founder-share **cap is rejected** (it breaks
the uniformity covenant, forces the ledger to under-record the truth at M0, and
creates a Sybil-laundering incentive for the party controlling the identity
layer). In its place:

- **Attestation gate.** `EpochOpened(n)` requires a signed public statement from
  **≥1 named non-beneficiary** — no ledger position, and no accrual intent in
  any attested epoch — per C.8.
- **Concentration tripwire.** A standing public dashboard of per-contributor
  epoch share. Any contributor exceeding **X%** of an epoch's vu auto-escalates
  the Annex A audit to full-worklog review. Tier assignments join this audit
  surface: budget-kissing patterns (attested ≈ budget across entries) flag for
  review.
  `[OPEN — for counsel: X is unset in the adopted text. This is council/mechanism
  content, not counsel content; noted here so it is not silently published as a
  blank.]`
- **Size-scaled challenge windows**, with founder entries challenge-eligible at
  a lower friction bar: anyone may flag, and the founder answers publicly.

**C.8 The attestation statement.** The attestor certifies **correspondence
only**, over three mechanically checkable facts:

1. V's rates match the cited referent within the stated tolerance;
2. there is no multiplier column;
3. the tier table is identical to the draft that stood in public comment for
   ≥14 days.

The signed statement prints this scope **verbatim**. The attestor certifies
nothing about solvency, payout likelihood, or that "contributors are compensated
at X". **No document, ever, composes "1 vu = €X owed"** — the referent prices
the meaning of the unit; a distribution prices the claim; they are separate
sentences. The attestation text carries the same contingency disclaimer as V.
The attestor holds no ledger position, receives no vu for attesting, and the
statement is published on the ledger page.

Recruitment: the first attestor comes from the warm circle (2–4 weeks);
OSS-sustainability figures serve as second attestor at M1–M2; **the NLnet
reviewer is never used** — a funder's evaluation role must not become applicant
governance.

`[OPEN — for counsel: the "stated tolerance" in C.8(1) is undefined in the
adopted text. Counsel to advise on how tightly it must be expressed for the
correspondence-only framing to hold.]`

`[OPEN — for counsel: draft the exact attestation instrument. socaity-19p fixes
its scope, its disclaimer requirement, and its refusals, but no wording exists.
Wage-representation exposure is rated "monitor, not material" — confirm at the
wording level.]`

**C.9 Evidentiary standard.** A neutral third party must be able to **re-derive
every vu figure from the artifact plus V alone**. Founder self-attestation ends
the moment a second attestor exists; until then, publication plus the open
challenge window **is** the attestation, and V says so.

**C.10 Vocabulary and tax rails.** V speaks of the **"valuation of a
contribution"** — never pay, wage, or compensation. The *vrijwilligersregeling*
framing appears nowhere. No euro-denominated claim exists at accrual. Entries
stay contingent, non-transferable, and defeasible until distribution, so that no
present-day tax event arises.

`[OPEN — for counsel / tax adviser: confirm the genietingsmoment analysis before
the first distribution (socaity-19p item 7). Adopted as a required consult, not
resolved.]`

---

## Annex D — Publisher, entity staging, and the uitkeringsverbod gate

*Source: socaity-gp2 (consolidating socaity-vwy), adopted by consent Round 2.
Included here because it fixes who publishes and signs this instrument, and
because it carries a hard gate into the same counsel engagement.*

**D.1 Publisher at M0.** The founder acts as a **natural person**. The first
NLnet application and MoU are submitted and signed personally; the application
never waits on incorporation. Proceeds are ledgered under the published rule
from euro one.

**D.2 Bridge entity.** A Dutch **stichting**. A sole-founder BV is refused as
the bridge: it makes the founder a DGA with aanmerkelijk belang and triggers
*gebruikelijk loon* (Wet LB art. 12a) — a deemed present-day tax event
decoupled from the ledger rule, contrary to C.10, and a de-facto special founder
channel contrary to clause 8.

Properties relied on: no shares, therefore no deemed-salary regime; the preferred
counterparty form for STF, NGI and foundations; **ANBI-compatible statutes** (no
ANBI application yet); a one-person bestuur at incorporation with a **statutory
commitment to expand to ≥3 board members** before any ANBI application or any
first above-de-minimis distribution; and forward-compatibility with the M5
Blender-pattern split — the stichting on top, the BV arriving later as the
service subsidiary. The reverse order is the expensive path.

**D.3 Incorporation trigger.** NLnet award notification, **or** the start of any
entity-requiring application (an STF/STA contractual conversation, a foundation
application) — whichever comes first. Backstop: before any second grant contract
of any kind. If the notary is slower than NLnet's MoU: sign personally and
novate later, which is routine for NLnet.

**D.4 Hard gates.**

- Never sign an entity-requiring contract as a natural person.
- **No distribution from the stichting to the founder** before licensed NL
  counsel has cleared the **uitkeringsverbod (art. 2:285(3) BW)** compensation
  structure and the statutes. Ledger-rule payments are structured and papered as
  **compensation for work performed**, never as profit distribution (the Blender
  precedent). *This gate is expressly part of the socaity-7kv counsel scope.*

`[OPEN — for counsel: the statutes themselves. Counsel/notary to draft an
ANBI-compatible stichting statute whose object accommodates (i) the standing
commitment in Part II, (ii) the uitkeringsverbod-compatible compensation
interface in D.4, and (iii) the ≥3-board-member expansion commitment.]`

`[OPEN — for counsel: how does this instrument itself move from the natural
person to the stichting? socaity-gp2 resolves novation for the NLnet MoU and is
silent on the commitment. Confirm whether the stichting adopts, ratifies, or
re-publishes it, and what happens to entries recorded in the interim.]`

---

## Appendix 1 — Vocabulary standard (clause 10 wordlist)

*Merged union of the legal-counsel and launch-strategist lists, socaity-1ux.
This list is the machine-checkable artifact behind clause 10.2 layer 1: it lives
in the repository and CI runs it over owned surfaces.*

### Banned outright

`token` · `coin` · `airdrop` · `tokenomics` · `mint` · `wallet` · `holders` ·
`get in early` · `upside` · `equity` · `equity-like` · `APY` · `yield` ·
`staking` · `investment` · `returns` · `dividend` · `profit share` ·
`clawback`

### Banned as entitlement triggers

`guaranteed` · `you will receive` · `you will be paid` · `owed` · `entitled` ·
`your share of future revenue` · `payout` *(in headlines)*

*Drafter-proposed additions, not in either adopted list:* `vested` ·
`redeem` *(of undeclared amounts)*. Both are consistent with socaity-zjr's
Round-2 correction of "confirmed forever" as reading like a vested right to
money, but neither was adopted as a banned term. They are held here as
proposals; adding a word to a permanently binding wordlist is a council call.

### Banned phrase

> "equity-like upside without issuing equity or tokens"

*Named in socaity-1ux as the single most quotable sentence for an AFM
characterization argument. It currently appears in doc/vision.md — see the open
item under clause 10.4.*

### Required / permitted lexicon

`ledger` · `record` · `recorded contribution` · `contribution` ·
`retroactive` · `retroactive grant` · `recognition` · `published rule` ·
`allocation rule` · `proportion` · `distribution` · `declaration` ·
`provisional` · `confirmed` · `validation` · `challenge` ·
`non-transferable` · `valuation of contribution`

### Required brand assertions

> "You cannot buy this and you cannot sell it."
>
> "No token. Nothing to trade. The ledger is a database, not a blockchain."

### Modifier rule

`fixed` and `locked` may modify only: **the rule**, **epoch parameters**, or **a
confirmed weight**. Never a share of money; never "what you'll get."

### Framing rules

- The earliness premium is explained **structurally** — fixed pie per epoch,
  smaller network, larger share. Never as a percentage, a multiple, or a
  projection. "Earliness premium" is not headline copy.
- Never "clawback of what you were promised". The vocabulary is **validation**
  and **challenge** — which is also mechanically accurate, since under
  provisional-by-default nothing is ever taken back.
- Valuation questions receive the structural answer, never a number.
- No headline overclaim with fine-print hedging. Diverging registers means the
  asset does not ship.
- Legalese is never the first screen; discretionary language lives in the
  operative register.

### The quote-out-of-context test

Every sentence of the plain register must survive being screenshotted alone into
a hostile comment thread. Apply it to Part I before every publication.

---

## Appendix 2 — Open items register

Items marked `[OPEN]` above, collected. **C** = for the licensed NL practitioner
in socaity-7kv. **Co** = council/mechanism content that this assembly may not
invent; listed so nothing publishes blank.

| # | Location | Item | Owner |
|---|---|---|---|
| 1 | Clause 4 | M0 values: epoch length, pie size, premium-curve parameters, comment-period length | Co (+ C to confirm no value representation) |
| 2 | Clause 4.2 | Enforceability/drafting of "executable code governs over prose"; incorporation by reference | C |
| 3 | Clause 9.3 | Reconcile no-derdenbeding with art. 6:248 BW reliance flagged in socaity-zjr | C |
| 4 | Clause 9 / Annex A | Consumer status of contributors; unfair-terms review of clause 5 discretion and A.7 process | C |
| 5 | Clause 10.4 | doc/vision.md still contains the banned "equity-like upside" phrasing; is vision.md an owned surface for clause 10.1? | C (then Co to authorise the edit) |
| 6 | A.7 | Operational definition of "frivolous" / "bad faith" | C |
| 7 | A.3 / A.7 | Reputation-stake characterization; custody and regulatory status of escrowed challenged shares | C |
| 8 | A.4 | Cluster-level GDPR art. 22 review vs the individual framing | C + identity-specialist |
| 9 | A.2/A.3/A.7 | Whether the 5% / ≥90-day / ≥30-day placeholders face any legal minimum | C, then Co to freeze |
| 10 | Annex B | Data controller during the natural-person M0 period; transfer on incorporation | C |
| 11 | Annex B | Privacy notice: scope, placement, M0 hook; DPIA linkage | C |
| 12 | C.6 | Publishing V with the referent named and the figure pending | C (figure: grant-writer) |
| 13 | C.7 | Concentration-tripwire threshold X | Co |
| 14 | C.8 | "Stated tolerance" for the correspondence check | C |
| 15 | C.8 | Exact attestation instrument wording; wage-representation check | C |
| 16 | C.10 | Genietingsmoment analysis before first distribution | C / tax adviser |
| 17 | D.4 | ANBI-compatible stichting statutes accommodating Part II and the compensation interface | C / notary |
| 18 | D | How this instrument transfers from natural person to stichting; interim entries | C |
| 19 | whole document | Governing law and jurisdiction clause — not addressed by any adopted resolution | C |
| 20 | whole document | Authoritative language (EN or NL) if both versions publish | C |
| 21 | Clause 3 | Succession on death/incapacity: does a ledger entry pass to an estate? Non-transferability as adopted covers purchase, sale, assignment, pledge only | C, then Co |
| 22 | Clause 7 | socaity-1ux clause 7 lists "annual statements"; socaity-7mk defines no such artifact (cadence, content, recipient, channel all unspecified) | Co, then C |
| 23 | Appendix 1 | `vested` and `redeem` are drafter-proposed banned terms, not in either adopted list | Co |

Items 19 and 20 are not traceable to any resolution: they are ordinary drafting
requirements that no council addressed, surfaced here rather than answered.
Items 21–23 are omissions or additions found on evaluation against the source
resolutions; each is flagged rather than decided.

---

## Standing constraints on this document

Carried from the paramount lists of the source resolutions; none may be relaxed
in drafting:

1. No present-tense entitlement wording anywhere in the M0 text.
2. No transferability or purchasability, now or by silent amendment.
3. Nothing publishes without Annex A and Annex B in the same document.
4. No operative text publishes before licensed NL counsel review.
5. No interest, indexation, or time-based accrual on undeclared amounts.
6. No marketing copy outside the Appendix 1 lexicon.
7. No personal data, and no free text, on the ledger — evidence is hash-only.
8. No platform custody of private keys as a default flow.
9. No founder carve-out; no discretion over relative allocation; no amendment
   to a closed or open epoch; no revocable ledger export.
10. No public claim that payout will be pseudonymous, or that the ledger is
    GDPR-exempt.
