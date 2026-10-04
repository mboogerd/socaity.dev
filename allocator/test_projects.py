# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 MacBoo

import unittest
from pathlib import Path

from allocator.projects import ProjectsError, load_projects, validate_projects


ROOT = Path(__file__).parents[1]


class TestProjects(unittest.TestCase):
    def test_registry_lists_the_three_worker_projects(self):
        registry = load_projects(ROOT / "projects.yaml")
        self.assertEqual(
            [project["name"] for project in registry["projects"]],
            ["socaity.dev", "glass-factory", "computenet"],
        )
        for project in registry["projects"]:
            source = project["task_source"]
            self.assertEqual(source["type"], "beads")
            self.assertEqual(source["sync"], "bd dolt pull")
            self.assertEqual(source["ready"], "bd ready --json")

    def test_rejects_duplicate_projects(self):
        document = load_projects(ROOT / "projects.yaml")
        document["projects"].append(document["projects"][0])
        with self.assertRaisesRegex(ProjectsError, "duplicate project"):
            validate_projects(document)

    def test_rejects_task_source_without_ready_command(self):
        document = load_projects(ROOT / "projects.yaml")
        del document["projects"][0]["task_source"]["ready"]
        with self.assertRaises(ProjectsError):
            validate_projects(document)


if __name__ == "__main__":
    unittest.main()
