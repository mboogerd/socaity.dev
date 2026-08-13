# socaity.dev — Vocabulary and Visual Standard

**Status:** binding on every public surface from M0 onward.
**Machine-readable half:** [`banned-words.txt`](banned-words.txt) (consumed by
the CI banned-wordlist gate, socaity-ddi).
**Derives from:** [vision.md](../vision.md), [sustainability.md](../sustainability.md)
(anti-commitments), council resolutions socaity-1ux (clause 10), socaity-xuz
(/ledger presentation rails), socaity-19p (valuation vocabulary), socaity-x8o
(epoch-share display rules), socaity-zjr ("validation", never "clawback"),
socaity-ue3 (blog, CI wordlist gates), socaity-sbb (intervals, never dates).

## 0. Why this document is a gate and not a style guide

One screen that pattern-matches an airdrop dashboard undoes the manifesto's
positioning, and the repair cost is a rebrand. The anti-crypto signal is
**visual before it is verbal**: a reader decides what kind of thing this is
before reading a sentence. So the rules below are written as **pass/fail
checks**, not preferences, and the wordlist is written as **regexes**, not
advice. If a check is subjective enough to argue about, it is written wrong —
fix the check, do not waive it.

### What counts as a surface

Anything a stranger can reach without asking us: site pages, the manifesto,
the FAQ, `/ledger`, README, blog posts and the weekly ledger digest, RSS
items, OG cards, social mirror-out copy, screenshots we publish, alt text,
and the public text of grant applications.

**Not** a surface, and deliberately exempt: `doc/`, `council/`,
`.claude/skills/`, code comments, and beads issues. Internal precision may use
words public copy must not — that boundary is what keeps the gate narrow
enough to stay switched on.

---

## 1. VOCABULARY

Format: **use this** → *never these* → why. Every "never" column entry with a
`regex` note appears in `banned-words.txt`; the rest are review-required (`~`
prefix in that file) and pass CI only with an inline
`<!-- vocab-ok: reason -->` waiver.

### 1.1 The record

| Use | Never | Why |
|---|---|---|
| **ledger**, **contribution ledger**, **the record**, **a database** | wallet, account, balance, holdings, treasury, portfolio, my position | "Wallet" imports custody, transfer and price in one word. The ledger holds no value; it records facts. 1ux: *"the ledger is a database, not a blockchain."* |
| **entry**, **recorded contribution**, **observation** | allocation, grant to me, my stake, my share (unqualified) | An entry is a record of work done, not a thing handed out. xuz: *"a pre-mine is a grant; this is a timesheet."* |
| **append-only public record** | on-chain, chain, blockchain, DLT, smart contract | We are a git-backed database with a hash chain. Saying so plainly is the whole differentiator; borrowing chain vocabulary throws it away for free. |
| **validation**, **challenge**, **challenge window** | clawback, slashing, penalty, dispute resolution (as courtroom framing) | Nothing is ever taken back — entries are provisional until confirmed, so "clawback" is *mechanically wrong*, not merely off-tone (socaity-zjr). |

### 1.2 The unit and the share

| Use | Never | Why |
|---|---|---|
| **vu (valuation unit)**, **valuation of contribution** | points, coins, credits-as-currency, tokens, XP | A vu is an internal measure of relative contribution to a contingent future distribution. Any word that sounds spendable creates an entitlement impression legal-counsel has ruled out (19p). |
| **epoch share**, always rendered as **% of a closed epoch** | balance, holdings, your total, a numeric lump | x8o: epoch weights are scale-invariant fractions; amounts exist only upon declaration. A number styled as a balance *is* the pre-mine screenshot (xuz). |
| **"if epoch N closed today: Y% — an upper bound; it can only fall"** | a bare open-epoch percentage; an open-epoch figure in a visual series with closed epochs | The numerator is fixed and the denominator only grows: the only surprise permitted is downside. Suppressing the figure entirely reads as coyness (xuz Round 2). |
| **earliness premium**, defined mechanically in the adjacent sentence | get in early, early bird, ground floor, upside, equity-like upside, early believers | The mechanism is real and must be explainable; the *marketing register* of it is the single most quotable sentence for an AFM characterization argument (1ux). Vision.md's "equity-like upside without issuing equity" never appears in public copy. |
| **distribution** (only once declared) | payout (in headlines), dividend, profit share, return, ROI, cash out | Declaration is discretionary until it happens; every alternative word asserts an obligation that does not exist. |

