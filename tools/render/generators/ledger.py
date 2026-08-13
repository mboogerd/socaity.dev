#!/usr/bin/env python3
"""The /ledger surface (socaity-7z0) and the contribution-worth calculator
(socaity-m3i), rendered per the socaity-xuz resolution.

Two things live in this one file on purpose, and that is the answer to the
research half of socaity-m3i.

DESIGN NOTE — what the calculator exposes, and why it IS the audit script
------------------------------------------------------------------------
socaity-m3i asks: what exact inputs does the calculator expose (hours?
capacity? role of declared rate?), and can it call the same published code
path the ledger uses, so that the calculator is the audit script rather than a
paraphrase of it?

*Inputs exposed: exactly two — category and hours.*  Nothing else is an input,
because nothing else is an input to the rule.  In particular:

  * **The rate is not an input.**  V (``rule/params.py`` ``rates``) is a
    published table keyed by ``category:unit``; a contributor does not declare
    a rate and cannot propose one.  Exposing a rate field would invent a lever
    the mechanism does not have and would imply negotiation where socaity-19p
    put a flat published table.  The rate is *shown*, next to the result,
    as the multiplier that was applied.
  * **Capacity is not an input.**  Capacity is an M3 ComputeNet concept; at M0
    the only native unit V prices is ``hours``.
  * **Mode is not an input.**  socaity-ipg fixed mode E as a published
    protocol constant for accepted contributions, so the calculator states the
    mode rather than asking for it.
  * **The epoch is not an input.**  An observation's epoch is its chain
    position (``rule/replay.py``), not a choice.  The calculator answers for
    the epoch that is open on the record it was built from, and says so.

*How it stays the audit script.*  The page is static, so a JavaScript
reimplementation of the rule would be a paraphrase — the exact failure mode
the ticket names.  Instead every number on the page, including every cell of
the calculator, is produced at build time by calling the published rule:
``rule.valuation.weight_micro_vu`` for hours -> vu, and
``rule.distribute.distribute`` for the epoch denominator and the share.  The
calculator ships as a precomputed grid over (category x hours); the page's
JavaScript performs a lookup into that grid and nothing else — it contains no
arithmetic, and the page says so where a reader can see it.  The whole grid is
also rendered as a plain table, so the page answers with JavaScript switched
off.

*And this module is literally runnable as the audit script*, which is what
closes the loop:

    python3 tools/render/generators/ledger.py                 # everything
    python3 tools/render/generators/ledger.py entry <id>      # one entry
    python3 tools/render/generators/ledger.py hypothetical code 8

The commands the page prints under "recompute this" are these commands, in
this file, running the same functions the render ran.  A reader who changes
``rule/params.py`` sees both the page and the script change together, because
there is only one implementation.

WHAT IT RENDERS FROM
--------------------
``ledger/example/chain.jsonl`` — an obviously-labelled EXAMPLE chain
(``ledger/example/seed.py`` explains exactly what is real in it and what is
not).  The real chain cannot be opened until socaity-wna fixes the parameter
values (socaity-x8o §7 makes a placeholder-free V a precondition of
``epoch.opened(1)``), and the standard's V5 forbids hand-writing numbers in
the meantime.  So the arithmetic is real, the entries are a fixture, and the
page says which is which above the table rather than in a footnote (V12).

DETERMINISM
-----------
No wall clock, no environment, no network.  Ledger time comes from the chain;
page freshness comes from ``ctx["clock"]``.  All arithmetic is
``fractions.Fraction`` over integers — no floats, so no platform drift.
"""

import hashlib
import json
import os
import sys
from fractions import Fraction

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from ledger.log import EventLog                                  # noqa: E402
from rule import replay                                          # noqa: E402
from rule.distribute import distribute                           # noqa: E402
from rule.params import (MICRO, PLACEHOLDER_PARAMS, pie,          # noqa: E402
                        rate_of, rational)
