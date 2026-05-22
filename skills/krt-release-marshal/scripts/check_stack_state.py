#!/usr/bin/env python3
"""Validate autonomous stacked PR parent/child state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_targets(values: list[str]) -> dict[str, str]:
    return dict(value.split("=", 1) for value in values if "=" in value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mutation-class", required=True)
    parser.add_argument("--target", action="append", default=[])
    parser.add_argument("--fixture", required=True)
    args = parser.parse_args()

    targets = parse_targets(args.target)
    state = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    reasons: list[str] = []

    if state.get("parent_state") == "merged":
        if not state.get("retargeted_to_base"):
            reasons.append("downstream-retarget-required")
        if not state.get("approvals_refreshed"):
            reasons.append("downstream-approvals-stale")
        if not state.get("checks_refreshed"):
            reasons.append("downstream-checks-stale")
    elif state.get("child_base") != state.get("parent_branch"):
        reasons.append("child-not-stacked-on-parent")

    result = {
        "allowed": not reasons,
        "mutation_class": args.mutation_class,
        "target": targets,
        "payload_hash": None,
        "block_reasons": reasons,
        "warnings": [],
        "live_state_summary": state,
        "audit_required": True,
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
