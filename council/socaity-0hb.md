# Council: socaity-0hb — M0 visual design system: what socaity.dev should look like

Participants: product-designer (owner), launch-strategist, platform-engineer, community-builder

Issue:

- **Context.** The site is functionally complete (home/manifesto, `/faq`,
  `/ledger`, `/claim`, `/roadmap`, node pages, `/blog`) but visually unstyled
  beyond the minimal CSS the toolchain shipped.
  `doc/standards/vocabulary-and-visual.md` fixes the constraints as pass/fail
  checks (V1–V14: editorial document register, no glassmorphism / neon / coin
  iconography / countdowns, every number links to its derivation, no
  colour-only signalling, WCAG AA) — but a checklist of refusals is not a
  design.
- **Question.** What is the positive visual language — typography, scale,
  colour, spacing, layout, the treatment of chips / tables / provenance /
  numbers, the 1200×630 crop, dark mode — that makes a stranger read this as a
  serious editorial document about public infrastructure rather than a product
  launch or a token site?
- **Why it matters.** The anti-crypto signal is visual before it is verbal
  (socaity-uun); the manifesto's first screen is where the pattern-match is won
  or lost (socaity-im1); and the five-user comprehension test (socaity-mqk)
  blocks launch on exactly this reading. Decisions taken now harden into the
  templates every future surface inherits.
- **Output shape.** A specification implementable as CSS plus template changes
  — not mood boards.

Constraint inputs: `doc/standards/vocabulary-and-visual.md` V1–V14;
`council/socaity-xuz.md` (ledger presentation rails); `council/socaity-z61.md`
and `socaity-sbb.md` (status chips, focus+context); the existing
`tools/render/templates/` and `tools/render/style.css`.

## Round 1
