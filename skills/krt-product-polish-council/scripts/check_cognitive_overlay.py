#!/usr/bin/env python3
"""Validate Council cognitive-load overlays and compute the Court referral gate."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


EXPECTED_EVALUATORS = {f"{number:02d}" for number in range(1, 13)}
FACTORS = {"M", "S", "I", "D", "U", "R"}
CLAIM_BASES = {
    "heuristic",
    "observed-behavior",
    "behavioral-measure",
    "self-report",
    "instrumented",
    "mixed",
}
PROFILE_SENSITIVITY = {
    "none",
    "possible-reversal",
    "confirmed-reversal",
    "unknown",
}
REFERRALS = {"no", "candidate"}
SEVERITIES = {"P0", "P1", "P2", "P3"}
EVALUATOR_ID = re.compile(r"^(\d{2})(?:\b|\s|\s*[-\u2014])")


def load_bundle(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError("top level must be an object")
    return value


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def parse_evaluator_id(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    match = EVALUATOR_ID.match(value.strip())
    return match.group(1) if match else None


def validate_bool(context: dict[str, Any], key: str, errors: list[str]) -> bool:
    value = context.get(key, False)
    if type(value) is not bool:
        errors.append(f"context.{key} must be boolean")
        return False
    return value


def validate(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    context = bundle.get("context", {})
    if not isinstance(context, dict):
        errors.append("context must be an object")
        context = {}
    explicit = validate_bool(context, "cognitive_load_requested", errors)
    comparison = validate_bool(context, "workload_comparison_required", errors)

    evaluators = bundle.get("evaluators")
    if not isinstance(evaluators, list):
        errors.append("evaluators must be a list")
        evaluators = []

    seen_evaluators: set[str] = set()
    finding_count = 0
    signals: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    triggers: list[dict[str, Any]] = []

    if explicit:
        triggers.append({"type": "explicit-request"})
    if comparison:
        triggers.append({"type": "workload-comparison"})

    for evaluator_index, evaluator in enumerate(evaluators):
        label = f"evaluators[{evaluator_index}]"
        if not isinstance(evaluator, dict):
            errors.append(f"{label} must be an object")
            continue
        evaluator_id = parse_evaluator_id(evaluator.get("evaluator"))
        if evaluator_id not in EXPECTED_EVALUATORS:
            errors.append(f"{label}.evaluator must start with 01 through 12")
            continue
        if evaluator_id in seen_evaluators:
            errors.append(f"duplicate evaluator: {evaluator_id}")
            continue
        seen_evaluators.add(evaluator_id)

        findings = evaluator.get("findings")
        if not isinstance(findings, list):
            errors.append(f"evaluator {evaluator_id}: findings must be a list")
            continue

        for finding_index, finding in enumerate(findings):
            finding_count += 1
            finding_label = f"evaluator {evaluator_id} finding[{finding_index}]"
            if not isinstance(finding, dict):
                errors.append(f"{finding_label} must be an object")
                continue
            finding_id = finding.get("id")
            if not nonempty_string(finding_id):
                errors.append(f"{finding_label}.id must be a non-empty string")
                finding_id = finding_label
            severity = finding.get("severity")
            if severity not in SEVERITIES:
                errors.append(f"{finding_id}: severity must be P0, P1, P2, or P3")

            affected = finding.get("affected")
            if not (
                isinstance(affected, list)
                and affected
                and all(nonempty_string(item) for item in affected)
            ):
                errors.append(f"{finding_id}: affected must contain strings")
                affected = []
            flows = sorted(
                item.strip()
                for item in affected
                if isinstance(item, str) and item.strip().startswith("FLOW-")
            )

            overlay = finding.get("cognitive_load")
            if not isinstance(overlay, dict):
                errors.append(f"{finding_id}: missing cognitive_load object")
                continue

            factors = overlay.get("factors")
            if not isinstance(factors, list) or any(
                factor not in FACTORS for factor in factors
            ):
                errors.append(
                    f"{finding_id}: cognitive_load.factors must contain only "
                    "M, S, I, D, U, or R"
                )
                factors = []
            elif len(factors) != len(set(factors)):
                errors.append(f"{finding_id}: cognitive_load.factors must be unique")

            profile = overlay.get("profile")
            if not nonempty_string(profile):
                errors.append(
                    f"{finding_id}: cognitive_load.profile must be a non-empty string"
                )
                profile = "unknown"
            else:
                profile = profile.strip()

            if not nonempty_string(overlay.get("rationale")):
                errors.append(
                    f"{finding_id}: cognitive_load.rationale must be a non-empty string"
                )
            claim_basis = overlay.get("claim_basis")
            if claim_basis not in CLAIM_BASES:
                errors.append(f"{finding_id}: invalid cognitive_load.claim_basis")
            sensitivity = overlay.get("profile_sensitivity")
            if sensitivity not in PROFILE_SENSITIVITY:
                errors.append(
                    f"{finding_id}: invalid cognitive_load.profile_sensitivity"
                )
            referral = overlay.get("court_referral")
            if referral not in REFERRALS:
                errors.append(f"{finding_id}: invalid cognitive_load.court_referral")

            if factors and not flows:
                errors.append(
                    f"{finding_id}: a cognitive factor requires an affected FLOW-*"
                )
            if not factors and referral == "candidate":
                errors.append(
                    f"{finding_id}: court_referral cannot be candidate without factors"
                )
            if not factors and sensitivity in {
                "possible-reversal",
                "confirmed-reversal",
            }:
                errors.append(
                    f"{finding_id}: profile reversal requires at least one factor"
                )

            finding_tuples: list[dict[str, str]] = []
            for flow in flows:
                for factor in factors:
                    signals[(flow, profile, factor)].add(evaluator_id)
                    finding_tuples.append(
                        {"flow": flow, "profile": profile, "factor": factor}
                    )

            if severity in {"P0", "P1"} and factors:
                triggers.append(
                    {
                        "type": "high-severity-cognitive-finding",
                        "finding": finding_id,
                        "tuples": finding_tuples,
                    }
                )
            if sensitivity in {"possible-reversal", "confirmed-reversal"}:
                triggers.append(
                    {
                        "type": "profile-reversal",
                        "finding": finding_id,
                        "sensitivity": sensitivity,
                        "tuples": finding_tuples,
                    }
                )

    missing = sorted(EXPECTED_EVALUATORS - seen_evaluators)
    extra = sorted(seen_evaluators - EXPECTED_EVALUATORS)
    if missing:
        errors.append(f"missing evaluators: {', '.join(missing)}")
    if extra:
        errors.append(f"unexpected evaluators: {', '.join(extra)}")

    signal_rows = []
    for (flow, profile, factor), evaluator_ids in sorted(signals.items()):
        row = {
            "flow": flow,
            "profile": profile,
            "factor": factor,
            "evaluators": sorted(evaluator_ids),
        }
        signal_rows.append(row)
        if len(evaluator_ids) >= 2:
            triggers.append({"type": "repeated-signal", **row})

    if errors:
        raise ValueError("\n".join(errors))

    return {
        "status": "valid",
        "evaluator_count": len(seen_evaluators),
        "finding_count": finding_count,
        "court_required": bool(triggers),
        "triggers": triggers,
        "signals": signal_rows,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args(argv[1:])
    try:
        result = validate(load_bundle(args.bundle))
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
