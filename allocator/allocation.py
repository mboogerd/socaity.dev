# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 MacBoo

"""Schema and validation for the allocator's declared weights artifact."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

from tools.gates.miniyaml import YAMLSubsetError, loads


SCHEMA_VERSION = 1
REQUIRED_FIELDS = frozenset(("schema", "window", "monthly_cap", "weights"))


class AllocationError(ValueError):
    """Raised when an allocation artifact does not satisfy schema v1."""


def _decimal(value: Any, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise AllocationError(f"{field} must be a number")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise AllocationError(f"{field} must be a number") from exc
    if not result.is_finite():
        raise AllocationError(f"{field} must be finite")
    return result


def validate_allocation(document: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a copy of one schema-v1 allocation document."""

    if not isinstance(document, Mapping):
        raise AllocationError("allocation must be a mapping")
    if set(document) != REQUIRED_FIELDS:
        raise AllocationError(
            "allocation fields must be exactly: " + ", ".join(sorted(REQUIRED_FIELDS))
        )
    if document["schema"] != SCHEMA_VERSION or isinstance(document["schema"], bool):
        raise AllocationError("schema must be the integer version 1")
    if not isinstance(document["window"], str) or not document["window"].strip():
        raise AllocationError("window must be a non-empty string")

    cap = document["monthly_cap"]
    if not isinstance(cap, Mapping) or set(cap) != {"hours"}:
        raise AllocationError("monthly_cap must contain exactly hours")
    hours = _decimal(cap["hours"], "monthly_cap.hours")
    if hours <= 0:
        raise AllocationError("monthly_cap.hours must be positive")

    weights = document["weights"]
    if not isinstance(weights, Mapping) or not weights:
        raise AllocationError("weights must be a non-empty mapping")
    total = Decimal(0)
    checked_weights: dict[str, str] = {}
    for project, value in weights.items():
        if not isinstance(project, str) or not project.strip():
            raise AllocationError("weight project names must be non-empty strings")
        ratio = _decimal(value, f"weights.{project}")
        if ratio < 0 or ratio > 1:
            raise AllocationError(f"weights.{project} must be between 0 and 1")
        total += ratio
        checked_weights[project] = str(ratio)
    if total != Decimal(1):
        raise AllocationError(f"weights must sum exactly to 1 (got {total})")

    return {
        "schema": SCHEMA_VERSION,
        "window": document["window"],
        "monthly_cap": {"hours": str(hours)},
        "weights": checked_weights,
    }


def load_allocation(path: str | Path) -> dict[str, Any]:
    """Parse and validate an allocation YAML file."""

    try:
        document = loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, YAMLSubsetError) as exc:
        raise AllocationError(f"cannot read allocation: {exc}") from exc
    return validate_allocation(document)


__all__ = ["AllocationError", "load_allocation", "validate_allocation"]
