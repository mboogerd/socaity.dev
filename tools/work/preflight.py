#!/usr/bin/env python3
"""Check the shared task source and publication access before claiming work."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


def executable(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    # Non-login desktop shells need not inherit Homebrew's PATH.
    for directory in ("/opt/homebrew/bin", "/usr/local/bin", "/usr/bin"):
        candidate = Path(directory) / name
        if candidate.is_file():
            return str(candidate)
    raise RuntimeError(f"Missing required executable: {name}")


def run(root: Path, command: list[str]) -> str:
    result = subprocess.run(command, cwd=root, text=True, capture_output=True,
                            timeout=60, check=False)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"{' '.join(command)} failed ({result.returncode}): {detail}")
    return result.stdout


def preflight(root: Path) -> None:
    git, bd, gh = (executable(name) for name in ("git", "bd", "gh"))
    remote = run(root, [git, "remote", "get-url", "origin"]).strip()
    if remote not in ("https://github.com/mboogerd/socaity.dev.git",
                      "git@github.com:mboogerd/socaity.dev.git"):
        raise RuntimeError(f"Unexpected origin: {remote}; expected mboogerd/socaity.dev")
    # Run from the shared repository: worktrees do not own independent task DBs.
    run(root, [bd, "dolt", "pull"])
    run(root, [git, "fetch", "origin", "main"])
    permissions = json.loads(run(root, [gh, "repo", "view", "mboogerd/socaity.dev",
                                       "--json", "viewerPermission"]))
    if permissions.get("viewerPermission") not in ("WRITE", "MAINTAIN", "ADMIN"):
        raise RuntimeError("GitHub account lacks branch/PR write access to mboogerd/socaity.dev")
    print("PASS: Beads synced, origin/main fetched, GitHub write access confirmed.")
    print("Load the work skills from origin/main; preserve shared checkout changes.")
    print("Network/auth checks do not prove a future approval or merge will succeed.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True,
                        help="Shared socaity.dev checkout containing the Beads database")
    args = parser.parse_args()
    try:
        preflight(args.root.resolve())
    except (RuntimeError, subprocess.TimeoutExpired, OSError, ValueError) as exc:
        print(f"PIPELINE PREFLIGHT FAILED: {exc}", file=sys.stderr)
        print("If DNS/network failed inside the sandbox, retry this exact preflight once "
              "through the runner's approved network escalation. A denial, auth error, "
              "or second failure ends the slot before claiming. Unattended runs need "
              "the project's socaity-work permission profile (network and Git writes).",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
