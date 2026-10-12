---
title: Weekly digest — 2026-W41
date: 2026-10-11
kind: digest
authorship: machine
summary: Week 2026-W41: 8 commit(s), 21 file(s) changed, 0 recorded contribution(s).
card: Week 2026-W41: 8 commit(s), 21 file(s) changed, 0 recorded contribution(s). Written by a program from the commit history of the socaity.dev repository, not by a person.
generator: python3 tools/blog/digest.py --week 2026-W41 --at 9bb6c30f64504ca5c19f10e67d05ebb87a5f88e4
window: 2026-10-05T00:00:00+00:00 .. 2026-10-12T00:00:00+00:00 (UTC), over the history reachable from 9bb6c30
---

**A public record of contributions. No token. Nothing to trade. This is a database.**

## The window

This digest covers ISO week 2026-W41: 2026-10-05 to 2026-10-11, in UTC. 8 commits landed in that window.

The first was `c9cb43d` at 2026-10-05T07:05:24+00:00; the last was `9bb6c30` at 2026-10-11T10:00:58+00:00.

## What changed, by area

| Area | Files changed |
|---|---|
| the toolchain: validator, renderer, gates | 19 |
| the blog itself | 1 |
| continuous integration | 1 |

Areas not listed had no file changed this week.

## The contribution ledger

There is no `ledger/log.jsonl` in this repository yet — no real record has been opened — so the honest count of recorded contributions this week is zero. The engine that will accept those events exists and is tested (`ledger/`), and the example chain the /ledger page renders (`ledger/example/chain.jsonl`) is an example: it is labelled as one there and it is not counted here. This section starts counting the week a `ledger/log.jsonl` file is committed. Nothing here estimates what the count would have been.

## Every commit in the window

| Commit | UTC | Subject |
|---|---|---|
| `c9cb43d` | 2026-10-05 07:05 | Fail clearly when gate dependencies are missing (#11) |
| `542e912` | 2026-10-05 13:46 | blog: weekly digest 2026-W40 (generated) |
| `c86822d` | 2026-10-06 07:09 | Implement allocator weighted draw (#12) |
| `15ed3ad` | 2026-10-07 07:09 | Add replayable allocator report (#13) |
| `45805f6` | 2026-10-08 07:01 | socaity-bdl (W4a): one card.html for every M0 surface, og tags, and the A1 disclosure split (#4) |
| `0830fb2` | 2026-10-10 06:57 | Retire spent accent wash waiver (#14) |
| `b1addf4` | 2026-10-10 08:23 | Repair unattended Codex pipeline access and workflow routing (#15) |
| `9bb6c30` | 2026-10-11 10:00 | Fix narrow viewport table overflow (#16) |

## How to check this

Every number above is a count of things in this repository's history, not an estimate. The counts are history as it stood at commit `9bb6c30`, which the command in this file's header names explicitly: clone the repository, run that command, and you get these bytes back whatever has landed since. `git log 9bb6c30 --since --until` over the same window shows the same commits.

A digest written while its week is still open reports the part of the week that had happened by that commit, and it is not rewritten afterwards — a corrected digest would be a new commit, visible as one.
