# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 MacBoo

"""Schema and validation for the allocator's project registry."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from tools.gates.miniyaml import YAMLSubsetError, loads


SCHEMA_VERSION = 1
REQUIRED_PROJECT_FIELDS = frozenset(("name", "code_repo", "task_source", "runner"))
REQUIRED_TASK_SOURCE_FIELDS = frozenset(("type", "repo", "sync", "ready"))


class ProjectsError(ValueError):
    """Raised when a project registry does not satisfy schema v1."""


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProjectsError(f"{field} must be a non-empty string")
    return value


def validate_projects(document: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and return a normalized copy of one schema-v1 registry."""

    if not isinstance(document, Mapping):
        raise ProjectsError("projects registry must be a mapping")
    if set(document) != {"schema", "projects"}:
        raise ProjectsError("registry fields must be exactly: projects, schema")
    if document["schema"] != SCHEMA_VERSION or isinstance(document["schema"], bool):
        raise ProjectsError("schema must be the integer version 1")

    projects = document["projects"]
    if not isinstance(projects, list) or not projects:
        raise ProjectsError("projects must be a non-empty sequence")

    checked: list[dict[str, Any]] = []
    names: set[str] = set()
    for index, project in enumerate(projects):
        prefix = f"projects[{index}]"
        if not isinstance(project, Mapping) or set(project) != REQUIRED_PROJECT_FIELDS:
            raise ProjectsError(
                f"{prefix} fields must be exactly: "
                + ", ".join(sorted(REQUIRED_PROJECT_FIELDS))
            )
        name = _text(project["name"], f"{prefix}.name")
        if name in names:
            raise ProjectsError(f"duplicate project name: {name}")
        names.add(name)
        code_repo = _text(project["code_repo"], f"{prefix}.code_repo")
        runner = _text(project["runner"], f"{prefix}.runner")

        source = project["task_source"]
        if not isinstance(source, Mapping) or set(source) != REQUIRED_TASK_SOURCE_FIELDS:
            raise ProjectsError(
                f"{prefix}.task_source fields must be exactly: "
                + ", ".join(sorted(REQUIRED_TASK_SOURCE_FIELDS))
            )
        checked_source = {
            key: _text(source[key], f"{prefix}.task_source.{key}")
            for key in sorted(REQUIRED_TASK_SOURCE_FIELDS)
        }
        if checked_source["type"] != "beads":
            raise ProjectsError(f"{prefix}.task_source.type must be beads")
        checked.append({
            "name": name,
            "code_repo": code_repo,
            "task_source": checked_source,
            "runner": runner,
        })

    return {"schema": SCHEMA_VERSION, "projects": checked}


def load_projects(path: str | Path) -> dict[str, Any]:
    """Parse and validate a project registry YAML file."""

    try:
        document = loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, YAMLSubsetError) as exc:
        raise ProjectsError(f"cannot read projects registry: {exc}") from exc
    return validate_projects(document)


__all__ = ["ProjectsError", "load_projects", "validate_projects"]
