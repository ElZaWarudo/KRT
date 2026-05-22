#!/usr/bin/env python3
"""Validate autonomous reviewer request mutations."""

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
    reviewer = targets.get("reviewer") or state.get("candidate_reviewer")
    reasons: list[str] = []
    no_op = False

    if args.mutation_class != "reviewer_request":
        reasons.append(f"unsupported-mutation-class:{args.mutation_class}")
    if reviewer not in state.get("allowed_reviewers", []):
        reasons.append("reviewer-out-of-scope")
    if reviewer in {state.get("author"), state.get("current_actor")}:
        reasons.append("reviewer-is-author-or-agent")
    if str(reviewer).endswith("[bot]") or reviewer in state.get("bot_reviewers", []):
        reasons.append("reviewer-is-bot")
    if reviewer in state.get("requested_reviewers", []):
        no_op = True

    result = {
        "allowed": not reasons,
        "mutation_class": args.mutation_class,
        "target": targets,
        "payload_hash": None,
        "block_reasons": reasons,
        "warnings": ["reviewer-already-requested"] if no_op else [],
        "live_state_summary": {"reviewer": reviewer, "no_op": no_op},
        "audit_required": True,
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