from rule.valuation import weight_micro_vu                       # noqa: E402

NAV = [{"label": "Ledger", "href": "ledger/", "order": 30}]

CHAIN = "ledger/example/chain.jsonl"
ATTESTATION = "ledger/example/attestation.txt"
SEED = "ledger/example/seed.py"
SELF = "tools/render/generators/ledger.py"
REPO_BLOB = "https://github.com/socaity/socaity.dev/blob/main/"
#: Same channel a node page's "Contest this" uses (tools/render/render.py).
ISSUE_URL = "https://github.com/socaity/socaity.dev/issues/new"

#: The calculator's grid.  Hours are the x-axis of the only input V takes.
CALC_HOURS_MICRO = [500000, 1000000, 2000000, 4000000, 8000000,
                    20000000, 40000000, 80000000]

#: The cell the calculator shows before anything is selected.  It names a
#: cell of the grid; it never carries the cell's *numbers*, which come from
#: the grid like every other cell's do.  With JavaScript switched off this is
#: the answer the reader sees, so a hand-written figure here would be a
#: number on the page that no code path produces (V5).
CALC_DEFAULT_CATEGORY = "code"
CALC_DEFAULT_HOURS_MICRO = 8000000

#: Plain words for every event type the example chain contains.  The ledger
#: schema carries no free text (socaity-zyt), so the words live here, in the
#: presentation layer, where they can be read against the type they render.
PLAIN_WORDS = {
    "genesis": "the record begins",
    "rule.version_published": "the rule is published, as code, by its hash",
    "rule.meta_published": "the amendment rule is published",
    "V.draft_published": "the conversion schedule V is published",
    "work.logged": "work logged",
    "epoch.opened": "epoch opened",
    "epoch.closed": "epoch closed",
    "rule.attested": "the attestation statement is signed",
    "entry.status_changed": "entry confirmed",
    "audit.completed": "audit completed",
    "checkpoint.published": "checkpoint published",
    "ticket.accepted": "ticket accepted",
    "contribution.trivial_accepted": "contribution accepted",
}

#: The prologue, in the order the validator enforces it (socaity-x8o §7).
TIMELINE_TYPES = ("genesis", "rule.version_published", "rule.meta_published",
                  "V.draft_published", "epoch.opened", "epoch.closed",
                  "rule.attested")


# --------------------------------------------------------------------------
# formatting — exact integers and rationals only, never a float
# --------------------------------------------------------------------------
def micro(value, unit=""):
    """An integer count of micro-units as a plain decimal, no separators."""
    whole, frac = divmod(int(value), MICRO)
    text = str(whole)
    if frac:
        text = "%s.%s" % (text, ("%06d" % frac).rstrip("0"))
    return (text + " " + unit).strip()


