# Council: socaity-ipg — Define the M0 first-contribution path end-to-end

Participants: community-builder, mechanism-designer, product-designer
Type: research · Priority: P0 · Was blocked by socaity-z61 (now adopted)

Issue:
- Context: M0's done-condition is "the ledger has recorded its first external contribution" — but what counts, how a stranger claims it, and what the ledger entry records were undefined at filing time.
- Question: Specify the path end-to-end: a stranger arrives at the manifesto → does something → an external ledger entry exists. Every step, every artifact, every actor.
- Why it matters: M0's done-condition; the launch cannot press "post" before this path is live (launch-strategist comment on file).

Adopted context binding this council (most of the path now exists — do not relitigate):
- socaity-z61: static site, contest workflow (issue templates → PRs), signed-patch courier path, tickets-as-files, CONTRIBUTING.md, SLO, seeded good-first-disputes, weekly digest.
- socaity-19p: 0.5 vu minimum-entry floor, ticket-free for trivial accepted contributions (contribution.trivial_accepted); artifact work via pre-opened tickets; founder gates inclusion never value.
- socaity-zyt: genesis prologue must complete (through epoch.opened(1)) before the first external entry; event types work.logged / ticket.accepted / contribution.trivial_accepted; mandatory fields incl. mode election, category, evidence hash.
- socaity-7mk: contributor = self-held Ed25519 keypair; in-browser keygen is M1+; at M0, keygen instructions + signed-patch or GitHub-attested linkage; entries signed.
- Remaining scope for THIS council: the exact end-to-end walkthrough (incl. WHO signs the ledger entry when the contributor came via GitHub PR and has no keypair yet — does the first-contribution flow require keygen, and how is that made non-fatal friction); what the ceremonial first entry records; how the moment is celebrated/communicated; failure modes (contributor bounces at keygen; contribution rejected; two contributors race for "first").