### 1.3 The work

| Use | Never | Why |
|---|---|---|
| **contribution**, **capacity**, **burn rate per node**, **pledged capacity** | mining, miners, hashrate, farming, staking, emissions, block rewards, rewards drop | Contribution is attested labor with evidence, verified by humans and adversarial review. Extraction vocabulary describes a machine printing units — the opposite claim. |
| **subsidy multiplier**, **the published rule**, **allocation rule** | credit multiplier (public copy), tokenomics, protocol economics, emission schedule | "Subsidy" is the accurate Pigouvian word and it is the one word crypto marketing never uses. See §4 on retiring the "credit" prefix publicly. |
| **contributor**, **participant**, **maintainer** | holder, investor, whale, community (as a euphemism for holders), degen | 1ux/launch-strategist brand hygiene: audience nouns are the fastest tell of what a project thinks it is selling. |
| **verification**, **red-teaming**, **acceptance review** | consensus, validators (as a role class), node operators | Verification here is a paid open market of humans and agents, not a protocol role. |

### 1.4 Money, obligation and time

| Use | Never | Why |
|---|---|---|
| **"No token. Nothing to trade. This is a database."** (required first-screen asset on any surface presenting the ledger or the mechanism) | any softer paraphrase | 1ux mandates the first-screen asset as "No token. Nothing to trade. The ledger is a database, not a blockchain."; xuz adopts the shorter register line above for `/ledger`. Either is verbatim-reusable; the shared prefix "No token. Nothing to trade." is what the gate asserts. Never paraphrase. |
| **the canonical paragraph, verbatim** — Part I of [`m0-standing-commitment.md`](../m0-standing-commitment.md) ("Every contribution is recorded on a public, append-only ledger from day one…"), whose one-line summary is *"we make no promise that money will ever be distributed; we bind ourselves publicly to the allocation rule if it ever is"* | you will be paid, you will receive, guaranteed, owed, entitled, your share of future revenue | The canonical two-register framing (1ux). The plain-language commitment is the **ceiling** for every future claim — no surface may promise more than it does. |
| **"not an investment"**, **"you cannot buy this and you cannot sell it"**, **non-transferable** | invest in, investors, equity stake, shareholders, securities offering, risk-free | Negated and definitional uses of *investment / dividend / equity-like / guaranteed* are exactly the required FAQ copy — hence review-required, not banned. Only the negated or definitional form passes review. |
| **"valuation of contribution"** | pay, wage, salary, compensation for your work, hourly rate you earn | 19p: hour-anchoring helps only if no wage framing attaches to it. Never invoke the *vrijwilligersregeling* anywhere. |
| **intervals: "Q3±1", "3–6 months", a range bar** | any point date, coming soon, ETA, countdown, days left | Vision requirement and sbb paramount: point-date estimates are banned in the schema, so they cannot exist in the UI either. |
| **state the fact** ("every entry links its evidence") | transparent, radically transparent, fully transparent, trustless | xuz: the page never says the word "transparent". Claiming the virtue is what a scheme does; exhibiting it is what a record does. |

### 1.5 Quotable-but-never-assertable

`pre-mine`, `scheme`, `ponzi`, `crypto` are review-required rather than banned:
xuz **requires** /ledger to name the pre-mine objection in the objector's own
words, and the FAQ must answer "is this a crypto thing?" without euphemism. The
waiver reason must state that the term appears as a quoted objection being
answered, never as our own description.

### 1.6 Enforcement contract for the CI gate (socaity-ddi)

- Patterns are POSIX ERE, case-insensitive, one per line, `#` comments.
- A leading `~` marks review-required: the gate reports the hit and passes only
  if the matching line carries `<!-- vocab-ok: reason -->` (Markdown/HTML) or
  `# vocab-ok: reason` (code/config). All other patterns fail the build with no
  waiver path.
- Required-string checks are the gate's second job and are not expressible as a
  banlist: any surface presenting the ledger or the mechanism must contain the
  exact string `No token. Nothing to trade.` — assert its presence, not its
  absence.
- **Never widen a pattern to a bare common English word.** A false positive
  teaches authors to disable the gate, which costs more than the word it caught.
  Add the phrase, not the word.

### Which tier a word gets

