# Council: socaity-aea — Mapping GitHub issue trackers onto the problem/solution AND/OR ontology

Participants: agent-engineer, product-designer
Type: research · Priority: P1

Issue:
- Context: M1 ingests a repo's issue tracker into a needs graph. But issues are not needs: many are solution-shaped ("add flag --foo"), some are bugs (problem-shaped but narrow), some are meta. The sbb ontology is exactly two node types (problem, solution) and three edge types (refines, requires, equivalent_to).
- Question: The mapping rules — what does an issue become, what do labels/milestones become, how are solution-shaped issues handled (invent the implicit problem node?), what does the decomposer add vs preserve, and what does the user see of the original issue?
- Why it matters: M1's first-run value is this mapping done well; a wrong ontology read produces graphs users don't recognize as their backlog.

Adopted context:
- sbb: two node types; OR = multiple refines edges into one problem; external_ref field; provenance mandatory (agent writes carry on_behalf_of/model/prompt_hash/run_id); estimates append-only intervals.
- 155's mapping precedent: problem nodes materialized one-per-solution where latent, merged on evidence.
- v9o: ingestion runs in the user's own agent via our skill; submission gate validates structure (competing OR branches present, granularity bounds, no orphan edges).
- 0vv (resolved): anti-solution-bias = multi-call independent branch generation + problem-restatement gate + mandatory null branch + distinctness filter.
- c1y: match-then-propose; decomposer is proposer-not-authority.
- z61/PD render contract: problem→children = "N competing approaches"; solution→children = "requires" checklist; users never taught AND/OR vocabulary.
