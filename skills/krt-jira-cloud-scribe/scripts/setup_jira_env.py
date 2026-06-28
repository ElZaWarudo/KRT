#!/usr/bin/env python3
"""Create a project-local Jira Cloud Scribe env file behind a deterministic ignore rule."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ENV_DIR = Path(".krt/env")
IGNORE_PATH = ENV_DIR / ".gitignore"
SECRET_PATH = ENV_DIR / "jira-cloud-scribe.env"
EXAMPLE_PATH = ENV_DIR / "jira-cloud-scribe.env.example"

IGNORE_CONTENT = """*
!.gitignore
!*.example
"""

ENV_CONTENT = """JIRA_CLOUD_HOST=
JIRA_CLOUD_EMAIL=
JIRA_CLOUD_API_TOKEN=
JIRA_CLOUD_PROJECT_KEY=

# Optional
JIRA_CLOUD_BOARD_ID=
"""

EXAMPLE_CONTENT = """JIRA_CLOUD_HOST=example.atlassian.net
JIRA_CLOUD_EMAIL=person@example.com
JIRA_CLOUD_API_TOKEN=replace-with-api-token
JIRA_CLOUD_PROJECT_KEY=KRT

# Optional
JIRA_CLOUD_BOARD_ID=
"""


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def fail(reason: str, *, root: Path, created_secret: bool = False) -> int:
    if created_secret:
        (root / SECRET_PATH).unlink(missing_ok=True)
    print(json.dumps({"ok": False, "reason": reason, "secret_path": str(SECRET_PATH)}))
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Consumer project root. Defaults to the current working directory.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.exists() or not root.is_dir():
        return fail("root-not-directory", root=root)

    worktree = git(root, "rev-parse", "--show-toplevel")
    if worktree.returncode != 0:
        return fail("not-a-git-worktree", root=root)

    tracked = git(root, "ls-files", "--error-unmatch", str(SECRET_PATH))
    if tracked.returncode == 0:
        return fail("secret-env-already-tracked", root=root)

    env_dir = root / ENV_DIR
    env_dir.mkdir(parents=True, exist_ok=True)
    (root / IGNORE_PATH).write_text(IGNORE_CONTENT, encoding="utf-8")

    ignored = git(root, "check-ignore", "-q", str(SECRET_PATH))
    if ignored.returncode != 0:
        return fail("secret-env-not-ignored", root=root)

    created_secret = False
    secret = root / SECRET_PATH
    if not secret.exists():
        secret.write_text(ENV_CONTENT, encoding="utf-8")
        created_secret = True

    ignored = git(root, "check-ignore", "-q", str(SECRET_PATH))
    if ignored.returncode != 0:
        return fail("secret-env-not-ignored-after-write", root=root, created_secret=created_secret)

    example = root / EXAMPLE_PATH
    if not example.exists():
        example.write_text(EXAMPLE_CONTENT, encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "secret_path": str(SECRET_PATH),
                "example_path": str(EXAMPLE_PATH),
                "ignore_path": str(IGNORE_PATH),
                "created_secret": created_secret,
                "message": "Fill jira-cloud-scribe.env locally; do not commit real Jira Cloud credentials.",
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
