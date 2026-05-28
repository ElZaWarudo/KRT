#!/usr/bin/env python3
"""Validate KRT PR body shape."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FORBIDDEN_PATTERNS = (
    (re.compile(r"\bstacked\b"), "stacked"),
    (re.compile(r"\bstackeada\b"), "stackeada"),
    (re.compile(r"\bstack\b"), "stack"),
    (re.compile(r"\bretarget\w*\b"), "retarget"),
    (re.compile(r"\bretargetear\w*\b"), "retargetear"),
    (re.compile(r"\btemporary base\b"), "temporary base"),
    (re.compile(r"\bbase temporal\b"), "base temporal"),
    (re.compile(r"\bdepends on\b"), "depends on"),
    (re.compile(r"\bdependency pr\b"), "dependency pr"),
    (re.compile(r"\bmerge sequencing\b"), "merge sequencing"),
    (re.compile(r"\breviewer\w*\b"), "reviewer"),
    (re.compile(r"\bverification\b"), "verification"),
    (re.compile(r"\btests pass\b"), "tests pass"),
    (re.compile(r"\bci\b|\bcontinuous integration\b"), "CI"),
)
FORBIDDEN_SECTION_HEADINGS = {"summary", "verification"}


def read_body(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    return args.body or sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    parser.add_argument("body", nargs="?")
    args = parser.parse_args()

    body = read_body(args).strip()
    errors: list[str] = []

    if not body:
        errors.append("PR body is empty")

    lowered = body.lower()
    for pattern, label in FORBIDDEN_PATTERNS:
        if pattern.search(lowered):
            errors.append(f"PR body contains forbidden operational context: {label!r}")

    lines = [line.rstrip() for line in body.splitlines()]
    jira_lines = [line for line in lines if re.fullmatch(r"https?://\S+/browse/[A-Z][A-Z0-9]+-\d+", line)]
    if jira_lines:
        if lines[-1] != jira_lines[-1]:
            errors.append("Jira URL must be the last line")
        jira_index = lines.index(jira_lines[-1])
        if jira_index > 0 and lines[jira_index - 1] != "":
            errors.append("Jira URL must be separated from change bullets by a blank line")
    elif any("/browse/" in line for line in lines):
        errors.append("Jira link does not match expected /browse/KEY-N format")

    for line in lines:
        if line.startswith("#") or line.startswith("##"):
            errors.append("PR body must not include headings")
        if line.strip().rstrip(":").lower() in FORBIDDEN_SECTION_HEADINGS:
            errors.append(f"PR body must not include {line.strip()!r} section headings")
    jira_index = lines.index(jira_lines[-1]) if jira_lines else len(lines)
    change_lines = [line for line in lines[:jira_index] if line]
    if not change_lines:
        errors.append("PR body must include at least one change bullet before the Jira URL")
    for line in change_lines:
        if not line.startswith("- "):
            errors.append("Use markdown bullets for change lines")

    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        return 1
    print("PR body checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
