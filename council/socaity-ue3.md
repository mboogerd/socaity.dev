# Council: socaity-ue3 — Build-in-public broadcast channel and cadence: commit before M0

Participants: launch-strategist, community-builder
Type: decision · Priority: P1

Issue:
- Question: The BROADCAST surface (distinct from the community channel): where does build-in-public content live canonically (blog on socaity.dev? newsletter? both?), what cadence is committed publicly, and what mirrors where? LS knowledge: "one canonical channel, weekly-or-honest cadence (skipping beats filler; announce the cadence you'll keep)"; z61 adopted the auto-generated weekly ledger digest as content.
- Also reconcile: socaity-vqo (resolved earlier by community-builder alone): the single M0 COMMUNITY channel = GitHub Discussions. But the z61 resolution's retention loop text says "the one channel (single Zulip/Discourse, public archives)". One of these must yield — settle the community channel here too, and the digest's home.
- Why it matters: committed-and-kept cadence is the trust signal; channel fragmentation is the named failure mode.

Adopted context: z61 (weekly auto-generated ledger digest; glass house), 1ux clause 10 (CI wordlist gates owned surfaces; canonical paragraph reuse), xuz (OG cards; archival register), M0 constraints (one founder — cadence must survive founder bandwidth).

## Round 1 (single-round convergence)

### [launch-strategist]
Canonical surface: **a blog living in the repo, rendered by the z61 generator onto socaity.dev** — every post is a commit (diffable, forkable, CI-gated by the 1ux wordlist); a newsletter service adds a subscriber database to minimize and a second source of truth. The weekly ledger digest publishes there as its own machine-labeled post type. Human cadence: **monthly founder letters** (decisions, open questions, honest misses) — weekly human writing dies at the first crunch and a broken promise costs more than a modest one; skips get a one-line "skipped: why" post. Mirror-out: fediverse/Bluesky get title + canonical paragraph + link home on every post; HN only when genuinely discussion-worthy, never on schedule. RSS day one (reader-sovereign); email as RSS-to-email via an export-friendly relay, deferred until requested — we hold no list we don't need. CONSENT, provided the digest's canonical home is the blog.

### [community-builder]
**vqo vs z61 settled: GitHub Discussions is the single M0 community channel; z61's "Zulip/Discourse" clause yields.** All machinery already lives in GitHub (PRs, issues, templates, the generator) — a second login is fragmentation by definition; Discussions archives are public, indexable, per-post linkable; one founder cannot moderate two venues. Zulip/Discourse reconsideration deferred until moderation load or threading pain actually appears — recorded, revisitable. Digest: canonical on the blog, one auto-opened Discussions thread per digest linking home — the blog is where it lives, Discussions where it's talked about. One artifact, one conversation venue. CONSENT.

## Resolution

ADOPTED by consent, Round 1.

**Broadcast + community surfaces (committed before M0):** blog in the repo rendered by the z61 generator (posts are commits; CI wordlist gates; OG cards; archival register); weekly auto-generated ledger digest as a machine-labeled post type + monthly human founder letters (public cadence commitment; skips announced with reasons); RSS from day one; email deferred to an export-friendly RSS relay on demand; mirror-out = title + canonical paragraph + link home (fediverse/Bluesky always, HN only when discussion-worthy, never scheduled). **Community channel: GitHub Discussions (amends the z61 resolution's Zulip/Discourse mention — vqo stands)**; per-digest auto-opened Discussions thread linking home; Zulip/Discourse revisit recorded as a trigger-based monitor (moderation load / threading pain).
