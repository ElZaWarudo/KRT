#!/usr/bin/env python3
"""Render an exact worker dispatch envelope from a validated contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from deterministic_artifacts import write_atomic
from worker_contract import terminal_validation_command, validate_contract


def render_envelope(
    contract: dict[str, Any], *, contract_path: str, terminal_path: str
) -> dict[str, Any]:
    validate_contract(contract)
    validator = terminal_validation_command(contract_path, terminal_path)
    dispatch = {
        "objective": contract["objective"],
        "owned_files": contract["owned_files"],
        "required_context": contract["required_context"],
        "closed_decisions": contract["closed_decisions"],
        "forbidden_changes": contract["forbidden_changes"],
        "acceptance_criteria": contract["acceptance_criteria"],
        "commands": contract["commands"],
        "execution_budget": contract["execution_budget"],
    }
    prompt = (
        f"Execute worker contract {contract['contract_id']} ({contract['contract_hash']}).\n"
        f"Canonical dispatch facts:\n{json.dumps(dispatch, indent=2, sort_keys=True)}\n"
        f"Write the terminal payload to {terminal_path}, then run exactly:\n{validator}\n"
        "The validator must be your final command. Return only that JSON object, "
        "with every schema field present and no prose or side-channel report."
    )
    return {
        "schema_version": 1,
        "contract_hash": contract["contract_hash"],
        "worker_profile": contract["profile"],
        "terminal_schema": contract["terminal_schema"],
        "terminal_validation_command": validator,
        "prompt": prompt,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--terminal-path", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
        if not isinstance(contract, dict):
            raise ValueError("contract must contain a JSON object")
        result = render_envelope(
            contract, contract_path=str(args.contract), terminal_path=args.terminal_path
        )
        write_atomic(args.output, result)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
