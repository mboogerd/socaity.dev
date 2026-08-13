# Council: socaity-zyt — Ledger event schema v1: observations vs valuations, hash chain, versioning

Participants: platform-engineer, mechanism-designer
Type: decision · Priority: P0 · Blocks the M0 done-criterion (first external ledger entry)

Issue:
- Question: Define ledger event schema v1: content-addressed hash-chained entries with explicit version field; strict separation of observation events (immutable) from valuation events (replayable with new parameters); what observation types must exist from entry #1 so M5 replay finds no gaps; which observations the epoch-share math requires.

Adopted context binding this council (do not relitigate — most of v1 is already fixed):
- socaity-7mk: actor_key = multibase z6Mk Ed25519; sig over canonical serialization; no PII/free text on-ledger (validator-enforced); evidence hash-only; key lifecycle events key.successor_designated / key.rotated / key.rebound; off-ledger erasable profile/link/evidence tables.
- socaity-x8o: rule/meta-rule events RuleVersionPublished, MetaRulePublished, EpochOpened(e, rule_version_hash), EpochClosed(e, checkpoint_hash); canonical JSON (RFC 8785-style); payout-table hash is a ledger event; epoch-assignment clamp; mode election lives in the immutable observation; exact rationals, no floats; genesis anchors epoch clock; epoch 0 = itemized founder position opened+closed at genesis.
- socaity-zjr: status-change entries (provisional → confirmed/discounted) are signed public entries citing evidence; challenges recorded on-ledger with stakes escrowed (reputation-only).
- socaity-19p: observations declare native units + category enum; timed work = worklog attestations; artifact work = ticket events (opened-with-tier, accepted); floor rule; attestation-of-V statement gates EpochOpened.
- Remaining scope for THIS council: the complete event-type catalog for v1 (any gaps beyond the adopted events?), the envelope (hash chain, version field, canonical form, signing), the observation/valuation boundary as schema discipline, and checkpoint mechanics.
