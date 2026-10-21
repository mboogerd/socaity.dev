# Governance

This project keeps governance in the open. The repository is the durable
record: decisions are files, moderation is a log, and contested graph edges
carry their own state and references.

## Decision records

Substantive decisions are recorded as one Markdown file under `doc/` or
`council/`. A decision record states the context, the question, the adopted
resolution, dissent or paramount objections, and the date. A pull request is
the review and publication mechanism; after merge, the record is not silently
rewritten. A later change gets a new record that links to the earlier one.

The existing `council/socaity-*.md` records are the canonical examples. Small
implementation choices may be documented in the relevant code or pull request
when they do not change a settled product or governance decision.

## Contested graph edges

An edge is contested through a public, structured sequence:

1. **Claim** — the challenger states which relationship is disputed and gives a
   specific reason. The edge changes from `asserted` to `disputed`; the
   dispute reference points to the public issue or pull request.
2. **Counter-claim** — the original claimant or another participant answers in
   the same public record. Both sides remain visible; a dispute does not delete
   the edge or rewrite its history.
3. **Cool-off** — allow at least 72 hours for evidence and replies before
   resolving the dispute, unless an immediate safety or legal issue requires a
   temporary moderation action.
4. **Resolution** — record the evidence and outcome in the public dispute
   record, then change the edge to `settled` with a resolution reference. A
   settled edge is not silently reopened; a new material claim starts a new
   dispute record.

The machine-readable edge fields are defined by `tools/validate/validate.py`:
`status`, `dispute_ref`, and `resolution`. The allowed state path is
`asserted → disputed → settled`. A dispute is about the relationship, not a
request to erase either node.

## Moderation

The project follows the [Code of Conduct](CODE_OF_CONDUCT.md). Moderation is
graduated: rate-limit or ask for correction before a ban where safety permits.
The founder is the visible, accountable backstop for unresolved reports, not
an invisible veto over ordinary graph disputes. Every moderation action is
recorded in [`MODERATION.log`](MODERATION.log), with private personal details
omitted or redacted.

No one should manufacture a dispute, activity, or consensus for appearance's
sake. If a founder is a participant in a contested edge, the conflict and the
reason for any backstop decision are recorded in the public record.