The tables above say what to *write*; the tier says how the gate *reacts*. A
"never" word is FAIL-level only when both of these hold:

1. it has no ordinary-English sense a public sentence could legitimately need
   (*airdrop*, *tokenomics*, *clawback*, *hashrate*, *HODL*), and
2. the required FAQ / manifesto copy never has to **negate** or **quote** it.

Everything else is review-required (`~`), which still reports every hit and
still demands a written waiver — it just does not hard-fail the build. Two
families sit there by construction:

- **Negation-required words.** The FAQ must be able to say *"there is no
  token"*, *"this is not an investment"*, *"no wage, no salary, no payout is
  owed"*, *"is this a crypto thing?"*. Banning these outright bans the very
  copy 1ux and xuz mandate. `token` (bare), `investment`, `dividend`,
  `equity-like`, `guaranteed`, `wage`, `salary`, `payout`, `crypto`,
  `pre-mine(d)`, `scheme`, `ponzi`. The wallet-grammar *compounds* built from
  them (`buy the token`, `token sale`, `your salary`, `equity stake`) stay
  FAIL: no sentence needs those, negated or not.
- **Ordinary-English collisions**, measured against this repo's own prose:
  *mining* (data/graph mining), *holding* / *holders* (rights holders, CC0
  copy), *staked* (our own "staked appeal"), *stake* ("at stake"), *yield*
  (the verb), *emissions* (carbon), *upside*, *transparent*, *make money*
  ("how does socaity make money?"), *APR* (case-insensitive `Apr`). These are
  narrowed to their crypto compound at FAIL level and left review-required as
  bare words.

Two consequences for the gate (socaity-ddi): `\b` is a GNU/BSD extension, not
POSIX ERE — the gate must run GNU `grep -E` (or Go/Python regex), not busybox;
and patterns are matched case-insensitively, so a pattern must never rely on
`[A-Z]` to mean "a capitalised month".

---

## 2. VISUAL

Editorial register, stated as checks. Each is pass/fail on a rendered page at
1280px and at 390px. A surface ships only with every check passing.

**V1 — Text face and measure.** Body copy is a readable text face (quiet sans
or a real serif) at ≥16px and ≥1.5 line-height, measure 60–80 characters.
Vertical rhythm is generous: ≥ 1 line of space between paragraphs, ≥ 2 above every heading, and ≥ 48px of padding around each content block at 1280px. FAIL: display/geometric or monospace faces used for body copy; measure >90ch; content packed edge-to-edge or dense enough that no block reads as a separate object (density is the dashboard tell).

**V2 — Palette.** Flat paper background, one accent hue maximum, light mode is
the primary register. FAIL: any multi-stop or animated gradient; saturated neon
on dark as the default look; glassmorphic blur or translucent panels; glow or
colored drop-shadow used as emphasis; a surface that exists only in a dark
neon register.

**V3 — Iconography and illustration.** Line diagrams, tables, arrows, plain
state chips. FAIL: coins, gems, diamonds, rockets, moons, chain links, 3D or
isometric token objects, robot faces, and generated hero imagery. Diagrams must
carry information — a decorative diagram fails the same as a coin.

**V4 — Motion.** FAIL: counting-up or animated numbers (a crypto tell, xuz),
countdown timers, marquees, parallax, particle backgrounds, auto-advancing
carousels. Motion is permitted only for disclosure (expand/collapse) and focus.

**V5 — Every number is derivable.** Each displayed number (a) is computed at
render from a published artifact, never hand-written; (b) links to, or sits
adjacent to, its derivation — with a "recompute this" affordance where the
published rule code applies; (c) is expressed as vu or as a percentage of a
closed epoch. FAIL: any number without a derivation path; any currency symbol
or thousands-separated money figure on `/ledger`; a hand-written percentage.

**V6 — No balance grammar.** FAIL: a hero number styled as a balance; an
aggregate per-person lump-sum row or total; portfolio-style KPI tiles; a
sparkline of "value over time"; any per-person figure larger in visual weight
than the rule that produced it.

**V7 — Forecasts are intervals.** Any time or effort estimate renders as a
range object (bar or band), with its freshness ("estimated 4 months ago").
FAIL: a point date, a point estimate with error bars styled as a point, an
undated estimate.

