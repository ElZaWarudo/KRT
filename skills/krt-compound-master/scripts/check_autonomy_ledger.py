#!/usr/bin/env python3
"""Validate a Compound Master autonomy ledger for one planned mutation."""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


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

SUPPORTED_SCHEMA_VERSION = 1

LIFECYCLE_STATES = {
    "pending-authorization",
    "active",
    "expired",
    "revoked",
    "scope-mismatch",
    "superseded",
    "resume-blocked",
}

REQUIRED_FIELDS = {
    "schema_version",
    "contract_id",
    "issued_at",
    "expires_at",
    "status",
    "issuer",
    "scope",
    "allowed_mutations",
    "stop_conditions",
    "audit",
    "contract_hash",
}

TARGET_REQUIREMENTS = {
    "branch_push": (("repository", "branch", "old_sha", "new_sha"), ()),
    "branch_force_push": (("repository", "branch", "old_sha", "new_sha"), ()),
    "branch_cleanup": (("repository", "branch"), ()),
    "pr_create": (("repository", "base_branch", "head_branch", "head_sha"), ()),
    "pr_update": (("repository", "base_branch", "head_branch", "head_sha"), (("pr_number", "pr_url"),)),
    "pr_ready": (("repository", "base_branch", "head_branch", "head_sha"), (("pr_number", "pr_url"),)),
    "reviewer_request": (("repository", "reviewer"), (("pr_number", "pr_url"),)),
    "jira_create": (("jira_project",), ()),
    "jira_update": (("jira_project", "jira_key"), ()),
    "jira_backlink": (("jira_project", "jira_key", "pr_url"), ()),
    "jira_transition_review": (("jira_project", "jira_key", "transition_id"), ()),
    "jira_transition_done": (("jira_project", "jira_key", "pr_url"), ()),
    "pr_merge": (("repository", "base_branch", "head_branch", "head_sha"), (("pr_number", "pr_url"),)),
    "pr_merge_queue": (("repository", "base_branch", "head_branch", "head_sha"), (("pr_number", "pr_url"),)),
    "pr_auto_merge": (("repository", "base_branch", "head_branch", "head_sha"), (("pr_number", "pr_url"),)),
}


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def parse_time(value: str) -> dt.datetime:
    if value.endswith("Z"):
        value = f"{value[:-1]}+00:00"
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def canonical_payload(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def contract_hash(ledger: dict[str, Any]) -> str:
    payload = {key: value for key, value in ledger.items() if key != "contract_hash"}
    return hashlib.sha256(canonical_payload(payload).encode("utf-8")).hexdigest()


def parse_targets(values: list[str]) -> dict[str, str]:
    targets: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"target must be key=value: {value}")
        key, raw = value.split("=", 1)
        if not key:
            raise ValueError(f"target key is empty: {value}")
        targets[key] = raw
    return targets


def payload_hash(payload_file: str | None) -> str | None:
    if not payload_file:
        return None
    data = Path(payload_file).read_bytes()
    return hashlib.sha256(data).hexdigest()


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def scope_allows(scope: dict[str, Any], targets: dict[str, str], reasons: list[str]) -> None:
    repo = targets.get("repository")
    if repo and scope.get("repository") and repo != scope["repository"]:
        reasons.append("scope-mismatch:repository")

    base = targets.get("base_branch")
    if base and scope.get("base_branch") and base != scope["base_branch"]:
        reasons.append("scope-mismatch:base_branch")

    branch = targets.get("branch") or targets.get("head_branch")
    patterns = as_list(scope.get("branch_patterns"))
    if branch and patterns and not any(fnmatch.fnmatch(branch, pattern) for pattern in patterns):
        reasons.append("scope-mismatch:branch")

    package = targets.get("package")
    packages = as_list(scope.get("packages"))
    if package and packages and package not in packages:
        reasons.append("scope-mismatch:package")

    review_unit = targets.get("review_unit")
    review_units = as_list(scope.get("review_units"))
    if review_unit and review_units and review_unit not in review_units:
        reasons.append("scope-mismatch:review_unit")

    jira_key = targets.get("jira_key")
    jira_keys = as_list(scope.get("jira_keys"))
    if jira_key and jira_keys and jira_key not in jira_keys:
        reasons.append("scope-mismatch:jira_key")

    jira_project = targets.get("jira_project")
    jira_projects = as_list(scope.get("jira_projects"))
    if jira_project and jira_projects and jira_project not in jira_projects:
        reasons.append("scope-mismatch:jira_project")


