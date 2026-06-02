#!/usr/bin/env python3
"""Validate manual stacked-PR choreography, especially around squash merges."""

from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-merge-method", choices=("merge", "rebase", "squash", "unknown"), required=True)
    parser.add_argument("--parent-state", choices=("open", "merged", "closed"), default="open")
    parser.add_argument("--parent-branch", required=True)
    parser.add_argument("--child-branch", required=True)
    parser.add_argument("--child-base", required=True)
    parser.add_argument("--final-base", required=True)
    parser.add_argument("--refresh-planned", action="store_true")
    parser.add_argument("--child-retargeted-to-final-base", action="store_true")
    parser.add_argument("--child-rebased-onto-final-base", action="store_true")
    parser.add_argument("--approvals-refreshed", action="store_true")
    parser.add_argument("--checks-refreshed", action="store_true")
    parser.add_argument("--parent-branch-deleted", action="store_true")
    args = parser.parse_args()

    reasons: list[str] = []
    warnings: list[str] = []

    is_stacked = args.child_base == args.parent_branch
    child_refreshed = args.child_retargeted_to_final_base or args.child_rebased_onto_final_base

    if args.final_base == args.parent_branch:
        warnings.append("final-base-matches-parent-branch")

    if not is_stacked and args.parent_state == "open":
        warnings.append("child-not-currently-stacked-on-parent")

    if is_stacked and args.parent_merge_method == "squash":
        if args.parent_state == "open":
            if not args.refresh_planned:
                reasons.append("downstream-refresh-plan-required-for-squash")
        elif args.parent_state == "merged":
            if not child_refreshed:
                reasons.append("downstream-refresh-required-after-squash-merge")
            if args.parent_branch_deleted and not child_refreshed:
                reasons.append("parent-branch-deleted-before-child-refresh")
            if child_refreshed:
                if not args.approvals_refreshed:
                    reasons.append("downstream-approvals-stale")
                if not args.checks_refreshed:
                    reasons.append("downstream-checks-stale")
        elif args.parent_state == "closed":
            reasons.append("parent-closed-before-stack-refresh")

    if is_stacked and args.parent_merge_method in {"merge", "rebase", "unknown"} and args.parent_state == "open":
        warnings.append("downstream-refresh-plan-still-recommended")

    result = {
        "allowed": not reasons,
        "block_reasons": reasons,
        "warnings": warnings,
        "summary": {
            "parent_merge_method": args.parent_merge_method,
            "parent_state": args.parent_state,
            "parent_branch": args.parent_branch,
            "child_branch": args.child_branch,
            "child_base": args.child_base,
            "final_base": args.final_base,
            "is_stacked": is_stacked,
            "refresh_planned": args.refresh_planned,
            "child_refreshed": child_refreshed,
            "approvals_refreshed": args.approvals_refreshed,
            "checks_refreshed": args.checks_refreshed,
            "parent_branch_deleted": args.parent_branch_deleted,
        },
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
