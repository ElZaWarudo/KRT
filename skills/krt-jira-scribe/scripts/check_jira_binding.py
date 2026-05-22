#!/usr/bin/env python3
"""Validate exact Jira issue to GitHub PR binding and backlink idempotency."""

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
    warnings: list[str] = []
    jira_key = targets.get("jira_key")
    pr_url = targets.get("pr_url")
    expected_global_id = f"github-pr:{pr_url}" if pr_url else None

    if args.mutation_class != "jira_backlink":
        reasons.append(f"unsupported-mutation-class:{args.mutation_class}")
    if not pr_url:
        reasons.append("missing-pr-url")
    if not jira_key or jira_key not in state.get("ledger_jira_keys", []):
        reasons.append("jira-key-not-ledger-bound")
    if state.get("issue_key") and jira_key != state["issue_key"]:
        reasons.append("jira-key-live-mismatch")
    remote_links = state.get("remote_links", [])
    matching = [link for link in remote_links if expected_global_id and link.get("globalId") == expected_global_id]
    conflicting = [link for link in remote_links if link.get("globalId", "").startswith("github-pr:") and link.get("object", {}).get("url") != pr_url]
    if conflicting:
        reasons.append("jira-linked-to-different-pr")
    if matching:
        warnings.append("backlink-already-present")

    result = {
        "allowed": not reasons,
        "mutation_class": args.mutation_class,
        "target": targets,
        "payload_hash": None,
        "block_reasons": reasons,
        "warnings": warnings,
        "live_state_summary": {"no_op": bool(matching), "globalId": expected_global_id},
        "audit_required": True,
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
