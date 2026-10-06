# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 MacBoo

"""Stateless weighted project selection for allocator worker slots."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import random
from typing import Any, Iterable, Mapping


class DrawError(ValueError):
    """Raised when a draw input cannot describe a valid allocation."""


def _decimal(value: Any, field: str) -> Decimal:
    if isinstance(value, bool):
        raise DrawError(f"{field} must be a finite number")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise DrawError(f"{field} must be a finite number") from None
    if not result.is_finite():
        raise DrawError(f"{field} must be a finite number")
    return result


@dataclass(frozen=True)
class DrawDecision:
    """The complete outcome of one allocator slot decision.

    ``starved`` is the raw R5 evidence: projects with a declared positive
    weight that had no ready work in this draw.  It is returned even when
    spillover leaves only one project eligible.
    """

    project: str | None
    starved: tuple[str, ...] = ()
    reason: str = "drawn"

    @property
    def cap_hit(self) -> bool:
        return self.reason == "cap-hit"

    def as_record(self) -> dict[str, Any]:
        """Return a stable, JSON-compatible record for an observation log."""

        return {
            "project": self.project,
            "starved": list(self.starved),
            "reason": self.reason,
        }


def draw_project(
    weights: Mapping[str, Any],
    ready: Iterable[str],
    seed: int,
    *,
    spent_hours: Any = 0,
    monthly_cap: Any | None = None,
) -> DrawDecision:
    """Select one ready project using a deterministic weighted lottery.

    Weights are renormalized over ready projects (spillover).  A positive
    weight whose project is absent from ``ready`` is reported in
    :attr:`DrawDecision.starved`.  If ``monthly_cap`` is supplied and the
    already enacted hours meet it, no lottery is performed.
    """

    if not isinstance(weights, Mapping) or not weights:
        raise DrawError("weights must be a non-empty mapping")
    checked: dict[str, Decimal] = {}
    for project, value in weights.items():
        if not isinstance(project, str) or not project.strip():
            raise DrawError("weight project names must be non-empty strings")
        ratio = _decimal(value, f"weights.{project}")
        if ratio < 0:
            raise DrawError(f"weights.{project} must not be negative")
        checked[project] = ratio
    if sum(checked.values(), Decimal(0)) <= 0:
        raise DrawError("weights must contain a positive total")

    if monthly_cap is not None:
        cap = _decimal(monthly_cap, "monthly_cap")
        spent = _decimal(spent_hours, "spent_hours")
        if cap <= 0:
            raise DrawError("monthly_cap must be positive")
        if spent < 0:
            raise DrawError("spent_hours must not be negative")
        if spent >= cap:
            return DrawDecision(None, reason="cap-hit")

    ready_set = set(ready)
    if any(not isinstance(project, str) or not project.strip() for project in ready_set):
        raise DrawError("ready project names must be non-empty strings")
    starved = tuple(project for project, ratio in checked.items()
                    if ratio > 0 and project not in ready_set)
    eligible = [(project, ratio) for project, ratio in checked.items()
                if ratio > 0 and project in ready_set]
    if not eligible:
        return DrawDecision(None, starved=starved, reason="no-ready-work")

    total = sum((ratio for _, ratio in eligible), Decimal(0))
    ticket = Decimal(str(random.Random(seed).random())) * total
    cumulative = Decimal(0)
    for project, ratio in eligible:
        cumulative += ratio
        if ticket < cumulative:
            return DrawDecision(project, starved=starved)
    # Decimal conversion and random's upper bound make this unreachable, but
    # retaining a final item keeps the function total if the RNG changes.
    return DrawDecision(eligible[-1][0], starved=starved)


__all__ = ["DrawDecision", "DrawError", "draw_project"]
