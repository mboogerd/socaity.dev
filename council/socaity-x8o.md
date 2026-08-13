# Council: socaity-x8o — Publish the epoch-share distribution rule as code before the first external ledger entry

Participants: mechanism-designer, legal-counsel, platform-engineer
Type: decision · Priority: P0 · Blocked by (open): socaity-19p (pricing heterogeneous contributions, founder rate), socaity-9cb (model the earliness premium curve) — this council may fix the architecture and delegate parameter values to those issues.

Issue:
- Context: vision.md "Credit" and milestones.md Principle 3 commit to an append-only ledger from day one with retroactive distribution in proportion to recorded contribution, with an epoch-share earliness premium; M0 is done when the ledger records its first external contribution. But the rule itself is unspecified: epoch boundaries and length, the pie schedule per epoch, how epoch-share and absolute pricing coexist, and the exact denominator of "recorded contribution".
- Question: What is the exact, machine-executable distribution rule — epoch length, pie schedule, epoch-share vs absolute interaction, rounding, and the retroactive formula — and can it be published as code alongside the first ledger entry?
- Why it matters: Retroactive-distribution ambiguity is the single most reliable source of community blowups. Every ledger entry accepted before the rule is fixed is a claim of unknown value.

Adopted context binding this council (do not relitigate):
- socaity-zjr (Ledger Validation Policy): provisional→confirmed lifecycle; confirmation fixes eligibility + relative weight, never amounts; pre-distribution audit blocking; challenged entries escrowed at declared weight; capped audit slice (placeholder 5%).
- socaity-1ux (Standing Commitment): rule ships at M0 as versioned executable code, authoritative over prose; formula STRUCTURE final for every epoch opened under it; parameter values amendable only for not-yet-opened epochs via a meta-rule itself published at M0; declaration discretionary; allocation binding; non-transferable; founder on the same rule at a declared rate.
- socaity-7mk: entries attributed to permanent keypair identities; observations vs valuations separated (socaity-zyt discipline): observations immutable, valuations recomputable by replay.
- Deterministic replay (platform): fixed-point/rational arithmetic, no wall-clock, byte-equal recomputation by strangers (forkability CI).
