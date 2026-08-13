# Council: socaity-6kb — OR-branch probability display at M1: provenance and rendering before any market exists

Participants: product-designer, agent-engineer, mechanism-designer
Type: research · Priority: P1

Issue:
- Question: At M1 the decomposer produces branch_probability estimates (sbb: scalar in [0,1], provenance + expires_at) but no market or contest mechanism validates them. How are OR-branch weights rendered in the M1 tool — numerals, buckets, or ranks — such that agent-guessed probabilities never read as mechanism-produced truth?
- Why it matters: fake precision is a trust leak (z61); but the decomposer's relative weighting is genuinely useful triage signal.

Adopted context (most of the answer exists — this council fixes the M1 rendering rule):
- sbb: branch_probability stored as scalar with mandatory provenance; weights never displayed without provenance + freshness chip.
- z61 (M0): "no probability decimals — no mechanism produces them honestly yet; plain-language weights ('currently favored', 'open')".
- aea: solution-shaped ingestion renders one authored solution + an actionable null branch; 0vv lazy.
- xuz register rule: evaluations of the published rule at provisional inputs share one verbal register ("computed, not a projection").
- 36f (open, P2): declared vs market-based weights and pricing losing branches — the MECHANISM question stays there; this council is display-only.

## Round 1 (single-round convergence)

### [product-designer]
Buckets, not numerals, not bare rank-order. Numerals promise unearned precision (z61's trust-leak argument survives M1 — a per-run scalar is still an agent's guess, just fresher); pure rank-order throws away magnitude the triage user wants. Four labeled buckets by fixed documented thresholds, never shown: "favored" (≥0.6), "contested" (0.4–0.6), "long shot" (0.15–0.4), "speculative" (<0.15). Bucket = pure function of the stored scalar; the scalar stays in storage and API, never in the UI. Every chip carries provenance ("estimated by decomposer, run <id>") + freshness; a stale weight decays to "unweighted", never showing old confidence. The M0 rule extends, not changes.

### [agent-engineer]
The scalar at M1 is a relative preference elicited from a model, NOT a calibrated probability — no resolution data, no scoring rule, no eval. Calling it a probability in the UI is evaluation theater; buckets claim only ordinal-plus-coarse-magnitude, roughly what the model can honestly deliver. Addition: log raw scalars per run so calibration is measurable when outcomes exist. RED LINE: no numeric probability surfaces user-facing until a calibration eval exists. CONSENT.

### [mechanism-designer]
Real anchoring concern: displayed weights become focal points; when 36f's market arrives, early prices gravitate toward what the UI trained users to believe. Bucketing mitigates (coarse anchors are weaker anchors); residual risk acceptable because the triage value is real. Conditions: (1) thresholds fixed before anyone can profit from moving a branch across one; (2) market-derived weights (36f) must be visually DISCONTINUOUS with these chips — never a "more precise" version. RED LINE: never blend agent-guessed and market-produced weights in one visual channel. CONSENT.

## Resolution

ADOPTED by consent, Round 1 (narrow display rule; all conditions mutually compatible).

**M1 OR-branch weight display:** four fixed-threshold buckets (favored / contested / long shot / speculative), derived as a pure function of the stored scalar; thresholds documented, never rendered; raw scalar never user-facing until a calibration eval exists (raw scalars logged per run for future calibration measurement); every chip carries decomposer provenance + freshness; stale → "unweighted", never aged confidence; thresholds fixed before anything economic can profit from bucket boundaries; when market weights arrive (36f) they get a visually discontinuous channel — agent guesses and market prices never share a visual language.
