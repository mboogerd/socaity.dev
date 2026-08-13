"""The closed, per-version event catalog (socaity-zyt resolution).

CATALOGS[v] maps every admissible event type to its payload schema.  A type
absent from the catalog for the claimed `v` is rejected at append time; a
payload field absent from the schema is rejected too.  The catalog is
additive-only: v1 is frozen, new types/fields arrive under a new version.

Field kinds are all machine-checkable -- there is no "string" kind, which is
how the no-free-text and hash-only-evidence paramounts are enforced
structurally rather than by review.
"""

# --- field kinds -----------------------------------------------------------
# hash      64 lowercase hex characters (SHA-256 digest)
# id        event_id: a hash, or the 64-zero genesis predecessor
# key       multibase z6Mk Ed25519 public key
# key?      key or null (contributor-nullable acceptance, socaity-ipg)
# int       non-negative integer
# rational  {"num": int, "den": int}, den > 0
# unit      rational additionally bounded to [0, 1] (discount factors)
# week      ISO week "YYYY-Www"
# hashes    non-empty list of hash (evidence is hash-only, always)
# ids       list of id
# enum:X    member of V["enums"]["X"] (closed enums, versioned in V)

GENESIS_PREV = "0" * 64

ZERO_ENUMS = {
    "category": ["code", "review", "docs", "ops", "design", "governance"],
    "unit": ["hours"],
    "mode": ["E", "A"],
    "tier": ["T1", "T2", "T3"],
    "currency": ["EUR", "USD"],
    "close_reason": ["rejected", "withdrawn", "expired"],
    "grounds": ["overstated_quantity", "miscategorisation", "misattribution",
                "evidence_unresolvable", "duplicate"],
    "challenge_outcome": ["upheld", "dismissed"],
    "review_outcome": ["clean", "finding"],
    "status": ["confirmed", "discounted", "withdrawn"],
}

