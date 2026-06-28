#!/usr/bin/env python3
"""Validate autonomous Jira review/done workflow transitions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DONE_NAMES = {"hecho", "done", "finalizado", "cerrado"}


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
    action = "transition"
    jira_key = targets.get("jira_key")

    if args.mutation_class not in {"jira_transition_review", "jira_transition_done"}:
        reasons.append(f"unsupported-mutation-class:{args.mutation_class}")
    if jira_key and state.get("issue_key") and jira_key != state["issue_key"]:
        reasons.append("jira-key-live-mismatch")
    if state.get("project") and targets.get("jira_project") and state["project"] != targets["jira_project"]:
        reasons.append("scope-mismatch:jira_project")
    if args.mutation_class == "jira_transition_done":
        if state.get("status_category") == "done" and state.get("bound_pr_merged") and state.get("remote_link_matches_pr"):
            action = "noop-already-done"
        else:
            if not state.get("bound_pr_merged"):
                reasons.append("linked-pr-not-merged")
            if not state.get("remote_link_matches_pr"):
                reasons.append("pr-remote-link-missing-or-mismatch")
            allowed_transition = targets.get("transition_id") or state.get("ledger_transition_id")
            done_transitions = [
                transition for transition in state.get("transitions", [])
                if str(transition.get("name", "")).lower() in DONE_NAMES
                or transition.get("to", {}).get("statusCategory", {}).get("key") == "done"
            ]
            if allowed_transition:
                if not any(str(transition.get("id")) == str(allowed_transition) for transition in done_transitions):
                    reasons.append("configured-done-transition-unavailable")
            elif len(done_transitions) == 1:
                action = f"transition:{done_transitions[0].get('id')}"
            elif len(done_transitions) > 1:
                reasons.append("multiple-done-transitions")
            else:
                reasons.append("done-transition-unavailable")
    else:
        if not jira_key:
            reasons.append("missing-jira-key")
        if not state.get("remote_link_matches_pr"):
            reasons.append("pr-remote-link-missing-or-mismatch")
        allowed_transition = targets.get("transition_id") or state.get("ledger_transition_id")
        review_transitions = [
            transition for transition in state.get("transitions", [])
            if str(transition.get("id")) == str(allowed_transition)
            or str(transition.get("name", "")).lower() == "en revisión"
        ]
        if allowed_transition:
            if not any(str(transition.get("id")) == str(allowed_transition) for transition in review_transitions):
                reasons.append("configured-review-transition-unavailable")
        elif len(review_transitions) == 1:
            action = f"transition:{review_transitions[0].get('id')}"
        elif len(review_transitions) > 1:
            reasons.append("multiple-review-transitions")
        else:
            reasons.append("review-transition-unavailable")

    result = {
        "allowed": not reasons,
        "mutation_class": args.mutation_class,
        "target": targets,
        "payload_hash": None,
        "block_reasons": reasons,
        "warnings": warnings,
        "live_state_summary": {
            "issue_key": state.get("issue_key"),
            "status": state.get("status"),
            "action": action,
            "available_transitions": [transition.get("name") for transition in state.get("transitions", [])],
        },
        "audit_required": True,
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
