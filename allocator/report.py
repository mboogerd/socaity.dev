# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 MacBoo

"""Replay allocator declarations and spend into a deterministic digest."""

from __future__ import annotations

import argparse
import datetime as _datetime
import json
import subprocess
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Mapping

from .allocation import AllocationError, validate_allocation
from .spend_log import SpendLog, ValidationError
from tools.gates.miniyaml import YAMLSubsetError, loads


class ReportError(ValueError):
    """Raised when the replay inputs cannot produce a report."""


def _timestamp(value: str) -> _datetime.datetime:
    try:
        return _datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReportError(f"invalid timestamp: {value}") from exc


@dataclass(frozen=True)
class AllocationRevision:
    committed: _datetime.datetime
    commit: str
    allocation: dict[str, Any]


def load_allocation_history(repo: str | Path, path: str = "allocation.yaml") -> list[AllocationRevision]:
    """Read every committed allocation revision in chronological order."""

    root = Path(repo)
    try:
        raw = subprocess.run(
            ["git", "-C", str(root), "log", "--reverse", "--format=%H%x00%cI", "--", path],
            check=True, capture_output=True, text=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReportError(f"cannot read allocation history: {exc}") from exc
    revisions: list[AllocationRevision] = []
    for line in raw.splitlines():
        if not line:
            continue
        commit, committed = line.split("\0", 1)
        try:
            text = subprocess.run(
                ["git", "-C", str(root), "show", f"{commit}:{path}"],
                check=True, capture_output=True, text=True,
            ).stdout
            allocation = validate_allocation(loads(text))
        except (OSError, subprocess.CalledProcessError, YAMLSubsetError, AllocationError) as exc:
            raise ReportError(f"invalid allocation at {commit[:12]}: {exc}") from exc
        revisions.append(AllocationRevision(_timestamp(committed), commit, allocation))
    if not revisions:
        raise ReportError(f"no committed allocation history for {path}")
    return revisions


def _effective(revisions: list[AllocationRevision], at: _datetime.datetime) -> AllocationRevision:
    selected = None
    for revision in revisions:
        if revision.committed <= at:
            selected = revision
        else:
            break
    if selected is None:
        raise ReportError(f"no allocation declaration precedes {at.isoformat()}")
    return selected


def _hours(started: _datetime.datetime, ended: _datetime.datetime) -> Decimal:
    return Decimal(str((ended - started).total_seconds())) / Decimal(3600)


def _month_bounds(moment: _datetime.datetime) -> tuple[_datetime.datetime, _datetime.datetime]:
    start = moment.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start.month == 12:
        next_month = start.replace(year=start.year + 1, month=1)
    else:
        next_month = start.replace(month=start.month + 1)
    return start, next_month


def _decimal_text(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


def replay(repo: str | Path, spend_log: str | Path, *, at: _datetime.datetime | None = None) -> dict[str, Any]:
    """Replay the committed allocation history and a spend log into JSON data."""

    revisions = load_allocation_history(repo)
    try:
        records = list(SpendLog(spend_log).records())
    except ValidationError as exc:
        raise ReportError(f"invalid spend log: {exc}") from exc
    cutoff = at or _datetime.datetime.now(_datetime.timezone.utc)
    sessions = []
    for record in records:
        started = _timestamp(record["started"])
        ended = _timestamp(record["ended"])
        if ended > cutoff:
            continue
        declaration = _effective(revisions, started)
        sessions.append((record, started, ended, declaration))
    projects: set[str] = set()
    for _, _, _, declaration in sessions:
        projects.update(declaration.allocation["weights"])
    for record, _, _, _ in sessions:
        projects.add(record["project"])
        projects.update(record.get("starved", []))
    rows: dict[str, dict[str, Any]] = {}
    for project in sorted(projects):
        rows[project] = {"declared_hours": Decimal(0), "enacted_hours": Decimal(0),
                         "starvation_events": 0, "starvation_days": 0}
    starvation_dates: dict[str, set[str]] = {project: set() for project in projects}
    total = Decimal(0)
    cap = None
    first = min((started for _, started, _, _ in sessions), default=None)
    last = max((ended for _, _, ended, _ in sessions), default=None)
    for record, started, ended, declaration in sessions:
        duration = _hours(started, ended)
        total += duration
        weights = declaration.allocation["weights"]
        for project, ratio in weights.items():
            rows[project]["declared_hours"] += duration * Decimal(ratio)
        rows[record["project"]]["enacted_hours"] += duration
        for project in record.get("starved", []):
            rows[project]["starvation_events"] += 1
            starvation_dates[project].add(started.date().isoformat())
        cap = Decimal(declaration.allocation["monthly_cap"]["hours"])
    for project, row in rows.items():
        row["starvation_days"] = len(starvation_dates[project])
        row["declared_share"] = (row["declared_hours"] / total if total else Decimal(0))
        row["enacted_share"] = (row["enacted_hours"] / total if total else Decimal(0))
        for key in ("declared_hours", "enacted_hours", "declared_share", "enacted_share"):
            row[key] = _decimal_text(row[key])
    projection = None
    if first is not None and last is not None and cap is not None:
        month_start, month_end = _month_bounds(last)
        elapsed = max((last - month_start).total_seconds(), 1)
        projection = total * Decimal(str((month_end - month_start).total_seconds())) / Decimal(str(elapsed))
    return {"from": first.isoformat().replace("+00:00", "Z") if first else None,
            "to": last.isoformat().replace("+00:00", "Z") if last else None,
            "sessions": len(sessions), "hours": _decimal_text(total),
            "monthly_cap_hours": _decimal_text(cap) if cap is not None else None,
            "projected_month_end_hours": _decimal_text(projection) if projection is not None else None,
            "projects": rows}


def render_report(data: Mapping[str, Any]) -> str:
    """Render replay data as stable, human-readable Markdown."""
    lines = [f"# Allocator report ({data['from'] or 'empty'} to {data['to'] or 'empty'})", "",
             f"Sessions: {data['sessions']}; enacted hours: {data['hours']}",
             f"Cap: {data['monthly_cap_hours'] or 'unknown'} hours; projected month-end burn: "
             f"{data['projected_month_end_hours'] or 'unknown'} hours", "", 
             "| Project | Declared share | Enacted share | Enacted hours | Starvation |",
             "| --- | ---: | ---: | ---: | --- |"]
    for project, row in data["projects"].items():
        starvation = f"{row['starvation_events']} events on {row['starvation_days']} days"
        lines.append(f"| {project} | {row['declared_share']} | {row['enacted_share']} | "
                     f"{row['enacted_hours']} | {starvation} |")
    return "\n".join(lines) + "\n"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--spend-log", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    data = replay(args.repo, args.spend_log)
    print(json.dumps(data, indent=2, sort_keys=True) if args.json else render_report(data), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
