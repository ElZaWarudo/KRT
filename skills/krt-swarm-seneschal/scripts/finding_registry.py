#!/usr/bin/env python3
"""Maintain a root-owned, digest-guarded registry of canonical review findings."""

from __future__ import annotations

import argparse
from copy import deepcopy
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
from typing import Any

if os.name == "nt":
    import msvcrt
else:
    import fcntl

from deterministic_artifacts import canonical_sha256, write_atomic, write_exclusive_atomic
from deterministic_validation import exact_object, load_object, non_empty_string, string_list
from validate_review_terminal import SEVERITIES, validate_finding


REGISTRY_FIELDS = {
    "schema_version",
    "registry_id",
    "contract_hash",
    "diff_digest",
    "revision",
    "findings",
    "registry_digest",
}
VERDICTS = {"confirmed", "revised", "rejected"}


@contextmanager
def _registry_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(f".{path.name}.lock")
    with lock_path.open("a+b") as stream:
        if os.name == "nt":
            stream.seek(0, os.SEEK_END)
            if stream.tell() == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == "nt":
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _registry_payload(registry: dict[str, Any]) -> dict[str, Any]:
    return {key: registry[key] for key in REGISTRY_FIELDS - {"registry_digest"}}


def _with_digest(registry: dict[str, Any]) -> dict[str, Any]:
    result = dict(registry)
    result["registry_digest"] = canonical_sha256(_registry_payload(result))
    return result


def new_registry(*, registry_id: str, contract_hash: str, diff_digest: str) -> dict[str, Any]:
    for value, field in (
        (registry_id, "registry_id"),
        (contract_hash, "contract_hash"),
        (diff_digest, "diff_digest"),
    ):
        non_empty_string(value, field)
    if not contract_hash.startswith("sha256:") or not diff_digest.startswith("sha256:"):
        raise ValueError("contract_hash and diff_digest must use sha256")
    return _with_digest(
        {
            "schema_version": 1,
            "registry_id": registry_id,
            "contract_hash": contract_hash,
            "diff_digest": diff_digest,
            "revision": 0,
            "findings": [],
        }
    )


