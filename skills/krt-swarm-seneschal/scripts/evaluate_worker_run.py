#!/usr/bin/env python3
"""Fail-closed evaluation for Spark and Luna worker runs."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import shlex
import sys
import time
from pathlib import Path, PurePosixPath
from typing import Any

from evaluate_luna_run import evaluate_run as evaluate_legacy_run
from evaluate_luna_run import terminal_reasons as legacy_terminal_reasons
from worker_contract import COMMAND_TRUST, is_terminal_validation_argv, validate_contract


PROFILES = {"spark", "luna", "luna_xhigh"}
CERTIFICATION_ROLES = {"reviewer", "security-sentinel"}
CERTIFICATION_STATUSES = {"passed", "failed"}
TERMINAL_FIELDS = {
    "status",
    "phase",
    "remaining_actions",
    "terminal_ready",
    "acceptance_criteria_resolved",
    "acceptance_evidence",
    "last_required_command",
    "verification",
    "verification_commands_run",
    "unowned_failures",
}


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a list of strings")
    return value


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _command_allowed(command: str, contract: dict[str, Any]) -> bool:
    commands = contract["commands"]
    verification = commands["verification"]
    exact = set(commands["exact"] + verification["focused"] + verification["natural"])
    if command in exact:
        return True
    if any(token in command for token in ("&&", "||", ";", "|", "\n", "`", "$(", ">", "<")):
        return False
    if _is_terminal_validator_command(command):
        return any("validate_worker_terminal.py" in prefix for prefix in commands["read_only_prefixes"])
    try:
        argv = shlex.split(command)
    except ValueError:
        return False
    for prefix in commands["read_only_prefixes"]:
        try:
            prefix_argv = shlex.split(prefix)
        except ValueError:
            continue
        if argv[: len(prefix_argv)] != prefix_argv:
            continue
        remainder = argv[len(prefix_argv) :]
        if not remainder:
            return command == prefix
        if any(arg.startswith("-") for arg in remainder):
            return False
        if any(PurePosixPath(arg).is_absolute() or ".." in PurePosixPath(arg).parts for arg in remainder):
            return False
        return True
    return False


def _is_terminal_validator_command(command: str) -> bool:
    try:
        argv = shlex.split(command)
    except ValueError:
        return False
    return is_terminal_validation_argv(argv)


def _acceptance_reasons(
    contract: dict[str, Any], final: dict[str, Any]
) -> list[str]:
    evidence = final.get("acceptance_evidence")
    if not isinstance(evidence, list):
        return ["acceptance-evidence-missing"]
    expected = [criterion["id"] for criterion in contract["acceptance_criteria"]]
    actual: list[str] = []
    reasons: list[str] = []
    statuses: dict[str, str] = {}
    for item in evidence:
        if not isinstance(item, dict) or set(item) != {
            "criterion_id",
            "status",
            "evidence",
        }:
            reasons.append("acceptance-evidence-invalid")
            continue
        criterion_id = item.get("criterion_id")
        status = item.get("status")
        detail = item.get("evidence")
        if (
            not isinstance(criterion_id, str)
            or status not in {"satisfied", "not_satisfied"}
            or not isinstance(detail, str)
            or not detail.strip()
        ):
            reasons.append("acceptance-evidence-invalid")
            continue
        actual.append(criterion_id)
        statuses[criterion_id] = status
    if Counter(actual) != Counter(expected):
        reasons.append("acceptance-evidence-incomplete")
    if final.get("status") in {"done", "done_with_baseline_gaps"} and any(
        statuses.get(criterion_id) != "satisfied" for criterion_id in expected
    ):
        reasons.append("acceptance-evidence-unresolved")
    return reasons


def _terminal_schema_reasons(final: dict[str, Any]) -> list[str]:
    fields = set(final)
    if not TERMINAL_FIELDS.issubset(fields):
        return ["terminal-schema-missing-fields"]
    if fields - (TERMINAL_FIELDS | {"scope_extension"}):
        return ["terminal-schema-unknown-fields"]
    return []


def validate_worker_terminal(
    contract: dict[str, Any], final: dict[str, Any]
) -> dict[str, Any]:
    """Validate the worker-owned terminal payload before it is returned."""
    validate_contract(contract)
    reasons = _terminal_schema_reasons(final)
    reasons.extend(_acceptance_reasons(contract, final))
    reasons.extend(
        legacy_terminal_reasons(
            {
                # Root-only deep-lane facts are intentionally excluded here.
                # Reconciliation validates them from the real observation.
                "profile": "luna",
                "verification_manifest": contract["commands"]["verification"],
            },
            final,
        )
    )
    reasons = list(dict.fromkeys(reasons))
    if reasons:
        raise ValueError("invalid worker terminal: " + ", ".join(reasons))
    return final


def _command_reasons(
    contract: dict[str, Any], observation: dict[str, Any], final: dict[str, Any]
) -> tuple[list[str], dict[str, Any]]:
    evidence = observation.get("command_evidence")
    if not isinstance(evidence, dict) or set(evidence) != {"trust", "commands"}:
        return ["command-evidence-invalid"], {
            "evidence_trust": "missing",
            "out_of_manifest_commands": 0,
            "repeated_verification_commands": 0,
        }
    trust = evidence.get("trust")
    entries = evidence.get("commands")
    if trust not in COMMAND_TRUST or not isinstance(entries, list):
        return ["command-evidence-invalid"], {
            "evidence_trust": str(trust),
            "out_of_manifest_commands": 0,
            "repeated_verification_commands": 0,
        }
    reasons: list[str] = []
    minimum_trust = contract["evidence_policy"]["minimum_command_trust"]
    if COMMAND_TRUST[trust] < COMMAND_TRUST[minimum_trust]:
        reasons.append("command-evidence-trust-too-low")
    commands: list[str] = []
    verification_commands: list[str] = []
    outside = 0
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"command", "kind"}:
            reasons.append("command-evidence-invalid")
            continue
        command = entry.get("command")
        kind = entry.get("kind")
        if not isinstance(command, str) or not command or kind not in {
            "read-only",
            "exact",
            "verification",
        }:
            reasons.append("command-evidence-invalid")
            continue
        commands.append(command)
        if kind == "verification":
            verification_commands.append(command)
        if not _command_allowed(command, contract):
            outside += 1
            reasons.append("command-outside-contract")
    expected_exact = Counter(contract["commands"]["exact"])
    actual_exact = Counter(
        entry["command"]
        for entry in entries
        if isinstance(entry, dict) and entry.get("kind") == "exact"
    )
    if final.get("status") in {"done", "done_with_baseline_gaps"} and actual_exact != expected_exact:
        reasons.append("exact-command-count-mismatch")
    elif any(command not in expected_exact for command in actual_exact):
        reasons.append("exact-command-outside-contract")
    reported_verification = final.get("verification_commands_run")
    if not isinstance(reported_verification, list) or verification_commands != reported_verification:
        reasons.append("command-audit-verification-mismatch")
    repeats = sum(count - 1 for count in Counter(verification_commands).values() if count > 1)
    expected_validator = observation.get("terminal_validation_command")
    validator_exit_code = observation.get("terminal_validation_exit_code")
    if final.get("terminal_ready") is True and (
        not isinstance(expected_validator, str)
        or not _is_terminal_validator_command(expected_validator)
        or not commands
        or commands[-1] != expected_validator
        or validator_exit_code != 0
    ):
        reasons.append("terminal-validation-not-final-command")
    return list(dict.fromkeys(reasons)), {
        "evidence_trust": trust,
        "out_of_manifest_commands": outside,
        "repeated_verification_commands": repeats,
    }


def _certification_state(
    contract: dict[str, Any], observation: dict[str, Any]
) -> tuple[list[str], list[str], dict[str, int]]:
    certifications = observation.get("certifications", [])
    if not isinstance(certifications, list):
        return ["certification-evidence-invalid"], [], {"p0": 0, "p1": 0, "p2": 0}
    valid: dict[str, str] = {}
    seen_roles: set[str] = set()
    reasons: list[str] = []
    findings = {"p0": 0, "p1": 0, "p2": 0}
    worker_id = observation.get("worker_id")
    observed_diff_digest = observation.get("diff_digest")
    if (
        not isinstance(observed_diff_digest, str)
        or not observed_diff_digest.startswith("sha256:")
    ):
        reasons.append("root-diff-digest-invalid")
    for certificate in certifications:
        if not isinstance(certificate, dict):
            reasons.append("certification-evidence-invalid")
            continue
        required_fields = {
            "role",
            "actor_id",
            "status",
            "contract_hash",
            "diff_digest",
            "findings",
        }
        if set(certificate) != required_fields:
            reasons.append("certification-evidence-invalid")
            continue
        role = certificate.get("role")
        actor_id = certificate.get("actor_id")
        status = certificate.get("status")
        raw_findings = certificate.get("findings")
        if (
            role not in CERTIFICATION_ROLES
            or not isinstance(actor_id, str)
            or not actor_id
            or actor_id == worker_id
            or status not in CERTIFICATION_STATUSES
            or certificate.get("contract_hash") != contract["contract_hash"]
            or not isinstance(certificate.get("diff_digest"), str)
            or not certificate["diff_digest"]
            or not isinstance(raw_findings, list)
        ):
            reasons.append("certification-evidence-invalid")
            continue
        if certificate["diff_digest"] != observed_diff_digest:
            reasons.append("certification-diff-digest-mismatch")
            continue
        if role in seen_roles:
            reasons.append("certification-evidence-duplicated")
            continue
        seen_roles.add(role)
        valid[role] = status
        for finding in raw_findings:
            if not isinstance(finding, dict) or finding.get("severity") not in findings:
                reasons.append("certification-evidence-invalid")
                continue
            findings[finding["severity"]] += 1
    missing = [role for role in contract["required_certifications"] if role not in valid]
    failed = [role for role in contract["required_certifications"] if valid.get(role) == "failed"]
    return list(dict.fromkeys(reasons)), missing + [f"failed:{role}" for role in failed], findings


def evaluate_worker_run(
    contract: dict[str, Any], observation: dict[str, Any], *, now_ms: int
) -> dict[str, Any]:
    validate_contract(contract)
    if observation.get("contract_hash") != contract["contract_hash"]:
        raise ValueError("observation contract_hash does not match contract")
    if observation.get("profile") != contract["profile"]:
        raise ValueError("observation profile does not match contract")
    transformed = dict(observation)
    transformed["profile"] = "luna" if contract["profile"] == "spark" else contract["profile"]
    transformed["owned_files"] = contract["owned_files"]
    transformed["verification_manifest"] = contract["commands"]["verification"]
    base = evaluate_legacy_run(transformed, now_ms=now_ms)
    reasons = list(base["reasons"])
    final = observation.get("final")
    started_at = observation.get("started_at_ms")
    returned_at = observation.get("returned_at_ms")
    elapsed_limit = contract["execution_budget"]["max_elapsed_ms"]
    elapsed_at_observation = (
        returned_at if isinstance(final, dict) and isinstance(returned_at, int) else now_ms
    )
    elapsed_budget_exhausted = (
        isinstance(started_at, int)
        and elapsed_at_observation >= started_at
        and elapsed_at_observation - started_at > elapsed_limit
    )
    if isinstance(final, dict) and elapsed_budget_exhausted:
        reasons.append("execution-elapsed-budget-exceeded")
    scope_violations = 0
    changed_files = _string_list(observation.get("changed_files", []), "changed_files")
    if observation.get("changed_files_source") != "root-diff":
        reasons.append("changed-files-not-root-observed")
    allowed_files = set(contract["owned_files"])
    if contract["profile"] == "luna_xhigh" and isinstance(observation.get("checkpoint"), dict):
        allowed_files = set(observation["checkpoint"].get("planned_files", []))
    scope_violations = sum(path not in allowed_files for path in changed_files)
    if scope_violations:
        reasons.append("changed-file-outside-contract")

    command_metrics = {
        "evidence_trust": "not-terminal",
        "out_of_manifest_commands": 0,
        "repeated_verification_commands": 0,
    }
    certification_pending: list[str] = []
    finding_counts = {"p0": 0, "p1": 0, "p2": 0}
    if isinstance(final, dict):
        reasons.extend(_terminal_schema_reasons(final))
        reasons.extend(_acceptance_reasons(contract, final))
        command_reasons, command_metrics = _command_reasons(contract, observation, final)
        reasons.extend(command_reasons)
        certification_reasons, certification_pending, finding_counts = _certification_state(
            contract, observation
        )
        reasons.extend(certification_reasons)

    reasons = list(dict.fromkeys(reasons))
    action = base["action"]
    successful_terminal = base["terminal_status"] in {"done", "done_with_baseline_gaps"}
    failed_certifications = [item for item in certification_pending if item.startswith("failed:")]
    missing_certifications = [item for item in certification_pending if not item.startswith("failed:")]
    if reasons:
        action = "contract_violation"
    elif not isinstance(final, dict) and elapsed_budget_exhausted:
        action = "return_now"
    elif action == "return_now":
        pass
    elif failed_certifications and successful_terminal:
        action = "needs_fix"
    elif missing_certifications and successful_terminal and action == "complete":
        action = "awaiting_certification"

    acceptance_latency = (
        now_ms - started_at
        if isinstance(started_at, int)
        and now_ms >= started_at
        and action == "complete"
        and successful_terminal
        else None
    )
    metrics = {
        **base["metrics"],
        **command_metrics,
        "scope_violations": scope_violations,
        "review_findings_p0": finding_counts["p0"],
        "review_findings_p1": finding_counts["p1"],
        "review_findings_p2": finding_counts["p2"],
        "acceptance_latency_ms": acceptance_latency,
        "elapsed_budget_exhausted": elapsed_budget_exhausted,
    }
    return {
        "action": action,
        "contract_hash": contract["contract_hash"],
        "evidence_trust": command_metrics["evidence_trust"],
        "metrics": metrics,
        "pending_certifications": missing_certifications if successful_terminal else [],
        "reasons": reasons,
        "terminal_status": base["terminal_status"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--now-ms", type=int)
    args = parser.parse_args()
    try:
        result = evaluate_worker_run(
            _load_object(args.contract),
            _load_object(args.input),
            now_ms=args.now_ms if args.now_ms is not None else time.time_ns() // 1_000_000,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
