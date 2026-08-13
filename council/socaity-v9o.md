# Council: socaity-v9o — Whose tokens run M1 decomposition: BYO agent vs hosted inference vs BYO-key

Participants: agent-engineer, platform-engineer
Type: decision · Priority: P1 · Determines socaity-xt4's remainder (agent-run observation payload + BYO attestation)

Issue:
- Question: Is M1 (a) a skill/CLI running inside the user's own Claude Code (BYO tokens, zero inference cost, limits UX and non-Claude users), (b) hosted with platform-paid inference (real per-repo cost during the grant bridge), or (c) BYO API key in a hosted UI? Decides M1 architecture, the cost floor on grant funding, and whether the first metered agent runs land on the ledger from day one.

Adopted context:
- sbb schema: agent writes carry provenance (on_behalf_of, model, prompt_hash, run_id); graph is repo files at M0, DB+event log at M1.
- zyt: agent-run observations enter as additive types when needed; metering must be auditable (x8o: compute credit backed by metered capacity).
- z61: static site M0; M1 = boring web app.
- 19p: timed/artifact work observation types exist; agent capacity converts via tokens-per-vu (rate delegated).
- M1 done-condition: "a stranger uses it on their own repo because it is the best triage tool available" (milestones.md).
- Grant reality: NLnet-scale budgets (€5–50k) — platform-paid inference at scale is not in the bridge budget.
