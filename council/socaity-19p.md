# Council: socaity-19p — Pricing heterogeneous M0–M2 contributions with no market: valuation rule and the founder rate-setting conflict

Participants: mechanism-designer, community-builder, legal-counsel
Type: decision · Priority: P1 (elevated in practice: HARD M0 precondition per socaity-x8o — no first external ledger entry until V is final) · Related: socaity-bgl (declare the founder rate before the first grant budget) depends on this.

Issue:
- Context: sustainability.md "The backbone" records founder labor at a publicly declared rate, and M0–M2 contributions (manifesto edits, design docs, code, outreach) hit the ledger before any market or verification mechanism exists to price them. The founder both sets the rate schedule and is the largest epoch-share beneficiary — the exact "founder-tuned parameters that move founder income" conflict sustainability.md itself names.
- Question: (a) What is the valuation rule for heterogeneous pre-market contributions — a published rate card per contribution class, time-based at declared rates, or negotiated-per-entry with public reasoning? (b) What commitment device constrains the founder as price-setter — rate changes apply only prospectively, a cap on founder share per epoch, or third-party attestation of rates?
- Why it matters: Regressional Goodhart — credit for estimated value pays estimation error, and at M0 the estimator is the conflicted party. The manifesto's credibility with exactly the M0 cohort (people who read incentive designs critically) depends on this being visibly solved.

Adopted context binding this council (do not relitigate):
- socaity-x8o: conversion schedule V (versioned code) maps native units → valuation units, 1 vu = 1 standard contributor-hour; founder rate = V applied to founder hours, same table as everyone, citing a verifiable external referent; V fixed per epoch before it opens, amendable only for unopened epochs via the meta-rule; accrual is a pure function of a confirmed past observation. EpochOpened(1) — and therefore the first external entry — is mechanically blocked until V contains no placeholder rates.
- socaity-zjr: all entries provisional; pre-distribution audit; challenge process with enumerated grounds incl. misrepresented capacity.
- socaity-1ux: founder on the identical rule at a declared rate (uniformity covenant); parameters amendable prospectively only; epoch parameters immutable once the epoch opens.
- Remaining scope for THIS council: the shape of V's rate card for heterogeneous contribution classes, the observation units for non-timed work (is a design doc "hours"? attested how?), and the founder-conflict commitment device beyond what is already adopted.