**V8 — Provenance is a designed object.** Every agent-generated block carries
its provenance label; quoted third-party text is visually quoted, attributed,
linked, and not editable in place. FAIL: an unlabeled generated block; a
provenance notice styled as a legal disclaimer rather than as part of the
design.

**V9 — CTA discipline.** At most two calls to action per surface, both
diegetic (they are facts about the record, e.g. a visibly empty claimable row).
FAIL: banners, modals, waitlist-position numbers, "spots left", numbered early
badges, scarcity or urgency mechanics of any kind.

**V10 — Crop test.** Take a real 1200×630 screenshot of the top of the page and
of every panel containing a large percentage. Each crop, caption-free and
link-free, must be self-explaining and self-indicting. FAIL: a crop whose
honesty depends on a caption or a link that the crop loses. The OG card is
authored as the disclosure, not as a headline.

**V11 — Honesty runs both directions.** The least flattering fact on a surface
is not de-emphasized: no burying below the fold, no footnoting, no scale trick,
no truncated axis. FAIL if the worst number is smaller, lower, or quieter than
the best one.

**V12 — No simulated activity.** Nothing on a surface depicts activity that did
not occur — no seeded challenges, no placeholder contributors, no example rows
styled like real rows, no fake counts. Reserved/empty states are allowed and
must read as empty (mechanism-designer paramount, xuz).

**V13 — Accessibility floor.** WCAG AA contrast, keyboard navigable, structural
headings, screen-reader-sensible order, no information carried by color alone.

**V14 — Required first-screen assets.** Any surface presenting the ledger or
the mechanism opens with the register line "A public record of contributions.
No token. Nothing to trade. This is a database." and, where a founder-share or
concentration figure appears, the denominator is the headline.

---

## 3. PROCESS — the pre-publish checklist

Copy this block into the PR that publishes or changes a surface. Every box is
ticked by a named person before merge; an unticked box blocks the merge.

```
## Pre-publish checklist — doc/standards/vocabulary-and-visual.md

Surface: ______________________   Reviewer: ______________________

Vocabulary
- [ ] CI banned-wordlist gate is green on this surface
- [ ] Every `~` review-required hit carries a `vocab-ok:` waiver with a reason
      that names the negated / quoted / definitional use justifying it
- [ ] Required strings present where applicable ("No token. Nothing to trade.")
- [ ] Canonical paragraph (m0-standing-commitment.md Part I) reused verbatim,
      not paraphrased
- [ ] No claim exceeds the plain-language Standing Commitment (the ceiling)
- [ ] Every forecast is an interval; no point dates anywhere in copy

Visual (V1–V14; check the rendered page at 1280px and 390px)
- [ ] V1 text face and measure
- [ ] V2 palette / no gradient, neon, glass, glow; light mode primary
- [ ] V3 no coin/gem/rocket/chain/3D iconography; diagrams carry information
- [ ] V4 no animated numbers, countdowns, parallax, carousels
- [ ] V5 every number computed at render and linked to its derivation
- [ ] V6 no balance grammar, no lump-sum row, no portfolio tiles
- [ ] V7 forecasts render as intervals with freshness
- [ ] V8 agent-generated content labeled; quoted text quoted and attributed
- [ ] V9 at most two diegetic CTAs; zero urgency/scarcity mechanics
- [ ] V10 real 1200×630 crop test run on the top of the page and every
      large-percentage panel — screenshots attached to this PR
- [ ] V11 the least flattering fact is not de-emphasized
- [ ] V12 nothing depicts activity that did not occur
- [ ] V13 WCAG AA contrast, keyboard navigable, structural headings
- [ ] V14 required first-screen assets present; denominator is the headline

Comprehension (surfaces carrying a number or the mechanism; M0 launch surfaces)
- [ ] 5-stranger test run: "what is this? who is it for? what's the catch?"
- [ ] Strangers state the WHY of any concentration figure ("because there is
      one contributor"), not the WHAT ("he kept it all")
- [ ] Nobody answers the catch question with "token", "airdrop", or "scheme"
- [ ] If it failed: the surface was redesigned — copy was NOT added on top

Sign-off
- [ ] Checklist result recorded in the PR; failures link to the fix commit
```

**Escalation rule.** A failing check is redesigned, never waived by adding
explanatory copy on top. Copy-on-top is the failure mode this standard exists
to prevent: it produces surfaces whose honesty depends on the reader finishing
the paragraph.

