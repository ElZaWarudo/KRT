#!/usr/bin/env python3
"""Validate non-certifying partial evidence from an interrupted review."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any

from deterministic_validation import exact_object, load_object, non_empty_string, string_list
from validate_review_terminal import (
    SEVERITIES,
    _assignment_from_plan,
    _validate_feedback,
    validate_finding,
)


RECOVERY_FIELDS = {
    "schema_version",
    "contract_hash",
    "diff_digest",
    "review_plan_hash",
    "reviewer_id",
    "surface_id",
    "risk_boundaries_checked",
    "candidate_findings",
    "candidate_feedback",
    "stop_reason",
    "certifies_review",
}
STOP_REASONS = {"blocked", "budget-exhausted", "interrupted"}


def validate_review_recovery(
    plan: dict[str, Any], recovery: dict[str, Any]
) -> dict[str, Any]:
    exact_object(recovery, RECOVERY_FIELDS, "review recovery")
    if recovery["schema_version"] != 1:
        raise ValueError("review recovery schema_version must be 1")
    surface_id = non_empty_string(recovery["surface_id"], "surface_id")
    assignment = _assignment_from_plan(plan, surface_id)
    for field in ("contract_hash", "diff_digest", "review_plan_hash"):
        if recovery[field] != plan[field]:
            raise ValueError(f"review recovery {field} does not match assignment")
    reviewer_id = non_empty_string(recovery["reviewer_id"], "reviewer_id")
    checked = string_list(
        recovery["risk_boundaries_checked"],
        "risk_boundaries_checked",
        unique=True,
    )
    expected = set(string_list(assignment["risk_boundaries"], "risk_boundaries"))
    if any(boundary not in expected for boundary in checked):
        raise ValueError("review recovery contains an unassigned risk boundary")
    raw_findings = recovery["candidate_findings"]
    if not isinstance(raw_findings, list):
        raise ValueError("candidate_findings must be a list")
    findings = [
        validate_finding(finding, index=index)
        for index, finding in enumerate(raw_findings)
    ]
    if Counter(finding["severity"] for finding in findings)["p2"] > 3:
        raise ValueError("review recovery may contain at most three actionable p2 findings")
    raw_feedback = recovery["candidate_feedback"]
    if not isinstance(raw_feedback, list):
        raise ValueError("candidate_feedback must be a list")
    feedback = [
        _validate_feedback(value, index=index)
        for index, value in enumerate(raw_feedback)
    ]
    if recovery["stop_reason"] not in STOP_REASONS:
        raise ValueError("review recovery stop_reason is invalid")
    if recovery["certifies_review"] is not False:
        raise ValueError("review recovery must set certifies_review to false")
    return {
        "valid": True,
        "certifies_review": False,
        "reviewer_id": reviewer_id,
        "surface_id": surface_id,
        "checked_boundary_count": len(checked),
        "candidate_finding_count": len(findings),
        "candidate_feedback_count": len(feedback),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate_review_recovery(load_object(args.plan), load_object(args.input))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
