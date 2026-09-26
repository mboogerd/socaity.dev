# External-contributor criteria and disclosure pledge

This document is the founder's pre-launch commitment for the first external
contribution. Its SHA-256 digest is recorded by the ledger as a
`commitment.precommitted` event before the launch announcement.

## Criteria

The first external contribution is the first ledger entry whose
`attribution.claimed` event:

1. is valid against an earlier escrow accepted by the founder;
2. carries a contributor key whose lineage is not one of the founder key
   lineages; and
3. passes the published claim-binding and attestation checks.

The underlying work must be a real contribution accepted through the published
GitHub or courier path. A founder-created, founder-controlled, staged, or
solicited entry does not qualify merely because it uses a different key.
Warm-circle participation is allowed, but it is not described as independent
or as a stranger contribution.

## Disclosure pledge

Before naming the contributor outside the ledger record, the founder will ask
for explicit consent. Any public account of the first contribution will say
whether the contributor was from the founder's warm circle. The founder will
not claim that a warm-circle entry was an unsolicited stranger contribution,
and will not announce M0 as complete until the first valid non-founder
`attribution.claimed` event exists.

This pledge is committed before launch; later commentary cannot rewrite the
criteria or erase the warm-circle disclosure.