**Amendment rule.** This standard changes by PR with the same 14-day public
comment convention the rule amendments use. The checklist lives in the repo
because a glass house cannot keep its own hygiene rules private.

---

## 4. Open question resolved: do we keep the word "credit"?

> **LAUNCH-STRATEGIST DECISION POINT** — ratification requested. The product
> designer raised it; the recommendation below is written to be adopted or
> rejected as a whole, because the manifesto and FAQ are written against it
> immediately.

### Recommendation: retire bare "credit" from public surfaces. Keep it in two bounded compounds and in internal documents.

**Public default vocabulary (M0):**

| Concept | Public term | Was |
|---|---|---|
| The record | **contribution ledger** | credit ledger |
| The unit | **vu (valuation unit)** / **recorded contribution** | credit |
| The share | **epoch share** (% of a closed epoch) | credit share |
| The pricing signal | **subsidy multiplier** | credit multiplier |
| The reputation layer | **standing** / **recognition** | reputation credit |
| The closed-loop compute claim (M3+) | **compute credit** *(kept)* | compute credit |
| Money attached to nodes (M5) | **the fiat rail**, **declared distribution** | credit redemption |

**Reasoning:**

1. **"Credit" is the one word that is simultaneously wallet-adjacent and
   regulator-adjacent.** *Krediet* is a financial-services term of art; the 1ux
   instrument spends ten clauses establishing that an entry is not a debt, a
   deposit, e-money, or a claim. A noun that means "an amount extended to you"
   fights that document in every sentence it appears in.

2. **The permitted lexicon already decided this without noticing.** 1ux clause
   10's required list is *retroactive grants, recognition, allocation rule,
   recorded contribution, validation, challenge*. "Credit" is absent. Every M0
   surface adopted since — xuz's /ledger, 19p's rate card, x8o's epoch weights
   — is fully expressible in vu, epoch share, and recorded contribution. There
   is no public sentence at M0 that needs the word. Keeping it would be
   maintaining vocabulary for a surface that does not exist yet.

3. **One word cannot serve three layers when the design's own thesis is that
   one instrument cannot.** vision.md deliberately splits credit into
   reputation, compute credit, and the fiat rail *because* conflation is
   dangerous — then names all three "credit". Splitting the words follows the
   mechanism instead of undoing it in the reader's head.

4. **It invites exactly the question the visual rails ban.** "Credit" prompts
   "what's my credit balance?", and a balance is a number without a
   derivation — V5, V6 and the xuz rails exist to prevent that screen. Killing
   the noun kills the question upstream of the design.

5. **"Compute credit" is the honest exception and should be kept.** At M3 it
   *is* a credit in the plain, pre-crypto, phone-plan sense: a metered claim on
   agent-hours the network actually has, denominated in the thing it is backed
   by. The compound is self-limiting — nobody reads "compute credit" as a
   holding — and it is the only place where a substitute word would be less
   accurate. Never render it as a balance; render it as metered hours.

6. **Cost asymmetry.** Renaming now costs one search-and-replace across
   unshipped copy. Renaming after the manifesto is quoted costs a rebrand plus
   an explanation of the rebrand — and "they renamed their credits" is itself a
   crypto-shaped story.

**What we are *not* doing:** we are not scrubbing "credit" from `doc/`.
vision.md's internal use is precise and its readers are us. The standard's
scope boundary (§0) already exempts internal documents, and pretending
otherwise would trade a real gain in public clarity for a fake one in
consistency. A follow-up issue should add a one-line vocabulary note to
vision.md mapping its internal "credit" to the public terms above, so the
manifesto author never has to guess.

**Enforcement:** `banned-words.txt` §8 bans the wallet-grammar compounds
outright (`your credits`, `credit balance`, `earn/spend/buy credits`,
`credit multiplier`) and marks bare `credits?` review-required — so an author
who genuinely needs "compute credit" writes one waiver and everyone else is
pushed to the accurate word.

**If the launch strategist rejects this:** the fallback is *keep "credit",
defuse it in the manifesto* — which requires a defusing sentence resident on
every surface that uses it (crop test: a cropped "credit" with no defusing
sentence is a wallet). Note that this makes the honesty of each surface
caption-dependent, which is the exact property xuz deleted the dilution band
for. That asymmetry is why the recommendation is to rename.
