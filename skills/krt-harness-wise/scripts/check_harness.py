#!/usr/bin/env python3
"""Validate a versionable coding harness artifact."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_FRONTMATTER = ("type", "task", "status", "scope", "confidence", "created", "updated")
ALLOWED = {
    "status": {"draft", "ready", "blocked", "review"},
    "scope": {"local", "cross-cutting", "architectural"},
    "confidence": {"high", "medium", "low", "unknown"},
}
REQUIRED_SECTIONS = (
    "# Coding Harness",
    "## Objective",
    "## Source Of Truth Ranking",
    "## Agent Initialization Context",
    "## Context Plan",
    "## Guardrails",
    "## Risks",
    "## Assumptions And Deferred Verification",
    "## Validation Expectations",
    "## Agent-Ready Instructions",
)
ABSOLUTE_PATH = re.compile(r"(?<![\w.-])(?:/[A-Za-z0-9_.-]+){2,}")
WINDOWS_PATH = re.compile(r"\b[A-Za-z]:\\")
BROAD_READ = re.compile(r"\bread (?:the )?(?:whole|entire|all of) [`']?[\w./-]+/?[`']?", re.I)
SELF_REFERENCE = re.compile(r"\bkrt-harness-wise\b|\$krt:harness-wise\b", re.I)


def parse_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    if not text.startswith("---\n"):
        return {}, ["missing-frontmatter"]
    end = text.find("\n---", 4)
    if end == -1:
        return {}, ["unterminated-frontmatter"]
    raw = text[4:end].strip()
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            errors.append(f"malformed-frontmatter-line:{line}")
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data, errors


def validate(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return {
            "allowed": False,
            "errors": [f"unreadable:{exc}"],
            "warnings": [],
            "summary": {},
            "paths": [str(path)],
        }

    frontmatter, fm_errors = parse_frontmatter(text)
    errors.extend(fm_errors)
    for key in REQUIRED_FRONTMATTER:
        if key not in frontmatter:
            errors.append(f"missing-frontmatter-field:{key}")
    if frontmatter.get("type") and frontmatter["type"] != "coding-harness":
        errors.append("frontmatter-type-must-be-coding-harness")
    for key, allowed in ALLOWED.items():
        if key in frontmatter and frontmatter[key] not in allowed:
            errors.append(f"invalid-{key}:{frontmatter[key]}")

    for required_section in REQUIRED_SECTIONS:
        if required_section not in text:
            errors.append(f"missing-section:{required_section}")

    absolute_matches = [match.group(0) for match in ABSOLUTE_PATH.finditer(text)]
    absolute_matches.extend(match.group(0) for match in WINDOWS_PATH.finditer(text))
    for match in sorted(set(absolute_matches)):
        errors.append(f"absolute-path:{match}")

    if SELF_REFERENCE.search(text):
        errors.append("self-reference:krt-harness-wise")
    if BROAD_READ.search(text):
        warnings.append("overbroad-read-instruction")

    return {
        "allowed": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "path": str(path),
            "status": frontmatter.get("status"),
            "scope": frontmatter.get("scope"),
            "confidence": frontmatter.get("confidence"),
            "required_sections": len(REQUIRED_SECTIONS),
        },
        "paths": [str(path)],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("harness")
    args = parser.parse_args()

    result = validate(Path(args.harness))
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