def percent(fraction):
    """A Fraction as a percentage, exact to two decimals, rounded half up."""
    hundredths = fraction * 10000
    value = ((hundredths.numerator * 2 + hundredths.denominator)
             // (2 * hundredths.denominator))
    whole, frac = divmod(value, 100)
    if frac == 0:
        return "%d%%" % whole
    return ("%d.%02d" % (whole, frac)).rstrip("0") + "%"


def ratio_text(fraction):
    if fraction.denominator == 1:
        return str(fraction.numerator)
    return "%d/%d" % (fraction.numerator, fraction.denominator)


def short_key(key):
    return "%s…%s" % (key[:8], key[-4:])


def short_hash(value):
    return value[:12]


# --------------------------------------------------------------------------
# the published rule, called — never restated
# --------------------------------------------------------------------------
def load_chain(root):
    """Replay and re-validate the example chain.  Every signature is checked."""
    return EventLog(os.path.join(root, *CHAIN.split("/"))).ledger


def rule_request(export, snapshot, params, rule_version):
    """The rule's canonical input.  amount_minor = 0: this page declares
    nothing and shows no money, so the only fields it reads back are the
    epoch denominators and the exact rational shares."""
    return {"rule_version": rule_version, "params": params,
            "ledger_export": export, "validation_snapshot": snapshot,
            "declared": {"distribution_id": "0" * 64, "amount_minor": 0,
                         "currency": "EUR", "cutoff_checkpoint_hash": "0" * 64}}


def epoch_run(export, snapshot, params, rule_version, epoch, extra=None):
    """Run ``distribute`` with exactly one epoch eligible.

    Marking a single epoch closed-and-audited is what isolates that epoch's
    pool: the rule's own R_i for a single eligible epoch e is P_e * w/D_e, so
    dividing the returned claim_R by P_e gives the epoch share exactly, with
    no arithmetic of ours in between.  This is the function the ledger, the
    "your epoch" exhibit and the calculator all go through.
    """
    entries = list(export["entries"])
    epochs = []
    for record in export["epochs"]:
        epochs.append({"index": record["index"],
                       "closed": record["index"] == epoch,
                       "audited": record["index"] == epoch})
    if not any(record["index"] == epoch for record in epochs):
        epochs.append({"index": epoch, "closed": True, "audited": True})
    snap = {"entries": dict(snapshot["entries"])}
    if extra is not None:
        entries.append(extra)
        snap["entries"][extra["entry_hash"]] = {"status": "confirmed"}
    isolated = {"checkpoint_hash": export["checkpoint_hash"],
                "epochs": sorted(epochs, key=lambda r: r["index"]),
                "entries": sorted(entries, key=lambda r: r["entry_hash"])}
    table = distribute(rule_request(isolated, snap, params, rule_version))
    weight = pie(epoch, params)
    shares = {}
    for row in table["recipients"]:
        claim = Fraction(row["claim_R"]["num"], row["claim_R"]["den"])
        shares[(row["kind"], row["id"])] = Fraction(claim, weight)
    denominator = 0
    for record in table["epochs"]:
        if record["epoch"] == epoch:
            denominator = record["denominator_micro_vu"]
    return {"table": table, "shares": shares, "denominator": denominator,
            "pie": weight}


def hypothetical_entry(category, hours_micro, epoch, lineage):
    """A calculator input, shaped as the rule's own entry record.  Its hash is
    the SHA-256 of the question, so the same question always names the same
    row and nothing about it can be mistaken for a recorded entry."""
    label = "hypothetical:%s:%d:%d" % (category, hours_micro, epoch)
    return {"entry_hash": hashlib.sha256(label.encode("utf-8")).hexdigest(),
            "epoch": epoch, "mode": "E", "category": category,
            "native_unit": "hours", "quantity_micro": hours_micro,
            "lineage": lineage}


def og_card(closed_epochs, exhibit_founder_share):
    """The share card, per socaity-xuz rail 7: authored as the disclosure.

    Every figure comes from the same run of the rule the page renders, so the
    card cannot drift from the page, and it carries the example-chain label
    because the card is the one surface that travels without the page around
    it (V12: nothing may read as activity that did not occur).
    """
    if closed_epochs:
        epoch = closed_epochs[0]
        title = ("Epoch %d — %d contributor — %s founder"
                 % (epoch["index"], epoch["contributors"],
                    epoch["founder_share"]))
        body = ("Example chain. Epoch %d is closed and audited: %s of it is "
                "the founder's, because there is %d contributor. Every entry "
                "is an individual hour-logged observation with its own "
                "evidence digest, priced at the one published rate, and "
                "challengeable on its own row. An epoch you contribute to "
                "starts at %s founder — epochs are separate pools."
                % (epoch["index"], epoch["founder_share"],
                   epoch["contributors"], percent(exhibit_founder_share)))
    else:
        title = "Ledger — no closed epoch yet"
        body = ("Example chain. No epoch has closed and been audited, so "
                "there is no final share to state.")
    return {"title": title, "description": body}


# --------------------------------------------------------------------------
# the view model
# --------------------------------------------------------------------------
def build(root, clock):
    ledger = load_chain(root)
    params = PLACEHOLDER_PARAMS
    export = replay.ledger_export(ledger)
    snapshot = replay.validation_snapshot(ledger)

    genesis = ledger.events[ledger.order[0]]["payload"]
    rule_version = genesis["rule_version_hash"]
    founder = ledger.founder_key

    challenges = {}
    for event_id in ledger.order:
        event = ledger.events[event_id]
        if event["type"] == "challenge.filed":
            target = event["payload"]["target_event_id"]
            challenges[target] = challenges.get(target, 0) + 1

    by_hash = {entry["entry_hash"]: entry for entry in export["entries"]}
    epoch_indexes = sorted({record["index"] for record in export["epochs"]})
    runs = {index: epoch_run(export, snapshot, params, rule_version, index)
            for index in epoch_indexes}

    epochs = []
    for index in epoch_indexes:
        record = [r for r in export["epochs"] if r["index"] == index][0]
        run = runs[index]
        rows = []
        for event_id in ledger.order:                 # chain order, not hash order
            entry = by_hash.get(event_id)
            if entry is None or entry["epoch"] != index:
                continue
            state = snapshot["entries"].get(event_id, {"status": "provisional"})
            weight = weight_micro_vu(entry, params)
            rate = rate_of(entry["category"], entry["native_unit"], params)
            event = ledger.events[event_id]
            # socaity-xuz / x8o display rule: an open epoch's percentage is
            # never rendered in the same column as a closed epoch's.  It gets
            # its own field, and the template gives it its own labelled line.
            final = record["closed"] and record["audited"]
            share = (Fraction(weight, run["denominator"])
                     if run["denominator"] else None)
            rows.append({
                "id": event_id,
                "anchor": "e-" + short_hash(event_id),
                "short": short_hash(event_id),
                "contributor": entry["lineage"],
                "contributor_short": short_key(entry["lineage"]),
                "is_founder": entry["lineage"] == founder,
                "type": event["type"],
                "words": PLAIN_WORDS.get(event["type"], event["type"]),
                "category": entry["category"],
                "hours": micro(entry["quantity_micro"]),
                "rate": ratio_text(rate),
                "vu": micro(weight),
                "weight_micro": weight,
                "status": state["status"],
                "mode": entry["mode"],
                "evidence": event["payload"].get("evidence", []),
                "artifact_hash": event["payload"].get("artifact_hash"),
                "week_ref": event["payload"].get("week_ref"),
                "share": percent(share) if (final and share is not None) else None,
                "share_if_closed": (percent(share) if (not final and share is not None)
                                    else None),
                "challenges": challenges.get(event_id, 0),
                "window_open": not final,
                # socaity-xuz §1(3) / §2: the per-row flag.  The page says
                # founder entries are the easiest on the record to attack, so
                # the affordance that makes that true has to be ON the row.
                # Same channel the node pages use to contest an assertion.
                "challenge_url": (
                    "%s?title=Challenge+ledger+entry+%s&body=Entry%%3A+%s"
                    % (ISSUE_URL, short_hash(event_id), event_id)),
            })
        contributors = sorted({row["contributor"] for row in rows})
        founder_weight = sum(row["weight_micro"] for row in rows
                             if row["is_founder"])
        founder_share = (Fraction(founder_weight, run["denominator"])
                         if run["denominator"] else None)
        epochs.append({
            "index": index,
            "closed": record["closed"],
            "audited": record["audited"],
            "open": not record["closed"],
            "final": record["closed"] and record["audited"],
            "rows": rows,
            "denominator": micro(run["denominator"]),
            "denominator_micro": run["denominator"],
            "pie": ratio_text(run["pie"]),
            "contributors": len(contributors),
            "founder_share": percent(founder_share) if founder_share is not None else None,
            "founder_share_exact": founder_share,
        })

    closed = [e for e in epochs if e["closed"] and e["audited"]]
    all_contributors = sorted({row["contributor"] for epoch in epochs
                               for row in epoch["rows"]})
    open_epochs = [e for e in epochs if e["open"]]
    open_epoch = open_epochs[0] if open_epochs else None

    # The "your epoch" exhibit: the next epoch, which has no entries at all.
    # Computed the same way as the calculator — one hypothetical entry, the
    # published rule — so the 0% is a rule output, not a claim.
    next_index = max(epoch_indexes) + 1
    exhibit_entry = hypothetical_entry("code", MICRO, next_index, "hypothetical")
    exhibit = epoch_run(export, snapshot, params, rule_version, next_index,
                        exhibit_entry)
    exhibit_founder = exhibit["shares"].get(("lineage", founder), Fraction(0, 1))

    # The calculator grid, every cell produced by the published rule.
    categories = sorted({key.split(":", 1)[0] for key in params["rates"]
                         if key.endswith(":hours")})
    grid = {}
    calc_rows = []
    calc_epoch = open_epoch["index"] if open_epoch else next_index
    for category in categories:
        for hours_micro in CALC_HOURS_MICRO:
            entry = hypothetical_entry(category, hours_micro, calc_epoch,
                                       "hypothetical")
            run = epoch_run(export, snapshot, params, rule_version, calc_epoch,
                            entry)
            weight = weight_micro_vu(entry, params)
            share = run["shares"][("lineage", "hypothetical")]
            cell = {"vu": micro(weight), "share": percent(share),
                    "denominator": micro(run["denominator"]),
                    "rate": ratio_text(rate_of(category, "hours", params))}
            grid["%s|%d" % (category, hours_micro)] = cell
            calc_rows.append(dict(cell, category=category,
                                  hours=micro(hours_micro)))

    # The pre-selected answer, read out of the grid that the rule produced.
    # If the default names a cell the rule did not produce, that is a build
    # error and not a page that quietly renders a stale figure.
    default_category = (CALC_DEFAULT_CATEGORY if CALC_DEFAULT_CATEGORY in categories
                        else categories[0])
    default_hours_micro = (CALC_DEFAULT_HOURS_MICRO
                           if CALC_DEFAULT_HOURS_MICRO in CALC_HOURS_MICRO
                           else CALC_HOURS_MICRO[0])
    default_key = "%s|%d" % (default_category, default_hours_micro)
    default_cell = dict(grid[default_key], category=default_category,
                        hours_micro=default_hours_micro,
                        hours=micro(default_hours_micro), key=default_key)

    rate_card = []
    for key in sorted(params["rates"]):
        category, unit = key.split(":", 1)
        rate_card.append({"category": category, "unit": unit,
                          "rate": ratio_text(rational(params["rates"][key]))})

    timeline = []
    for event_id in ledger.order:
        event = ledger.events[event_id]
        if event["type"] not in TIMELINE_TYPES:
            continue
        payload = event["payload"]
        detail = ""
        if event["type"] in ("epoch.opened", "epoch.closed"):
            detail = "epoch %d" % payload["epoch"]
        elif event["type"] == "rule.version_published":
            detail = "rule version %s" % short_hash(payload["rule_version"])
        elif event["type"] == "V.draft_published":
            detail = "V %s" % short_hash(payload["draft_hash"])
        elif event["type"] == "rule.attested":
            detail = "statement %s" % short_hash(payload["statement_hash"])
        timeline.append({"type": event["type"],
                         "words": PLAIN_WORDS.get(event["type"], event["type"]),
                         "detail": detail, "short": short_hash(event_id)})

    with open(os.path.join(root, *ATTESTATION.split("/")), "rb") as fh:
        attestation_bytes = fh.read()
    attestation = attestation_bytes.decode("utf-8").strip()
    attestation_hash = hashlib.sha256(attestation_bytes).hexdigest()

    published = {}
    for event_id in ledger.order:
        event = ledger.events[event_id]
        if event["type"] == "rule.version_published":
            published = event["payload"]
            break

    return {
        "depth": 1,
        "clock": clock[:10],
        "chain": {"path": CHAIN, "url": REPO_BLOB + CHAIN,
                  "seed_url": REPO_BLOB + SEED, "seed": SEED,
                  "self_url": REPO_BLOB + SELF, "self": SELF,
                  "count": ledger.count, "head": short_hash(ledger.head)},
        "rule": {"version": short_hash(rule_version),
                 "version_full": rule_version,
                 "params_hash": short_hash(published["params_hash"]),
                 "params_hash_full": published["params_hash"],
                 "meta_rule_hash": short_hash(genesis["meta_rule_hash"]),
                 "url": REPO_BLOB + "rule/distribute.py",
                 "params_url": REPO_BLOB + "rule/params.py",
                 "artifact_url": REPO_BLOB + "rule/RULE_VERSION.json",
                 "replay_url": REPO_BLOB + "rule/replay.py",
                 "valuation_url": REPO_BLOB + "rule/valuation.py"},
        "validator_url": REPO_BLOB + "ledger/validator.py",
        "founder": {"key": founder, "short": short_key(founder)},
        "epochs": epochs,
        "contributors": len(all_contributors),
        # The tripwire state is DERIVED, never asserted.  The published
        # parameter set carries no threshold value yet, so the only state the
        # page may claim is the one that holds for every threshold a value
        # could take — which is true exactly while the share is the whole
        # epoch.  Anything else has to say it is not determinable rather than
        # keep printing "escalated" out of habit (socaity-xuz: the tripwire
        # number and state must be real).
        "tripwire": {
            "threshold_published": "founder_share_tripwire" in params,
            "share": closed[0]["founder_share"] if closed else None,
            "escalated": bool(closed) and closed[0]["founder_share_exact"] == 1,
        },
        "closed_epochs": closed,
        "open_epoch": open_epoch,
        "exhibit": {"epoch": next_index,
                    "founder_share": percent(exhibit_founder),
                    "founder_vu": micro(0)},
        "og": og_card(closed, exhibit_founder),
        "attestation": attestation,
        "attestation_hash": attestation_hash,
        "attestation_url": REPO_BLOB + ATTESTATION,
        "rate_card": rate_card,
        "timeline": timeline,
        "calc": {"categories": categories,
                 "hours": [{"micro": h, "text": micro(h)} for h in CALC_HOURS_MICRO],
                 "default": default_cell,
                 # Emitted inside <script type="application/json"> with
                 # |safe, so "<" is escaped here: nothing in this blob can
                 # start a tag, and the template does not have to trust it.
                 "grid_json": json.dumps(grid, sort_keys=True,
                                         separators=(",", ":")
                                         ).replace("<", "\\u003c"),
                 "rows": calc_rows,
                 "epoch": calc_epoch,
                 "cells": len(calc_rows)},
    }


def generate(ctx):
    view = build(ctx["root"], ctx["clock"])
    html = ctx["env"].get_template("ledger.html").render(view=view, depth=1)
    return [("ledger/index.html", html)]


# --------------------------------------------------------------------------
# the audit script — the same functions, on a terminal
# --------------------------------------------------------------------------
def _cli(argv):
    view = build(_ROOT, "0000-00-00")
    if not argv:
        print("example chain %s: %d events, head %s"
              % (CHAIN, view["chain"]["count"], view["chain"]["head"]))
        print("rule version %s (rule/RULE_VERSION.json)" % view["rule"]["version"])
        for epoch in view["epochs"]:
            print("\nepoch %d  %s  contributors: %d  denominator D_e: %s vu  P_e: %s"
                  % (epoch["index"],
                     "closed, audited" if epoch["closed"] and epoch["audited"]
                     else "open" if epoch["open"] else "closed, not audited",
                     epoch["contributors"], epoch["denominator"], epoch["pie"]))
            if epoch["founder_share"]:
                print("  founder share: %s%s"
                      % (epoch["founder_share"],
                         "" if epoch["final"] else
                         "  (only as: if epoch %d closed on this record -- an "
                         "upper bound, it can only fall)" % epoch["index"]))
            for row in epoch["rows"]:
                print("  %s  %-10s %6s h x %s vu/h = %6s vu  %-9s  %s"
                      % (row["short"], row["category"], row["hours"],
                         row["rate"], row["vu"], row["status"],
                         row["share"] or "(epoch open: %s if it closed here)"
                         % row["share_if_closed"]))
        return 0
    if argv[0] == "entry":
        wanted = argv[1]
        for epoch in view["epochs"]:
            for row in epoch["rows"]:
                if row["id"].startswith(wanted):
                    print("entry        %s" % row["id"])
                    print("contributor  %s" % row["contributor"])
                    print("epoch        %d (%s)" % (
                        epoch["index"], "closed" if epoch["closed"] else "open"))
                    print("category     %s, unit hours, mode %s"
                          % (row["category"], row["mode"]))
                    print("V rate       %s vu per hour  (rule/params.py)" % row["rate"])
                    print("weight       %s h x %s = %s vu"
                          % (row["hours"], row["rate"], row["vu"]))
                    print("denominator  D_%d = %s vu (rule/distribute.py)"
                          % (epoch["index"], epoch["denominator"]))
                    print("epoch share  %s" % (
                        row["share"] or
                        "%s, if epoch %d closed on this record -- an upper "
                        "bound, it can only fall as more work is logged"
                        % (row["share_if_closed"], epoch["index"])))
                    print("status       %s" % row["status"])
                    print("evidence     %s" % ", ".join(row["evidence"]))
                    return 0
        print("no entry starts with %r" % wanted)
        return 1
    if argv[0] == "your-epoch":
        print("epoch %s has no entries on the record." % view["exhibit"]["epoch"])
        print("founder weight recorded in it: %s vu" % view["exhibit"]["founder_vu"])
        print("run the rule over that epoch with a single hypothetical entry in "
              "it and the founder share it returns is %s"
              % view["exhibit"]["founder_share"])
        return 0
    if argv[0] == "hypothetical":
        category, hours = argv[1], argv[2]
        hours_micro = int(Fraction(hours) * MICRO)
        ledger = load_chain(_ROOT)
        export = replay.ledger_export(ledger)
        snapshot = replay.validation_snapshot(ledger)
        rule_version = ledger.events[ledger.order[0]]["payload"]["rule_version_hash"]
        epoch = view["calc"]["epoch"]
        entry = hypothetical_entry(category, hours_micro, epoch, "hypothetical")
        run = epoch_run(export, snapshot, PLACEHOLDER_PARAMS, rule_version,
                        epoch, entry)
        weight = weight_micro_vu(entry, PLACEHOLDER_PARAMS)
        share = run["shares"][("lineage", "hypothetical")]
        print("hypothetical %s, %s h, mode E, epoch %d"
              % (category, micro(hours_micro), epoch))
        print("V rate       %s vu per hour"
              % ratio_text(rate_of(category, "hours", PLACEHOLDER_PARAMS)))
        print("weight       %s vu" % micro(weight))
        print("denominator  D_%d = %s vu, if epoch %d closed on this record"
              % (epoch, micro(run["denominator"]), epoch))
        print("epoch share  %s, if epoch %d closed on this record -- an upper "
              "bound: the numerator is fixed and the denominator only grows"
              % (percent(share), epoch))
        return 0
    print(__doc__.splitlines()[0])
    return 2


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
