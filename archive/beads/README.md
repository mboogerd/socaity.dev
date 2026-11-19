# Retired Beads archive

Beads and the autonomous backlog workflow were retired on 19 November 2026 at the project owner's request. These records are historical context, not a live queue. Pending and in-progress statuses describe the snapshot; they do not authorize further work.

- `issues.jsonl`: explicit `bd export --all` snapshot containing 181 issues (including dependencies and comments) and one persistent memory.
- `interactions.jsonl`: the existing interaction audit trail.
- `integration/`: former Beads configuration and Git hooks, agent instructions, context hooks, backlog skills, and worker preflight tooling. They are outside the active configuration paths.

The issue export supports reading and migration; it is not a full Dolt database backup. The original local `.beads/` directory, including its embedded database and existing backups, is retained in the ignored `local-state/` directory in the original checkout. It is intentionally not published in Git or included in the website. Existing remote Dolt history is left intact.

The Codex automation “Autonomously Develop Socaity.dev” was already paused when the archive was made. The former GitHub Actions workflows, including the scheduled drift and digest jobs, have been removed. Only `.github/workflows/pages.yml` publishes the website.

Do not run these archived instructions or restore the queue as part of ordinary website work. To inspect an issue, search `issues.jsonl` for its ID. Legacy research documents retain their historical issue references.
