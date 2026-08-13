# Council: socaity-a8o — Key loss and recovery for day-one contributors (remainder)

Participants: identity-specialist, platform-engineer
Type: research · Priority: P1

Already fixed by socaity-7mk: key lifecycle = forward-only ledger events (key.successor_designated repeatable/latest-wins; key.rotated by old key or successor; key.rebound only via zjr adjudication); no privileged mutation; contributions stay with orphaned keys until adjudicated rebinding.
Remaining scope: (a) onboarding UX for successor designation (the /claim flow from ipg creates keys for non-crypto-native contributors — when/how is a successor prompted without adding friction to the 2-minute claim?); (b) recovery as a Sybil/attack vector (rate limits on rotation/rebinding; does frequent rotation launder identity across the concentration tripwire or challenge history?); (c) what the rebind adjudication evidence standard is pre-M3 (queued) and post-M3.

## Round 1 (single-round convergence)

### [identity-specialist]
(a) Successor designation stays OUT of the 2-minute claim (every added concept is a bounce risk) and out of the immediate afterglow (at 0.5 vu the prompt reads as ceremony). Prompt at **first meaningful accrual** (threshold in V; propose: first entry above the floor); the undesignated state is designed, not nagged — same pattern as the unclaimed escrow. (b) **Rate-limit by lineage, not key** — rotation/rebind never reset the concentration tripwire, challenge/withdrawal history, budget-kissing record, or the weekly cap (all lineage-keyed at replay). Limits as V parameters, validator-enforced: 1 rotation/lineage/epoch (excess → adjudication); successor re-designation laxer; a successor/new key already active in another lineage is REJECTED — lineage merges only via zjr, else rotation launders concentration. (c) Pre-M3: rebind requests filed on-ledger with evidence hashes frozen at filing (memory fresh, adjudication deferred, no founder interim rulings); one pending request per orphaned lineage. Post-M3 standard: claimant proves control of pre-loss anchors (GitHub attestation, courier channel, designated successor) — never testimony; notice, 30-day response, one staked appeal. CONSENT.

### [platform-engineer]
Confirmed: replay folds lifecycle events into a lineage id (root key of the chain); tripwire, challenge history, skew tells, weekly cap are valuation-side functions over lineage — rotation resetting them is impossible by construction, not policy. Rate limits are validator predicates (V parameters, checkpoint-bounded — same pattern as the staleness window). Fresh-key rule append-time-checkable. Schema deltas for zyt (additive, v1): **key.rebind_requested** {orphan_key, claimant_key, evidence hashes} so the pre-M3 queue has a type; key.rebound gains rebind_request_ref alongside adjudication_ref. CONSENT.

## Resolution

ADOPTED by consent, Round 1.

**Key recovery (remainder):** successor designation prompted at first meaningful accrual (V threshold), never inside the claim flow; undesignated is a designed state. All audit surfaces (tripwire, challenge history, caps) are lineage-keyed at replay — rotation/rebinding cannot reset them by construction. Validator-enforced V-parameter rate limits: 1 rotation/lineage/epoch, one pending rebind per orphaned lineage, fresh-key rule (no cross-lineage key reuse; merges only via adjudication). Pre-M3 rebinds queue on-ledger with evidence frozen at filing; post-M3 standard = control of pre-loss anchors, never testimony, with notice/response/one staked appeal. Additive schema delta: key.rebind_requested event + rebind_request_ref on key.rebound (→ socaity-mxu/zyt implementation).
