#!/usr/bin/env python3
"""Materialize or check a hashed executable Seneschal worker contract."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from worker_contract import materialize_contract, validate_contract


def load_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("contract must be a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check == bool(args.output):
        parser.error("choose exactly one of --check or --output")
    try:
        document = load_object(args.input)
        if args.check:
            result = validate_contract(document)
        else:
            result = materialize_contract(document)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(
        {"contract_hash": result["contract_hash"], "valid": True},
        sys.stdout,
        indent=2,
        sort_keys=True,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
