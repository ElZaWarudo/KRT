#!/usr/bin/env python3
"""Execute a command with checkout-local Jira Cloud env vars loaded."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from jira_env_runtime import REQUIRED_VARS, SECRET_PATH, bool_map, load_env_from_secret


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Consumer project root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute after `--`.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        print(json.dumps({"ok": False, "reason": "root-not-directory"}))
        return 1

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print(json.dumps({"ok": False, "reason": "missing-command"}))
        return 1

    secret = root / SECRET_PATH
    if not secret.exists():
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "missing-secret-env-file",
                    "secret_path": str(secret),
                }
            )
        )
        return 1

    try:
        env, loaded_vars = load_env_from_secret(root, base_env=os.environ)
    except ValueError as exc:
        print(json.dumps({"ok": False, "reason": "env-file-parse-error", "detail": str(exc)}))
        return 1

    missing_required = [
        name for name, present in bool_map(env, REQUIRED_VARS).items() if not present
    ]
    if missing_required:
        print(
            json.dumps(
                {
                    "ok": False,
                    "reason": "missing-required-vars",
                    "missing_required_vars": missing_required,
                    "loaded_vars": loaded_vars,
                }
            )
        )
        return 1

    completed = subprocess.run(command, env=env, check=False)
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
