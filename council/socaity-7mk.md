# Council: socaity-7mk — Ledger contributor identity must be a user-held keypair from the first entry

Participants: identity-specialist, platform-engineer, legal-counsel
Type: decision · Priority: P0 · Blocks: socaity-5c5 (GDPR erasure), socaity-a8o (key loss/recovery), socaity-5d0 (fork-portable standing)

Issue:
- Context: milestones.md M0 ("ledger has recorded its first external contribution", "ledger always") and sustainability.md (founder labor on ledger from day zero). The ledger is append-only, public, and pays out retroactively at M5 — so whatever identifies a contributor in entry #1 is permanent.
- Question: What is the identity primitive for a ledger entry? Proposal on the table from the issue: contributors are identified by a self-generated keypair they hold (entries signed; platform stores only the public key plus an optional display name off-ledger). GitHub handles/emails as the primary key would foreclose pseudonymity, break fork portability, and put personal data on an unerasable ledger.
- Why it matters: This is the one identity decision M0 cannot defer. Retrofitting keys under recorded entries later means re-attributing value claims — exactly the dispute the ledger exists to prevent. Blocks the "done when" of M0.

Adopted context from socaity-zjr (relevant): ledger entries are provisional-by-default and adjudicated by a published process; entries and status changes are signed public entries.
