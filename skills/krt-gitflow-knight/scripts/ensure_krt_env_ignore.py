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


def result(
    ok: bool,
    *,
    reasons: list[str],
    changed: bool,
    would_change: bool,
    check_only: bool,
    checked_paths: list[str],
) -> int:
    print(
        json.dumps(
            {
                "ok": ok,
                "changed": changed,
                "would_change": would_change,
                "check_only": check_only,
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
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Report whether the ignore guard would change without writing to the repository.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        return result(
            False,
            reasons=["root-not-directory"],
            changed=False,
            would_change=False,
            check_only=args.check_only,
            checked_paths=[],
        )

    worktree = git(root, "rev-parse", "--show-toplevel")
    if worktree.returncode != 0:
        return result(
            False,
            reasons=["not-a-git-worktree"],
            changed=False,
            would_change=False,
            check_only=args.check_only,
            checked_paths=[],
        )

    ignore_file = root / IGNORE_PATH
    would_change = not ignore_file.exists() or ignore_file.read_text(encoding="utf-8") != IGNORE_CONTENT
    changed = False
    if would_change and not args.check_only:
        ignore_file.parent.mkdir(parents=True, exist_ok=True)
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

        if not (args.check_only and would_change):
            ignored = git(root, "check-ignore", "-q", path_text)
            if ignored.returncode != 0:
                reasons.append(f"secret-env-not-ignored:{path_text}")

    return result(
        not reasons,
        reasons=reasons,
        changed=changed,
        would_change=would_change,
        check_only=args.check_only,
        checked_paths=checked_paths,
    )


if __name__ == "__main__":
    sys.exit(main())