def validate_registry(registry: dict[str, Any]) -> dict[str, Any]:
    exact_object(registry, REGISTRY_FIELDS, "registry")
    if registry["schema_version"] != 1:
        raise ValueError("registry schema_version must be 1")
    non_empty_string(registry["registry_id"], "registry_id")
    if not isinstance(registry["revision"], int) or registry["revision"] < 0:
        raise ValueError("registry revision must be a non-negative integer")
    if not isinstance(registry["findings"], list):
        raise ValueError("registry findings must be a list")
    identifiers = [finding.get("id") for finding in registry["findings"] if isinstance(finding, dict)]
    if len(identifiers) != len(registry["findings"]) or len(identifiers) != len(set(identifiers)):
        raise ValueError("registry finding ids must be present and unique")
    entry_fields = {
        "id", "fingerprint", "contract_hash", "diff_digest", "review_plan_hashes",
        "surface_ids", "severity", "principle", "rule_id", "observation", "impact",
        "recommendation", "evidence", "status", "reporters", "feedback",
        "validation", "resolution",
    }
    for index, finding in enumerate(registry["findings"]):
        exact_object(finding, entry_fields, f"registry finding {index}")
        non_empty_string(finding["id"], f"registry finding {index}.id")
        non_empty_string(finding["fingerprint"], f"registry finding {index}.fingerprint")
        if finding["contract_hash"] != registry["contract_hash"] or finding["diff_digest"] != registry["diff_digest"]:
            raise ValueError("registry finding hash binding is invalid")
        validate_finding(
            {key: finding[key] for key in (
                "severity", "principle", "rule_id", "observation", "impact",
                "recommendation", "evidence",
            )},
            index=index,
        )
        string_list(
            finding["review_plan_hashes"],
            f"registry finding {index}.review_plan_hashes",
            allow_empty=False,
            unique=True,
        )
        string_list(
            finding["surface_ids"],
            f"registry finding {index}.surface_ids",
            allow_empty=False,
            unique=True,
        )
        reporters = string_list(finding["reporters"], f"registry finding {index}.reporters", allow_empty=False)
        if len(reporters) != len(set(reporters)):
            raise ValueError("registry finding reporters must be unique")
        if not isinstance(finding["feedback"], list):
            raise ValueError("registry finding feedback must be a list")
        for feedback in finding["feedback"]:
            exact_object(
                feedback,
                {"actor_id", "action", "rationale", "evidence"},
                "registry feedback",
            )
            non_empty_string(feedback["actor_id"], "feedback.actor_id")
            if feedback["action"] not in {"corroborate", "challenge"}:
                raise ValueError("registry feedback action is invalid")
            non_empty_string(feedback["rationale"], "feedback.rationale")
            string_list(feedback["evidence"], "feedback.evidence", allow_empty=False)
        status = finding["status"]
        if status not in {"proposed", "confirmed", "revised", "rejected", "fixed", "deferred"}:
            raise ValueError("registry finding status is invalid")
        validation = finding["validation"]
        if validation is not None:
            exact_object(
                validation,
                {"validator_id", "verdict", "evidence", "revised_finding"},
                "registry validation",
            )
            validator_id = non_empty_string(validation["validator_id"], "validation.validator_id")
            if validator_id in reporters or validation["verdict"] not in VERDICTS:
                raise ValueError("registry validation identity or verdict is invalid")
            string_list(validation["evidence"], "validation.evidence", allow_empty=False)
            revised_finding = validation["revised_finding"]
            if validation["verdict"] == "revised":
                exact_object(
                    revised_finding,
                    {"severity", "observation", "impact", "recommendation"},
                    "validation.revised_finding",
                )
                if revised_finding["severity"] not in SEVERITIES:
                    raise ValueError("validation revised severity is invalid")
                for field in ("observation", "impact", "recommendation"):
                    non_empty_string(
                        revised_finding[field], f"validation.revised_finding.{field}"
                    )
            elif revised_finding is not None:
                raise ValueError("only revised validation may contain revised_finding")
        resolution = finding["resolution"]
        if resolution is not None:
            exact_object(
                resolution,
                {"resolver_id", "resolution", "evidence", "resolved_diff_digest"},
                "registry resolution",
            )
            non_empty_string(resolution["resolver_id"], "resolution.resolver_id")
            if resolution["resolution"] not in {"fixed", "deferred"}:
                raise ValueError("registry resolution is invalid")
            string_list(resolution["evidence"], "resolution.evidence", allow_empty=False)
            digest = non_empty_string(resolution["resolved_diff_digest"], "resolved_diff_digest")
            if not digest.startswith("sha256:"):
                raise ValueError("resolved_diff_digest must use sha256")
        if status == "proposed" and (validation is not None or resolution is not None):
            raise ValueError("proposed finding cannot have validation or resolution")
        if status in {"confirmed", "revised", "rejected"} and (
            validation is None or validation["verdict"] != status or resolution is not None
        ):
            raise ValueError("validated finding lifecycle is inconsistent")
        if status in {"fixed", "deferred"} and (
            validation is None
            or validation["verdict"] not in {"confirmed", "revised"}
            or resolution is None
            or resolution["resolution"] != status
        ):
            raise ValueError("resolved finding lifecycle is inconsistent")
    if registry["registry_digest"] != canonical_sha256(_registry_payload(registry)):
        raise ValueError("registry digest is invalid")
    return registry


def _mutating_copy(registry: dict[str, Any], expected_digest: str) -> dict[str, Any]:
    validate_registry(registry)
    if registry["registry_digest"] != expected_digest:
        raise ValueError("registry does not match expected digest")
    result = deepcopy(registry)
    result.pop("registry_digest")
    return result


def _finish_mutation(
    original: dict[str, Any], result: dict[str, Any], *, changed: bool = True
) -> dict[str, Any]:
    if not changed:
        return original
    result["revision"] += 1
    return _with_digest(result)


def _finding_birth(registry: dict[str, Any], finding: dict[str, Any]) -> tuple[str, str]:
    birth = {
        "contract_hash": registry["contract_hash"],
        "diff_digest": registry["diff_digest"],
        "finding": finding,
    }
    fingerprint = canonical_sha256(birth)
    return f"F-{fingerprint.removeprefix('sha256:')[:8].upper()}", fingerprint


