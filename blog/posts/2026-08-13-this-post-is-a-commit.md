---
title: This post is a commit
date: 2026-08-13
kind: note
authorship: human
summary: The blog, its feed, its preview cards and the program that writes the weekly digest now exist in the repository. This post is the file that proves it.
card: socaity.dev now publishes from its own repository. A post is a Markdown file; its edit history is a commit log; the weekly digest is written by a program, not by a person.
---

There is now a blog, and it is not a content management system. A post is a
Markdown file under `blog/posts/`, added by a commit and rendered by the same
program that renders the rest of this site. There is no editor, no draft store
and no publish button. A post exists when its file is merged, and every change
to it afterwards is a commit anyone can read.

That is the only property of this blog worth announcing. A written record whose
history you cannot inspect is a claim; one whose history is a commit log is
checkable. The register on the [blog index](/blog/) links each post to its own
file and to that file's history, side by side, because the interesting question
about a build-in-public post is not what it says today but whether it said
something else last week.

## What exists as of this commit

| Thing | Where |
|---|---|
| Post sources | [`blog/posts/`](../../blog/posts/) |
| The page generator | [`tools/render/generators/blog.py`](../../tools/render/generators/blog.py) |
| The feed | [`blog/feed.xml`](/blog/feed.xml) |
| The program that writes the weekly digest | [`tools/blog/digest.py`](../../tools/blog/digest.py) |
| The step that opens one discussion thread per digest | [`tools/blog/announce_digest.py`](../../tools/blog/announce_digest.py) |

Each post also has a preview card — the 1200×630 rectangle a link preview crops
to. Ours are written as the disclosure rather than as a headline: cut every link
and caption away and the rectangle still has to say what this project is and
what it is not. You can read the card for this post at the bottom of the page.

## The cadence, stated so it can be held against us

Two kinds of post, on two different clocks:

- **A weekly digest**, written by a program from the commit history and from
  the contribution record. It is labeled as machine-written on the page, in the
  feed, and on its card. A thin week produces a thin digest — the program has
  no filler to reach for, which is the point of having a program write it.
- **A monthly letter** written by a person: decisions taken, questions still
  open, and what was missed. Weekly human writing dies at the first crunch, and
  a cadence broken quietly costs more than a modest one kept.

If a letter is skipped, the skip is posted as a one-line note saying why. A gap
with no note in it is a failure of this commitment, and it will be visible in
this register as an empty stretch, not hidden by a backdated entry.

## What is deliberately absent

There is no mailing list. A list is a copy of your address that we would then
have to hold, secure, and eventually migrate; the [feed](/blog/feed.xml) does the
same job and leaves the copy with you. If email is ever added, it will be a
relay that reads this feed, and it will be able to export and delete itself.

There is no comment box on this site either. Discussion happens in GitHub
Discussions, which archives publicly and links per thread. One artifact, one
place to argue about it.

The step that opens one thread per digest is written and committed, and it has
not run yet: no thread exists, `blog/discussions.json` is an empty object, and
the register shows no discussion link for any post because there is none to
show. When the first digest is published on the schedule, that step runs
against GitHub for the first time — and the honest thing to say until then is
that it is untested against the live API.
