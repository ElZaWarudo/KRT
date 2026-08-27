#!/usr/bin/env python3
"""Compile a deterministic, surface-owned review plan for one observed diff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any

from deterministic_artifacts import canonical_sha256
from deterministic_validation import exact_object, non_empty_string, string_list


REVIEWER_ROLES = {"reviewer", "security-sentinel"}


def _path_list(value: Any, field: str, *, allow_empty: bool = True) -> list[str]:
    paths = string_list(value, field, allow_empty=allow_empty, unique=True)
    for path in paths:
        candidate = PurePosixPath(path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"{field} must contain repo-relative paths")
    return paths


def _normalize_surface(value: Any) -> dict[str, Any]:
    surface = exact_object(
        value,
        {
            "id",
            "reviewer_role",
            "owned_paths",
            "risk_boundaries",
            "cross_cutting",
            "priority",
        },
        "surface",
    )
    identifier = non_empty_string(surface["id"], "surface.id")
    role = surface["reviewer_role"]
    if role not in REVIEWER_ROLES:
        raise ValueError(f"surface {identifier} has an unsupported reviewer_role")
    if not isinstance(surface["cross_cutting"], bool):
        raise ValueError(f"surface {identifier}.cross_cutting must be boolean")
    priority = surface["priority"]
    if not isinstance(priority, int) or isinstance(priority, bool) or priority < 0:
        raise ValueError(f"surface {identifier}.priority must be a non-negative integer")
    return {
        "id": identifier,
        "reviewer_role": role,
        "owned_paths": sorted(_path_list(surface["owned_paths"], f"surface {identifier}.owned_paths")),
        "risk_boundaries": sorted(
            string_list(
                surface["risk_boundaries"],
                f"surface {identifier}.risk_boundaries",
                allow_empty=False,
                unique=True,
            )
        ),
        "cross_cutting": surface["cross_cutting"],
        "priority": priority,
    }


def plan_review_wave(plan: dict[str, Any]) -> dict[str, Any]:
    exact_object(
        plan,
        {
            "schema_version",
            "contract_hash",
            "diff_digest",
            "changed_paths",
            "reviewer_capacity",
            "surfaces",
        },
        "review plan",
    )
    if plan["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    contract_hash = non_empty_string(plan["contract_hash"], "contract_hash")
    diff_digest = non_empty_string(plan["diff_digest"], "diff_digest")
    if not contract_hash.startswith("sha256:") or not diff_digest.startswith("sha256:"):
        raise ValueError("contract_hash and diff_digest must use sha256")
    changed_paths = sorted(_path_list(plan["changed_paths"], "changed_paths", allow_empty=False))
    capacity = plan["reviewer_capacity"]
    if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 1:
        raise ValueError("reviewer_capacity must be a positive integer")
    if not isinstance(plan["surfaces"], list) or not plan["surfaces"]:
        raise ValueError("surfaces must be a non-empty list")
    surfaces = [_normalize_surface(surface) for surface in plan["surfaces"]]
    identifiers = [surface["id"] for surface in surfaces]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("surface ids must be unique")

    primary = [surface for surface in surfaces if not surface["cross_cutting"]]
    if not primary:
        raise ValueError("at least one primary surface is required")
    owners: dict[str, list[str]] = {path: [] for path in changed_paths}
    for surface in primary:
        for path in surface["owned_paths"]:
            if path not in owners:
                raise ValueError(f"surface {surface['id']} owns unchanged path {path}")
            owners[path].append(surface["id"])
    uncovered = sorted(path for path, path_owners in owners.items() if not path_owners)
    overlapping = {
        path: path_owners for path, path_owners in owners.items() if len(path_owners) > 1
    }
    if uncovered:
        raise ValueError(f"changed paths lack a primary review surface: {uncovered}")
    if overlapping:
        raise ValueError(f"primary review surfaces overlap: {overlapping}")

    ordered = sorted(surfaces, key=lambda item: (item["priority"], item["id"]))
    admitted = ordered[:capacity]
    queued = [
        {"assignment": surface, "reason": "reviewer-capacity"}
        for surface in ordered[capacity:]
    ]
    payload = {
        "schema_version": 1,
        "contract_hash": contract_hash,
        "diff_digest": diff_digest,
        "changed_paths": changed_paths,
        "assignments": admitted,
        "queued": queued,
        "coverage_complete": not queued,
        "validation_wave_required": len(ordered) > 1 or any(
            surface["cross_cutting"] for surface in ordered
        ),
    }
    return {**payload, "review_plan_hash": canonical_sha256(payload)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        value = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("input must contain a JSON object")
        result = plan_review_wave(value)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
