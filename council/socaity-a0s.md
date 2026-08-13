# Council: socaity-a0s — Choose licenses now: platform code, graph/ledger data, observatory index

Participants: grant-writer, legal-counsel, platform-engineer
Type: decision · Priority: P1 (blocks socaity-4we, the NLnet application, which must state licenses)

Issue:
- Question: Which license for platform code (AGPL to protect forkability vs Apache for adoption), which for graph and ledger data (ODbL/CC-BY?), which for the M2 index dataset — and does the choice keep the observatory service model (sustainability.md §3: "data forkable; freshness, curation, accountability are not") coherent?
- Why it matters: NLnet applications must state licenses; changing later is expensive; the license is the technical form of the forkability guarantee the vision treats as its capture-check.

Adopted context:
- Forkability is executable (wg8 CI; fork = clone + one command; renderer travels with data; rule-as-code exportable at all times). Contributions arrive via PR (z61) — contribution licensing/DCO interacts (socaity-g0e covers AI-PR provenance separately).
- Revenue models the licenses must not break: hosted convenience (sustainability §4 — Ghost model: zero proprietary code), observatory sponsorship + fresh-API service (§3), compute margin (§2). Anti-commitment: no proprietary data moat — "the graph and the ledger stay exportable even when commercially inconvenient."
- M2 ingests third-party data (deps.dev, ecosyste.ms, registries) — outbound license must be compatible with inbound terms (socaity-2p5 handles inbound clearance; this council sets the outbound target).
