#!/usr/bin/env python3
"""Validate a Fixer finding-to-change terminal against its assignment."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any

from deterministic_validation import exact_object, load_object, non_empty_string, string_list


ASSIGNMENT_FIELDS = {
    "contract_hash",
    "registry_digest",
    "finding_ids",
    "owned_paths",
    "verification_commands",
}
TERMINAL_FIELDS = {
    "contract_hash",
    "registry_digest",
    "fixer_id",
    "finding_changes",
    "blockers",
    "stop_reason",
}
MAPPING_FIELDS = {"finding_id", "changed_paths", "verification_commands"}


def _paths(value: Any, field: str) -> list[str]:
    paths = string_list(value, field, unique=True)
    for path in paths:
        candidate = PurePosixPath(path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"{field} must contain repo-relative paths")
    return paths


def validate_fixer_terminal(
    assignment: dict[str, Any], terminal: dict[str, Any]
) -> dict[str, Any]:
    exact_object(assignment, ASSIGNMENT_FIELDS, "fixer assignment")
    exact_object(terminal, TERMINAL_FIELDS, "fixer terminal")
    for field in ("contract_hash", "registry_digest"):
        expected = non_empty_string(assignment[field], f"assignment.{field}")
        if terminal[field] != expected:
            raise ValueError(f"fixer terminal {field} does not match assignment")
    fixer_id = non_empty_string(terminal["fixer_id"], "fixer_id")
    finding_ids = string_list(
        assignment["finding_ids"], "assignment.finding_ids", allow_empty=False, unique=True
    )
    owned_paths = set(_paths(assignment["owned_paths"], "assignment.owned_paths"))
    expected_commands = string_list(
        assignment["verification_commands"],
        "assignment.verification_commands",
        allow_empty=False,
        unique=True,
    )
    mappings = terminal["finding_changes"]
    if not isinstance(mappings, list):
        raise ValueError("finding_changes must be a list")
    mapped_ids: list[str] = []
    mapped_commands: list[str] = []
    for index, raw_mapping in enumerate(mappings):
        field = f"finding_changes[{index}]"
        mapping = exact_object(raw_mapping, MAPPING_FIELDS, field)
        finding_id = non_empty_string(mapping["finding_id"], f"{field}.finding_id")
        if finding_id not in finding_ids:
            raise ValueError(f"{field}.finding_id is not assigned")
        changed_paths = _paths(mapping["changed_paths"], f"{field}.changed_paths")
        if not changed_paths:
            raise ValueError(f"{field}.changed_paths must not be empty")
        if any(path not in owned_paths for path in changed_paths):
            raise ValueError(f"{field}.changed_paths contains an unowned path")
        commands = string_list(
            mapping["verification_commands"],
            f"{field}.verification_commands",
            allow_empty=False,
            unique=True,
        )
        if any(command not in expected_commands for command in commands):
            raise ValueError(f"{field}.verification_commands contains an unassigned command")
        mapped_ids.append(finding_id)
        mapped_commands.extend(commands)
    blockers = string_list(terminal["blockers"], "blockers", unique=True)
    stop_reason = terminal["stop_reason"]
    if stop_reason not in {"mapping-complete", "blocked"}:
        raise ValueError("stop_reason is invalid")
    if len(mapped_ids) != len(set(mapped_ids)):
        raise ValueError("finding_changes must not duplicate an assigned finding")
    if stop_reason == "mapping-complete":
        if Counter(mapped_ids) != Counter(finding_ids):
            raise ValueError("finding_changes must map every assigned finding exactly once")
        if set(mapped_commands) != set(expected_commands):
            raise ValueError(
                "finding_changes must account for every assigned verification command"
            )
        if blockers:
            raise ValueError("mapping-complete terminal must not contain blockers")
    elif not blockers:
        raise ValueError("blocked terminal must contain a blocker")
    return {
        "valid": True,
        "fixer_id": fixer_id,
        "finding_count": len(mapped_ids),
        "changed_paths": sorted(
            {path for mapping in mappings for path in mapping["changed_paths"]}
        ),
        "stop_reason": stop_reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assignment", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate_fixer_terminal(
            load_object(args.assignment), load_object(args.input)
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