# type -> (class, required fields, optional fields)
#   class "G" = governance, "O" = observation.  There are zero valuation types.
V1 = {
    # --- governance --------------------------------------------------------
    "genesis": ("G", {"rule_version_hash": "hash", "meta_rule_hash": "hash",
                      "checkpoint_key": "key", "L": "int"}, {}),
    "rule.version_published": ("G", {"rule_version": "hash", "source_hash": "hash",
                                     "params_hash": "hash"}, {}),
    "rule.meta_published": ("G", {"meta_rule_hash": "hash"}, {}),
    "V.draft_published": ("G", {"draft_hash": "hash"}, {}),
    "rule.attested": ("G", {"rule_version_hash": "hash", "epoch": "int",
                            "statement_hash": "hash"}, {}),
    "epoch.opened": ("G", {"epoch": "int", "rule_version_hash": "hash"}, {}),
    "epoch.closed": ("G", {"epoch": "int", "checkpoint_hash": "hash"}, {}),
    "distribution.declared": ("G", {"distribution_id": "hash", "amount_minor": "int",
                                    "currency": "enum:currency",
                                    "cutoff_checkpoint_hash": "hash"}, {}),
    "distribution.table_published": ("G", {"distribution_id": "hash",
                                           "table_hash": "hash"}, {}),
    "audit.completed": ("G", {"distribution_id": "hash",
                              "scope_checkpoint_hash": "hash",
                              "report_hash": "hash"}, {}),
    "audit.review_opened": ("G", {"review_id": "hash", "target_event_id": "id"}, {}),
    "audit.review_closed": ("G", {"review_id": "hash",
                                  "outcome": "enum:review_outcome"}, {}),
    "checkpoint.published": ("G", {"checkpoint_seq": "int", "head_event_id": "id",
                                   "event_count": "int",
                                   "prev_checkpoint_ref": "id"}, {}),
    "ticket.closed": ("G", {"ticket_id": "hash", "reason": "enum:close_reason"}, {}),
    "challenge.filed": ("G", {"challenge_id": "hash", "target_event_id": "id",
                              "grounds": "enum:grounds", "stake_ref": "id"}, {}),
    "challenge.responded": ("G", {"challenge_id": "hash", "response_hash": "hash"}, {}),
    "challenge.decided": ("G", {"challenge_id": "hash",
                                "outcome": "enum:challenge_outcome",
                                "discount": "unit"}, {}),
    "challenge.appealed": ("G", {"challenge_id": "hash", "appeal_id": "hash"}, {}),
    "appeal.decided": ("G", {"appeal_id": "hash", "outcome": "enum:challenge_outcome",
                             "discount": "unit"}, {}),
    "entry.status_changed": ("G", {"target_event_id": "id", "from": "enum:status",
                                   "to": "enum:status", "basis_refs": "ids"}, {}),
    "entry.withdrawn": ("G", {"target_event_id": "id"}, {}),
    "stake.escrowed": ("G", {"stake_id": "hash", "weight": "unit"}, {}),
    "stake.returned": ("G", {"stake_id": "hash"}, {}),
    "stake.burned": ("G", {"stake_id": "hash"}, {}),
    # --- observations ------------------------------------------------------
    "key.successor_designated": ("O", {"successor_key": "key"}, {}),
    "key.rotated": ("O", {"new_key": "key"}, {}),
    "key.rebind_requested": ("O", {"orphan_key": "key", "claimant_key": "key",
                                   "evidence": "hashes"}, {}),
    "key.rebound": ("O", {"orphan_key": "key", "rebind_request_ref": "id",
                          "adjudication_ref": "id"}, {}),
    "work.logged": ("O", {"category": "enum:category", "native_unit": "enum:unit",
                          "quantity": "int", "mode": "enum:mode",
                          "evidence": "hashes", "week_ref": "week",
                          "artifact_hash": "hash"}, {}),
    "ticket.opened": ("O", {"ticket_id": "hash", "tier": "enum:tier",
                            "category": "enum:category", "spec_hash": "hash"}, {}),
    "ticket.accepted": ("O", {"ticket_ref": "id", "ticket_id": "hash",
                              "contributor": "key?", "attested_micro_hours": "int",
                              "mode": "enum:mode", "category": "enum:category",
                              "evidence": "hashes", "artifact_hash": "hash",
                              "week_ref": "week"},
                        {"claim_binding": "hash"}),
    "contribution.trivial_accepted": ("O", {"contributor": "key?",
                                            "category": "enum:category",
                                            "mode": "enum:mode",
                                            "evidence": "hashes",
                                            "artifact_hash": "hash",
                                            "week_ref": "week"},
                                      {"claim_binding": "hash"}),
    "attribution.claimed": ("O", {"escrow_ref": "id", "claim_binding": "hash",
                                  "attestation_hash": "hash"},
                            {"adjudication_ref": "id"}),
}

CATALOGS = {1: V1}

#: Observations that carry accrual weight -- MD's mandatory-field list in
#: socaity-zyt round 1 section A applies to exactly these.
ACCRUAL_TYPES = ("work.logged", "ticket.accepted", "contribution.trivial_accepted")

#: Fields whose presence is checked as its own named predicate
#: (provenance completeness), beyond ordinary schema-required checks.
ACCRUAL_MANDATORY = {
    "work.logged": ("category", "native_unit", "quantity", "mode", "evidence",
                    "week_ref", "artifact_hash"),
    "ticket.accepted": ("ticket_ref", "category", "mode", "evidence", "week_ref",
                        "artifact_hash", "attested_micro_hours"),
    "contribution.trivial_accepted": ("category", "mode", "evidence", "week_ref",
                                      "artifact_hash"),
}

#: Types that may appear inside the genesis prologue stage that collects the
#: itemised epoch-0 founder position (socaity-zyt / socaity-x8o).
EPOCH0_TYPES = ("V.draft_published", "work.logged", "ticket.opened",
                "ticket.accepted", "contribution.trivial_accepted",
                "key.successor_designated")
