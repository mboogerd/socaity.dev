#!/usr/bin/env python3
"""Write the weekly digest post from git history and the contribution record.

council/socaity-z61 (community-builder, 4) adopted a "weekly ledger digest
auto-generated from git history"; council/socaity-ue3 made it a machine-labeled
post type on the blog. This is that program. Nobody edits its output: the post
it writes is committed as generated, and the post page says so and prints the
command that reproduces it.

Why a separate program rather than a renderer that reads git: the site is a
pure function of the merged tree (z61, platform-engineer 1). A renderer that
shelled out to git would render differently from a shallow clone and would
change between two runs whenever a commit landed in between --
tools/check.sh renders twice and diffs. So history is read here, once, and the
result is committed as an ordinary post file. The renderer still only reads
files.

Determinism: given a week and a commit to read history from, the output bytes
are fixed. The program never asks what time it is -- the default week is the ISO
week of the newest commit, and the post's own date is the day of the last commit
inside the window, both read from history. The commit history is read from is
pinned (--at, default HEAD) and the resolved sha is written into the post's
header, because a digest of a week that is still open is otherwise a function of
when you happened to run it, and the post promises the reader that running the
command in its header returns these bytes.

Honesty: a thin week produces a thin digest. There is no minimum length, no
filler section and no rounding up. If nothing happened in an area, the digest
says nothing happened in that area.

Usage:
  python3 tools/blog/digest.py [--root .] [--week 2026-W33] [--at HEAD] [--stdout]
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

POSTS_DIR = os.path.join("blog", "posts")

# Where the append-only event log lives once there is one. It does not exist
# yet, and the digest reports that as a fact rather than skipping the section.
LEDGER_LOG = os.path.join("ledger", "log.jsonl")

# Areas of the repository, in the order the digest lists them. The label is
# what a reader sees; the prefix is what git paths are matched against.
AREAS = (
    ("graph/nodes/", "the needs graph (nodes and edges)"),
    ("graph/tickets/", "tickets"),
    ("ledger/", "the contribution record's engine"),
    ("rule/", "the allocation rule as code"),
    ("doc/", "documents, standards and instruments"),
    ("council/", "council deliberations and resolutions"),
    ("tools/", "the toolchain: validator, renderer, gates"),
    ("blog/", "the blog itself"),
    (".github/", "continuous integration"),
)


# The digest is a published surface, and the only part of it not written here is
# the commit subjects it quotes. Commit messages are explicitly outside the
# vocabulary standard's scope, so this program checks them before publishing
# them (doc/standards/vocabulary-and-visual.md 1.5, 1.6).
#
# A FAIL-level word in a subject stops the digest; no waiver path exists, by
# design.
#
# A REVIEW-REQUIRED word also stops the digest -- and this program does NOT
# write its own waiver for one. The standard says a review-required hit "still
# demands a written waiver", and §0 says "if a check is subjective enough to
# argue about, it is written wrong -- fix the check, do not waive it". A program
# that generates the text, generates the waiver for the text, and then commits,
# pushes and announces the result on a cron has no person in the loop anywhere:
# the review tier would collapse to nothing on the one surface that is fully
# automated, and anybody who can land a commit subject could put a
# review-required word onto the blog, the feed and a Discussions thread with
# nobody having looked. That the generated reason happens to be true does not
# make it reviewed.
#
# So the waiver is a FILE a person edits, in a commit, and each entry is pinned
# to one full commit sha: it can excuse the subject of that commit and can never
# generalise to a future one. The weekly job fails until a human adds the line,
# which is exactly what a review tier is for. Nobody edits the digest's output
# to resolve it -- the fix is a separate reviewable commit, so "the post is
# committed as generated" still holds.
WORDLIST = os.path.join("doc", "standards", "banned-words.txt")
QUOTED_WAIVERS = os.path.join("doc", "standards", "quoted-subject-waivers.txt")


def load_patterns(root):
    """[(tier, raw_pattern, compiled)] from the standard's machine half."""
    path = os.path.join(root, WORDLIST)
    if not os.path.isfile(path):
        raise SystemExit("digest: %s is missing; refusing to publish unchecked "
                         "text" % WORDLIST.replace(os.sep, "/"))
    patterns = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            tier = "review" if line.startswith("~") else "fail"
            raw = line[1:] if tier == "review" else line
            patterns.append((tier, raw, re.compile(raw, re.IGNORECASE)))
    return patterns


