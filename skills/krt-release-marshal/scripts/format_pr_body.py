#!/usr/bin/env python3
"""Format a strict KRT pull request body from noisy draft text."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


JIRA_URL = re.compile(r"https?://\S+/browse/[A-Z][A-Z0-9]+-\d+")
BULLET_PREFIX = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
CHECKBOX_PREFIX = re.compile(r"^\[[ xX]\]\s+")
WHITESPACE = re.compile(r"\s+")

KEEP_SECTIONS = {"summary", "changes", "change summary", "pr body"}
SKIP_SECTIONS = {
    "verification",
    "verified",
    "test",
    "tests",
    "test plan",
    "checks",
    "validation",
    "stack",
    "stacked",
    "stack context",
    "reviewers",
    "reviewer plan",
}
SECTION_HEADINGS = KEEP_SECTIONS | SKIP_SECTIONS

COMMAND_PREFIXES = (
    "npm ",
    "npm run ",
    "pnpm ",
    "yarn ",
    "bun ",
    "pytest",
    "python -m pytest",
    "python3 -m pytest",
    "cargo test",
    "go test",
    "rspec",
    "bundle exec",
    "make ",
    "rtk ",
)

OPERATIONAL_PATTERNS = (
    re.compile(r"\bstacked\s+on\s+pr\b", re.IGNORECASE),
    re.compile(r"\bstackeada\s+en\s+pr\b", re.IGNORECASE),
    re.compile(r"\btemporary\s+base\b", re.IGNORECASE),
    re.compile(r"\bbase\s+temporal\b", re.IGNORECASE),
    re.compile(r"\bretarget\w*\b", re.IGNORECASE),
    re.compile(r"\bdepends\s+on\b", re.IGNORECASE),
    re.compile(r"\bdependency\s+pr\b", re.IGNORECASE),
)


def read_body(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    return args.body or sys.stdin.read()


def section_name(line: str) -> str | None:
    cleaned = line.strip().strip("#").strip().rstrip(":").lower()
    return cleaned if cleaned in SECTION_HEADINGS else None


def change_text(line: str) -> str:
    text = BULLET_PREFIX.sub("", line.strip())
    text = CHECKBOX_PREFIX.sub("", text).strip()
    text = WHITESPACE.sub(" ", text)
    return text.rstrip(".").strip()


def is_operational(line: str) -> bool:
    lowered = line.lower().strip()
    if lowered.startswith(COMMAND_PREFIXES):
        return True
    return any(pattern.search(line) for pattern in OPERATIONAL_PATTERNS)


def format_body(body: str, jira_url: str | None = None) -> str:
    lines = body.splitlines()
    explicit_jira = jira_url
    discovered_jira = next((line.strip() for line in lines if JIRA_URL.fullmatch(line.strip())), None)
    selected_jira = explicit_jira or discovered_jira

    current_section: str | None = None
    saw_keep_section = False
    changes: list[str] = []
    seen: set[str] = set()

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            continue
        if JIRA_URL.fullmatch(stripped):
            continue

        section = section_name(stripped)
        if section:
            current_section = section
            saw_keep_section = section in KEEP_SECTIONS
            continue

        if current_section in SKIP_SECTIONS:
            continue
        if saw_keep_section and current_section not in KEEP_SECTIONS:
            continue
        if is_operational(stripped):
            continue

        text = change_text(stripped)
        if not text or section_name(text) or is_operational(text):
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        changes.append(text)

    if not changes:
        raise ValueError("no change lines found")

    output = "\n".join(f"- {line}" for line in changes)
    if selected_jira:
        output = f"{output}\n\n{selected_jira}"
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    parser.add_argument("--jira-url")
    parser.add_argument("body", nargs="?")
    args = parser.parse_args()

    try:
        print(format_body(read_body(args), args.jira_url))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
