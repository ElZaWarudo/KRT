#!/usr/bin/env python3
"""Validate autonomous PR create, update, and ready mutations."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SUPPORTED = {"pr_create", "pr_update", "pr_ready"}
UNSUPPORTED_REVIEW_STATE = {"pr_approve", "review_dismiss", "thread_resolve", "branch_protection_bypass"}


def parse_targets(values: list[str]) -> dict[str, str]:
    return dict(value.split("=", 1) for value in values if "=" in value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mutation-class", required=True)
    parser.add_argument("--target", action="append", default=[])
    parser.add_argument("--fixture")
    parser.add_argument("--payload-file")
    args = parser.parse_args()

    targets = parse_targets(args.target)
    reasons: list[str] = []
    payload_hash = hashlib.sha256(Path(args.payload_file).read_bytes()).hexdigest() if args.payload_file else None

    if args.mutation_class in UNSUPPORTED_REVIEW_STATE or args.mutation_class not in SUPPORTED:
        reasons.append(f"unsupported-mutation-class:{args.mutation_class}")

    if not args.fixture:
        reasons.append("live-pr-state-required")
        state = {}
    else:
        state = json.loads(Path(args.fixture).read_text(encoding="utf-8"))

    if targets.get("repository") and state.get("repository") and targets["repository"] != state["repository"]:
        reasons.append("scope-mismatch:repository")
    if targets.get("base_branch") and state.get("base_branch") and targets["base_branch"] != state["base_branch"]:
        reasons.append("scope-mismatch:base_branch")
    if not (state.get("head_sha") or targets.get("head_sha")):
        reasons.append("missing-head-sha")
    if state.get("branch_owned") is False:
        reasons.append("head-branch-not-run-owned")
    if state.get("body_valid") is False:
        reasons.append("pr-body-invalid")
    if args.mutation_class == "pr_ready" and not state.get("draft"):
        reasons.append("pr-ready-noop:not-draft")

    for pr in state.get("open_prs", []):
        if pr.get("head") == state.get("head_branch") and pr.get("base") == state.get("base_branch"):
            if args.mutation_class == "pr_create":
                reasons.append("duplicate-open-pr")

    result = {
        "allowed": not reasons,
        "mutation_class": args.mutation_class,
        "target": targets,
        "payload_hash": payload_hash,
        "block_reasons": reasons,
        "warnings": [],
        "live_state_summary": {
            "head_sha": state.get("head_sha") or targets.get("head_sha"),
            "draft": state.get("draft"),
        },
        "audit_required": True,
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
