# Council: socaity-s0n — Design critique against the rendered artifact

Participants: product-designer (owner), launch-strategist, community-builder,
independent critic (no prior involvement)

This is a **critique round**, not a fresh design council. The design was
specified in `socaity-0hb` and built in W0–W2. Every ticket verified against its
own checklist and against the resolution's own checks, and all of them passed.
Nobody looked at the finished rendered result and asked whether it meets the
audience.

The founder has, and the verdict is negative:

> I would have expected better styling than what is currently there, given that
> I asked several designers to look at it and come up with a design that would
> work. I feel like there is no thought put into meeting the audience that we
> aim to approach.

**The question.** Looking at the built site — not the spec — does this recruit
the developer M0 is written for? If not, what specifically changes, and is the
failure in the **resolution** (the register was chosen wrong) or in the
**execution** (the register is right and thinly built)?

**Why it matters.** The design hardens into every future surface at W4–W5.
Amending is cheap now and expensive once the cards and the dark palette are
built around it.

**Ground rule.** Every participant inspects the rendered site before writing.
An independent critic with no prior involvement participates specifically so the
adopted spec has someone with no reason to defend it.

## Round 1

### [independent critic]

*(No prior involvement; read the adopted resolution only after forming a judgement.)*

**The founder is not looking at a design he disagrees with. He is looking at a design that was never applied.** `style.css` declares a complete type scale in `@layer tokens` — and nothing consumes `--t-h1/h2/h3` for actual headings. The `base` layer still carries the pre-design rules verbatim, so every `<h2>` computes to **19.55px against 17px body text**. That is a 1.15 ratio: *below the threshold at which the eye registers a size change at all*, which is why the FAQ reads as one undifferentiated grey slab. Same for colour — the ground painted is the legacy `#fdfdfc`, not the measured `--paper`; `.muted`, `.provenance` and the nav separators resolve to the legacy grey; links are a hardcoded literal, not `--accent`. "A token layer that reads like a typography manual, sitting inert above a 2014-era default stylesheet that wins every cascade contest for headings, ground, muted text and links. It looks underdesigned. It *is* undesigned, on ~80% of its surface area."

**Five seconds, cold:** eight browser-default blue links; then six lines of 13.9px grey explaining the build system — *the first substantive words on the page are about the build system*; then the sitename at 20.4px reading as a subtitle; the thesis; then **144px of pure white nothing** — one scroll notch gives a completely blank viewport. Conclusion: *"someone's personal wiki."* The signal that this is a serious engineering artifact is 4,000px below the fold.

**Restraint vs underdesign, concretely.** "Restraint is a budget deliberately spent in few places. Underdesign is a budget never allocated." LWN has hierarchy readable with your eyes closed; here an `<h2>` and a bolded lead-in sentence are *visually the same object*. An annual report treats numbers as a designed material; `tabular-nums` appears four times, all in the ledger. Stripe's docs make commands first-class; **four of six `<pre>` blocks on `/claim` overflow and are silently clipped** (918/746, 887/746, 1061/746, 733/686) — under macOS overlay scrollbars a visitor sees `ssh-keygen -t ed25519 -f ~/.socaity/claim-key -C` ending in mid-air. "The one thing you are asking a developer to *do* is a truncated command with no copy button." An RFC earns trust by boring consistency; `/roadmap` prints a raw `t-mkfutwlnzxuxuqyn2t2zo4cyte` as body copy, and a state chip `Open` sits beside a weight chip `open` in an identical box.

**Highest leverage, one day, in order:** wire `--t-h1/h2/h3` into `base` and retire `--bg`/`--muted` (~20 lines, and it is a *deletion* of legacy rules, not new design); separate headings from bold lead-ins; fix `/claim`'s code blocks; fill the 144px void with the glass-house evidence strip, moving the artifact links from y≈3,483 to the first scroll; `aria-current` + tabular numerals + `nowrap` dates.

**Must survive:** the chip system ("do not let anyone add colour to this"), the provenance object ("better thinking than most funded design systems produce"), the mobile ledger de-tabling, the figure discipline, the commented stylesheet, the tail-tuned font stack, and the serif body at 17px on warm paper.

