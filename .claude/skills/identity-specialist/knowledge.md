# Identity & proof-of-personhood — domain knowledge

## Mechanism landscape

| Mechanism | Sybil resistance | Exclusion | Privacy | Notes |
|---|---|---|---|---|
| World ID (iris biometric) | Strong | High (orb access; global-south skew in practice) | ZK-proofs, but biometric custody controversy | Reputational risk: crypto association contradicts the no-token brand |
| Government eID (eIDAS 2.0 / EUDI wallet) | Strong in EU | Excludes non-EU + undocumented | Good with ZK selective disclosure; wallet rollout 2026+ | Best EU-native fit; watch member-state rollout pace |
| BrightID / social-graph vouching | Moderate; graph attacks documented | Low tech barrier, high social barrier for isolated people | Pseudonymous | Bootstrap-friendly; degrades under paid vouching |
| Idena (synchronized Turing tests) | Moderate | High (synchronous ceremonies, quirky) | Pseudonymous | Interesting prior art, impractical UX |
| Phone/payment-card verification | Weak (farms exist at ~$0.1–$1/number) | Low | Poor (number linkage) | Fine for M4 personhood-lite, must not gate M5 money |
| Proof-of-humanity (video + deposit + challenge) | Moderate | Moderate | Poor (public video) | Kleros PoH: deposit + challenge game is reusable; public video is not |
| Web-of-trust from *contribution history* | Weak alone vs demand-side Sybils | Low for the platform's own community | Pseudonymous | Good reputation input; never demand-side gate (resource-weighted by construction) |

## Design rules

- **Stage it**: M4 = personhood-lite (phone/eID/vouching, pick per-user —
  a *menu* of attestations each yielding the same "1 person" credential
  reduces exclusion; require harder attestations only when stakes rise).
- **Separate personhood from identity**: the platform needs "this is a
  distinct human, counted once", never "who this is". Anonymous
  credentials (BBS+ signatures, Semaphore-style nullifiers) give exactly
  this: one nullifier per human per context, unlinkable across contexts.
  Per-context nullifiers also stop cross-context correlation of sensitive
  demand (health wishes unlinkable from finance wishes).
- **Receipt-freeness for demand expression** (from MACI, with
  `mechanism-designer`): if a user can prove to a briber how they voted,
  votes become sellable. Design demand signals so they cannot be proven to
  third parties.
- **User-held credentials** (with `platform-engineer`): keys on the user's
  side, platform holds only nullifier registry — this is what makes
  standing portable across forks and is also the GDPR-minimal posture.
- **Revocation and recovery**: humans lose keys. Social recovery or
  re-attestation paths must exist, and each is itself a Sybil vector —
  rate-limit recovery, decay old nullifiers.

## Sybil economics (the budget equation)

Security condition: `cost(fake person) > credit unlocked by one demand-side
identity × time-to-detection`. Demand-side identities unlock *influence*,
not credit directly — the attack is influence → node inflation → colluder
supplies it → credit. So the relevant bound is on the *whole pipeline*;
model it with `mechanism-designer` per milestone. Publish the assumed
attack cost; it is a tunable, not a constant.

## Exclusion audit checklist

For each mechanism ask: no smartphone? no government ID? no bank? not in
EU? disability (biometrics, synchronous ceremonies)? at-risk pseudonymity
needs (activists, health)? Every "excluded" needs a documented alternative
attestation path — the platform's constituency includes precisely the
under-resourced.

## GDPR notes (hand to `legal-counsel` when concrete)

- Biometric personhood = Art. 9 special-category data; avoid custody
  entirely (verify via third-party attestation, store only nullifiers).
- Nullifiers/pseudonyms are still personal data under GDPR; append-only
  ledgers vs right-to-erasure needs design attention: keep personal data
  off-ledger, ledger holds only pseudonymous contribution facts.
