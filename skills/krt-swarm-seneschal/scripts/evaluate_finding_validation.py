#!/usr/bin/env python3
"""Evaluate a targeted validator batch against the canonical finding registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from deterministic_validation import load_object, non_empty_string
from finding_registry import validate_registry
from validate_review_terminal import validate_finding


def evaluate_finding_validation(
    registry: dict[str, Any], batch: dict[str, Any]
) -> dict[str, Any]:
    validate_registry(registry)
    fields = {
        "contract_hash",
        "diff_digest",
        "validator_id",
        "finding_ids",
        "allow_new_critical",
        "new_critical_findings",
    }
    if not isinstance(batch, dict) or set(batch) != fields:
        raise ValueError("validator batch has missing or unknown fields")
    for field in ("contract_hash", "diff_digest"):
        if batch[field] != registry[field]:
            raise ValueError(f"validator batch {field} does not match registry")
    validator_id = non_empty_string(batch["validator_id"], "validator_id")
    finding_ids = batch["finding_ids"]
    if (
        not isinstance(finding_ids, list)
        or not all(isinstance(item, str) and item for item in finding_ids)
        or len(finding_ids) != len(set(finding_ids))
    ):
        raise ValueError("finding_ids must be a unique string list")
    if not finding_ids and any(
        finding["status"] == "proposed" for finding in registry["findings"]
    ):
        raise ValueError("empty finding_ids cannot omit proposed findings")
    if not isinstance(batch["allow_new_critical"], bool):
        raise ValueError("allow_new_critical must be boolean")
    if not isinstance(batch["new_critical_findings"], list):
        raise ValueError("new_critical_findings must be a list")
    critical = [
        validate_finding(finding, index=index)
        for index, finding in enumerate(batch["new_critical_findings"])
    ]
    if critical and not batch["allow_new_critical"]:
        raise ValueError("validator batch does not allow new critical findings")
    if any(finding["severity"] not in {"p0", "p1"} for finding in critical):
        raise ValueError("targeted validators may add only new p0 or p1 findings")

    wanted = set(finding_ids)
    registry_findings = {
        finding["id"]: finding
        for finding in registry["findings"]
        if finding["id"] in wanted
    }
    missing = sorted(wanted - set(registry_findings))
    if missing:
        raise ValueError(f"unknown targeted finding ids: {missing}")
    actionable: list[str] = []
    rejected: list[str] = []
    for finding_id in finding_ids:
        finding = registry_findings.get(finding_id)
        validation = finding["validation"]
        if not isinstance(validation, dict):
            raise ValueError(f"targeted finding lacks validation: {finding_id}")
        if validation.get("validator_id") != validator_id:
            raise ValueError(f"targeted finding validator mismatch: {finding_id}")
        if finding["status"] in {"confirmed", "revised"}:
            actionable.append(finding_id)
        elif finding["status"] == "rejected":
            rejected.append(finding_id)
        else:
            raise ValueError(f"targeted finding has invalid validation status: {finding_id}")
    return {
        "status": "complete",
        "registry_digest": registry["registry_digest"],
        "validator_id": validator_id,
        "actionable_finding_ids": sorted(actionable),
        "rejected_finding_ids": sorted(rejected),
        "new_critical_findings": critical,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = evaluate_finding_validation(
            load_object(args.registry), load_object(args.input)
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
