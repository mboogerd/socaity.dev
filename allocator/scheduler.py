# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 MacBoo

"""Composition layer for one allocator worker slot."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from .allocation import load_allocation
from .draw import DrawDecision, draw_project
from .projects import load_projects
from .session import run_session
from .spend_log import SpendLog


class Scheduler:
    """Load the MVP artifacts and enact one independent worker slot.

    Task discovery and execution are callbacks because each project owns its
    own beads repository and runner.  This keeps the allocator stateless and
    makes the boundary testable without embedding a shell or credentials.
    """

    def __init__(self, projects: dict[str, Any], allocation: dict[str, Any], log: SpendLog):
        self.projects = projects
        self.allocation = allocation
        self.log = log

    @classmethod
    def from_files(cls, projects_path: str | Path, allocation_path: str | Path,
                   spend_log: str | Path) -> "Scheduler":
        return cls(load_projects(projects_path), load_allocation(allocation_path),
                   SpendLog(spend_log))

    def slot(self, machine: str, seed: int, ready: Iterable[str],
             next_item: Callable[[str], str], run: Callable[[str, str], Any],
             *, spent_hours: Any = 0, clock: Callable[[], Any] | None = None) -> DrawDecision:
        """Draw and, when possible, execute exactly one project work item."""

        decision = draw_project(
            self.allocation["weights"], ready, seed,
            spent_hours=spent_hours,
            monthly_cap=self.allocation["monthly_cap"]["hours"],
        )
        if decision.project is None:
            return decision
        work_item = next_item(decision.project)
        run_session(
            self.log, decision.project, machine, work_item,
            lambda: run(decision.project, work_item), clock=clock,
            starved=list(decision.starved), reason=decision.reason,
        )
        return decision


__all__ = ["Scheduler"]