**Against the spec:** §A defines a scale but *no ticket owns making elements use it* — and the W2 discipline of "append-only within your own named section," which made concurrent merges clean, **guaranteed nobody touches `base`**. "The process protected the merge and lost the design. That is a spec-level defect, not an implementer's slip." §J's gates are fortified against one failure mode (an unqualified percentage reaching a hostile thread) and completely unguarded against the one that happened: a dead-token gate is five lines and would have caught this the day W0 merged. §G gives the share-card a whole wave while `/claim`'s clipped commands appear nowhere in A–K — "they will forgive a plain unfurl and they will not forgive a truncated `ssh-keygen` line."

### [launch-strategist]

**The five-second conclusion is not "scam." It is "someone's markdown, published."** The nav is the loudest object on the screen and it is styled exactly like an unstyled `<ul>`. "The thesis is the only thing on the page that anyone decided about. Everything around it is browser default wearing a serif."

**I got exactly what I asked for and I will not pretend otherwise.** My crop checks pass. No CTA, no hero, no logo, no recruitment grammar. **And yes, I conflated two things: "does not look like a scam" is a *floor*; "looks like something serious people built" is a *position*. A floor is verified by prohibitions; a position is asserted by choices.** My round-1 "would not accept" list is six clauses and every one is a refusal; I spent none of my turn saying what the page should positively be. The structural proof is §J: every gate we shipped is a prohibition. **Not one gate asserts that anything looks like anything.** The council brief opened by saying "a checklist of refusals is not a design," and the mechanism we built to enforce the design was a checklist of refusals. I signed the sequencing that made that true.

The cost is not that the page fails to sell. "It is that a page which only proves it isn't a scam gives the fifty right readers nothing to join." Nothing on it produces an email.

**The reference registers share four properties and the site has one.** Masthead weight — the CSS comment says "Small on purpose: the site name is not the argument," citing §H, citing my R1b: **I asked for the tagline not to outweigh the register; it was executed as "nothing outweighs the register," and the masthead was the casualty. That one is mine.** Sectional hierarchy — the legacy heading rules, unmigrated. Table craft — `/blog` wraps a date onto two lines; `/ledger`'s header reads `vuStatus` and the `confirmed` chip overlaps the vu number at 1280. Density — `/roadmap` is two bullets with room left over. **"Restraint is a full page held quiet. What shipped is a sparse page held quiet, and a reader cannot tell the difference from the outside — which means it isn't a difference."**

**My pre-gate, applied honestly:** nobody says crypto. My gate passes. They say "a manifesto," "someone's blog," "an RFC draft," and at least one says "is this a placeholder?" **"My pre-gate can only return 'not a scam'. It is a one-sided test, and I proposed it as if it were verification. A test that can only fail in one direction is how a council convinces itself it checked something."**

**Doctrine amendment.** Stands: the register, no filled CTA, no hero art, no logo beyond a wordmark, no recruitment or scarcity grammar, register-before-detail in every crop. **Withdrawn: the implicit corollary that restraint is achieved *subtractively* — that every increase in visual force is a step toward the landing page. That is false, and it is what produced a 1.15× heading ratio, a 20px masthead and default-blue nav links.** Replaced by: *the register is set by hierarchy and density, not by quietness* — and operationally, **every refusal in a design spec must be paired with a positive assertion at the same level of specificity, and a gate that checks a refusal never counts as verification of the assertion beside it.**

### [product-designer]

**Yes, the founder is right. Not partly.** And the sharpest evidence is something I did not expect: **there is no masthead on this site.** `base.html`'s `<header>` contains a nav and nothing else; the wordmark is an `h1` inside `doc/manifesto.md`. **The site's identity appears on one of seven surfaces.** A stranger landing on `/ledger` sees eight underlined blue words and then "Ledger". "That is not a styling shortfall. That is a site with no identity object."

Token audit: `--paper` **0 uses**, `--accent` **0**, `--accent-wash` **0**, `--t-h3` **0**, `--t-h1`/`--t-h2` one each. "The warm-paper decision and the eight-step scale — the two things that would have made this read as a printed document — never reached a pixel."

