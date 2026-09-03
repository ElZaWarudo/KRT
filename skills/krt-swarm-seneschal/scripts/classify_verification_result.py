#!/usr/bin/env python3
"""Conservatively classify a verification result from root-captured evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from deterministic_validation import exact_object, load_object, non_empty_string, string_list


RESULT_FIELDS = {"schema_version", "command", "current", "baseline", "environment", "owned_surface_changed"}
ATTEMPT_FIELDS = {"exit_code", "failure_fingerprint"}
BASELINE_FIELDS = {"attempted", "source_revision", "exit_code", "failure_fingerprint"}
ENVIRONMENT_FIELDS = {"dependencies_available", "evidence"}


def _exit_code(value: Any, field: str, *, optional: bool = False) -> int | None:
    if optional and value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field} must be an integer")
    return value


def _fingerprint(value: Any, field: str, *, optional: bool = False) -> str | None:
    if optional and value is None:
        return None
    fingerprint = non_empty_string(value, field)
    if not fingerprint.startswith("sha256:"):
        raise ValueError(f"{field} must use sha256")
    return fingerprint


def classify_verification_result(document: dict[str, Any]) -> dict[str, Any]:
    exact_object(document, RESULT_FIELDS, "verification result")
    if document["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    command = non_empty_string(document["command"], "command")
    current = exact_object(document["current"], ATTEMPT_FIELDS, "current")
    current_exit = _exit_code(current["exit_code"], "current.exit_code")
    current_fingerprint = _fingerprint(
        current["failure_fingerprint"],
        "current.failure_fingerprint",
        optional=current_exit == 0,
    )
    baseline = exact_object(document["baseline"], BASELINE_FIELDS, "baseline")
    if not isinstance(baseline["attempted"], bool):
        raise ValueError("baseline.attempted must be boolean")
    source_revision = baseline["source_revision"]
    baseline_exit = _exit_code(
        baseline["exit_code"], "baseline.exit_code", optional=not baseline["attempted"]
    )
    baseline_fingerprint = _fingerprint(
        baseline["failure_fingerprint"],
        "baseline.failure_fingerprint",
        optional=not baseline["attempted"] or baseline_exit == 0,
    )
    if baseline["attempted"]:
        non_empty_string(source_revision, "baseline.source_revision")
    elif source_revision is not None or baseline_exit is not None or baseline_fingerprint is not None:
        raise ValueError("unattempted baseline must not contain result evidence")
    environment = exact_object(
        document["environment"], ENVIRONMENT_FIELDS, "environment"
    )
    dependencies_available = environment["dependencies_available"]
    if dependencies_available is not True and dependencies_available is not False and dependencies_available is not None:
        raise ValueError("environment.dependencies_available must be true, false, or null")
    environment_evidence = string_list(
        environment["evidence"], "environment.evidence", unique=True
    )
    if dependencies_available is False and not environment_evidence:
        raise ValueError("missing dependencies require environment evidence")
    if not isinstance(document["owned_surface_changed"], bool):
        raise ValueError("owned_surface_changed must be boolean")

    reasons: list[str]
    if current_exit == 0:
        classification = "passed"
        reasons = ["current-command-passed"]
    elif dependencies_available is False:
        classification = "environment_failure"
        reasons = ["dependency-preflight-failed"]
    elif baseline["attempted"] and baseline_exit == 0:
        classification = "regression"
        reasons = ["same-command-passed-on-sealed-baseline"]
    elif (
        baseline["attempted"]
        and baseline_exit != 0
        and baseline_fingerprint == current_fingerprint
        and document["owned_surface_changed"] is False
    ):
        classification = "baseline_failure"
        reasons = ["matching-failure-on-sealed-baseline", "relevant-owned-surface-unchanged"]
    else:
        classification = "unclassified_failure"
        reasons = ["insufficient-attribution-evidence"]
    return {
        "schema_version": 1,
        "command": command,
        "classification": classification,
        "reasons": reasons,
        "certifies_readiness": classification == "passed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = classify_verification_result(load_object(args.input))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
