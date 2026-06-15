#!/usr/bin/env python3
"""Validate Compound Master work-package review-unit guardrails."""

from __future__ import annotations

import re
import sys
from pathlib import Path


DOC_SECTIONS = (
    "docs/brainstorms",
    "docs/plans",
    "docs/work-packages",
    "docs/orchestration/compound-master-state.md",
)

MUTATION_CLASSES = {
    "branch_push",
    "branch_force_push",
    "branch_cleanup",
    "pr_create",
    "pr_update",
    "pr_ready",
    "reviewer_request",
    "jira_create",
    "jira_update",
    "jira_backlink",
    "jira_transition_review",
    "jira_transition_done",
    "pr_merge",
    "pr_merge_queue",
    "pr_auto_merge",
}


def section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", re.M | re.S)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check_work_package.py <work-package.md>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    warnings: list[str] = []

    if "review_units:" not in text:
        errors.append("frontmatter must include review_units: [RU1, ...]")

    autonomous_ledger = re.search(r"^autonomous_ledger:\s*(.+)$", text, re.M)
    allowed_mutations = re.search(r"^allowed_mutation_classes:\s*\[(.*?)\]\s*$", text, re.M)
    if autonomous_ledger:
        ledger_value = autonomous_ledger.group(1).strip()
        if ledger_value not in {"none", "null", "[]"} and not ledger_value.startswith("docs/orchestration/autonomy-ledgers/"):
            errors.append("autonomous_ledger must be none or a docs/orchestration/autonomy-ledgers/ path")
        if ledger_value not in {"none", "null", "[]"} and not allowed_mutations:
            errors.append("autonomous_ledger requires allowed_mutation_classes: [...]")
    if allowed_mutations:
        raw_values = [value.strip().strip("'\"") for value in allowed_mutations.group(1).split(",") if value.strip()]
        invalid = [value for value in raw_values if value not in MUTATION_CLASSES]
        if invalid:
            errors.append(f"invalid allowed_mutation_classes: {', '.join(invalid)}")

    review_units = section(text, "Review Units")
    if not review_units:
        errors.append("missing ## Review Units section")
    elif not re.search(r"\|\s*RU\d+\s*\|", review_units):
        errors.append("## Review Units must include table rows named RU1, RU2, ...")

    handoff = section(text, "Branch and PR Handoff Inputs")
    if not handoff:
        errors.append("missing ## Branch and PR Handoff Inputs section")
    else:
        if "Review unit:" not in handoff:
            errors.append("handoff inputs must name the selected Review unit")
        if "PR body bullets" not in handoff:
            errors.append("handoff inputs must include PR body bullets")
        if "PR body sentences" in handoff:
            errors.append("use PR body bullets, not PR body sentences")

    reviewability = section(text, "Reviewability Diagnosis")
    if not reviewability:
        warnings.append(
            "missing ## Reviewability Diagnosis section; record reviewer-experience "
            "rationale and the open-stack plan (Reviewability Gate)"
        )

    stacked = re.search(r"^pr_strategy:\s*stacked\s*$", text, re.M)
    if stacked:
        stack_signal = (
            re.search(r"^max_open_stack:\s*\S", text, re.M)
            or "wait-for-parent-merge" in text
            or "collapse-to-integration-base" in text
        )
        if not stack_signal:
            errors.append(
                "pr_strategy: stacked requires open-stack governance: set max_open_stack "
                "(target <=2, max 3) and an at-cap action (wait-for-parent-merge or "
                "collapse-to-integration-base)"
            )

    files_tests = section(text, "Files and Tests")
    review_scope = f"{files_tests}\n{review_units}\n{handoff}"
    mixed_docs = [p for p in DOC_SECTIONS if p in files_tests]
    runtime_hint = bool(re.search(r"\b(src|app|web-application|backend|frontend|lib)/", files_tests))
    if mixed_docs and runtime_hint:
        warnings.append(
            "package appears to mix orchestration docs with runtime files; "
            "ensure this is split into review units or explicitly justified"
        )

    generated_hint = re.search(r"(\.auto\.|generated|bindings|definitions\.ts)", review_scope, re.I)
    if generated_hint and "generated" not in review_units.lower():
        warnings.append("generated/mechanical artifacts detected; Review Units should isolate or justify them")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        return 1
    print("work package review-unit checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