**Where the failure is, charge by charge, against my own text.** Build metadata in the top-left: **my spec** — §C enumerated the rail's contents and specified no order and no offset, so the first fixation on the page is the colophon. "A colophon belongs at the back of the book and I put it in the masthead position by omission." Wordmark vs tagline: **my spec** — R1 assigned both the same rung, "two objects on one rung, the longer one wins." 857px floating in 1280: **my spec** — "I specified a column and called it a page." Flatness: 60% spec — §B's total hue ban "was argued from the anti-crypto premise, but the requirement was never *hue-free*, it was *hue-never-alone*, and §D had **already** won that with three redundant channels. Having earned redundancy, I then banned the third channel for no remaining reason."

**Did the refusals crowd out the design? Yes. That is the root cause, and I wrote it.** Thirteen refusals in R1; §B's centre is a refusal; §D is four; §F's paramount is a refusal. "Of §J's nine gates, eight test for the presence of a defect; none tests whether anything is well-made. The positive content of the whole resolution amounts to a type scale, a palette table, a two-column grid and four component sketches. That is a constraint set, not a design. It leaves an implementer exactly one degree of freedom — the minimum — and every positive was phrased as permission while every negative was phrased as a gate. So the implementer took the minimum, correctly, and every check went green. Nothing in that apparatus could ever have caught *'this page is boring'*, because I specified twenty ways to fail and zero ways to succeed."

