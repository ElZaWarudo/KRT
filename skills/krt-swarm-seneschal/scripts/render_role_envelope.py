#!/usr/bin/env python3
"""Render executable Reviewer and Fixer envelopes with concrete paths."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import shlex
import sys
from typing import Any

from deterministic_artifacts import file_sha256, write_atomic
from deterministic_validation import exact_object, load_object, non_empty_string, string_list
from validate_fixer_terminal import ASSIGNMENT_FIELDS as FIXER_ASSIGNMENT_FIELDS
from validate_review_terminal import _assignment_from_plan


ROLE_VALIDATORS = {
    "reviewer": ("validate_review_terminal.py", "--plan"),
    "fixer": ("validate_fixer_terminal.py", "--assignment"),
}


def _absolute_existing(path: Path, field: str, *, directory: bool = False) -> Path:
    if not path.is_absolute():
        raise ValueError(f"{field} must be an absolute path")
    resolved = path.resolve(strict=True)
    if directory and not resolved.is_dir():
        raise ValueError(f"{field} must be a directory")
    if not directory and not resolved.is_file():
        raise ValueError(f"{field} must be a file")
    return resolved


def _absolute_output(path: Path, field: str) -> Path:
    if not path.is_absolute():
        raise ValueError(f"{field} must be an absolute path")
    parent = path.parent.resolve(strict=True)
    if not parent.is_dir():
        raise ValueError(f"{field} parent must be a directory")
    return parent / path.name


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def render_role_envelope(
    *,
    role: str,
    actor_id: str,
    assignment_path: Path,
    workspace_root: Path,
    terminal_path: Path,
    surface_id: str | None = None,
    recovery_path: Path | None = None,
) -> dict[str, Any]:
    if role not in ROLE_VALIDATORS:
        raise ValueError("role must be reviewer or fixer")
    assignment = _absolute_existing(assignment_path, "assignment_path")
    actor = non_empty_string(actor_id, "actor_id")
    assignment_document = load_object(assignment)
    if role == "reviewer":
        if surface_id is None:
            raise ValueError("surface_id is required for reviewer envelopes")
        bound_assignment = _assignment_from_plan(
            assignment_document, non_empty_string(surface_id, "surface_id")
        )
        terminal_shape: dict[str, Any] = {
            "contract_hash": assignment_document["contract_hash"],
            "diff_digest": assignment_document["diff_digest"],
            "review_plan_hash": assignment_document["review_plan_hash"],
            "reviewer_id": actor,
            "surface_id": bound_assignment["id"],
            "risk_boundaries_checked": bound_assignment["risk_boundaries"],
            "findings": [],
            "finding_feedback": [],
            "suppressed_speculative_count": 0,
            "stop_reason": "coverage-complete",
        }
    else:
        if surface_id is not None:
            raise ValueError("surface_id is supported only for reviewer envelopes")
        exact_object(assignment_document, FIXER_ASSIGNMENT_FIELDS, "fixer assignment")
        non_empty_string(assignment_document["contract_hash"], "contract_hash")
        non_empty_string(assignment_document["registry_digest"], "registry_digest")
        string_list(
            assignment_document["finding_ids"], "finding_ids", allow_empty=False, unique=True
        )
        owned_paths = string_list(
            assignment_document["owned_paths"], "owned_paths", unique=True
        )
        if any(
            PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts
            for path in owned_paths
        ):
            raise ValueError("owned_paths must contain repo-relative paths")
        string_list(
            assignment_document["verification_commands"],
            "verification_commands",
            allow_empty=False,
            unique=True,
        )
        bound_assignment = assignment_document
        terminal_shape = {
            "contract_hash": assignment_document["contract_hash"],
            "registry_digest": assignment_document["registry_digest"],
            "fixer_id": actor,
            "finding_changes": "one exact mapping per assigned finding_id",
            "blockers": [],
            "stop_reason": "mapping-complete | blocked",
        }
    workspace = _absolute_existing(workspace_root, "workspace_root", directory=True)
    terminal = _absolute_output(terminal_path, "terminal_path")
    recovery = (
        _absolute_output(recovery_path, "recovery_path")
        if recovery_path is not None
        else None
    )
    if _inside(terminal, workspace):
        raise ValueError("terminal_path must be outside the worker workspace")
    if recovery is not None:
        if role != "reviewer":
            raise ValueError("recovery_path is supported only for reviewer envelopes")
        if recovery == terminal:
            raise ValueError("recovery_path must differ from terminal_path")
        if _inside(recovery, workspace):
            raise ValueError("recovery_path must be outside the worker workspace")

    validator_name, assignment_flag = ROLE_VALIDATORS[role]
    validator_path = Path(__file__).with_name(validator_name).resolve()
    validator_argv = [
        "rtk",
        "python3",
        str(validator_path),
        assignment_flag,
        str(assignment),
        "--input",
        str(terminal),
    ]
    validator = shlex.join(validator_argv)
    recovery_instruction = ""
    if recovery is not None:
        recovery_validator = Path(__file__).with_name(
            "validate_review_recovery.py"
        ).resolve()
        recovery_instruction = (
            f"\nThis assignment has bounded recovery enabled. After each completed risk "
            f"boundary, atomically replace {recovery} with a review-recovery-v1 candidate "
            f"and validate it with:\n"
            f"{shlex.join(['rtk', 'python3', str(recovery_validator), '--plan', str(assignment), '--input', str(recovery)])}\n"
            "The recovery artifact is untrusted partial evidence and never certifies review. "
            "Do not send heartbeat messages."
        )
    prompt = (
        f"Run the bounded {role} assignment in {workspace}.\n"
        f"Actor ID: {actor}\n"
        f"Canonical assignment: {assignment}\n"
        f"Assignment digest: {file_sha256(assignment)}\n"
        f"Bound assignment:\n{json.dumps(bound_assignment, indent=2, sort_keys=True)}\n"
        f"Exact terminal shape:\n{json.dumps(terminal_shape, indent=2, sort_keys=True)}\n"
        f"Write the final terminal to {terminal}, then run exactly:\n{validator}\n"
        "The passing validator must be your final command. Return only the exact JSON "
        "terminal, with no acknowledgement, prose, or side-channel report."
        f"{recovery_instruction}"
    )
    return {
        "schema_version": 1,
        "role": role,
        "actor_id": actor,
        "surface_id": bound_assignment["id"] if role == "reviewer" else None,
        "assignment_path": str(assignment),
        "assignment_digest": file_sha256(assignment),
        "workspace_root": str(workspace),
        "terminal_path": str(terminal),
        "recovery_path": str(recovery) if recovery is not None else None,
        "terminal_validation_command": validator,
        "prompt": prompt,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=sorted(ROLE_VALIDATORS), required=True)
    parser.add_argument("--actor-id", required=True)
    parser.add_argument("--assignment", type=Path, required=True)
    parser.add_argument("--workspace-root", type=Path, required=True)
    parser.add_argument("--terminal-path", type=Path, required=True)
    parser.add_argument("--surface-id")
    parser.add_argument("--recovery-path", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = render_role_envelope(
            role=args.role,
            actor_id=args.actor_id,
            assignment_path=args.assignment,
            workspace_root=args.workspace_root,
            terminal_path=args.terminal_path,
            surface_id=args.surface_id,
            recovery_path=args.recovery_path,
        )
        write_atomic(args.output, result)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
