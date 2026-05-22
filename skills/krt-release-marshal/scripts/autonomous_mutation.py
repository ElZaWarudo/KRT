#!/usr/bin/env python3
"""Validate, optionally execute, and audit autonomous external mutations."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import autonomous_audit


DEFAULT_LEDGER_CHECK = Path(__file__).resolve().parents[2] / "krt-compound-master" / "scripts" / "check_autonomy_ledger.py"
SKILLS_DIR = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent

VALIDATOR_REGISTRY = {
    "branch_push": SCRIPT_DIR / "check_branch_mutation.py",
    "branch_force_push": SCRIPT_DIR / "check_branch_mutation.py",
    "branch_cleanup": SCRIPT_DIR / "check_branch_mutation.py",
    "pr_create": SCRIPT_DIR / "check_pr_mutation.py",
    "pr_update": SCRIPT_DIR / "check_pr_mutation.py",
    "pr_ready": SCRIPT_DIR / "check_pr_mutation.py",
    "reviewer_request": SCRIPT_DIR / "check_reviewer_request.py",
    "pr_merge": SCRIPT_DIR / "check_merge_eligibility.py",
    "pr_merge_queue": SCRIPT_DIR / "check_merge_eligibility.py",
    "pr_auto_merge": SCRIPT_DIR / "check_merge_eligibility.py",
    "jira_create": SKILLS_DIR / "krt-jira-scribe" / "scripts" / "check_jira_issue_mutation.py",
    "jira_update": SKILLS_DIR / "krt-jira-scribe" / "scripts" / "check_jira_issue_mutation.py",
    "jira_backlink": SKILLS_DIR / "krt-jira-scribe" / "scripts" / "check_jira_binding.py",
    "jira_transition_review": SKILLS_DIR / "krt-jira-scribe" / "scripts" / "check_jira_transition.py",
    "jira_transition_done": SKILLS_DIR / "krt-jira-scribe" / "scripts" / "check_jira_transition.py",
}


def sha256_file(path: Path | None) -> str | None:
    if path is None:
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_targets(values: list[str]) -> dict[str, str]:
    targets: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"target must be key=value: {value}")
        key, raw = value.split("=", 1)
        targets[key] = raw
    return targets


def run_json_command(command: list[str]) -> tuple[int, dict[str, Any]]:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        data = {
            "allowed": False,
            "block_reasons": ["validator-output-not-json"],
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    return completed.returncode, data


def append_audit_or_block(audit_dir: Path, event: dict[str, Any], reasons: list[str]) -> dict[str, Any] | None:
    try:
        return autonomous_audit.append_event(audit_dir, event)
    except Exception as exc:
        reasons.append(f"audit-write-failed:{exc}")
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--mutation-class", required=True)
    parser.add_argument("--target", action="append", default=[])
    parser.add_argument("--payload-file")
    parser.add_argument("--state-file", help="Live-state JSON fixture or fetched state for the class validator")
    parser.add_argument("--audit-dir")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true", help="Request execution through a registered command template")
    parser.add_argument("--enforcement-confirmed", action="store_true")
    parser.add_argument("--ledger-check", default=str(DEFAULT_LEDGER_CHECK))
    parser.add_argument("--expected-contract-hash")
    parser.add_argument("--now")
    args = parser.parse_args()

    targets = parse_targets(args.target)
    payload_path = Path(args.payload_file) if args.payload_file else None
    payload_digest = sha256_file(payload_path)
    reasons: list[str] = []
    validator_path = VALIDATOR_REGISTRY.get(args.mutation_class)
    if validator_path is None:
        reasons.append(f"unknown-mutation-class:{args.mutation_class}")
    elif not validator_path.exists():
        reasons.append(f"validator-missing:{validator_path}")
    if not args.state_file:
        reasons.append("state-file-required")

    ledger_path = Path(args.ledger)
    ledger_json = json.loads(ledger_path.read_text(encoding="utf-8"))
    audit_dir = Path(args.audit_dir or ledger_json.get("audit", {}).get("path", "autonomous-audit"))
    actual_audit_head = autonomous_audit.latest_hash(audit_dir)
    reasons.extend(autonomous_audit.verify_head(audit_dir))
    if args.execute and not args.expected_contract_hash:
        reasons.append("expected-contract-hash-required-for-execution")

    ledger_cmd = [
        sys.executable,
        args.ledger_check,
        args.ledger,
        "--mutation-class",
        args.mutation_class,
    ]
    for key, value in targets.items():
        ledger_cmd.extend(["--target", f"{key}={value}"])
    if args.payload_file:
        ledger_cmd.extend(["--payload-file", args.payload_file])
    if args.now:
        ledger_cmd.extend(["--now", args.now])
    if args.expected_contract_hash:
        ledger_cmd.extend(["--expected-contract-hash", args.expected_contract_hash])
    ledger_cmd.extend(["--expected-audit-head", actual_audit_head])

    _, ledger_result = run_json_command(ledger_cmd)
    if not ledger_result.get("allowed"):
        reasons.extend(ledger_result.get("block_reasons", ["ledger-validation-failed"]))

    if validator_path and args.state_file:
        validator_cmd = [
            sys.executable,
            str(validator_path),
            "--mutation-class",
            args.mutation_class,
            "--fixture",
            args.state_file,
        ]
        for key, value in targets.items():
            validator_cmd.extend(["--target", f"{key}={value}"])
        if args.payload_file:
            validator_cmd.extend(["--payload-file", args.payload_file])
        _, validator_result = run_json_command(validator_cmd)
        if not validator_result.get("allowed"):
            reasons.extend(validator_result.get("block_reasons", ["payload-validation-failed"]))
    else:
        validator_result = {
            "allowed": False,
            "block_reasons": ["validator-not-run"],
        }

    planned_event = {
        "stage": "planned",
        "contract_id": ledger_result.get("contract_id") or ledger_json.get("contract_id"),
        "mutation_class": args.mutation_class,
        "target": targets,
        "payload_hash": payload_digest,
        "ledger_result": ledger_result,
        "validator_result": validator_result,
        "execution_requested": bool(args.execute),
        "actual_audit_head": actual_audit_head,
    }
    planned_audit = append_audit_or_block(audit_dir, planned_event, reasons)

    execution_mode = "dry-run"
    command_result: dict[str, Any] | None = None
    if args.execute:
        if not args.enforcement_confirmed:
            reasons.append("enforcement-boundary-unconfirmed")
            execution_mode = "validation-only"
        else:
            reasons.append("execution-template-unavailable")
            execution_mode = "validation-only"

    final_event = {
        "stage": "validated" if not reasons else "validation-failed",
        "contract_id": ledger_result.get("contract_id") or ledger_json.get("contract_id"),
        "mutation_class": args.mutation_class,
        "target": targets,
        "payload_hash": payload_digest,
        "execution_mode": execution_mode,
        "block_reasons": reasons,
        "command_result": command_result,
        "planned_event_hash": planned_audit.get("event_hash") if planned_audit else None,
    }
    final_audit = append_audit_or_block(audit_dir, final_event, reasons)

    result = {
        "allowed": not reasons and execution_mode in {"dry-run", "executed"},
        "mutation_class": args.mutation_class,
        "target": targets,
        "payload_hash": payload_digest,
        "block_reasons": reasons,
        "warnings": [],
        "live_state_summary": {
            "ledger_allowed": ledger_result.get("allowed", False),
            "validator_allowed": validator_result.get("allowed", False),
            "execution_mode": execution_mode,
        },
        "audit_required": True,
        "audit": {
            "planned": planned_audit,
            "final": final_audit,
        },
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
