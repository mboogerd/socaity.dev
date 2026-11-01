# M1–M2 grant work packages

This is the reviewer-facing decomposition of [M1 and M2](milestones.md). Each
package has one accountable outcome, a linkable acceptance artifact, and a
budget line. The amounts are planning estimates in EUR, not a funding promise;
they include implementation, review, documentation, and release work. Packages
are independently reviewable, but the dependency column makes the critical path
explicit.

The plan keeps M1 and M2 separate: M1 proves that one developer can turn a
repository backlog into a useful needs graph, while M2 proves that public
software data can produce a reproducible, actionable observatory. M2 can start
with the data contract and source adapters while M1 is still in progress.

## M1 — single-player graph tool

**Milestone outcome:** a stranger uses the tool on their own GitHub repository
for backlog triage and roadmap planning, without needing a network of users.

| ID | Work package and verifiable deliverable | Acceptance evidence a reviewer can inspect | Depends on | Budget | Duration |
|---|---|---|---|---:|---:|
| M1.1 | **Capture and graph schema.** Define the input contract for a desired change, permanent node identity, AND/OR edges, alternatives, estimates, and provenance; ship a CLI that writes a valid graph. | Schema and examples in `graph/`; validator fixture suite; `python tools/...` command documented and reproducible from a clean clone. | — | €7,500 | 1 month |
| M1.2 | **Agent decomposition runner.** Turn one captured need into a proposed decomposition with explicit alternatives, dependencies, estimates, and provenance labels. | Three fixed golden cases plus their expected structural properties; repeat-run report showing variance and a human-reviewable proposal artifact. | M1.1 | €9,000 | 1.5 months |
| M1.3 | **Review and correction loop.** Make proposals contestable: accept, reject, edit, merge, or link equivalent nodes while preserving history and author attribution. | End-to-end fixtures for accept/reject/edit/merge; rendered before/after artifact; ledger-eligible provenance remains intact after correction. | M1.1, M1.2 | €6,500 | 1 month |
| M1.4 | **Estimation and dependency view.** Render a focused roadmap view that explains blockers, alternatives, estimate intervals, and the next actionable leaves without hiding unresolved edges. | Static HTML generated from fixture data; keyboard/CSS-off checks; screenshots or HTML snapshots for a root problem, a blocker, and competing approaches. | M1.1, M1.3 | €6,500 | 1 month |
| M1.5 | **GitHub issue ingestion.** Import issues, labels, links, and discussion provenance from a repository into the graph without making GitHub identity the graph identity. | Offline fixture repository plus import manifest; idempotent second import; mapped issue URLs and a report of ambiguous matches requiring review. | M1.1, M1.3 | €8,000 | 1.5 months |
| M1.6 | **Single-player release and evaluation.** Package the tool, document the clean-clone path, and test it with independent repositories and users against the M1 done-when. | Versioned release; two external-repository replay reports; usability protocol and results; a stranger can reproduce the graph and identify a blocker from the published artifact. | M1.2–M1.5 | €10,500 | 1.5 months |
|  | **M1 total** |  |  | **€48,000** | **~6 months elapsed with overlap** |

M1.2 and M1.5 may proceed in parallel after M1.1. M1.4 can use fixture data
before ingestion is complete. M1.6 is the release and evaluation gate, not a
request to accept a claim based only on a demo.

## M2 — commons observatory

**Milestone outcome:** publish a reproducible index of foundational,
under-supported software on real public data, and make at least one result
useful to people the project did not recruit directly.

| ID | Work package and verifiable deliverable | Acceptance evidence a reviewer can inspect | Depends on | Budget | Duration |
|---|---|---|---|---:|---:|
| M2.1 | **Open data contract and provenance ledger.** Specify canonical package/project identity, version and edge semantics, source timestamps, licence/ToS notes, missingness, and refresh rules. | Versioned schema; provenance examples for npm, PyPI, Maven, and GitHub; fixture validation and a data-source decision log. | M1.1 | €6,000 | 1 month |
| M2.2 | **Dependency graph ingestion.** Build source adapters and a deterministic merge pipeline for public dependency graphs from npm, PyPI, Maven, and GitHub. | Reproducible sample snapshot; adapter tests; duplicate/redirect report; rerunning the same snapshot yields byte-identical graph output. | M2.1 | €10,000 | 2 months |
| M2.3 | **Funding-signal join.** Join support signals such as GitHub Sponsors, Open Collective, and OpenSSF criticality without publishing unsupported personal or financial inferences. | Source-by-source join specification; privacy/terms review record; fixture with missing, conflicting, and stale signals; coverage report. | M2.1, M2.2 | €7,000 | 1.5 months |
| M2.4 | **Foundationalness computation.** Implement the published measure, including OR-branch weighting, decay, reliability, and missing-data behavior, using integer/rational deterministic arithmetic where applicable. | Formal method note; golden vectors; reproducibility hash; sensitivity report for one fabricated edge, need-splitting, and support-signal perturbation. | M2.2, M2.3 | €10,000 | 2 months |
| M2.5 | **Actionable public index.** Publish the ranked observatory with source links, confidence/coverage limits, “why this node” explanations, and an export that an agent can consume. | Versioned static release; top-result drill-downs from source data to score; machine-readable export; accessibility and link-check reports. | M2.3, M2.4 | €7,000 | 1.5 months |
| M2.6 | **External validation and refresh operation.** Run a documented refresh, invite independent review, and record whether an uncontacted maintainer, funder, or researcher cites or uses a result. | Rebuild log from a clean clone; independent review/issues and responses; dated citation or usage evidence; operations runbook with failure and rollback paths. | M2.2–M2.5 | €10,000 | 1.5 months |
|  | **M2 total** |  |  | **€50,000** | **~6 months elapsed with overlap** |

M2.1 and the first M2.2 adapters can start while M1 is in evaluation. M2.4 is
intentionally downstream of the data and provenance contracts: publishing a
ranking before its inputs and attack surface are inspectable would make the
index look more precise than it is. M2.6 is the evidence gate for the milestone,
not a promise that citation can be manufactured by outreach.

## Budget and review rules

- The two milestone totals are separate envelopes: **M1 €48,000** and
  **M2 €50,000**. They are compatible with a first-grant ceiling in the current
  funding notes, but the target programme and ceiling must be re-checked before
  submission ([funding calendar](funding-calendar-2026.md)).
- A package is complete only when its acceptance artifact is public or
  reproducible from a clean clone, its limitations are recorded, and a reviewer
  can verify the result without trusting a private demo.
- Duration is elapsed calendar time with overlap, not a promise that one person
  can deliver every package simultaneously. A grant application should convert
  these lines into the funder's required person-month and rate format.
- Packages that touch third-party data must retain source terms, licence, and
  privacy evidence beside the snapshot. If that evidence is unavailable, the
  adapter is not accepted merely because the code works.
