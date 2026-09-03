#!/usr/bin/env python3
"""Validate and immutably persist an accepted Reviewer or Fixer terminal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from deterministic_artifacts import file_sha256, write_exclusive_atomic
from deterministic_validation import load_object
from validate_fixer_terminal import validate_fixer_terminal
from validate_review_terminal import validate_review_terminal


def persist_role_terminal(
    *,
    role: str,
    expected_actor_id: str,
    assignment_path: Path,
    input_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    assignment = load_object(assignment_path)
    terminal = load_object(input_path)
    if role == "reviewer":
        validation = validate_review_terminal(assignment, terminal)
        actual_actor_id = terminal.get("reviewer_id")
    elif role == "fixer":
        validation = validate_fixer_terminal(assignment, terminal)
        actual_actor_id = terminal.get("fixer_id")
    else:
        raise ValueError("role must be reviewer or fixer")
    if actual_actor_id != expected_actor_id:
        raise ValueError("terminal actor ID does not match the dispatched actor")
    write_exclusive_atomic(output_path, terminal)
    return {
        "valid": True,
        "role": role,
        "terminal_path": str(output_path.resolve()),
        "terminal_digest": file_sha256(output_path),
        "validation": validation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=("reviewer", "fixer"), required=True)
    parser.add_argument("--expected-actor-id", required=True)
    parser.add_argument("--assignment", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = persist_role_terminal(
            role=args.role,
            expected_actor_id=args.expected_actor_id,
            assignment_path=args.assignment,
            input_path=args.input,
            output_path=args.output,
        )
    except (FileExistsError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
