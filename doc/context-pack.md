# Context pack

A context pack is the small, per-node artifact an agent receives when a
maintainer has made a graph node actionable. It describes the target without
turning the platform into a captive runtime: the agent still runs in the
target repository, with the repository's own tools and credentials.

The pack is an additive view of a graph node. It does not replace the node's
permanent ID, body, edges, estimates, or provenance, and it must not rewrite
the source issue. A producer may omit a field only when it records `unknown`
with a reason; an absent field is not evidence that the target has no such
information.

## Contract

The transport is YAML (or the equivalent JSON object) with `schema: 1`:

```yaml
schema: 1
node_id: n-7oxaigycyqpnb7mkj35qhg6hqa
generated_at: '2026-08-03T14:08:12Z'
source:
  external_ref: https://github.com/example/project/issues/42
  snapshot_at: '2026-08-03T14:05:00Z'
need:
  statement: "The generator must preserve source links in its graph export."
  evidence:
    - "Exported graph.json currently drops the source URL."
acceptance:
  criteria:
    - "graph.json contains the source URL for every exported node."
  source: quoted
conventions:
  - kind: contributing
    ref: https://github.com/example/project/blob/main/CONTRIBUTING.md
    observed_at: '2026-08-03T14:05:00Z'
entry_points:
  - command: "python -m pytest"
    purpose: tests
    status: verified
    observed_at: '2026-08-03T14:06:00Z'
verification:
  hooks:
    - command: "python -m pytest tests/test_export.py"
      purpose: acceptance
      status: verified
      observed_at: '2026-08-03T14:06:00Z'
  disclosure:
    attribution: "Source issue and acceptance text remain attributed to the reporter."
    agent_authorship: "Generated fields are labelled as generated."
provenance:
  generated_by: observation-run-0001
  input_digest: sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
```

The names have deliberately boring meanings:

- `node_id` is the graph node's permanent ID. Durable references use this ID,
  never a mutable slug.
- `need.statement` is a concise restatement of the need. `need.evidence` holds
  quoted or hash-addressed source evidence; a producer must not manufacture a
  problem that the source does not support.
- `acceptance.criteria` is the reporter's acceptance shape when one exists.
  `acceptance.source` is `quoted`, `derived`, or `unknown`; `derived` requires
  evidence and must remain visibly distinct from quoted text.
- `conventions` points to repository-owned instructions such as
  `CONTRIBUTING.md`, a formatter configuration, or a directory-specific
  README. Each pointer has an observation timestamp and a `status` of
  `verified`, `unverified`, or `unknown`.
- `entry_points` lists reproducible commands or file paths that orient an agent
  in the target repository. A command is an entry point, not a claim that it
  succeeds; `status` records whether it was run in the captured snapshot.
- `verification.hooks` lists commands, checks, or review actions that can test
  the acceptance criteria. Hooks are advisory until a run records their result.
- `verification.disclosure` keeps source attribution and generated content
  explicit. It must not imply that an agent run proves the change is useful or
  welcome.
- `provenance` binds the pack to the observation run and input snapshot. It is
  separate from the node's assertion provenance and never grants authorship of
  the source issue to the producer.

## Population and rendering rules

The M2 pipeline computes the pack's fields from public repository artifacts and
stores the method, snapshot time, and result for every field. The four
specifiability signals are therefore falsifiable:

1. A need statement is populated only when a source issue or node body exists.
2. Acceptance criteria are populated from explicit criteria, or marked
   derived/unknown; the pipeline does not silently turn a title into a test.
3. Convention pointers resolve to a file or documented repository setting.
4. Entry points and verification hooks are executable or inspectable in the
   captured snapshot, with failures retained as named failures.

Unknown stays unknown. A failed command is not converted into an empty list,
and a missing consent record is not converted into permission to target a
maintainer. Rendering may show facts for outreach research, but a context pack
is an agent-targeting affordance only when the separate consent tier permits
it.

Packs are regenerated when their source snapshot changes. They are not ledger
events and do not accrue value units. A run manifest may identify the producer
and artifact digests, but prompt text, credentials, source contents, and token
text stay outside the pack.

## Compatibility

The format is additive. Consumers must reject an unknown `schema` version,
preserve unknown fields when round-tripping a known version, and fail loudly
when a required field has the wrong shape. A graph node can carry a reference
to the pack or an inline copy; the node ID and the pack's `provenance` make the
association explicit. This keeps M1's graph export sufficient for M3 without
making inference, hosting, or a specific agent client part of the graph
schema.
