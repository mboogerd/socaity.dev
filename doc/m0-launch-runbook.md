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

## Checkpoint anchoring

After every checkpoint is appended, export the signed checkpoint event and the
exact ledger digest:

```bash
python3 tools/checkpoint.py export \
  --ledger ledger/chain.jsonl --out checkpoint.json
```

Publish `checkpoint.json` and the `checkpoint_artifact_sha256` printed by the
command to a public mirror outside the project's control (for example, a
Codeberg mirror) and retain the URL in the release or mirror record. Publish
the same artifact to the project's GitHub repository as a second, convenient
anchor. Never edit the artifact after publishing it; export a new checkpoint
instead.

Anyone with a copy of the ledger and the external artifact can verify both the
signed checkpoint and the exact byte-level ledger it attests to:

```bash
python3 tools/checkpoint.py verify \
  --ledger ledger/chain.jsonl --checkpoint checkpoint.json
```

The verifier replays the append-only log, checks the checkpoint signature and
chain position, and rejects changes to either the artifact or ledger. The
external mirror is therefore an observation point, not a trusted custodian.