def required_targets_present(mutation_class: str, targets: dict[str, str], reasons: list[str]) -> None:
    required, alternatives = TARGET_REQUIREMENTS.get(mutation_class, ((), ()))
    for key in required:
        if not targets.get(key):
            reasons.append(f"missing-target:{key}")
    for group in alternatives:
        if not any(targets.get(key) for key in group):
            reasons.append(f"missing-target:{'|'.join(group)}")


def validate(
    ledger: dict[str, Any],
    mutation_class: str,
    targets: dict[str, str],
    *,
    now: dt.datetime,
    expected_contract_hash: str | None,
    expected_audit_head: str | None,
    payload_file: str | None,
) -> dict[str, Any]:
    reasons: list[str] = []
    warnings: list[str] = []

    missing = sorted(REQUIRED_FIELDS - ledger.keys())
    if missing:
        reasons.append(f"schema-error:missing:{','.join(missing)}")

    schema_version = ledger.get("schema_version")
    if "schema_version" in ledger and (
        type(schema_version) is not int
        or schema_version != SUPPORTED_SCHEMA_VERSION
    ):
        reasons.append(f"schema-error:unsupported-version:{schema_version}")

    status = ledger.get("status")
    if status not in LIFECYCLE_STATES:
        reasons.append("schema-error:unknown-status")
    elif status != "active":
        reasons.append(f"ledger-not-active:{status}")

    if mutation_class not in MUTATION_CLASSES:
        reasons.append(f"unsupported-mutation-class:{mutation_class}")
    elif mutation_class not in as_list(ledger.get("allowed_mutations")):
        reasons.append(f"mutation-not-allowed:{mutation_class}")
    else:
        required_targets_present(mutation_class, targets, reasons)

    issuer = ledger.get("issuer")
    if not isinstance(issuer, dict):
        reasons.append("schema-error:issuer")
    elif not issuer.get("approval_hash") or not (issuer.get("id") or issuer.get("approval_ref")):
        reasons.append("missing-issuer-approval-binding")

    scope = ledger.get("scope")
    if not isinstance(scope, dict):
        reasons.append("schema-error:scope")
    else:
        scope_allows(scope, targets, reasons)

    audit = ledger.get("audit")
    if not isinstance(audit, dict) or not audit.get("path"):
        reasons.append("schema-error:audit-path")
    elif expected_audit_head is not None and audit.get("head_hash") != expected_audit_head:
        reasons.append("audit-chain-mismatch")

    try:
        expires_at = parse_time(str(ledger.get("expires_at")))
        if expires_at <= now:
            reasons.append("expired")
    except Exception:
        reasons.append("schema-error:expires_at")

    actual_hash = contract_hash(ledger)
    embedded_hash = ledger.get("contract_hash")
    if not embedded_hash:
        reasons.append("missing-contract-hash")
    elif embedded_hash != actual_hash:
        reasons.append("contract-hash-mismatch")
    if expected_contract_hash and expected_contract_hash != actual_hash:
        reasons.append("unexpected-contract-hash")

    superseded_by = ledger.get("superseded_by")
    if superseded_by:
        reasons.append(f"superseded:{superseded_by}")

    if ledger.get("revoked_reason") and status != "revoked":
        warnings.append("revoked_reason-present-on-active-ledger")

    result = {
        "allowed": not reasons,
        "mutation_class": mutation_class,
        "target": targets,
        "payload_hash": payload_hash(payload_file),
        "block_reasons": reasons,
        "warnings": warnings,
        "live_state_summary": {
            "source": "ledger",
            "contract_id": ledger.get("contract_id"),
            "status": status,
            "expires_at": ledger.get("expires_at"),
        },
        "audit_required": True,
        "contract_id": ledger.get("contract_id"),
        "contract_hash": actual_hash,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", help="Path to autonomy ledger JSON")
    parser.add_argument("--mutation-class", required=True)
    parser.add_argument("--target", action="append", default=[], help="Target scope as key=value")
    parser.add_argument("--payload-file")
    parser.add_argument("--now", help="ISO timestamp for deterministic tests")
    parser.add_argument("--expected-contract-hash")
    parser.add_argument("--expected-audit-head")
    args = parser.parse_args()

    try:
        targets = parse_targets(args.target)
        ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
        now = parse_time(args.now) if args.now else utc_now()
        result = validate(
            ledger,
            args.mutation_class,
            targets,
            now=now,
            expected_contract_hash=args.expected_contract_hash,
            expected_audit_head=args.expected_audit_head,
            payload_file=args.payload_file,
        )
    except Exception as exc:
        result = {
            "allowed": False,
            "mutation_class": args.mutation_class,
            "target": {},
            "payload_hash": None,
            "block_reasons": [f"validator-error:{exc}"],
            "warnings": [],
            "live_state_summary": {},
            "audit_required": True,
        }

    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
