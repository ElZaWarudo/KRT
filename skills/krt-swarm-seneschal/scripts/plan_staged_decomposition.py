#!/usr/bin/env python3
"""Compile one coupled implementation unit into gated serial/parallel stages."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any

from deterministic_artifacts import canonical_sha256
from deterministic_validation import exact_object, load_object, non_empty_string, string_list


PLAN_FIELDS = {
    "schema_version",
    "parent_unit_id",
    "parent_owned_paths",
    "shared_api_paths",
    "foundation",
    "dependents",
    "integration",
    "aggregate_commands",
}
UNIT_FIELDS = {
    "id",
    "title",
    "owned_paths",
    "depends_on",
    "focused_commands",
    "generated_paths",
}


def _paths(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    paths = string_list(value, field, allow_empty=allow_empty, unique=True)
    for path in paths:
        candidate = PurePosixPath(path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"{field} must contain repo-relative paths")
    return sorted(paths)


def _normalize_unit(value: Any, field: str, *, allow_empty_paths: bool = False) -> dict[str, Any]:
    unit = exact_object(value, UNIT_FIELDS, field)
    identifier = non_empty_string(unit["id"], f"{field}.id")
    owned_paths = _paths(
        unit["owned_paths"], f"{field}.owned_paths", allow_empty=allow_empty_paths
    )
    generated_paths = _paths(
        unit["generated_paths"], f"{field}.generated_paths", allow_empty=True
    )
    if any(path not in owned_paths for path in generated_paths):
        raise ValueError(f"{field}.generated_paths must be owned by the same unit")
    focused_commands = string_list(
        unit["focused_commands"],
        f"{field}.focused_commands",
        allow_empty=allow_empty_paths,
        unique=True,
    )
    if owned_paths and not focused_commands:
        raise ValueError(f"{field}.focused_commands must not be empty when it owns paths")
    return {
        "id": identifier,
        "title": non_empty_string(unit["title"], f"{field}.title"),
        "owned_paths": owned_paths,
        "depends_on": sorted(
            string_list(unit["depends_on"], f"{field}.depends_on", unique=True)
        ),
        "focused_commands": focused_commands,
        "generated_paths": generated_paths,
    }


def _assert_disjoint_partition(parent_paths: list[str], units: list[dict[str, Any]]) -> None:
    owners: dict[str, list[str]] = {path: [] for path in parent_paths}
    for unit in units:
        for path in unit["owned_paths"]:
            if path not in owners:
                raise ValueError(f"unit {unit['id']} owns path outside parent unit: {path}")
            owners[path].append(unit["id"])
    overlaps = {path: ids for path, ids in owners.items() if len(ids) > 1}
    missing = sorted(path for path, ids in owners.items() if not ids)
    if overlaps:
        raise ValueError(f"staged ownership overlaps: {overlaps}")
    if missing:
        raise ValueError(f"parent paths lack a staged owner: {missing}")


def _dependent_waves(
    foundation_id: str, dependents: list[dict[str, Any]]
) -> list[list[str]]:
    dependent_ids = {unit["id"] for unit in dependents}
    allowed = dependent_ids | {foundation_id}
    for unit in dependents:
        unknown = sorted(set(unit["depends_on"]) - allowed)
        if unknown:
            raise ValueError(f"unit {unit['id']} has unknown dependencies: {unknown}")
        if unit["id"] in unit["depends_on"]:
            raise ValueError(f"unit {unit['id']} depends on itself")

    completed = {foundation_id}
    remaining = {unit["id"]: unit for unit in dependents}
    waves: list[list[str]] = []
    while remaining:
        ready = sorted(
            identifier
            for identifier, unit in remaining.items()
            if set(unit["depends_on"]).issubset(completed)
        )
        if not ready:
            raise ValueError("dependent graph contains a cycle or lacks foundation ancestry")
        waves.append(ready)
        completed.update(ready)
        for identifier in ready:
            del remaining[identifier]

    for unit in dependents:
        ancestors: set[str] = set()
        frontier = list(unit["depends_on"])
        lookup = {candidate["id"]: candidate for candidate in dependents}
        while frontier:
            dependency = frontier.pop()
            if dependency in ancestors:
                continue
            ancestors.add(dependency)
            if dependency in lookup:
                frontier.extend(lookup[dependency]["depends_on"])
        if foundation_id not in ancestors:
            raise ValueError(f"unit {unit['id']} does not descend from foundation")
    return waves


def plan_staged_decomposition(plan: dict[str, Any]) -> dict[str, Any]:
    exact_object(plan, PLAN_FIELDS, "staged decomposition plan")
    if plan["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    parent_unit_id = non_empty_string(plan["parent_unit_id"], "parent_unit_id")
    parent_paths = _paths(plan["parent_owned_paths"], "parent_owned_paths")
    shared_api_paths = _paths(plan["shared_api_paths"], "shared_api_paths")
    foundation = _normalize_unit(plan["foundation"], "foundation")
    if foundation["depends_on"]:
        raise ValueError("foundation must not depend on another staged unit")
    if not set(shared_api_paths).issubset(foundation["owned_paths"]):
        raise ValueError("foundation must own every shared API path")

    raw_dependents = plan["dependents"]
    if not isinstance(raw_dependents, list) or len(raw_dependents) < 2:
        raise ValueError("staged decomposition requires at least two dependent units")
    dependents = [
        _normalize_unit(value, f"dependents[{index}]")
        for index, value in enumerate(raw_dependents)
    ]
    integration = _normalize_unit(
        plan["integration"], "integration", allow_empty_paths=True
    )
    all_units = [foundation, *dependents, integration]
    identifiers = [unit["id"] for unit in all_units]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("staged unit ids must be unique")
    if parent_unit_id in identifiers:
        raise ValueError("staged unit id must differ from parent_unit_id")
    _assert_disjoint_partition(parent_paths, all_units)

    dependent_waves = _dependent_waves(foundation["id"], dependents)
    dependent_ids = {unit["id"] for unit in dependents}
    if set(integration["depends_on"]) != dependent_ids:
        raise ValueError("integration must depend on every dependent unit")
    aggregate_commands = string_list(
        plan["aggregate_commands"], "aggregate_commands", allow_empty=False, unique=True
    )

    units = [
        {**foundation, "stage": "foundation"},
        *({**unit, "stage": "dependent"} for unit in dependents),
        {**integration, "stage": "integration"},
    ]
    waves = [
        {
            "stage": "foundation",
            "unit_ids": [foundation["id"]],
            "requires_release_ready": [],
        }
    ]
    dependent_lookup = {unit["id"]: unit for unit in dependents}
    for unit_ids in dependent_waves:
        required = sorted(
            {
                dependency
                for unit_id in unit_ids
                for dependency in dependent_lookup[unit_id]["depends_on"]
            }
        )
        waves.append(
            {
                "stage": "dependent",
                "unit_ids": unit_ids,
                "requires_release_ready": required,
            }
        )
    waves.append(
        {
            "stage": "integration",
            "unit_ids": [integration["id"]],
            "requires_release_ready": sorted(dependent_ids),
        }
    )
    payload = {
        "schema_version": 1,
        "parent_unit_id": parent_unit_id,
        "shared_api_paths": shared_api_paths,
        "units": units,
        "waves": waves,
        "foundation_gate": {
            "unit_id": foundation["id"],
            "required_status": "release-ready",
            "required_evidence": "focused-contract-and-triggered-review-gates",
        },
        "aggregate_commands": aggregate_commands,
        "aggregate_owner": "seneschal-root",
    }
    return {**payload, "topology_hash": canonical_sha256(payload)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = plan_staged_decomposition(load_object(args.input))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
