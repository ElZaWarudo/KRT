#!/usr/bin/env python3
"""Validate that a user message explicitly authorizes merging one PR."""

from __future__ import annotations

import argparse
import json
import re
from typing import Any


PR_REF = re.compile(r"(?:#|(?:\bPR\b|\bpr\b)\s*#?\s*)(\d+)")
CONTEXTUAL_PR_REF = re.compile(
    r"\b("
    r"(?:la|el|esta|este|esa|ese|the|this|that)\s+"
    r"(?:PR|pr|pull\s+request)"
    r")\b",
    re.I,
)
MERGE_INTENT = re.compile(
    r"\b("
    r"mergea(?:r)?|merge(?:ar|d)?|haz\s+merge|hacer\s+merge|"
    r"fusiona(?:r)?|integra(?:r)?|"
    r"merge|merge\s+now"
    r")\b",
    re.I,
)
GENERIC_APPROVAL = re.compile(
    r"\b("
    r"apruebo|aprobado|dale|contin[uú]a|sigue|ship|release|lanza|"
    r"ok|okay|yes|si|sí"
    r")\b",
    re.I,
)


def validate(text: str, expected_pr: int | None, allow_generic_context: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    refs = sorted({int(match.group(1)) for match in PR_REF.finditer(text)})
    has_merge_intent = bool(MERGE_INTENT.search(text))
    has_generic_approval = bool(GENERIC_APPROVAL.search(text))
    resolved_from_context = False
    resolved_from_generic_context = False

    if not refs and expected_pr is not None and has_merge_intent and CONTEXTUAL_PR_REF.search(text):
        refs = [expected_pr]
        resolved_from_context = True

    if not refs and expected_pr is not None and allow_generic_context and has_generic_approval:
        refs = [expected_pr]
        has_merge_intent = True
        resolved_from_generic_context = True

    if not refs:
        errors.append("missing-pr-reference")
    if len(refs) > 1:
        errors.append("multiple-pr-references")
    if expected_pr is not None and refs and refs != [expected_pr]:
        errors.append(f"wrong-pr-reference:expected-{expected_pr}:found-{','.join(str(ref) for ref in refs)}")
    if not has_merge_intent:
        errors.append("missing-merge-intent")
    if has_generic_approval and not has_merge_intent:
        warnings.append("generic-approval-is-not-merge-authorization")

    return {
        "allowed": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "expected_pr": expected_pr,
            "pr_references": refs,
            "has_merge_intent": has_merge_intent,
            "has_generic_approval": has_generic_approval,
            "resolved_from_context": resolved_from_context,
            "resolved_from_generic_context": resolved_from_generic_context,
        },
        "paths": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", required=True, help="User-visible authorization text to validate")
    parser.add_argument("--pr-number", type=int, help="Expected pull request number")
    parser.add_argument(
        "--allow-generic-context",
        action="store_true",
        help="Allow generic approval when this text answers an explicit pending merge prompt for --pr-number",
    )
    args = parser.parse_args()

    result = validate(args.text, args.pr_number, args.allow_generic_context)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
