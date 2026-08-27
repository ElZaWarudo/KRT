#!/usr/bin/env python3
"""Evaluate one lightweight Luna observation and emit the root action."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import sys
import time
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
PROFILES = {"luna", "luna_xhigh"}
TERMINAL_STATUSES = {
    "done",
    "done_with_baseline_gaps",
    "needs_review",
    "blocked",
}
INTERVENTION_ACTIONS = {
    "dispatch_implementation",
    "return_now",
}
ATTEMPT_OUTCOMES = {"passed", "failed", "baseline_failure", "unowned_failure"}
CHECKPOINT_FIELDS = {
    "discovery_complete_at_ms",
    "edit_path_found",
    "event",
    "evidence_digest",
    "planned_files",
}


def require_non_negative_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def optional_timestamp(observation: dict[str, Any], field: str) -> int | None:
    value = observation.get(field)
    if value is None:
        return None
    return require_non_negative_int(value, field)


def string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a list of strings")
    return value


def calculate_metrics(
    observation: dict[str, Any],
    *,
    final: dict[str, Any] | None,
    returned_at: int | None,
) -> dict[str, Any]:
    started_at = require_non_negative_int(
        observation.get("started_at_ms"), "started_at_ms"
    )
    first_change = optional_timestamp(observation, "first_change_at_ms")
    command_finished = optional_timestamp(
        observation, "last_required_command_finished_at_ms"
    )
    phase_duration = observation.get("phase_duration_ms", {})
    if not isinstance(phase_duration, dict):
        raise ValueError("phase_duration_ms must be an object")
    discovery_ms = require_non_negative_int(
        phase_duration.get("discovery", 0), "phase_duration_ms.discovery"
    )
    implementation_ms = require_non_negative_int(
        phase_duration.get("implementation", 0),
        "phase_duration_ms.implementation",
    )

    manifest = observation.get("verification_manifest", {})
    if not isinstance(manifest, dict):
        raise ValueError("verification_manifest must be an object")
    focused = string_list(manifest.get("focused", []), "focused")
    natural = string_list(manifest.get("natural", []), "natural")
    outside_manifest_count = 0
    if final is not None:
        commands_run = string_list(
            final.get("verification_commands_run", []),
            "verification_commands_run",
        )
        allowed_commands = set(focused)
        allowed_commands.update(natural)
        outside_manifest_count = sum(
            command not in allowed_commands for command in commands_run
        )

    return {
        "discovery_implementation_ratio": (
            round(discovery_ms / implementation_ms, 3)
            if implementation_ms
            else None
        ),
        "last_required_command_to_return_ms": (
            returned_at - command_finished
            if returned_at is not None
            and command_finished is not None
            and returned_at >= command_finished
            else None
        ),
        "out_of_manifest_commands": outside_manifest_count,
        "root_interventions": len(
            string_list(observation.get("interventions_sent", []), "interventions_sent")
        ),
        "time_to_first_change_ms": (
            first_change - started_at
            if first_change is not None and first_change >= started_at
            else None
        ),
    }


def timeline_reasons(
    observation: dict[str, Any], *, now_ms: int, returned_at: int | None
) -> list[str]:
    started_at = require_non_negative_int(
        observation.get("started_at_ms"), "started_at_ms"
    )
    first_change = optional_timestamp(observation, "first_change_at_ms")
    discovery_returned = optional_timestamp(observation, "discovery_returned_at_ms")
    implementation_started = optional_timestamp(
        observation, "implementation_started_at_ms"
    )
    changed_files = string_list(observation.get("changed_files", []), "changed_files")
    command_finished = optional_timestamp(
        observation, "last_required_command_finished_at_ms"
    )
    timestamps = [
        first_change,
        discovery_returned,
        implementation_started,
        command_finished,
        returned_at,
    ]
    checkpoint = observation.get("checkpoint")
    checkpoint_at: int | None = None
    if isinstance(checkpoint, dict):
        checkpoint_at = optional_timestamp(checkpoint, "discovery_complete_at_ms")
        timestamps.append(checkpoint_at)
    if started_at > now_ms or any(
        value is not None and (value < started_at or value > now_ms)
        for value in timestamps
    ):
        return ["invalid-timestamp-order"]

    if returned_at is not None and (
        (first_change is not None and returned_at < first_change)
        or (command_finished is not None and returned_at < command_finished)
        or (checkpoint_at is not None and returned_at < checkpoint_at)
    ):
        return ["invalid-timestamp-order"]
    if (
        first_change is not None
        and command_finished is not None
        and command_finished < first_change
    ):
        return ["invalid-timestamp-order"]
    if (
        observation.get("profile") == "luna_xhigh"
        and checkpoint_at is not None
        and discovery_returned is not None
        and discovery_returned < checkpoint_at
    ):
        return ["invalid-timestamp-order"]
    if observation.get("profile") == "luna_xhigh" and implementation_started is not None:
        if checkpoint_at is None or implementation_started < checkpoint_at:
            return ["invalid-timestamp-order"]
        if discovery_returned is not None and implementation_started < discovery_returned:
            return ["invalid-timestamp-order"]
    if first_change is not None and (
        implementation_started is None or first_change < implementation_started
    ) and observation.get("profile") == "luna_xhigh":
        return ["write-before-implementation-dispatch"]
    if (
        observation.get("profile") == "luna_xhigh"
        and changed_files
        and implementation_started is None
    ):
        return ["write-before-implementation-dispatch"]
    return []


def checkpoint_reasons(
    observation: dict[str, Any], *, require_checkpoint: bool
) -> list[str]:
    profile = observation.get("profile")
    checkpoint_count = require_non_negative_int(
        observation.get("checkpoint_count", 0), "checkpoint_count"
    )
    checkpoint = observation.get("checkpoint")
    if profile == "luna":
        return (
            ["unexpected-checkpoint"]
            if checkpoint_count != 0 or checkpoint is not None
            else []
        )
    if checkpoint is None:
        return ["invalid-checkpoint-count"] if require_checkpoint or checkpoint_count else []

    reasons: list[str] = []
    if checkpoint_count != 1:
        reasons.append("invalid-checkpoint-count")
    if not isinstance(checkpoint, dict):
        reasons.append("invalid-checkpoint-shape")
        return reasons
    if set(checkpoint) != CHECKPOINT_FIELDS:
        reasons.append("invalid-checkpoint-fields")
    try:
        require_non_negative_int(
            checkpoint.get("discovery_complete_at_ms"),
            "discovery_complete_at_ms",
        )
        require_non_negative_int(
            observation.get("discovery_returned_at_ms"),
            "discovery_returned_at_ms",
        )
    except ValueError:
        reasons.append("invalid-checkpoint-shape")
        return reasons
    if not isinstance(checkpoint.get("edit_path_found"), bool):
        reasons.append("invalid-checkpoint-shape")
        return reasons
    if checkpoint.get("event") != "discovery_complete":
        reasons.append("invalid-checkpoint-event")
    try:
        planned_files = string_list(checkpoint.get("planned_files"), "planned_files")
        owned_files = set(string_list(observation.get("owned_files"), "owned_files"))
    except ValueError:
        reasons.append("invalid-checkpoint-shape")
        return reasons
    evidence_digest = checkpoint.get("evidence_digest")
    if not isinstance(evidence_digest, str) or not evidence_digest.strip():
        reasons.append("checkpoint-missing-evidence-digest")
    if checkpoint["edit_path_found"]:
        if not planned_files:
            reasons.append("checkpoint-missing-planned-files")
        if len(planned_files) != len(set(planned_files)):
            reasons.append("checkpoint-duplicate-planned-files")
        if any(path not in owned_files for path in planned_files):
            reasons.append("checkpoint-plans-unowned-file")
        if len(owned_files) > 1 and set(planned_files) == owned_files:
            reasons.append("checkpoint-did-not-narrow-ownership")
        if isinstance(evidence_digest, str) and evidence_digest.strip():
            evidence_lines = evidence_digest.splitlines()
            edit_evidence = {
                path: next(
                    (
                        line.split("|", 1)[1].strip()
                        for line in evidence_lines
                        if line.startswith(f"edit {path} |")
                    ),
                    None,
                )
                for path in planned_files
            }
            unjustified = [path for path, detail in edit_evidence.items() if detail is None]
            if unjustified:
                reasons.append("checkpoint-missing-file-justification")
            vague = [
                path
                for path, detail in edit_evidence.items()
                if detail is not None
                and (
                    not any(
                        marker in detail
                        for marker in ("symbol=", "pattern=", "callers=")
                    )
                    or "why=" not in detail
                )
            ]
            if vague:
                reasons.append("checkpoint-vague-file-justification")
    elif planned_files:
        reasons.append("checkpoint-has-unexpected-planned-files")
    return reasons


def edit_scope_reasons(observation: dict[str, Any]) -> list[str]:
    if observation.get("profile") != "luna_xhigh":
        return []
    checkpoint = observation.get("checkpoint")
    if not isinstance(checkpoint, dict):
        return []
    try:
        planned_files = set(string_list(checkpoint.get("planned_files"), "planned_files"))
        changed_files = string_list(observation.get("changed_files"), "changed_files")
    except ValueError:
        return ["invalid-changed-files"]
    return (
        ["changed-file-outside-checkpoint"]
        if any(path not in planned_files for path in changed_files)
        else []
    )


def scope_extension_reasons(final: dict[str, Any]) -> list[str]:
    extension = final.get("scope_extension")
    if extension is None:
        return []
    if final.get("status") != "needs_review" or not isinstance(extension, dict):
        return ["invalid-scope-extension"]
    try:
        additional_files = string_list(
            extension.get("additional_files"), "additional_files"
        )
    except ValueError:
        return ["invalid-scope-extension"]
    reason = extension.get("reason")
    if not additional_files or not isinstance(reason, str) or not reason.strip():
        return ["invalid-scope-extension"]
    return []


def verification_reasons(
    observation: dict[str, Any], final: dict[str, Any]
) -> list[str]:
    reasons: list[str] = []
    manifest = observation.get("verification_manifest")
    if not isinstance(manifest, dict):
        return ["invalid-verification-manifest"]
    try:
        required = string_list(manifest.get("focused", []), "focused") + string_list(
            manifest.get("natural", []), "natural"
        )
        max_retries = require_non_negative_int(
            manifest.get("max_retries_per_command", 0),
            "max_retries_per_command",
        )
        commands_run = string_list(
            final.get("verification_commands_run"), "verification_commands_run"
        )
    except ValueError:
        return ["invalid-verification-result"]
    if len(required) != len(set(required)):
        reasons.append("verification-manifest-duplicates")

    verification = final.get("verification")
    if not isinstance(verification, dict):
        return [*reasons, "invalid-verification-result"]
    attempted = verification.get("attempted")
    skipped = verification.get("skipped")
    if not isinstance(attempted, list) or not isinstance(skipped, list):
        return [*reasons, "invalid-verification-result"]

    accounted: list[str] = []
    expected_attempts: Counter[str] = Counter()
    for entry in attempted:
        if not isinstance(entry, dict):
            reasons.append("invalid-verification-result")
            continue
        command = entry.get("command")
        attempts = entry.get("attempts")
        outcome = entry.get("outcome")
        if (
            not isinstance(command, str)
            or not command
            or not isinstance(attempts, int)
            or isinstance(attempts, bool)
            or attempts < 1
            or outcome not in ATTEMPT_OUTCOMES
        ):
            reasons.append("invalid-verification-result")
            continue
        accounted.append(command)
        expected_attempts[command] = attempts
        if attempts > max_retries + 1:
            reasons.append("verification-retry-limit-exceeded")
    for entry in skipped:
        if not isinstance(entry, dict):
            reasons.append("invalid-verification-result")
            continue
        command = entry.get("command")
        reason = entry.get("reason")
        if (
            not isinstance(command, str)
            or not command
            or not isinstance(reason, str)
            or not reason.strip()
        ):
            reasons.append("invalid-verification-result")
            continue
        accounted.append(command)

    if len(accounted) != len(set(accounted)):
        reasons.append("verification-command-duplicated")
    if set(accounted) != set(required):
        reasons.append("verification-manifest-incomplete")
    if any(command not in set(required) for command in accounted):
        reasons.append("verification-command-outside-manifest")
    if Counter(commands_run) != expected_attempts:
        reasons.append("verification-attempt-count-mismatch")
    expected_sequence = [
        command
        for command in required
        for _ in range(expected_attempts.get(command, 0))
    ]
    if commands_run != expected_sequence:
        reasons.append("verification-command-order-invalid")
    expected_last = commands_run[-1] if commands_run else None
    if final.get("last_required_command") != expected_last:
        reasons.append("invalid-last-required-command")
    return list(dict.fromkeys(reasons))


def terminal_reasons(
    observation: dict[str, Any], final: dict[str, Any]
) -> list[str]:
    reasons: list[str] = []
    status = final.get("status")
    if status not in TERMINAL_STATUSES:
        reasons.append("invalid-terminal-status")
    if (
        final.get("phase") != "closeout"
        or final.get("remaining_actions") != []
        or final.get("terminal_ready") is not True
    ):
        reasons.append("invalid-terminal-shape")
    unowned_failures = final.get("unowned_failures")
    if not isinstance(unowned_failures, list) or not all(
        isinstance(failure, str) for failure in unowned_failures
    ):
        reasons.append("invalid-unowned-failures")
    acceptance_resolved = final.get("acceptance_criteria_resolved")
    if not isinstance(acceptance_resolved, bool):
        reasons.append("invalid-acceptance-criteria-state")
    elif status in {"done", "done_with_baseline_gaps"} and not acceptance_resolved:
        reasons.append("acceptance-criteria-unresolved")
    if status == "done" and final.get("unowned_failures"):
        reasons.append("done-with-unowned-failures")
    verification = final.get("verification")
    if status == "done" and isinstance(verification, dict):
        attempted = verification.get("attempted")
        skipped = verification.get("skipped")
        if isinstance(attempted, list) and any(
            isinstance(entry, dict) and entry.get("outcome") != "passed"
            for entry in attempted
        ):
            reasons.append("done-with-verification-gaps")
        if skipped:
            reasons.append("done-with-skipped-verification")
    if status == "done_with_baseline_gaps" and isinstance(verification, dict):
        attempted = verification.get("attempted")
        has_reported_gap = bool(unowned_failures) or (
            isinstance(attempted, list)
            and any(
                isinstance(entry, dict)
                and entry.get("outcome") in {"baseline_failure", "unowned_failure"}
                for entry in attempted
            )
        )
        if not has_reported_gap:
            reasons.append("baseline-gap-status-without-gap")
    if observation.get("profile") == "luna_xhigh" and status in {
        "done",
        "done_with_baseline_gaps",
    }:
        try:
            changed_files = string_list(
                observation.get("changed_files", []), "changed_files"
            )
        except ValueError:
            changed_files = []
        if not changed_files:
            reasons.append("successful-terminal-without-changes")
        elif observation.get("first_change_at_ms") is None:
            reasons.append("successful-terminal-missing-first-change")
    reasons.extend(verification_reasons(observation, final))
    reasons.extend(scope_extension_reasons(final))
    return reasons


def evaluate_run(
    observation: dict[str, Any],
    *,
    now_ms: int,
) -> dict[str, Any]:
    if observation.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    profile = observation.get("profile")
    if profile not in PROFILES:
        raise ValueError(f"profile must be one of {', '.join(sorted(PROFILES))}")
    now_ms = require_non_negative_int(now_ms, "now_ms")
    final = observation.get("final")
    if final is not None and not isinstance(final, dict):
        raise ValueError("final must be an object")
    returned_at = optional_timestamp(observation, "returned_at_ms")
    metrics = calculate_metrics(
        observation, final=final, returned_at=returned_at
    )
    reasons = timeline_reasons(observation, now_ms=now_ms, returned_at=returned_at)
    reasons.extend(edit_scope_reasons(observation))
    action = "continue"
    terminal_status: str | None = final.get("status") if final is not None else None

    if final is not None:
        reasons.extend(terminal_reasons(observation, final))
        reasons.extend(checkpoint_reasons(observation, require_checkpoint=True))
        checkpoint = observation.get("checkpoint")
        if (
            profile == "luna_xhigh"
            and isinstance(checkpoint, dict)
            and checkpoint.get("edit_path_found") is False
            and observation.get("implementation_started_at_ms") is not None
        ):
            reasons.append("implementation-dispatched-without-edit-path")
        if profile == "luna_xhigh" and observation.get("implementation_started_at_ms") is None:
            reasons.append("implementation-not-dispatched")
        if metrics["out_of_manifest_commands"]:
            reasons.append("verification-command-outside-manifest")
        if reasons:
            action = "contract_violation"
        elif returned_at is None:
            action = "return_now"
        else:
            action = "complete"
    elif returned_at is not None:
        action = "contract_violation"
        reasons.append("return-missing-terminal-result")
    elif profile == "luna":
        reasons.extend(checkpoint_reasons(observation, require_checkpoint=False))
        if reasons:
            action = "contract_violation"
    elif profile == "luna_xhigh":
        reasons.extend(checkpoint_reasons(observation, require_checkpoint=False))
        checkpoint = observation.get("checkpoint")
        if reasons:
            action = "contract_violation"
        elif isinstance(checkpoint, dict):
            if checkpoint["edit_path_found"] is False:
                if observation.get("implementation_started_at_ms") is not None:
                    action = "contract_violation"
                    reasons.append("implementation-dispatched-without-edit-path")
                else:
                    action = "complete"
                    terminal_status = "needs_review"
            elif observation.get("implementation_started_at_ms") is None:
                action = "dispatch_implementation"

    interventions_sent = string_list(
        observation.get("interventions_sent", []), "interventions_sent"
    )
    if len(interventions_sent) != len(set(interventions_sent)) or any(
        intervention not in INTERVENTION_ACTIONS
        for intervention in interventions_sent
    ):
        raise ValueError("interventions_sent contains invalid or duplicate actions")
    if (
        profile == "luna_xhigh"
        and observation.get("implementation_started_at_ms") is not None
        and "dispatch_implementation" not in interventions_sent
    ):
        reasons.append("implementation-dispatch-not-recorded")
        action = "contract_violation"
    if (
        profile == "luna_xhigh"
        and observation.get("implementation_started_at_ms") is None
        and "dispatch_implementation" in interventions_sent
    ):
        reasons.append("implementation-dispatch-start-not-recorded")
        action = "contract_violation"
    if action != "contract_violation" and action in interventions_sent:
        action = "continue"

    return {
        "action": action,
        "metrics": metrics,
        "reasons": list(dict.fromkeys(reasons)),
        "terminal_status": terminal_status,
    }


def load_observation(path: Path | None) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8") if path else sys.stdin.read()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("observation must be a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="JSON observation; stdin by default")
    parser.add_argument("--now-ms", type=int)
    args = parser.parse_args()
    try:
        result = evaluate_run(
            load_observation(args.input),
            now_ms=args.now_ms if args.now_ms is not None else time.time_ns() // 1_000_000,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