def load_quoted_waivers(root):
    """{(full sha, pattern): reason} written by a person, one commit per line.

    A missing file means no waivers, which is the correct default: it makes the
    program stop rather than publish.
    """
    path = os.path.join(root, QUOTED_WAIVERS)
    waivers = {}
    if not os.path.isfile(path):
        return waivers
    with open(path, encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [part.strip() for part in line.split("|")]
            if len(parts) != 3:
                raise SystemExit("digest: %s line %d is not `sha | pattern | "
                                 "reason`" % (QUOTED_WAIVERS, number))
            sha, pattern, reason = parts
            if not re.fullmatch(r"[0-9a-f]{40}", sha):
                raise SystemExit("digest: %s line %d: %r is not a full commit "
                                 "sha (a short sha could later become "
                                 "ambiguous)" % (QUOTED_WAIVERS, number, sha))
            if not reason:
                raise SystemExit("digest: %s line %d has no reason, and a "
                                 "waiver without one waives nothing"
                                 % (QUOTED_WAIVERS, number))
            waivers[(sha, pattern)] = reason
    return waivers


def check_subject(sha, subject, patterns, waivers):
    """[(pattern, human reason)] for a quoted subject, or stop the digest."""
    review = []
    for tier, raw, compiled in patterns:
        if not compiled.search(subject):
            continue
        if tier == "fail":
            raise SystemExit(
                "digest: commit %s has a subject that matches the banned "
                "pattern %s and there is no waiver path for one: %r. Publish "
                "nothing until a person decides what to do about it."
                % (sha[:7], raw, subject))
        reason = waivers.get((sha, raw))
        if not reason:
            raise SystemExit(
                "digest: commit %s has a subject matching the review-required "
                "pattern %s: %r\n"
                "This program does not write its own waiver. A person decides, "
                "in a commit, by adding one line to %s:\n\n"
                "    %s | %s | <why publishing this quoted subject is right>\n\n"
                "See doc/standards/vocabulary-and-visual.md §1.5 and §1.6 for "
                "what a reason has to say."
                % (sha[:7], raw, subject, QUOTED_WAIVERS.replace(os.sep, "/"),
                   sha, raw))
        review.append((raw, reason))
    return review


def git(root, *args):
    out = subprocess.run(["git", "-C", root, *args], check=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return out.stdout.decode("utf-8")


def utc(stamp):
    """An ISO-8601 commit timestamp as a UTC datetime, offset included."""
    return datetime.datetime.fromisoformat(stamp).astimezone(datetime.timezone.utc)


def read_commits(root, rev="HEAD"):
    """Every commit reachable from `rev`, newest first: sha, UTC time, subject."""
    raw = git(root, "log", rev, "--date=iso-strict", "--format=%H%x1f%cI%x1f%s")
    commits = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        sha, stamp, subject = line.split("\x1f", 2)
        commits.append({"sha": sha, "at": utc(stamp), "subject": subject})
    return commits


def week_bounds(iso_week):
    """'YYYY-Www' -> [Monday 00:00 UTC, next Monday 00:00 UTC)."""
    year, _, week = iso_week.partition("-W")
    start = datetime.datetime.fromisocalendar(int(year), int(week), 1)
    start = start.replace(tzinfo=datetime.timezone.utc)
    return start, start + datetime.timedelta(days=7)


def files_of(root, sha):
    raw = git(root, "show", "--name-only", "--format=", sha)
    return [line.strip() for line in raw.splitlines() if line.strip()]


def ledger_events(root, start, end):
    """Events appended to the record inside the window, or None if there is no log."""
    path = os.path.join(root, LEDGER_LOG)
    if not os.path.isfile(path):
        return None
    inside = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            stamp = event.get("ts")
            if not stamp:
                continue
            when = utc(stamp) if isinstance(stamp, str) else datetime.datetime.fromtimestamp(
                stamp, datetime.timezone.utc)
            if start <= when < end:
                inside.append(event)
    return inside


def escape_cell(text):
    return text.replace("|", "\\|")


def build(root, iso_week, tip):
    start, end = week_bounds(iso_week)
    commits = [c for c in read_commits(root, tip) if start <= c["at"] < end]
    commits.sort(key=lambda c: (c["at"], c["sha"]))

    touched = {prefix: set() for prefix, _label in AREAS}
    for commit in commits:
        for path in files_of(root, commit["sha"]):
            for prefix, _label in AREAS:
                if path.startswith(prefix):
                    touched[prefix].add(path)

    events = ledger_events(root, start, end)
    last = commits[-1] if commits else None
    date = (last["at"] if last else end - datetime.timedelta(days=1)).date().isoformat()

    patterns = load_patterns(root)
    waivers = load_quoted_waivers(root)

    lines = []
    add = lines.append

    # V14: a surface presenting the record opens with the register line.
    add("**A public record of contributions. No token. Nothing to trade. "
        "This is a database.**")
    add("")
    add("## The window")
    add("")
    add("This digest covers ISO week %s: %s to %s, in UTC. "
        % (iso_week, start.date().isoformat(), (end - datetime.timedelta(days=1)).date().isoformat())
        + ("%d commits landed in that window." % len(commits) if commits
           else "No commits landed in that window, and this digest is the record of that."))
    add("")

    if commits:
        add("The first was `%s` at %s; the last was `%s` at %s."
            % (commits[0]["sha"][:7], commits[0]["at"].isoformat(),
               commits[-1]["sha"][:7], commits[-1]["at"].isoformat()))
        add("")

    add("## What changed, by area")
    add("")
    rows = [(label, sorted(touched[prefix])) for prefix, label in AREAS if touched[prefix]]
    if rows:
        add("| Area | Files changed |")
        add("|---|---|")
        for label, paths in rows:
            add("| %s | %d |" % (escape_cell(label), len(paths)))
        add("")
        add("Areas not listed had no file changed this week.")
    else:
        add("No file in any tracked area changed this week.")
    add("")

    add("## The contribution ledger")
    add("")
    if events is None:
        add("There is no `%s` in this repository yet — no real record has been "
            "opened — so the honest count of recorded contributions this week "
            "is zero. The engine that will accept those events exists and is "
            "tested (`ledger/`), and the example chain the /ledger page renders "
            "(`ledger/example/chain.jsonl`) is an example: it is labelled as "
            "one there and it is not counted here. This section starts counting "
            "the week a `%s` file is committed. Nothing here estimates what the "
            "count would have been."
            % (LEDGER_LOG.replace(os.sep, "/"), LEDGER_LOG.replace(os.sep, "/")))
    elif not events:
        add("No events were appended to the record this week.")
    else:
        add("%d event(s) were appended to the record this week:" % len(events))
        add("")
        add("| Event | Type |")
        add("|---|---|")
        for event in events:
            add("| `%s` | %s |" % (escape_cell(str(event.get("id", "?"))[:16]),
                                   escape_cell(str(event.get("type", "?")))))
    add("")

    add("## Every commit in the window")
    add("")
    if commits:
        add("| Commit | UTC | Subject |")
        add("|---|---|---|")
        for commit in commits:
            review = check_subject(commit["sha"], commit["subject"], patterns,
                                   waivers)
            row = ("| `%s` | %s | %s |"
                   % (commit["sha"][:7], commit["at"].strftime("%Y-%m-%d %H:%M"),
                      escape_cell(commit["subject"])))
            for raw, reason in review:
                # The reason is transcribed from the waiver file, not composed
                # here: what reaches the page is what a person wrote, and the
                # pattern and sha it was pinned to travel with it.
                row += (" <!-- vocab-ok: %s (quoted subject of commit %s, "
                        "matching %s; waiver in %s) -->"
                        % (reason, commit["sha"][:7], raw,
                           QUOTED_WAIVERS.replace(os.sep, "/")))
            add(row)
    else:
        add("None.")
    add("")

    add("## How to check this")
    add("")
    add("Every number above is a count of things in this repository's history, "
        "not an estimate. The counts are history as it stood at commit `%s`, "
        "which the command in this file's header names explicitly: clone the "
        "repository, run that command, and you get these bytes back whatever "
        "has landed since. `git log %s --since --until` over the same window "
        "shows the same commits." % (tip[:7], tip[:7]))
    add("")
    add("A digest written while its week is still open reports the part of the "
        "week that had happened by that commit, and it is not rewritten "
        "afterwards — a corrected digest would be a new commit, visible as "
        "one.")
    add("")

    summary = ("Week %s: %d commit(s), %d file(s) changed, %s recorded contribution(s)."
               % (iso_week, len(commits),
                  sum(len(paths) for _label, paths in rows),
                  "0" if not events else str(len(events))))
    card = ("%s Written by a program from the commit history of the socaity.dev "
            "repository, not by a person." % summary)

    header = [
        "---",
        "title: Weekly digest — %s" % iso_week,
        "date: %s" % date,
        "kind: digest",
        "authorship: machine",
        "summary: %s" % summary,
        "card: %s" % card,
        "generator: python3 tools/blog/digest.py --week %s --at %s"
        % (iso_week, tip),
        "window: %s .. %s (UTC), over the history reachable from %s"
        % (start.isoformat(), end.isoformat(), tip[:7]),
        "---",
        "",
    ]
    return "%s-ledger-digest.md" % iso_week, "\n".join(header + lines).rstrip("\n") + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--week", default=None,
                    help="ISO week, e.g. 2026-W33 (default: the week of the newest commit)")
    ap.add_argument("--at", default="HEAD",
                    help="the commit to read history from (default: HEAD). The "
                         "resolved sha is written into the post, so the printed "
                         "command reproduces the bytes after later commits land.")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing the file")
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)

    # Pinned once, up front: two git calls a second apart must not read two
    # different histories, and an unpinned digest cannot honour the "run this
    # command and get these bytes" promise it prints.
    tip = git(root, "rev-parse", "%s^{commit}" % args.at).strip()

    week = args.week
    if week is None:
        commits = read_commits(root, tip)
        if not commits:
            raise SystemExit("digest: this repository has no commits to summarise")
        year, number, _day = commits[0]["at"].isocalendar()
        week = "%04d-W%02d" % (year, number)

    name, text = build(root, week, tip)
    if args.stdout:
        sys.stdout.write(text)
        return 0
    path = os.path.join(root, POSTS_DIR, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print("wrote %s" % os.path.relpath(path, root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
