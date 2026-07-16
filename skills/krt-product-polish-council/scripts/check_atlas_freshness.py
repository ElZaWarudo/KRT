#!/usr/bin/env python3
"""Check whether an application atlas matches the current Git tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_git(repo: Path, *args: str) -> bytes:
    process = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode != 0:
        message = process.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(message or f"git {' '.join(args)} failed")
    return process.stdout


def repository_root(start: Path) -> Path:
    output = run_git(start, "rev-parse", "--show-toplevel")
    return Path(output.decode().strip()).resolve()


def parse_frontmatter(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)

    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("atlas must start with YAML frontmatter")

    metadata: dict[str, Any] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"unsupported frontmatter line: {line}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if key in {"tracked_paths", "excluded_paths"}:
            try:
                value = json.loads(raw_value)
            except json.JSONDecodeError as error:
                raise ValueError(f"{key} must be an inline JSON array") from error
            if not isinstance(value, list) or not all(
                isinstance(item, str) and item for item in value
            ):
                raise ValueError(f"{key} must contain non-empty strings")
            metadata[key] = value
        elif raw_value.startswith('"'):
            try:
                metadata[key] = json.loads(raw_value)
            except json.JSONDecodeError as error:
                raise ValueError(f"invalid quoted value for {key}") from error
        else:
            metadata[key] = raw_value
    else:
        raise ValueError("atlas frontmatter is not closed")

    return metadata


def is_excluded(path: str, excluded_paths: list[str]) -> bool:
    normalized = path.strip("/")
    for excluded in excluded_paths:
        candidate = excluded.strip("/")
        if normalized == candidate or normalized.startswith(f"{candidate}/"):
            return True
    return False


def tree_lines(repo: Path, tracked_paths: list[str], excluded_paths: list[str]) -> list[str]:
    output = run_git(repo, "ls-tree", "-r", "--full-tree", "HEAD", "--", *tracked_paths)
    lines = output.decode("utf-8", errors="strict").splitlines()
    included: list[str] = []
    for line in lines:
        _, separator, path = line.partition("\t")
        if not separator:
            raise ValueError(f"unexpected git ls-tree output: {line}")
        if not is_excluded(path, excluded_paths):
            included.append(line)
    return sorted(included)


def fingerprint(lines: list[str]) -> str:
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def changed_paths(repo: Path, tracked_paths: list[str], excluded_paths: list[str]) -> list[str]:
    commands = [
        ("diff", "--name-only", "-z", "--", *tracked_paths),
        ("diff", "--cached", "--name-only", "-z", "--", *tracked_paths),
        ("ls-files", "--others", "--exclude-standard", "-z", "--", *tracked_paths),
    ]
    changed: set[str] = set()
    for command in commands:
        output = run_git(repo, *command)
        for raw_path in output.split(b"\0"):
            if not raw_path:
                continue
            path = raw_path.decode("utf-8", errors="surrogateescape")
            if not is_excluded(path, excluded_paths):
                changed.add(path)
    return sorted(changed)


def emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return
    order = [
        "status",
        "atlas",
        "head",
        "verified_source_commit",
        "expected_fingerprint",
        "current_fingerprint",
        "covered_files",
        "relevant_changes",
        "reason",
    ]
    for key in order:
        if key in payload:
            value = payload[key]
            if isinstance(value, list):
                value = ", ".join(value) if value else "none"
            print(f"{key}: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas", default="docs/product/application-atlas.md")
    parser.add_argument("--repo", default=".")
    parser.add_argument(
        "--compute",
        action="store_true",
        help="print the current fingerprint without comparing it",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        repo = repository_root(Path(args.repo).resolve())
        atlas = Path(args.atlas)
        if not atlas.is_absolute():
            atlas = repo / atlas
        atlas = atlas.resolve()
        if not atlas.exists():
            emit(
                {
                    "status": "missing",
                    "atlas": str(atlas),
                    "reason": "create the versioned application atlas before evaluation",
                },
                args.json,
            )
            return 2

        metadata = parse_frontmatter(atlas)
        tracked_paths = metadata.get("tracked_paths")
        excluded_paths = metadata.get("excluded_paths", [])
        if not tracked_paths:
            raise ValueError("tracked_paths is required and cannot be empty")

        try:
            atlas_relative = atlas.relative_to(repo).as_posix()
        except ValueError as error:
            raise ValueError("atlas must live inside the repository") from error
        if atlas_relative not in excluded_paths:
            excluded_paths = [*excluded_paths, atlas_relative]

        lines = tree_lines(repo, tracked_paths, excluded_paths)
        if not lines:
            raise ValueError("tracked_paths do not match files in HEAD")

        current = fingerprint(lines)
        head = run_git(repo, "rev-parse", "HEAD").decode().strip()
        changes = changed_paths(repo, tracked_paths, excluded_paths)
        payload: dict[str, Any] = {
            "atlas": str(atlas),
            "head": head,
            "verified_source_commit": metadata.get("verified_source_commit", "missing"),
            "current_fingerprint": current,
            "covered_files": len(lines),
            "relevant_changes": changes,
        }

        if args.compute:
            payload.update(
                {
                    "status": "computed",
                    "reason": "copy current_fingerprint into the atlas after substantive verification",
                }
            )
            emit(payload, args.json)
            return 0

        expected = metadata.get("application_fingerprint")
        if not isinstance(expected, str) or not expected.startswith("sha256:"):
            raise ValueError("application_fingerprint must be a quoted sha256:<digest>")
        payload["expected_fingerprint"] = expected

        if changes:
            payload.update(
                {
                    "status": "stale",
                    "reason": "relevant working-tree or index changes are not represented by HEAD",
                }
            )
            emit(payload, args.json)
            return 1
        if expected != current:
            payload.update(
                {
                    "status": "stale",
                    "reason": "the covered application tree differs from the atlas fingerprint",
                }
            )
            emit(payload, args.json)
            return 1

        payload.update(
            {
                "status": "fresh",
                "reason": "the atlas fingerprint matches the current commit and relevant paths are clean",
            }
        )
        emit(payload, args.json)
        return 0
    except FileNotFoundError as error:
        emit(
            {"status": "missing", "atlas": str(error.filename), "reason": str(error)},
            args.json,
        )
        return 2
    except (OSError, RuntimeError, ValueError) as error:
        emit({"status": "invalid", "reason": str(error)}, args.json)
        return 2


if __name__ == "__main__":
    sys.exit(main())
