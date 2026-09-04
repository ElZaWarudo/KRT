#!/usr/bin/env python3
"""Compile role-aware, one-invocation-per-worktree workspace assignments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

from deterministic_artifacts import canonical_sha256
from deterministic_validation import exact_object, load_object, non_empty_string, string_list


PLAN_FIELDS = {
    "schema_version",
    "run_id",
    "base_revision",
    "worktree_parent",
    "invocations",
}
OPTIONAL_PLAN_FIELDS = {"integration_branch"}
INVOCATION_FIELDS = {
    "id",
    "unit_id",
    "role",
    "depends_on",
    "candidate_invocations",
    "owned_paths",
}
ROLE_MODES = {
    "planner": ("read-only", "base"),
    "discovery": ("read-only", "dependency"),
    "implementer": ("mutable", "dependency"),
    "reviewer": ("read-only", "candidate"),
    "security-reviewer": ("read-only", "candidate"),
    "targeted-validator": ("disposable-verification", "candidate"),
    "ci-validator": ("disposable-verification", "candidate"),
    "fixer": ("mutable", "candidate"),
    "documenter": ("mutable", "consolidated"),
    "compound-master": ("mutable", "dependency"),
    "integrator": ("mutable-consolidation", "dependency"),
}
READ_ONLY_ROLES = {role for role, (mode, _) in ROLE_MODES.items() if mode != "mutable" and not mode.startswith("mutable-")}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def _identifier(value: Any, field: str) -> str:
    result = non_empty_string(value, field)
    if not ID_PATTERN.fullmatch(result):
        raise ValueError(f"{field} must contain only lowercase path-safe characters")
    return result


def _paths(value: Any, field: str, *, allow_empty: bool) -> list[str]:
    paths = string_list(value, field, allow_empty=allow_empty, unique=True)
    for path in paths:
        candidate = PurePosixPath(path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"{field} must contain repo-relative paths")
    return sorted(paths)


def plan_worker_workspaces(plan: dict[str, Any]) -> dict[str, Any]:
    if (
        not isinstance(plan, dict)
        or PLAN_FIELDS - set(plan)
        or set(plan) - PLAN_FIELDS - OPTIONAL_PLAN_FIELDS
    ):
        raise ValueError("workspace plan has missing or unknown fields")
    if plan["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    integration_branch_enabled = plan.get("integration_branch", True)
    if not isinstance(integration_branch_enabled, bool):
        raise ValueError("integration_branch must be boolean")
    run_id = _identifier(plan["run_id"], "run_id")
    base_revision = non_empty_string(plan["base_revision"], "base_revision")
    parent = PurePosixPath(non_empty_string(plan["worktree_parent"], "worktree_parent"))
    if not parent.is_absolute():
        raise ValueError("worktree_parent must be an absolute path")
    raw_invocations = plan["invocations"]
    if not isinstance(raw_invocations, list) or not raw_invocations:
        raise ValueError("invocations must be a non-empty list")

    normalized: list[dict[str, Any]] = []
    ids: set[str] = set()
    for index, raw in enumerate(raw_invocations):
        item = exact_object(raw, INVOCATION_FIELDS, f"invocations[{index}]")
        invocation_id = _identifier(item["id"], f"invocations[{index}].id")
        if invocation_id in ids:
            raise ValueError("invocation ids must be unique")
        ids.add(invocation_id)
        role = non_empty_string(item["role"], f"invocations[{index}].role")
        if role not in ROLE_MODES:
            raise ValueError(f"unsupported worker role: {role}")
        mode, baseline_source = ROLE_MODES[role]
        owned_paths = _paths(
            item["owned_paths"],
            f"invocations[{index}].owned_paths",
            allow_empty=role in READ_ONLY_ROLES,
        )
        if role in READ_ONLY_ROLES and owned_paths:
            raise ValueError(f"{role} workspaces must not own mutable paths")
        normalized.append(
            {
                "invocation_id": invocation_id,
                "unit_id": _identifier(item["unit_id"], f"invocations[{index}].unit_id"),
                "role": role,
                "mode": mode,
                "baseline_source": baseline_source,
                "depends_on": sorted(string_list(item["depends_on"], f"invocations[{index}].depends_on", unique=True)),
                "candidate_invocations": sorted(string_list(item["candidate_invocations"], f"invocations[{index}].candidate_invocations", unique=True)),
                "owned_paths": owned_paths,
            }
        )

    integration = [item for item in normalized if item["role"] == "integrator"]
    if len(integration) != 1:
        raise ValueError("exactly one integrator consolidation workspace is required")
    for item in normalized:
        referenced = set(item["depends_on"] + item["candidate_invocations"])
        unknown = sorted(referenced - ids)
        if unknown:
            raise ValueError(f"invocation {item['invocation_id']} references unknown invocations: {unknown}")
        if item["invocation_id"] in referenced:
            raise ValueError(f"invocation {item['invocation_id']} references itself")
        needs_candidate = item["baseline_source"] == "candidate"
        if needs_candidate != bool(item["candidate_invocations"]):
            requirement = "requires" if needs_candidate else "must not declare"
            raise ValueError(f"role {item['role']} {requirement} candidate_invocations")
        if item["role"] == "integrator" and not item["depends_on"]:
            raise ValueError("integrator must depend on at least one worker invocation")

    remaining = {item["invocation_id"]: item for item in normalized}
    completed: set[str] = set()
    execution_waves: list[list[str]] = []
    while remaining:
        ready = sorted(
            identifier
            for identifier, item in remaining.items()
            if set(item["depends_on"] + item["candidate_invocations"]).issubset(completed)
        )
        if not ready:
            raise ValueError("workspace dependency/candidate graph contains a cycle")
        execution_waves.append(ready)
        completed.update(ready)
        for identifier in ready:
            del remaining[identifier]

    lookup = {item["invocation_id"]: item for item in normalized}
    consolidation_id = integration[0]["invocation_id"]
    consolidation_ancestors: set[str] = set()
    frontier = list(lookup[consolidation_id]["depends_on"])
    while frontier:
        identifier = frontier.pop()
        if identifier in consolidation_ancestors:
            continue
        consolidation_ancestors.add(identifier)
        ancestor = lookup[identifier]
        frontier.extend(ancestor["depends_on"] + ancestor["candidate_invocations"])
    unconsolidated = sorted(
        item["invocation_id"]
        for item in normalized
        if item["mode"].startswith("mutable")
        and item["invocation_id"] != consolidation_id
        and item["invocation_id"] not in consolidation_ancestors
    )
    if unconsolidated:
        raise ValueError(f"mutable invocations do not feed consolidation: {unconsolidated}")

    workspaces = []
    for item in normalized:
        invocation_id = item["invocation_id"]
        branch = (
            f"seneschal/{run_id}/integration"
            if item["role"] == "integrator" and integration_branch_enabled
            else None
        )
        payload = {
            **item,
            "workspace_id": f"{run_id}-{invocation_id}",
            "path": str(parent / run_id / invocation_id),
            "branch": branch,
            "detached": branch is None,
            "worker_git_mutation": "forbidden",
            "base_revision": base_revision,
            "dependency_patch_hashes": [],
            "baseline_tree": None,
        }
        workspaces.append(payload)
    result = {
        "schema_version": 1,
        "run_id": run_id,
        "base_revision": base_revision,
        "worktree_parent": str(parent),
        "consolidation_invocation": consolidation_id,
        "integration_branch": f"seneschal/{run_id}/integration" if integration_branch_enabled else None,
        "execution_waves": execution_waves,
        "patch_application_order": [
            identifier
            for wave in execution_waves
            for identifier in wave
            if next(item for item in normalized if item["invocation_id"] == identifier)["mode"].startswith("mutable")
        ],
        "workspaces": workspaces,
        "lifecycle": ["create", "seed-index", "seal-baseline", "dispatch", "observe", "export-patch", "reconcile", "cleanup"],
    }
    return {**result, "workspace_plan_hash": canonical_sha256(result)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = plan_worker_workspaces(load_object(args.input))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
