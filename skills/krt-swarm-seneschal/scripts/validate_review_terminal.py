#!/usr/bin/env python3
"""Validate a surface review terminal against its deterministic assignment."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any

from deterministic_artifacts import canonical_sha256
from deterministic_validation import exact_object, load_object, non_empty_string, string_list
from review_policy import COORDINATED_REVIEW_TIERS, normalize_assurance_tier


SEVERITIES = {"p0", "p1", "p2"}
PRINCIPLES = {
    "correctness",
    "security",
    "contract",
    "testing",
    "kiss",
    "yagni",
    "dry-knowledge",
    "maintainability-modularity",
    "maintainability-analysability",
    "maintainability-modifiability",
    "maintainability-testability",
    "scope",
}
FINDING_FIELDS = {
    "severity",
    "principle",
    "rule_id",
    "observation",
    "impact",
    "recommendation",
    "evidence",
}
PLAN_FIELDS = {
    "schema_version",
    "assurance_tier",
    "contract_hash",
    "diff_digest",
    "changed_paths",
    "assignments",
    "queued",
    "coverage_complete",
    "validation_wave_required",
    "approval_required",
    "review_plan_hash",
}
FEEDBACK_ACTIONS = {"corroborate", "challenge"}


def validate_finding(value: Any, *, index: int) -> dict[str, Any]:
    field = f"findings[{index}]"
    if not isinstance(value, dict) or set(value) != FINDING_FIELDS:
        raise ValueError(f"{field} has missing or unknown fields")
    if value["severity"] not in SEVERITIES:
        raise ValueError(f"{field}.severity is invalid")
    if value["principle"] not in PRINCIPLES:
        raise ValueError(f"{field}.principle is invalid")
    for name in ("rule_id", "observation", "impact", "recommendation"):
        non_empty_string(value[name], f"{field}.{name}")
    evidence = string_list(value["evidence"], f"{field}.evidence")
    if not evidence:
        raise ValueError(f"{field}.evidence must not be empty")
    return value


def _assignment_from_plan(plan: dict[str, Any], surface_id: str) -> dict[str, Any]:
    exact_object(plan, PLAN_FIELDS, "review plan")
    if plan["schema_version"] != 2:
        raise ValueError("review plan schema_version must be 2")
    assurance_tier = normalize_assurance_tier(
        plan["assurance_tier"], "review plan assurance_tier"
    )
    if assurance_tier not in COORDINATED_REVIEW_TIERS:
        raise ValueError("review plan assurance tier is not coordinated")
    if plan["validation_wave_required"] is not True:
        raise ValueError("coordinated review requires independent validation")
    expected_approval = assurance_tier == "critical"
    if plan["approval_required"] is not expected_approval:
        raise ValueError("review plan approval requirement does not match assurance tier")
    payload = {key: plan[key] for key in PLAN_FIELDS - {"review_plan_hash"}}
    if plan["review_plan_hash"] != canonical_sha256(payload):
        raise ValueError("review plan hash is invalid")
    assignments = plan["assignments"]
    queued = plan["queued"]
    if not isinstance(assignments, list) or not isinstance(queued, list):
        raise ValueError("review plan assignments and queued must be lists")
    candidates = list(assignments)
    for index, queued_item in enumerate(queued):
        exact_object(queued_item, {"assignment", "reason"}, f"queued[{index}]")
        if queued_item["reason"] != "reviewer-capacity":
            raise ValueError(f"queued[{index}].reason is invalid")
        candidates.append(queued_item["assignment"])
    matches = [
        item for item in candidates
        if isinstance(item, dict) and item.get("id") == surface_id
    ]
    if len(matches) != 1:
        raise ValueError("terminal surface_id does not identify one plan assignment")
    assignment = matches[0]
    exact_object(
        assignment,
        {"id", "reviewer_role", "owned_paths", "risk_boundaries", "cross_cutting", "priority"},
        "assignment",
    )
    return assignment


def _validate_feedback(value: Any, *, index: int) -> dict[str, Any]:
    field = f"finding_feedback[{index}]"
    feedback = exact_object(
        value, {"finding_id", "action", "rationale", "evidence"}, field
    )
    non_empty_string(feedback["finding_id"], f"{field}.finding_id")
    if feedback["action"] not in FEEDBACK_ACTIONS:
        raise ValueError(f"{field}.action is invalid")
    non_empty_string(feedback["rationale"], f"{field}.rationale")
    string_list(feedback["evidence"], f"{field}.evidence", allow_empty=False)
    return feedback


def validate_review_terminal(plan: dict[str, Any], terminal: dict[str, Any]) -> dict[str, Any]:
    terminal_fields = {
        "contract_hash",
        "diff_digest",
        "review_plan_hash",
        "reviewer_id",
        "surface_id",
        "risk_boundaries_checked",
        "findings",
        "finding_feedback",
        "suppressed_speculative_count",
        "stop_reason",
    }
    if not isinstance(terminal, dict) or set(terminal) != terminal_fields:
        raise ValueError("review terminal has missing or unknown fields")
    surface_id = non_empty_string(terminal["surface_id"], "surface_id")
    assignment = _assignment_from_plan(plan, surface_id)
    expected = {
        "contract_hash": plan["contract_hash"],
        "diff_digest": plan["diff_digest"],
        "review_plan_hash": plan["review_plan_hash"],
        "surface_id": assignment["id"],
    }
    for field, value in expected.items():
        if terminal[field] != value:
            raise ValueError(f"review terminal {field} does not match assignment")
    reviewer_id = non_empty_string(terminal["reviewer_id"], "reviewer_id")
    expected_boundaries = string_list(assignment["risk_boundaries"], "risk_boundaries")
    checked_boundaries = string_list(
        terminal["risk_boundaries_checked"], "risk_boundaries_checked"
    )
    if Counter(expected_boundaries) != Counter(checked_boundaries):
        raise ValueError("risk boundary coverage is incomplete or duplicated")
    raw_findings = terminal["findings"]
    if not isinstance(raw_findings, list):
        raise ValueError("findings must be a list")
    findings = [validate_finding(finding, index=index) for index, finding in enumerate(raw_findings)]
    raw_feedback = terminal["finding_feedback"]
    if not isinstance(raw_feedback, list):
        raise ValueError("finding_feedback must be a list")
    feedback = [
        _validate_feedback(item, index=index) for index, item in enumerate(raw_feedback)
    ]
    finding_counts = Counter(finding["severity"] for finding in findings)
    if finding_counts["p2"] > 3:
        raise ValueError("review terminal may contain at most three actionable p2 findings")
    suppressed = terminal["suppressed_speculative_count"]
    if not isinstance(suppressed, int) or isinstance(suppressed, bool) or suppressed < 0:
        raise ValueError("suppressed_speculative_count must be a non-negative integer")
    if terminal["stop_reason"] != "coverage-complete":
        raise ValueError("stop_reason must be coverage-complete")
    return {
        "valid": True,
        "reviewer_id": reviewer_id,
        "surface_id": assignment["id"],
        "finding_counts": {severity: finding_counts[severity] for severity in sorted(SEVERITIES)},
        "finding_feedback_count": len(feedback),
        "suppressed_speculative_count": suppressed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate_review_terminal(
            load_object(args.plan), load_object(args.input)
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
