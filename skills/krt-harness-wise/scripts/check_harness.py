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
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE = re.compile(r"(?:\+?\d[\d .()-]{7,}\d)")
IBAN = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")
SECRET_ASSIGNMENT = re.compile(r"\b(?:api[_-]?key|token|secret|password|passwd|pwd)\s*[:=]\s*['\"]?[^'\"\s]+", re.I)
CURRENCY_AMOUNT = re.compile(r"(?:\b\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{2})?\s?(?:€|EUR|USD|\$)\b|\b(?:€|EUR|USD|\$)\s?\d{1,3}(?:[.,]\d{3})+)", re.I)
GENERATED_SOURCE = re.compile(r"docs/harnesses/sources/[^\s)`]+", re.I)
GENERATED_IMAGE = re.compile(r"docs/harnesses/images/[^\s)`]+", re.I)
SOURCE_HASH = re.compile(r"\bsource_sha256\b|\b[a-f0-9]{64}\b", re.I)
PRIVATE_URL = re.compile(r"https?://(?:localhost|127\.0\.0\.1|10\.|172\.(?:1[6-9]|2\d|3[01])\.|192\.168\.|[^/\s]*(?:internal|intranet|corp|local))[^)\s]*", re.I)


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
    if EMAIL.search(text):
        warnings.append("publication-safety:email")
    phone_matches = []
    for match in PHONE.finditer(text):
        value = match.group(0)
        digits = re.sub(r"\D", "", value)
        if len(digits) >= 9 and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            phone_matches.append(value)
    if phone_matches:
        warnings.append("publication-safety:phone-like-value")
    if IBAN.search(text):
        warnings.append("publication-safety:iban-like-value")
    if SECRET_ASSIGNMENT.search(text):
        errors.append("publication-safety:secret-like-assignment")
    if CURRENCY_AMOUNT.search(text):
        warnings.append("publication-safety:exact-currency-amount")
    if PRIVATE_URL.search(text):
        warnings.append("publication-safety:private-url")
    if SOURCE_HASH.search(text):
        warnings.append("publication-safety:source-hash-or-raw-digest")
    if GENERATED_IMAGE.search(text):
        warnings.append("publication-safety:generated-image-reference")
    if GENERATED_SOURCE.search(text):
        warnings.append("publication-safety:generated-source-fallback-reference")
        read_first_block = re.search(r"## Source Of Truth Ranking(?P<body>.*?)(?:\n## |\Z)", text, re.S)
        if read_first_block:
            unsafe_source_lines = [
                line for line in read_first_block.group("body").splitlines()
                if GENERATED_SOURCE.search(line) and not re.search(r"\b(?:Inspect If Needed|fallback)\b", line, re.I)
            ]
        else:
            unsafe_source_lines = []
        if unsafe_source_lines:
            errors.append("publication-safety:generated-source-in-source-ranking")

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