def ingest_findings(
    registry: dict[str, Any], submission: dict[str, Any], *, expected_digest: str
) -> dict[str, Any]:
    exact_object(
        submission,
        {
            "contract_hash",
            "diff_digest",
            "review_plan_hash",
            "surface_id",
            "reporter_id",
            "findings",
        },
        "finding submission",
    )
    result = _mutating_copy(registry, expected_digest)
    for field in ("contract_hash", "diff_digest"):
        if submission[field] != result[field]:
            raise ValueError(f"finding submission {field} does not match registry")
    review_plan_hash = non_empty_string(submission["review_plan_hash"], "review_plan_hash")
    surface_id = non_empty_string(submission["surface_id"], "surface_id")
    reporter_id = non_empty_string(submission["reporter_id"], "reporter_id")
    if not isinstance(submission["findings"], list):
        raise ValueError("finding submission findings must be a list")
    by_fingerprint = {finding["fingerprint"]: finding for finding in result["findings"]}
    by_id = {finding["id"]: finding for finding in result["findings"]}
    changed = False
    for index, raw_finding in enumerate(submission["findings"]):
        finding = validate_finding(raw_finding, index=index)
        identifier, fingerprint = _finding_birth(result, finding)
        existing = by_fingerprint.get(fingerprint)
        if existing is not None:
            reporters = sorted(set(existing["reporters"] + [reporter_id]))
            surface_ids = sorted(set(existing["surface_ids"] + [surface_id]))
            plan_hashes = sorted(
                set(existing["review_plan_hashes"] + [review_plan_hash])
            )
            if reporters != existing["reporters"]:
                existing["reporters"] = reporters
                changed = True
            if surface_ids != existing["surface_ids"]:
                existing["surface_ids"] = surface_ids
                changed = True
            if plan_hashes != existing["review_plan_hashes"]:
                existing["review_plan_hashes"] = plan_hashes
                changed = True
            continue
        entry = {
            "id": identifier,
            "fingerprint": fingerprint,
            "contract_hash": result["contract_hash"],
            "diff_digest": result["diff_digest"],
            "review_plan_hashes": [review_plan_hash],
            "surface_ids": [surface_id],
            **deepcopy(finding),
            "status": "proposed",
            "reporters": [reporter_id],
            "feedback": [],
            "validation": None,
            "resolution": None,
        }
        if identifier in by_id and by_id[identifier]["fingerprint"] != fingerprint:
            raise ValueError(f"canonical finding id collision: {identifier}")
        result["findings"].append(entry)
        by_fingerprint[fingerprint] = entry
        by_id[identifier] = entry
        changed = True
    result["findings"] = sorted(result["findings"], key=lambda item: item["id"])
    return _finish_mutation(registry, result, changed=changed)


def record_finding_feedback(
    registry: dict[str, Any], feedback: dict[str, Any], *, expected_digest: str
) -> dict[str, Any]:
    exact_object(
        feedback,
        {"finding_id", "actor_id", "action", "rationale", "evidence"},
        "finding feedback",
    )
    result = _mutating_copy(registry, expected_digest)
    finding = _find(result, non_empty_string(feedback["finding_id"], "finding_id"))
    actor = non_empty_string(feedback["actor_id"], "actor_id")
    action = feedback["action"]
    if action not in {"corroborate", "challenge"}:
        raise ValueError("finding feedback action is invalid")
    rationale = non_empty_string(feedback["rationale"], "rationale")
    evidence = string_list(feedback["evidence"], "feedback.evidence", allow_empty=False)
    finding["feedback"].append(
        {
            "actor_id": actor,
            "action": action,
            "rationale": rationale,
            "evidence": deepcopy(evidence),
        }
    )
    return _finish_mutation(registry, result)


