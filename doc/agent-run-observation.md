# Agent-run observation manifest

This is the minimum provenance record emitted by an agent run that produces
graph work. It is designed for M0/M1 BYO-agent tooling and is the payload for
the future additive `agent.run_observed` ledger observation type. The manifest
records what can be checked without pretending that a local agent's token
counter or model identity is independently trusted.

## Contract

The manifest is a mapping with exactly these fields in schema version 1:

| Field | Required shape | Meaning |
| --- | --- | --- |
| `schema` | `1` | Manifest format. Unknown versions are rejected. |
| `run_id` | non-empty stable string | Caller-chosen identifier for this run; unique within the submitting actor's run history. |
| `model` | non-empty string | Model name as reported by the agent client. It is descriptive, not proof of model identity. |
| `prompt_hash` | `sha256:<64 lowercase hex>` | Digest of the exact prompt/context envelope supplied to the agent. Prompt text is never included. |
| `started_at` | UTC RFC 3339 timestamp | Run start time. |
| `finished_at` | UTC RFC 3339 timestamp | Run completion time; must not precede `started_at`. |
| `input_digest` | `sha256:<64 lowercase hex>` | Digest of the input artifact set (for example, the repository snapshot and context pack). |
| `output_digest` | `sha256:<64 lowercase hex>` | Digest of the output artifact set submitted for validation. |
| `tokens` | mapping of non-negative integers | Self-reported `input`, `output`, and `total` counts. `total` must equal `input + output`. |
| `attestation` | `self-reported` or `platform-verified` | Evidence tier for the measurements. M1 BYO runs use `self-reported`. |
| `verifier_signature` | `null` or a verifier-defined signature object | Reserved slot for a future verifier receipt. It is `null` for self-reported runs. |

The canonical field order for hashing and signing is the lexicographic order
shown by RFC 8785 canonical JSON. YAML is only a human-friendly transport;
producers must convert it to the canonical JSON form before hashing.

Example:

```yaml
schema: 1
run_id: run-2026-08-03T140500Z-0001
model: claude-code
prompt_hash: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
started_at: '2026-08-03T14:05:00Z'
finished_at: '2026-08-03T14:08:12Z'
input_digest: sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
output_digest: sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
tokens:
  input: 12000
  output: 1800
  total: 13800
attestation: self-reported
verifier_signature: null
```

## Privacy and evidence rules

- Prompt, context, output, source files, and token text are not ledger fields.
  Their digests allow equality checks without publishing potentially sensitive
  content; the artifacts may be retained by the contributor under their own
  access policy.
- Timestamps are operational metadata, not a claim that the agent worked
  continuously for the elapsed interval. Wall-clock duration is derived, never
  substituted for tokens.
- A BYO-agent client may report a model and token count, but the platform must
  label both as self-reported. It must not turn those values into compute
  credit, burn-rate settlement, or value-unit accrual at M1.
- `platform-verified` is reserved for a future path that can observe the
  relevant measurement without requiring server-side custody of a user's API
  key. The ordering to investigate is client-side evidence first, then a
  transit-only proxy, with server custody as a last resort after identity and
  abuse controls exist.
- A non-null `verifier_signature` is meaningful only when the corresponding
  verifier and key are published with the observation. A signature does not
  make the model claim or the output's real-world usefulness true; it only
  authenticates the verifier's statement.

## Validation and ledger boundary

The M0/M1 submission gate validates the shape, digest syntax, timestamp order,
token arithmetic, and that the output artifact is the one being submitted. It
also preserves the manifest unchanged so the run can be audited later.

The manifest is provenance, not an accrual event. In particular:

1. A self-reported manifest may be stored and rendered with its attestation
   label, but contributes zero value units.
2. A future platform-verified manifest still uses this same shape; only the
   attestation value and verifier slot change. No migration or second manifest
   type is introduced.
3. Conversion from verified capacity to value units requires a separately
   published rate and ledger rule. This document does not create that rate.

The eventual ledger event is additive to the frozen v1 catalog. Until that
event type and its validator predicates are adopted in a new ledger version,
the manifest remains an off-chain submission artifact and must not be smuggled
into `work.logged` or another accrual-bearing event.
