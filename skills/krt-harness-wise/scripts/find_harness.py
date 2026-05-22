#!/usr/bin/env python3
"""Find existing coding harness candidates."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


HARNESS_DIRS = ("docs/harnesses", "harnesses", ".harnesses", "docs/agents")


def slugify(value: str) -> str:
    words = re.findall(r"[a-zA-Z0-9]+", value.lower())
    return "-".join(words[:8])


def score(path: Path, root: Path, slug: str | None) -> int:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:2000]
    except OSError:
        text = ""
    rel = str(path.relative_to(root))
    result = 0
    if "type: coding-harness" in text:
        result += 50
    if "# Coding Harness" in text:
        result += 25
    if slug and slug in path.stem:
        result += 20
    if rel.startswith("docs/harnesses/"):
        result += 10
    return result


def candidate(path: Path, root: Path, slug: str | None) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(root)),
        "score": score(path, root, slug),
        "size_bytes": path.stat().st_size,
    }


def scan(root: Path, task: str | None, explicit: str | None) -> dict[str, Any]:
    warnings: list[str] = []
    errors: list[str] = []
    candidates: list[dict[str, Any]] = []
    slug = slugify(task) if task else None

    if explicit:
        path = Path(explicit)
        resolved = (root / path).resolve()
        if path.is_absolute() or not resolved.is_relative_to(root):
            errors.append(f"harness-path-must-be-repo-relative:{explicit}")
        elif not resolved.exists():
            errors.append(f"harness-not-found:{explicit}")
        elif resolved.is_file():
            candidates.append(candidate(resolved, root, slug))
        else:
            errors.append(f"harness-not-file:{explicit}")

    for rel_dir in HARNESS_DIRS:
        directory = root / rel_dir
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*.md")):
            if path.is_file():
                candidates.append(candidate(path, root, slug))

    deduped = {entry["path"]: entry for entry in candidates}
    ordered = sorted(deduped.values(), key=lambda entry: (-entry["score"], entry["path"]))
    if not ordered:
        warnings.append("no-existing-harness-found")
    return {
        "allowed": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "task_slug": slug,
            "count": len(ordered),
            "best": ordered[0]["path"] if ordered else None,
        },
        "paths": ordered,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--task")
    parser.add_argument("--harness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        result = {
            "allowed": False,
            "errors": [f"root-not-found:{args.root}"],
            "warnings": [],
            "summary": {},
            "paths": [],
        }
    else:
        result = scan(root, args.task, args.harness)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
