#!/usr/bin/env python3
"""Validate a Seneschal worker's exact terminal JSON before return."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evaluate_worker_run import validate_worker_terminal
from verification_evidence import load_json_object


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        contract = load_json_object(args.contract)
        terminal = load_json_object(args.input)
        validate_worker_terminal(contract, terminal)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump({"valid": True}, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