**Three clauses of my own I now think are wrong:** §B's total hue ban (withdraw; hue as redundant third channel only, marker and word unchanged); §C's closed rail list (replace with an *ordered* list plus: nothing enters the rail that annotates the masthead, and the rail's first item aligns to the first block it annotates, never to the `h1`); and R1's "no hero image, generated illustration or decorative diagram" — "'decorative' was doing all the work, and a site about a *needs graph* currently ships zero pictures of a graph."

**Must survive:** the figure component, the chip system, the provenance object, the mobile ledger, thesis-before-tagline and the ruled register strip, the rail as a structure, no-webfont byte-identical render.

### [community-builder]

*(Inspected post-`b2f5563`; notes that only W0–W2 are built, so the founder is judging ~60% of the spec and the missing 40% is disproportionately the audience-facing part — which mitigates the verdict without answering it.)*

**My four wins, as built.** *Contested as the darkest chip* — implemented exactly, **and the effect did not arrive: `chip-open` is also `--ink`.** "Contested is the darkest chip and so is its neighbour, so it reads as one more metadata token. I won 'not a fault' and lost 'emphasis'." *Provenance symmetry* — implemented, and at 375 the result is a **330px stamp between the title and the claim**, pushing the statement ~660px down. "My paramount forbade the agent object being louder; it never capped either. Parity got achieved by levelling **up**, and the claim lost its own first screen." */claim floor* — **cleanly won, the one place where winning the rule produced the outcome** — though raising `pre` to 17px is what pushed four commands past the measure. *No recruitment grammar* — total, "and also no CONTRIBUTING or code-of-conduct link anywhere in the rendered site."

**The positive version exists — and is buried.** Home's closing section says "open a challenge against anything in the record that you think is wrong." At 375 that sits at **90% scroll depth, and "open a challenge" is not a link.** Home contains zero in-body links to `/roadmap`, `/claim` or any node — every body link goes to a GitHub blob. On `/ledger` the empty external-contributor row — the best object on the site for my audience — sits at **94% depth, drawn in a dotted border: the same idiom the chip vocabulary uses for *withdrawn*. The one open door on the site is at the bottom of the longest page, rendered in the texture that means inert.**

**The suspicious maintainer, thirty seconds.** *Who is asking* — answered fast and honestly; "network of one" is above the fold. *Will you spam me* — the FAQ's second question is his question verbatim, at y=3,420 of a 14,310px page **with no jump list and no anchors**. *Can I make it stop* — "Consent first" at y=3,649. "My council ask was that the consent tier be one click from any surface a maintainer can land on; as built it is one click plus 3,600px of scrolling, from one surface." He leaves without finding the thing that would have converted him.

**`.ledger-derivation` is 13.6px — under the adopted 13.94px floor, ~30 instances — and it carries "Challenge this entry · permalink" on every row. The per-row contest affordance is the smallest text on the site: my paramount inverted, on the surface where it matters most.**

**On the charter question: not hostile, not yet welcoming — separated by exactly one property.** The accessibility floors genuinely landed and I would defend them without qualification. "But every one of those wins is a *refusal of harm*. Every affordance that would constitute welcome is present in the tree and rendered at the smallest size, the greyest ink, or the greatest scroll depth available. The site currently does nothing to a contributor. **The gap is not styling: it is that I specified what may never be louder than what, and never once specified what must be loud.**"

### Facilitator

**Four independent assessments, one diagnosis.** Every participant — including the critic who was kept away from the resolution until after judging, and the three who wrote it — reached the same conclusion without conferring: **the register was chosen correctly and the specification was made almost entirely of refusals, so the implementation took the minimum the refusals allowed and every check went green.**

**The single largest finding was a delivery failure, now fixed** (`b2f5563`): the adopted palette and scale were declared in `@layer tokens` and never consumed — `h2` at 19.55px against 17px body, `--paper`/`--accent`/`--accent-wash` at zero uses. Root cause is in the orchestration, not the roles: the W2 instruction to work append-only inside named sections made concurrent merges clean and thereby forbade any ticket from touching the `base` layer where the legacy rules lived.

**Convergent findings not yet fixed**, each named independently by two or more participants:

1. **No masthead component.** The wordmark exists on one of seven surfaces. (PD, LS, IC)
2. **The colophon holds the first-read slot**; on mobile it precedes the page's own name. (PD, IC)
3. **`/claim`'s commands are silently truncated** — four of six overflow at desktop width, on the site's only conversion surface. (IC, CB)
4. **The invitation is present but rendered smallest, greyest, or deepest** — "open a challenge" unlinked at 90% depth, the empty ledger row at 94% depth in the texture that means *inert*, the per-row challenge link at the smallest size on the site. (CB, LS)
5. **The gates test refusals only.** No gate asserts quality; a five-line dead-token gate would have caught the delivery failure on the day W0 merged. (IC, LS, PD)
6. **`/roadmap` is a two-item stub** and is a flagship M0 surface. (PD, LS, IC)
7. **Chip taxonomy collision** — `Open` (state) beside `open` (weight) in identical boxes; and `chip-open` shares `--ink` with contested, cancelling the emphasis CB won. (IC, CB)

**Clauses their authors withdrew or amended, unprompted:** §B's total hue ban (PD); §C's unordered closed rail list (PD); R1's blanket ban on diagrams (PD); R1b's implicit "nothing may be large" (LS); the subtractive-restraint corollary (LS); the one-sided five-second pre-gate (LS); and CB's four provenance conditions, which capped loudness in one direction only.

**Proposed amendment, for the founder's decision — this round cannot adopt it, because it revises a resolution adopted by consent in socaity-0hb:**

- **A1. Every refusal is paired with a positive assertion at the same specificity** (LS). A prohibition may not ship without the assertion it protects.
- **A2. §J gains assertion gates**: no `:root` token with zero `var()` references; no heading below 1.4× body size; no `<pre>` exceeding its container; every declared surface carries the identity object.
- **A3. §H gains a masthead component** on all surfaces — wordmark at `--t-h2`, full-bleed band on `--paper-sunk` with a `--ink` bottom rule, nav as a table of contents at `--t-micro` with `aria-current`; tagline drops to `--t-body`.
- **A4. §C's rail list becomes ordered**, with: nothing that annotates the masthead may enter the rail; the first rail item aligns to the first block it annotates, never the `h1`; the colophon moves to the footer; the provenance object collapses to one line with its `<dl>` inside a `<details>`.
- **A5. §B permits hue as a redundant third channel** — marker shape and word unchanged, greyscale legibility preserved.
- **A6. A new clause names what must be LOUD** (CB): on every surface, the affordance to act is at least `--t-body` in `--ink`, and no contest or claim affordance may be the smallest text on its page.
- **A7. `/claim` commands wrap rather than clip**, and `/roadmap` is designed rather than listed.
- **A8. R1 permits one honest diagram** drawn from real data on `/roadmap`.
