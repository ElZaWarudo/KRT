#!/usr/bin/env python3
"""Validate autonomous branch push, force-push, and cleanup mutations."""

from __future__ import annotations

import argparse
import fnmatch
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
    branch = targets.get("branch") or state.get("branch")
    reasons: list[str] = []

    if args.mutation_class not in {"branch_push", "branch_force_push", "branch_cleanup"}:
        reasons.append(f"unsupported-mutation-class:{args.mutation_class}")
    if branch == state.get("default_branch") or branch in state.get("protected_branches", []):
        reasons.append("protected-branch-target")
    if not any(fnmatch.fnmatch(str(branch), pattern) for pattern in state.get("owned_patterns", [])):
        reasons.append("branch-not-run-owned")
    if args.mutation_class == "branch_force_push" and not state.get("force_with_lease_allowed"):
        reasons.append("force-with-lease-not-ledger-enabled")
    if targets.get("old_sha") and state.get("old_sha") and targets["old_sha"] != state["old_sha"]:
        reasons.append("old-sha-mismatch")
    if args.mutation_class == "branch_cleanup" and not (state.get("merged") or state.get("abandoned")):
        reasons.append("cleanup-branch-not-merged-or-abandoned")

    result = {
        "allowed": not reasons,
        "mutation_class": args.mutation_class,
        "target": targets,
        "payload_hash": None,
        "block_reasons": reasons,
        "warnings": [],
        "live_state_summary": {"branch": branch, "old_sha": state.get("old_sha")},
        "audit_required": True,
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
