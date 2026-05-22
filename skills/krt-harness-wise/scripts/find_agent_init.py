#!/usr/bin/env python3
"""Find agent initialization context files for Harness Wise."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


INIT_CANDIDATES = (
    ("AGENTS.md", "agent-rules", "read"),
    ("CLAUDE.md", "compat-agent-rules", "summarize"),
    (".codex", "codex-config", "summarize"),
    (".agents", "agent-runtime-config", "summarize"),
)


def candidate_entry(root: Path, rel: str, kind: str, action: str) -> dict[str, Any] | None:
    path = root / rel
    if not path.exists():
        return None
    if path.is_dir():
        children = sorted(
            str(child.relative_to(root))
            for child in path.rglob("*")
            if child.is_file() and "__pycache__" not in child.parts
        )
        return {
            "path": rel,
            "kind": kind,
            "action": action,
            "is_dir": True,
            "children": children[:50],
            "truncated": len(children) > 50,
        }
    return {
        "path": rel,
        "kind": kind,
        "action": action,
        "is_dir": False,
        "size_bytes": path.stat().st_size,
    }


def find_skill_metadata(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return entries
    for metadata in sorted(skills_dir.glob("*/agents/openai.yaml")):
        entries.append(
            {
                "path": str(metadata.relative_to(root)),
                "kind": "skill-runtime-metadata",
                "action": "inspect-if-needed",
                "is_dir": False,
                "size_bytes": metadata.stat().st_size,
            }
        )
    return entries


def scan(root: Path) -> dict[str, Any]:
    paths: list[dict[str, Any]] = []
    for rel, kind, action in INIT_CANDIDATES:
        entry = candidate_entry(root, rel, kind, action)
        if entry:
            paths.append(entry)
    paths.extend(find_skill_metadata(root))
    return {
        "allowed": True,
        "errors": [],
        "warnings": [] if paths else ["no-agent-initialization-context-found"],
        "summary": {
            "root": str(root),
            "count": len(paths),
            "primary": next((entry["path"] for entry in paths if entry["path"] == "AGENTS.md"), None),
        },
        "paths": paths,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root to scan")
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
        result = scan(root)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
