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
