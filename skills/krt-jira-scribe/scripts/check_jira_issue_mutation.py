#!/usr/bin/env python3
"""Validate autonomous Jira issue create/update payloads."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


TEXT_PATH = Path(__file__).resolve().parent / "check_jira_text.py"
spec = importlib.util.spec_from_file_location("check_jira_text", TEXT_PATH)
text_mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(text_mod)


ALLOWED_FIELDS = {"project", "issuetype", "summary", "description", "parent", "labels", "components"}


def parse_targets(values: list[str]) -> dict[str, str]:
    return dict(value.split("=", 1) for value in values if "=" in value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mutation-class", required=True)
    parser.add_argument("--target", action="append", default=[])
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--payload-file")
    args = parser.parse_args()

    targets = parse_targets(args.target)
    state = json.loads(Path(args.fixture).read_text(encoding="utf-8"))
    payload = json.loads(Path(args.payload_file).read_text(encoding="utf-8")) if args.payload_file else state.get("payload", {})
    reasons: list[str] = []
    payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest() if payload else None

    if args.mutation_class not in {"jira_create", "jira_update"}:
        reasons.append(f"unsupported-mutation-class:{args.mutation_class}")
    unapproved = sorted(set(payload) - ALLOWED_FIELDS)
    if unapproved:
        reasons.append(f"unapproved-fields:{','.join(unapproved)}")
    if targets.get("jira_project") and payload.get("project") != targets["jira_project"]:
        reasons.append("scope-mismatch:jira_project")
    if state.get("duplicate_candidates", 0) > 1:
        reasons.append("ambiguous-duplicate-candidates")
    if state.get("duplicate_candidates", 0) == 1 and args.mutation_class == "jira_create":
        reasons.append("equivalent-issue-exists")
    if state.get("subtask") and not payload.get("parent"):
        reasons.append("subtask-parent-missing")
    if state.get("parent_key") and payload.get("parent") and payload["parent"] != state["parent_key"]:
        reasons.append("subtask-parent-mismatch")
    for field in ("summary", "description"):
        if payload.get(field):
            reasons.extend(f"{field}:{reason}" for reason in text_mod.validate_text(str(payload[field])))

    result = {
        "allowed": not reasons,
        "mutation_class": args.mutation_class,
        "target": targets,
        "payload_hash": payload_hash,
        "block_reasons": reasons,
        "warnings": [],
        "live_state_summary": {
            "duplicate_candidates": state.get("duplicate_candidates", 0),
            "issue_type": payload.get("issuetype"),
        },
        "audit_required": True,
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
