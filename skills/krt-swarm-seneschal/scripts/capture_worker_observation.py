#!/usr/bin/env python3
"""Capture root-owned changed-file evidence and bind it to a content digest."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from deterministic_artifacts import canonical_sha256, file_sha256, write_atomic


def _git_paths(repo_root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def observe_diff(repo_root: Path, base_revision: str) -> dict[str, Any]:
    if not base_revision.strip():
        raise ValueError("base_revision must be non-empty")
    tracked = _git_paths(repo_root, "diff", "--name-only", "-z", "--no-ext-diff", base_revision, "--")
    untracked = _git_paths(repo_root, "ls-files", "--others", "--exclude-standard", "-z")
    paths = sorted(set(tracked + untracked))
    entries: list[dict[str, str]] = []
    for relative in paths:
        path = repo_root / relative
        if path.is_symlink():
            digest = f"symlink:{os.readlink(path)}"
        elif path.is_file():
            digest = file_sha256(path)
        else:
            digest = "deleted"
        entries.append({"path": relative, "digest": digest})
    payload = {"base_revision": base_revision, "changed_files": entries}
    return {
        "changed_files": paths,
        "changed_files_source": "root-diff",
        "diff_digest": canonical_sha256(payload),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--base-revision", required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        observation = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(observation, dict):
            raise ValueError("input must contain a JSON object")
        repo_root = args.repo_root.resolve()
        for artifact in (args.input.resolve(), args.output.resolve()):
            try:
                artifact.relative_to(repo_root)
            except ValueError:
                continue
            raise ValueError("observation input and output must be outside repo_root")
        observation.update(observe_diff(repo_root, args.base_revision))
        write_atomic(args.output, observation)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    json.dump(observation, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
