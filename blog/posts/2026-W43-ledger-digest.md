---
title: Weekly digest — 2026-W43
date: 2026-10-25
kind: digest
authorship: machine
summary: Week 2026-W43: 7 commit(s), 19 file(s) changed, 0 recorded contribution(s).
card: Week 2026-W43: 7 commit(s), 19 file(s) changed, 0 recorded contribution(s). Written by a program from the commit history of the socaity.dev repository, not by a person.
generator: python3 tools/blog/digest.py --week 2026-W43 --at 290fc19f071adeb424439ffc31ac6675c635e5e8
window: 2026-10-19T00:00:00+00:00 .. 2026-10-26T00:00:00+00:00 (UTC), over the history reachable from 290fc19
---

**A public record of contributions. No token. Nothing to trade. This is a database.**

## The window

This digest covers ISO week 2026-W43: 2026-10-19 to 2026-10-25, in UTC. 7 commits landed in that window.

The first was `8a23469` at 2026-10-19T07:16:53+00:00; the last was `49d4a9f` at 2026-10-25T08:01:03+00:00.

## What changed, by area

| Area | Files changed |
|---|---|
| the contribution record's engine | 2 |
| the toolchain: validator, renderer, gates | 15 |
| the blog itself | 1 |
| continuous integration | 1 |

Areas not listed had no file changed this week.

## The contribution ledger

There is no `ledger/log.jsonl` in this repository yet — no real record has been opened — so the honest count of recorded contributions this week is zero. The engine that will accept those events exists and is tested (`ledger/`), and the example chain the /ledger page renders (`ledger/example/chain.jsonl`) is an example: it is labelled as one there and it is not counted here. This section starts counting the week a `ledger/log.jsonl` file is committed. Nothing here estimates what the count would have been.

## Every commit in the window

| Commit | UTC | Subject |
|---|---|---|
| `8a23469` | 2026-10-19 07:16 | site: add semantic freshness dates (#20) |
| `9ab2a54` | 2026-10-19 12:19 | blog: weekly digest 2026-W42 (generated) |
| `2916d14` | 2026-10-20 07:25 | Add signed patch courier verification |
| `e53d775` | 2026-10-21 07:08 | Add public governance kit (#22) |
| `de66fd0` | 2026-10-22 07:03 | Enforce ledger checkpoint publication cadence |
| `3fe4c52` | 2026-10-24 07:09 | Add signed founder operations CLI |
| `49d4a9f` | 2026-10-25 08:01 | ci: allow graph check manual dispatch (#26) |

## How to check this

Every number above is a count of things in this repository's history, not an estimate. The counts are history as it stood at commit `290fc19`, which the command in this file's header names explicitly: clone the repository, run that command, and you get these bytes back whatever has landed since. `git log 290fc19 --since --until` over the same window shows the same commits.

A digest written while its week is still open reports the part of the week that had happened by that commit, and it is not rewritten afterwards — a corrected digest would be a new commit, visible as one.
