#!/usr/bin/env python3
"""Validate autonomous GitHub PR merge, queue, or auto-merge eligibility."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


MERGE_CLASSES = {"pr_merge", "pr_merge_queue", "pr_auto_merge"}
REVIEW_OPTIONAL_BASE_PREFIXES = (
    "experimental",
    "experiment",
    "spike",
    "sandbox",
    "prototype",
    "playground",
)


def parse_targets(values: list[str]) -> dict[str, str]:
    return dict(value.split("=", 1) for value in values if "=" in value)


def output(mutation_class: str, targets: dict[str, str], reasons: list[str], summary: dict[str, Any], action: str | None = None) -> int:
    result = {
        "allowed": not reasons,
        "mutation_class": mutation_class,
        "target": targets,
        "payload_hash": None,
        "block_reasons": reasons,
        "warnings": [],
        "live_state_summary": {**summary, "action": action},
        "audit_required": True,
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


def review_user(review: dict[str, Any]) -> str:
    user = review.get("user")
    if isinstance(user, dict):
        return str(user.get("login", ""))
    return str(user or "")


def is_review_optional_base(branch: str) -> bool:
    lowered = branch.strip().lower()
    for prefix in REVIEW_OPTIONAL_BASE_PREFIXES:
        if lowered == prefix or lowered.startswith(f"{prefix}/") or lowered.startswith(f"{prefix}-"):
            return True
    return False


def check_state(state: dict[str, Any], mutation_class: str, targets: dict[str, str], current_actor: str | None) -> tuple[list[str], dict[str, Any], str | None]:
    reasons: list[str] = []
    pr = state.get("pr", state)
    author = str(pr.get("author", {}).get("login") or pr.get("author") or "")
    head_sha = str(pr.get("headRefOid") or pr.get("head_sha") or "")
    base_branch = str(pr.get("baseRefName") or targets.get("base_branch") or "")
    review_optional_base = is_review_optional_base(base_branch)

    if mutation_class not in MERGE_CLASSES:
        reasons.append(f"unsupported-mutation-class:{mutation_class}")
    if pr.get("state") != "OPEN":
        reasons.append("pr-not-open")
    if pr.get("isDraft"):
        reasons.append("pr-is-draft")
    if not head_sha:
        reasons.append("missing-head-sha")
    if targets.get("base_branch") and pr.get("baseRefName") != targets["base_branch"]:
        reasons.append("scope-mismatch:base_branch")
    if targets.get("head_branch") and pr.get("headRefName") != targets["head_branch"]:
        reasons.append("scope-mismatch:head_branch")
    branch_protection = state.get("branch_protection")
    if not branch_protection or branch_protection.get("available") is False:
        reasons.append("branch-protection-unavailable")
    if branch_protection and branch_protection.get("rulesets_available") is False:
        reasons.append("ruleset-state-unavailable")
    if branch_protection and branch_protection.get("code_owner_reviews_required") and not branch_protection.get("code_owner_approved"):
        reasons.append("code-owner-review-missing")

    required_count = int((branch_protection or {}).get("required_approving_review_count") or 0)
    code_owner_required = bool((branch_protection or {}).get("code_owner_reviews_required"))
    review_required = not review_optional_base or required_count > 0 or code_owner_required
    minimum_approval_count = max(required_count, 1) if review_required else 0
    review_decision = pr.get("reviewDecision")
    if review_required:
        if review_decision is None:
            reasons.append("review-state-unavailable")
        elif str(review_decision).upper() != "APPROVED":
            reasons.append(f"review-decision-not-approved:{review_decision}")

    reviews = list(pr.get("latestReviews") or pr.get("reviews") or [])
    approval_count = 0
    for review in reviews:
        state_name = str(review.get("state", "")).upper()
        actor = review_user(review)
        if state_name == "CHANGES_REQUESTED" and not review.get("dismissed"):
            reasons.append("unresolved-change-request")
        if state_name != "APPROVED":
            continue
        if review.get("dismissed"):
            continue
        if review.get("commit_id") not in {None, head_sha}:
            continue
        if actor and actor == author:
            continue
        if current_actor and actor == current_actor:
            continue
        if actor.endswith("[bot]") or review.get("actor_type") == "Bot":
            continue
        approval_count += 1

    if approval_count < minimum_approval_count:
        reasons.append("current-head-human-approval-missing")

    required = set(state.get("required_checks") or [])
    checks = {str(check.get("name") or check.get("context")): check for check in pr.get("statusCheckRollup", [])}
    for name in sorted(required):
        check = checks.get(name)
        if not check:
            reasons.append(f"required-check-unavailable:{name}")
            continue
        conclusion = str(check.get("conclusion") or "").upper()
        status = str(check.get("status") or check.get("state") or "").upper()
        if conclusion:
            green = conclusion in {"SUCCESS", "PASS"}
        else:
            green = status in {"SUCCESS", "PASS"}
        if not green:
            reasons.append(f"required-check-not-green:{name}:{conclusion or status or 'unknown'}")

    if pr.get("mergeable") in {False, "CONFLICTING"}:
        reasons.append("pr-not-mergeable")
    if pr.get("mergeStateStatus") in {"DIRTY", "BLOCKED", "UNKNOWN"}:
        reasons.append(f"merge-state-blocked:{pr.get('mergeStateStatus')}")

    queue_required = bool(state.get("merge_queue_required") or (branch_protection or {}).get("merge_queue_required"))
    action = "merge"
    if queue_required:
        if mutation_class == "pr_merge":
            reasons.append("merge-queue-required")
        elif mutation_class == "pr_merge_queue":
            action = "enqueue"
        elif mutation_class == "pr_auto_merge":
            action = "enable-auto-merge"

    summary = {
        "pr_number": pr.get("number"),
        "base_branch": base_branch,
        "head_sha": head_sha,
        "review_optional_base": review_optional_base,
        "review_required": review_required,
        "approval_count": approval_count,
        "required_approval_count": minimum_approval_count,
        "merge_queue_required": queue_required,
    }
    return reasons, summary, action


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mutation-class", required=True)
    parser.add_argument("--target", action="append", default=[])
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--current-actor")
    args = parser.parse_args()

    targets = parse_targets(args.target)
    state = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    reasons, summary, action = check_state(state, args.mutation_class, targets, args.current_actor)
    return output(args.mutation_class, targets, reasons, summary, action)


if __name__ == "__main__":
    raise SystemExit(main())
