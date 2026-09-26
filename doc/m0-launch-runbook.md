# M0 launch runbook

The launch announcement is gated on the following pre-launch checks:

- [ ] The [external-contributor criteria and disclosure pledge](pre-launch-external-contributor-criteria.md)
      is present and its SHA-256 digest matches the
      `commitment.precommitted` event in the ledger.
- [ ] The genesis prologue is complete and the claim path is passing its
      automated checks.
- [ ] M0 is announced only after the first valid non-founder
      `attribution.claimed` event. An unclaimed escrow does not satisfy this
      gate.
- [ ] The founder has asked consent before naming the contributor outside the
      ledger, and the public account discloses warm-circle status when relevant.

The criteria document is the source of truth for the first gate. The ledger
event is the immutable commitment; this checklist is the operator's launch
surface.
