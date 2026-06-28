#!/usr/bin/env python3
"""Report Jira Cloud env readiness using the checkout-local jira-cloud-scribe env contract."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from jira_env_runtime import (
    EXAMPLE_PATH,
    IGNORE_PATH,
    OPTIONAL_VARS,
    REQUIRED_VARS,
    SECRET_PATH,
    bool_map,
    load_env_from_secret,
)


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
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
    parser.add_argument(
        "--no-auto-load",
        action="store_true",
        help="Disable the default behavior of loading non-empty Jira Cloud variables from .krt/env/jira-cloud-scribe.env before checking readiness.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        print(json.dumps({"ok": False, "reason": "root-not-directory"}))
        return 1

    env = dict(os.environ)
    auto_load_error: str | None = None
    auto_loaded_vars: list[str] = []
    secret = root / SECRET_PATH

    auto_load_enabled = not args.no_auto_load

    if auto_load_enabled and secret.exists():
        try:
            env, auto_loaded_vars = load_env_from_secret(root, base_env=env)
        except ValueError as exc:
            auto_load_error = str(exc)

    required_present = bool_map(env, REQUIRED_VARS)
    optional_present = bool_map(env, OPTIONAL_VARS)
    missing_required = [name for name, present in required_present.items() if not present]

    worktree = git(root, "rev-parse", "--show-toplevel")
    in_git = worktree.returncode == 0

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

    if auto_load_error:
        diagnosis = "env-file-parse-error"
        next_step = "Fix .krt/env/jira-cloud-scribe.env formatting and rerun the check."
        warnings.append(auto_load_error)
    elif not secret_exists and not missing_required:
        diagnosis = "env-loaded-without-project-secret-file"
        next_step = "Create .krt/env/jira-cloud-scribe.env for this checkout, load it, and rerun the check."
        warnings.append("required-vars-present-without-project-secret-file")

    if not config_ready:
        if secret_exists and missing_required and not any(required_present.values()):
            if auto_load_enabled:
                diagnosis = "env-file-present-but-empty-or-incomplete"
                next_step = "Fill the required Jira Cloud values in .krt/env/jira-cloud-scribe.env and rerun the check."
            else:
                diagnosis = "env-file-present-but-not-loaded"
                next_step = (
                    "Load .krt/env/jira-cloud-scribe.env into the shell, or rerun this check without --no-auto-load, "
                    "and rerun the check."
                )
        elif secret_exists and missing_required:
            if auto_load_enabled:
                diagnosis = "env-file-present-but-empty-or-incomplete"
                next_step = "Fill the missing Jira Cloud values in .krt/env/jira-cloud-scribe.env and rerun the check."
            else:
                diagnosis = "partial-env-loaded"
                next_step = "Reload .krt/env/jira-cloud-scribe.env into the shell, or rerun this check without --no-auto-load."
        elif example.exists():
            diagnosis = "example-present-secret-missing"
            next_step = "Create/fill .krt/env/jira-cloud-scribe.env locally and rerun the check."
        elif missing_required:
            if auto_load_enabled:
                diagnosis = "jira-env-not-configured"
                next_step = "Run setup_jira_env.py, fill .krt/env/jira-cloud-scribe.env, and rerun the check."
            else:
                diagnosis = "jira-env-not-configured"
                next_step = "Run setup_jira_env.py, fill .krt/env/jira-cloud-scribe.env, load it or rerun this check without --no-auto-load."

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
        "auto_load_attempted": auto_load_enabled,
        "auto_loaded_vars": auto_loaded_vars,
        "next_step": next_step,
        "warnings": warnings,
    }
    print(json.dumps(result))

    if args.strict and not config_ready:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
