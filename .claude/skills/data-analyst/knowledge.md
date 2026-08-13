# OSS ecosystem data — domain knowledge

## Source catalog

| Source | What | Notes |
|---|---|---|
| deps.dev (Google) | Cross-ecosystem dependency graph + API | Best free starting point; npm/PyPI/Maven/Go/Cargo/NuGet |
| ecosyste.ms | Packages, repos, advisories, funding links | Open data + API, built for exactly this kind of analysis |
| OpenSSF Criticality Score | Composite criticality per repo | Known-flawed weights; use as baseline to beat, cite the critiques |
| OSV / GitHub advisories | Vulnerability history | Security incidents as natural experiments in under-maintenance |
| GitHub Sponsors / Open Collective / thanks.dev | Funding signals | Sparse and skewed; absence of funding data ≠ absence of funding (corporate employment is invisible) |
| Libraries.io dataset | Historical SourceRank | Stale but useful for longitudinal decay studies |
| CHAOSS metrics | Community-health definitions | Vocabulary and legitimacy; cite their definitions where compatible |

## Metric pitfalls (each one has embarrassed a published ranking)

- **Transitive double-counting**: naive transitive dependents explode on
  utility packages; a leftpad-alike outranks OpenSSL. Weight by *unique
  reverse-dependency trees* or use PageRank-family damping, and say so.
- **Dev vs runtime dependencies**: test-only deps inflate criticality.
  Separate them; ecosystems differ in how honestly they're declared.
- **Monorepo distortion**: one repo, 200 packages (babel, aws-sdk) — decide
  package-level vs project-level identity *before* computing anything.
- **Download counts are garbage**: CI dominates, mirrors distort, npm
  weekly downloads are trivially inflatable. Never rank on them; if shown,
  show as context only.
- **Bus factor naivety**: commit-count concentration misses corporate teams
  rotating through one bot account, and misses the maintainer who reviews
  everything but commits little. Triangulate: commits + reviews + release
  authorship.
- **Funding false negatives**: a package with zero Sponsors but a
  maintainer employed by Google to work on it is *not* under-supported.
  This is the #1 way the index gets publicly dunked on. Mitigation: detect
  corporate-affiliated maintainer activity (commit email domains, org
  membership) and mark support as "unknown", never "zero", when signals
  conflict.

## The foundationalness-vs-support quadrant

- X: support (funding signals + active maintainer capacity, with the
  false-negative mitigations above).
- Y: foundationalness (damped reverse-dependency value; later, the vision's
  full centrality measure — coordinate with `mechanism-designer` so the M2
  index and the platform's subsidy signal are the *same* computation,
  which is the whole dogfooding point).
- The publishable artifact is the top-right-to-bottom-left *diagonal*:
  high-foundationalness, low-support. Publish the top N with per-item
  evidence dossiers, not just scores — every item will be challenged.

## Credibility checklist before the index goes public

- [ ] Methodology document published alongside, with known limitations.
- [ ] Every top-20 entry hand-reviewed against the false-negative list.
- [ ] Maintainers of listed projects contacted *before* publication
      (coordinate with `community-builder`) — being listed as "under-
      supported" without warning reads as an attack; with warning it reads
      as advocacy.
- [ ] Historical validation: does the index retro-predict known crises
      (xz, log4j, core-js, event-stream, colors/faker)? That backtest *is*
      the press story.
- [ ] Data and code released with the index (forkability is the brand).

## Prior-art positioning

Libraries.io proved the data was collectable and went dormant — sustain-
ability of the observatory itself matters (grant-funded operation, see
`grant-writer`). Criticality Score proved a composite metric draws critique
of weights — publish sensitivity analysis. CHAOSS proved definitions earn
legitimacy — reuse their vocabulary. The differentiator is closing the
loop: rank → point an agent at it → show the PR. Nobody else closes it.
