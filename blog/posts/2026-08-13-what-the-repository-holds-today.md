---
title: What the repository contains today
date: 2026-08-13
kind: note
authorship: human
summary: An inventory of what is actually committed right now — five graph nodes, two tickets, the standards, the validator, the renderer, the rule as code — and an equally plain list of what is not there yet.
card: An inventory of what socaity.dev has actually built so far, with the empty parts named as empty. Five graph nodes, two tickets, no recorded contributions yet.
---

Build-in-public writing goes wrong in a predictable way: the post describes the
plan and the reader assumes the plan is the state. So this one is an inventory,
and every row is a file you can open.

## What is committed

| In the repository | What it is |
|---|---|
| [`doc/manifesto.md`](../../doc/manifesto.md) | the manifesto, published as the site's front page |
| [`doc/faq.md`](../../doc/faq.md) | the pre-launch questions, answered without hedging |
| [`doc/standards/vocabulary-and-visual.md`](../../doc/standards/vocabulary-and-visual.md) | the words and the look, written as pass/fail checks |
| [`doc/standards/banned-words.txt`](../../doc/standards/banned-words.txt) | the machine half of that standard, run over every page in CI |
| [`graph/nodes/`](../../graph/nodes/) | the needs graph: five nodes, edges inline, provenance mandatory |
| [`graph/tickets/`](../../graph/tickets/) | two ticket files — claim state is a file, never a label |
| [`tools/validate/`](../../tools/validate/) | the offline validator that rejects a malformed graph |
| [`tools/render/`](../../tools/render/) | this site, as a pure function of the merged tree |
| [`rule/`](../../rule/) | the allocation rule as code, with golden vectors and no floating-point arithmetic on the mechanism path |
| [`ledger/`](../../ledger/) | the append-only event-log engine and the validator that accepts events into it — plus an example chain, and no real record yet |
| [`council/`](../../council/) | the deliberations behind each of the above, kept whether or not they flatter us |

Five nodes is a small graph. It is also the true number, and the roadmap page
shows it without padding.

## What is not there

The contribution ledger has an engine and no real record: there is no
`ledger/log.jsonl` in this repository, so the count of recorded contributions
is zero. The weekly digest reports that zero rather than skipping the section,
and it will keep reporting it until the first entry is appended. No token.
Nothing to trade. This is a database.

The `/ledger` page is published, and what it renders is an **example chain**
([`ledger/example/chain.jsonl`](../../ledger/example/chain.jsonl)) signed by a
key whose secret is printed in the repository. It says so on its own first
screen, and it exists because the rule refuses to open a real epoch under
parameter values that are not final yet. The arithmetic on that page is real —
computed at build time by `rule/` over that file — and the entries are not. So:
this site does contain example entries and an example contributor, in exactly
one place, labelled there and labelled here. There are no placeholder rows
anywhere that fail to say what they are, and no count on this site is an
estimate.

## Why the inventory is the post

Everything above is checkable in about five minutes with a clone and no
account, which is the only claim this project can make honestly at this size.
The interesting numbers do not exist yet. When they do, they will arrive in the
weekly digest, computed from history by a program, and the first one that is
embarrassing will be printed at the same size as the rest.
