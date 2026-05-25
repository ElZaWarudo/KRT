#!/usr/bin/env python3
"""Ensure KRT local env secrets are ignored before planning or creating commits."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ENV_DIR = Path(".krt/env")
IGNORE_PATH = ENV_DIR / ".gitignore"
SECRET_PATHS = [ENV_DIR / "jira-scribe.env"]

IGNORE_CONTENT = """*
!.gitignore
!*.example
"""


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def result(ok: bool, *, reasons: list[str], changed: bool, checked_paths: list[str]) -> int:
    print(
        json.dumps(
            {
                "ok": ok,
                "changed": changed,
                "ignore_path": str(IGNORE_PATH),
                "checked_paths": checked_paths,
                "block_reasons": reasons,
            },
            sort_keys=True,
        )
    )
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root. Defaults to the current working directory.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        return result(False, reasons=["root-not-directory"], changed=False, checked_paths=[])

    worktree = git(root, "rev-parse", "--show-toplevel")
    if worktree.returncode != 0:
        return result(False, reasons=["not-a-git-worktree"], changed=False, checked_paths=[])

    env_dir = root / ENV_DIR
    env_dir.mkdir(parents=True, exist_ok=True)

    ignore_file = root / IGNORE_PATH
    changed = False
    if not ignore_file.exists() or ignore_file.read_text(encoding="utf-8") != IGNORE_CONTENT:
        ignore_file.write_text(IGNORE_CONTENT, encoding="utf-8")
        changed = True

    reasons: list[str] = []
    checked_paths: list[str] = []
    for path in SECRET_PATHS:
        path_text = str(path)
        checked_paths.append(path_text)

        tracked = git(root, "ls-files", "--error-unmatch", path_text)
        if tracked.returncode == 0:
            reasons.append(f"secret-env-tracked:{path_text}")

        ignored = git(root, "check-ignore", "-q", path_text)
        if ignored.returncode != 0:
            reasons.append(f"secret-env-not-ignored:{path_text}")

    return result(not reasons, reasons=reasons, changed=changed, checked_paths=checked_paths)


if __name__ == "__main__":
    sys.exit(main())
