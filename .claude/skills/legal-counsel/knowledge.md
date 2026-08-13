# Legal — domain knowledge (EU/NL focus)

Not legal advice; a map of what to analyze and when to buy real counsel.

## Characterization of the credit layers

- **Reputation**: non-transferable, non-redeemable → lowest risk. Keep it
  that way; transferability is the cliff edge.
- **Compute credit** (closed-loop claims on network agent-hours):
  closed-loop instruments redeemable only in services on the issuing
  platform generally fall outside e-money definitions (EMD2: e-money =
  claim on issuer, accepted by *third parties*). Two triggers to watch:
  (1) fiat off-ramp (explicitly deferred — good; the *moment* it opens,
  redeemability analysis changes), (2) transferability between users +
  a secondary market = de facto exchange token → MiCA territory even
  without issuing a "token".
- **Epoch shares**: claims on future inflows distributed pro-rata to
  contribution. Risk: participation-right/security characterization
  (profit-sharing certificate analogy). Mitigants to design in: earned by
  work (not purchase), non-transferable, distributions discretionary until
  declared. The standing commitment's wording matters enormously — "we
  commit to distribute" vs "we intend to distribute" changes the analysis.
  Buy real counsel on this text before M0 publishes it. NL angle: AFM
  guidance on profit-sharing instruments; avoid anything resembling
  deposit-taking (Wft).
- **The framing that helps**: retroactive *grants* to past contributors
  (RetroPGF precedent) reads very differently from *entitlements*. Keep
  founder communications disciplined; marketing language gets quoted in
  characterization disputes.

## The fiat rail (M5, but groundwork earlier)

- Platform escrows money attached to nodes, settles to contributors →
  prima facie money remittance / payment service (PSD2 Annex I). Options,
  cheapest first:
  1. **Licensed PSP partner** holds and settles funds (Stripe Connect,
     Mangopay, Opp — the marketplace-payments pattern). Platform never
     touches the money flow; this is how most EU marketplaces avoid
     licensing. Strong default.
  2. Commercial-agent exemption (PSD2 art. 3(b)) — narrow, DNB reads it
     strictly for two-sided platforms; do not rely on it without advice.
  3. Own PI license — years and capital; only if the platform's scale ever
     justifies it.
- Grants/bounties/sponsorships settling to contributors also raise:
  withholding obligations, VAT on platform fee (take rate is a service fee
  → VAT-able), DAC7 reporting for platform operators paying sellers/
  service-providers in the EU. DAC7 applies well before M5 feels "big".

## Entity staging

- **Now (M0–M2)**: operate as eenmanszaak or single BV. BV preferred once
  grants land (limited liability, clean grant counterparty, VAT identity).
  Cheap, reversible.
- **The split (named in sustainability.md)**: stichting (foundation) owns
  mechanism/ledger/parameter-tuning; BV sells hosting/compute/reports.
  Dutch precedent is rich (this is the Blender structure). Trigger
  conditions to watch: first employee paid from take-rate revenue, or
  founder income visibly coupled to parameters the founder tunes.
  Stichting has no members/shareholders — governance design (board
  composition, community accountability) is the real work; forkability
  remains the backstop.
- Grant compatibility: NLnet/NGI contracts fine with individuals or BVs;
  STF contracts with the maintaining entity — check each funder's
  requirements before incorporating around them.

## Contributor compensation

- Ledger entries at declared rates + later distribution: at distribution
  time this is income to recipients (NL: likely row income / winst uit
  onderneming depending on status); platform may have reporting duties
  (DAC7 again). Cross-border contributors = their local tax problem, but
  the platform should issue annual statements from day one — the ledger
  makes this nearly free; do it.
- Regular contributors paid in epoch shares: watch employment-relation
  factors (NL: wet DBA / deemed employment) — self-directed choice of
  nodes and own tooling are helpful facts; instruction-authority is the
  danger factor. The self-directed design is genuinely protective here.

## GDPR posture (with `identity-specialist`)

- Personal data off-ledger; ledger holds pseudonymous facts only. Legal
  basis mapping per processing purpose; DPIA required before M4 (large-
  scale processing, potentially sensitive demand data).
- Demand data on health/family/finance can be special-category even when
  pseudonymous — design so the platform stores need *content* separated
  from any identity linkage, with the linkage user-held.

## Risk register seed (blocking / material / monitor)

- Blocking before M0: epoch-share commitment wording review.
- Material before M2: entity for grant contracts; VAT registration.
- Material before M3: contributor statements process; DAC7 assessment.
- Material before M5: PSP partner selection; full credit-characterization
  opinion; DPIA refresh.
- Monitor: MiCA guidance evolution, EUDI wallet rollout, wet DBA
  enforcement practice.
