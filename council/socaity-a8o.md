# Council: socaity-a8o — Key loss and recovery for day-one contributors (remainder)

Participants: identity-specialist, platform-engineer
Type: research · Priority: P1

Already fixed by socaity-7mk: key lifecycle = forward-only ledger events (key.successor_designated repeatable/latest-wins; key.rotated by old key or successor; key.rebound only via zjr adjudication); no privileged mutation; contributions stay with orphaned keys until adjudicated rebinding.
Remaining scope: (a) onboarding UX for successor designation (the /claim flow from ipg creates keys for non-crypto-native contributors — when/how is a successor prompted without adding friction to the 2-minute claim?); (b) recovery as a Sybil/attack vector (rate limits on rotation/rebinding; does frequent rotation launder identity across the concentration tripwire or challenge history?); (c) what the rebind adjudication evidence standard is pre-M3 (queued) and post-M3.