def validate_finding_verdict(
    registry: dict[str, Any], verdict: dict[str, Any], *, expected_digest: str
) -> dict[str, Any]:
    fields = {
        "finding_id",
        "validator_id",
        "verdict",
        "evidence",
        "revised_severity",
        "revised_observation",
        "revised_impact",
        "revised_recommendation",
    }
    exact_object(verdict, fields, "validation verdict")
    result = _mutating_copy(registry, expected_digest)
    finding = _find(result, non_empty_string(verdict["finding_id"], "finding_id"))
    validator_id = non_empty_string(verdict["validator_id"], "validator_id")
    if validator_id in finding["reporters"]:
        raise ValueError("a finding reporter cannot validate the same finding")
    if finding["validation"] is not None:
        raise ValueError("finding already has a validation verdict")
    decision = verdict["verdict"]
    if decision not in VERDICTS:
        raise ValueError("validation verdict is invalid")
    evidence = string_list(verdict["evidence"], "validation.evidence", allow_empty=False)
    revised_fields = (
        "revised_severity",
        "revised_observation",
        "revised_impact",
        "revised_recommendation",
    )
    if decision == "revised":
        if verdict["revised_severity"] not in SEVERITIES:
            raise ValueError("revised verdict requires a valid revised_severity")
        for field in revised_fields[1:]:
            non_empty_string(verdict[field], field)
        revised_finding = {
            "severity": verdict["revised_severity"],
            "observation": verdict["revised_observation"],
            "impact": verdict["revised_impact"],
            "recommendation": verdict["revised_recommendation"],
        }
    elif any(verdict[field] is not None for field in revised_fields):
        raise ValueError("only a revised verdict may carry revised fields")
    else:
        revised_finding = None
    finding["validation"] = {
        "validator_id": validator_id,
        "verdict": decision,
        "evidence": evidence,
        "revised_finding": revised_finding,
    }
    finding["status"] = decision
    return _finish_mutation(registry, result)


def resolve_finding(
    registry: dict[str, Any], resolution: dict[str, Any], *, expected_digest: str
) -> dict[str, Any]:
    exact_object(
        resolution,
        {
            "finding_id",
            "resolver_id",
            "resolution",
            "evidence",
            "resolved_diff_digest",
        },
        "resolution",
    )
    result = _mutating_copy(registry, expected_digest)
    finding = _find(result, non_empty_string(resolution["finding_id"], "finding_id"))
    if finding["status"] not in {"confirmed", "revised"}:
        raise ValueError("only confirmed or revised findings can be resolved")
    decision = resolution["resolution"]
    if decision not in {"fixed", "deferred"}:
        raise ValueError("resolution must be fixed or deferred")
    resolved_diff_digest = non_empty_string(
        resolution["resolved_diff_digest"], "resolved_diff_digest"
    )
    if not resolved_diff_digest.startswith("sha256:"):
        raise ValueError("resolved_diff_digest must use sha256")
    finding["resolution"] = {
        "resolver_id": non_empty_string(resolution["resolver_id"], "resolver_id"),
        "resolution": decision,
        "evidence": string_list(resolution["evidence"], "resolution.evidence", allow_empty=False),
        "resolved_diff_digest": resolved_diff_digest,
    }
    finding["status"] = decision
    return _finish_mutation(registry, result)


def _find(registry: dict[str, Any], finding_id: str) -> dict[str, Any]:
    for finding in registry["findings"]:
        if finding["id"] == finding_id:
            return finding
    raise ValueError(f"unknown finding id: {finding_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    initialize = subparsers.add_parser("init")
    initialize.add_argument("--registry", type=Path, required=True)
    initialize.add_argument("--registry-id", required=True)
    initialize.add_argument("--contract-hash", required=True)
    initialize.add_argument("--diff-digest", required=True)
    for name in ("ingest", "feedback", "validate", "resolve"):
        command = subparsers.add_parser(name)
        command.add_argument("--registry", type=Path, required=True)
        command.add_argument("--input", type=Path, required=True)
        command.add_argument("--expected-registry-digest", required=True)
    status = subparsers.add_parser("status")
    status.add_argument("--registry", type=Path, required=True)
    args = parser.parse_args()
    try:
        with _registry_lock(args.registry):
            if args.command == "init":
                result = new_registry(
                    registry_id=args.registry_id,
                    contract_hash=args.contract_hash,
                    diff_digest=args.diff_digest,
                )
                write_exclusive_atomic(args.registry, result)
            else:
                registry = load_object(args.registry)
                if args.command == "status":
                    result = validate_registry(registry)
                else:
                    event = load_object(args.input)
                    operation = {
                        "ingest": ingest_findings,
                        "feedback": record_finding_feedback,
                        "validate": validate_finding_verdict,
                        "resolve": resolve_finding,
                    }[args.command]
                    result = operation(
                        registry, event, expected_digest=args.expected_registry_digest
                    )
                    if result["registry_digest"] != registry["registry_digest"]:
                        write_atomic(args.registry, result)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
