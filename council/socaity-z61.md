# Council: socaity-z61 — Roadmap-as-graph medium at M0: how do believers contest edges before M1 tooling exists

Participants: community-builder, platform-engineer, product-designer
Type: research · Priority: P0 · Related: blocks socaity-ipg (first-contribution path); the M0→M1 retention mechanism

Issue:
- Context: milestones.md M0 requires the roadmap as the first needs graph, in the platform's own conventions, before any M1 tool exists; the graph doubles as what manifesto believers *do* between M0 and M1 (engagement + dogfooding).
- Question: What is the concrete M0 medium and workflow for reading the roadmap graph and contesting its edges — how does a stranger browse it, propose a node, dispute an edge, and see the live state — with zero platform tooling built?
- Why it matters: M0's retention depends on believers having structural work; the first contested edge is the first proof the conventions work.

Adopted context binding this council (do not relitigate):
- socaity-sbb: graph = one YAML per node in graph/nodes/ (schema:1, permanent n- IDs, slug sugar pinned at merge, edges inline in source node's file as refines/requires/equivalent_to records with provenance, estimates append-only, mandatory provenance block incl. human writes, CI validation); git history = M0 event log; PR diffs = the contestation record at N=1 (socaity-5u4: edit-with-history, dispute ceremony reserved for M4).
- socaity-7mk: contributor identity = keypair; GitHub linkage = revocable off-ledger attestation.
- socaity-19p/zjr: accepted graph contributions are ledger-eligible (0.5 vu floor, tickets for larger work).
- Prior recommendation on this issue (product-designer comment): static focus+context read view rendered from repo data; PR/issue-based edge contestation.
- Remaining scope: the reader experience (static site generation from graph/ files — what exactly renders at M0), the contest workflow mechanics (PR templates? who merges? how does "contested" show?), the contributor-facing conventions doc, and how this stays honest with sbb's status lifecycle.
