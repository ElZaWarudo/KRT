#!/usr/bin/env python3
"""Report Jira env readiness using the checkout-local jira-scribe env contract."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


REQUIRED_VARS = ("JIRA_HOST", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY")
OPTIONAL_VARS = ("JIRA_EMAIL", "JIRA_BOARD_ID")

ENV_DIR = Path(".krt/env")
IGNORE_PATH = ENV_DIR / ".gitignore"
SECRET_PATH = ENV_DIR / "jira-scribe.env"
EXAMPLE_PATH = ENV_DIR / "jira-scribe.env.example"


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def bool_map(names: tuple[str, ...]) -> dict[str, bool]:
    return {name: bool(os.environ.get(name)) for name in names}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Consumer project root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when required Jira variables are missing.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        print(json.dumps({"ok": False, "reason": "root-not-directory"}))
        return 1

    required_present = bool_map(REQUIRED_VARS)
    optional_present = bool_map(OPTIONAL_VARS)
    missing_required = [name for name, present in required_present.items() if not present]

    worktree = git(root, "rev-parse", "--show-toplevel")
    in_git = worktree.returncode == 0

    secret = root / SECRET_PATH
    example = root / EXAMPLE_PATH
    ignore = root / IGNORE_PATH

    secret_ignored = False
    if in_git:
        ignored = git(root, "check-ignore", "-q", str(SECRET_PATH))
        secret_ignored = ignored.returncode == 0

    diagnosis = "ready"
    next_step = "Proceed with Jira API verification."
    warnings: list[str] = []
    secret_exists = secret.exists()
    config_ready = secret_exists and not missing_required

    if not secret_exists and not missing_required:
        diagnosis = "env-loaded-without-project-secret-file"
        next_step = "Create .krt/env/jira-scribe.env for this checkout, load it, and rerun the check."
        warnings.append("required-vars-present-without-project-secret-file")

    if not config_ready:
        if secret_exists and missing_required and not any(required_present.values()):
            diagnosis = "env-file-present-but-not-loaded"
            next_step = (
                "Load .krt/env/jira-scribe.env into the shell (for example via direnv) "
                "and rerun the check."
            )
        elif secret_exists and missing_required:
            diagnosis = "partial-env-loaded"
            next_step = "Reload .krt/env/jira-scribe.env into the shell and rerun the check."
        elif example.exists():
            diagnosis = "example-present-secret-missing"
            next_step = "Create/fill .krt/env/jira-scribe.env locally, load it, and rerun the check."
        elif missing_required:
            diagnosis = "jira-env-not-configured"
            next_step = "Run setup_jira_env.py, fill .krt/env/jira-scribe.env, load it, and rerun the check."

        if secret_exists and in_git and not secret_ignored:
            warnings.append("secret-env-file-exists-but-is-not-ignored")
        if not in_git:
            warnings.append("not-a-git-worktree")
    else:
        if secret_exists and in_git and not secret_ignored:
            warnings.append("secret-env-file-exists-but-is-not-ignored")
        if not secret_exists and not example.exists():
            warnings.append("project-local-jira-env-files-not-present")

    result = {
        "ok": config_ready,
        "diagnosis": diagnosis,
        "missing_required_vars": missing_required,
        "required_present": required_present,
        "optional_present": optional_present,
        "project_files": {
            "secret_env_exists": secret_exists,
            "secret_env_ignored": secret_ignored,
            "example_env_exists": example.exists(),
            "ignore_file_exists": ignore.exists(),
        },
        "next_step": next_step,
        "warnings": warnings,
    }
    print(json.dumps(result))

    if args.strict and not config_ready:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
