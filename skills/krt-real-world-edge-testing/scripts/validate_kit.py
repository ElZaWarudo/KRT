#!/usr/bin/env python3
"""Validate a real-world edge-testing starter kit without external dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any


PRIORITIES = {"critical", "high", "medium", "low"}
EXECUTION_RISKS = {
    "read_only",
    "reversible_mutation",
    "isolated_destructive",
    "external_side_effect",
    "production_forbidden",
}
RESULTS = {"pass", "fail", "blocked", "not_run"}
RECOVERY_STATUSES = {
    "not_required",
    "pending",
    "recovered",
    "failed_recovery",
    "blocked",
}
EXPECTED_TREATMENTS = {"parse", "reject", "quarantine", "deduplicate", "preserve_bytes"}
PROVENANCE_KINDS = {"generated", "versioned_static"}
MAX_JSON_BYTES = 2 * 1024 * 1024
MAX_ARTIFACT_BYTES = 10 * 1024 * 1024
MAX_TOTAL_ARTIFACT_BYTES = 50 * 1024 * 1024
MAX_ARTIFACT_REFERENCES = 1000
MAX_FIXTURE_BYTES = 20 * 1024 * 1024
MAX_GENERATED_BYTES = 100 * 1024 * 1024
MAX_GENERATED_FILES = 1000
MAX_GENERATED_ENTRIES = 2000
MAX_CANARIES_PER_FIXTURE = 100
MAX_CANARY_CHARS = 1024
MAX_JSON_DEPTH = 50
MAX_JSON_NODES = 100_000
SENSITIVE_KEYS = {
    "apikey",
    "authorization",
    "awsaccesskeyid",
    "clientsecret",
    "cookie",
    "credential",
    "credentials",
    "githubtoken",
    "password",
    "passwd",
    "privatekey",
    "accesstoken",
    "refreshtoken",
    "secret",
    "sessionid",
    "setcookie",
    "token",
}
BEARER = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}", re.IGNORECASE)
PRIVATE_KEY = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
PROVIDER_TOKEN = re.compile(
    r"\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})\b"
)
JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")


def json_node_count(value: object, depth: int = 0) -> int:
    if depth > MAX_JSON_DEPTH:
        raise ValueError(f"JSON nesting exceeds {MAX_JSON_DEPTH}")
    if isinstance(value, dict):
        return 1 + sum(json_node_count(child, depth + 1) for child in value.values())
    if isinstance(value, list):
        return 1 + sum(json_node_count(child, depth + 1) for child in value)
    return 1


def reject_json_constant(value: str) -> None:
    raise ValueError(f"invalid JSON constant {value}")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = child
    return value


def load_object(path: Path, root: Path, errors: list[str]) -> dict[str, Any]:
    try:
        if path.is_symlink() or not path.is_file():
            raise ValueError("must be a regular non-symlink file")
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("must remain inside the kit root")
        if path.stat().st_size > MAX_JSON_BYTES:
            raise ValueError(f"exceeds {MAX_JSON_BYTES} bytes")
        value = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=reject_json_constant,
            object_pairs_hook=reject_duplicate_keys,
        )
        if json_node_count(value) > MAX_JSON_NODES:
            raise ValueError(f"JSON structure exceeds {MAX_JSON_NODES} nodes")
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        errors.append(f"{path}: {error}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path}: top level must be an object")
        return {}
    return value


def is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def require_string(value: object, label: str, errors: list[str]) -> bool:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")
        return False
    return True


def require_string_list(
    value: object, label: str, errors: list[str], *, nonempty: bool = False
) -> bool:
    if (
        not isinstance(value, list)
        or (nonempty and not value)
        or not all(
            isinstance(item, str) and item.strip() for item in value
        )
    ):
        qualifier = "a non-empty list" if nonempty else "a list"
        errors.append(f"{label} must be {qualifier} of non-empty strings")
        return False
    return True


def safe_relative(value: object, label: str, errors: list[str]) -> bool:
    if not require_string(value, label, errors):
        return False
    normalized = str(value).replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        str(value) != normalized
        or path.as_posix() != normalized
        or normalized in {".", ".."}
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        errors.append(f"{label} must be a normalized relative path")
        return False
    return True


def priority_for(score: int) -> str:
    if score >= 75:
        return "critical"
    if score >= 40:
        return "high"
    if score >= 15:
        return "medium"
    return "low"


def oracle_digest(oracle: dict[str, Any]) -> str:
    """Return the campaign contract's canonical SHA-256 oracle digest."""
    canonical = json.dumps(oracle, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def is_rfc3339(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def read_regular_file(path: Path, root: Path, max_bytes: int) -> bytes:
    """Read one bounded regular file without following a final-component symlink."""
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("must be a contained non-symlink file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError("must be a regular file")
        if metadata.st_size > max_bytes:
            raise ValueError(f"exceeds {max_bytes} bytes")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = -1
            data = stream.read(max_bytes + 1)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if len(data) > max_bytes:
        raise ValueError(f"exceeds {max_bytes} bytes")
    return data


def validate_risk(
    risk: object, priority: object, label: str, errors: list[str]
) -> None:
    if not isinstance(priority, str) or priority not in PRIORITIES:
        errors.append(f"{label}.priority must be one of {sorted(PRIORITIES)}")
    if risk is None:
        return
    if not isinstance(risk, dict):
        errors.append(f"{label}.risk must be an object when supplied")
        return
    dimensions: list[int] = []
    for field in ("impact", "likelihood", "detectability"):
        value = risk.get(field)
        if not is_integer(value) or not 1 <= value <= 5:
            errors.append(f"{label}.risk.{field} must be an integer from 1 to 5")
        else:
            dimensions.append(value)
    score = risk.get("score")
    if not is_integer(score):
        errors.append(f"{label}.risk.score must be an integer")
    elif len(dimensions) == 3:
        expected = dimensions[0] * dimensions[1] * dimensions[2]
        if score != expected:
            errors.append(f"{label}.risk.score must equal {expected}")
        derived = priority_for(expected)
        if isinstance(priority, str) and priority in PRIORITIES and priority != derived:
            errors.append(
                f"{label}.priority must be {derived!r} for numeric score {expected}"
            )
    require_string(risk.get("rationale"), f"{label}.risk.rationale", errors)


def validate_campaign(
    value: dict[str, Any], errors: list[str]
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    if value.get("schemaVersion") != 1:
        errors.append("campaign.schemaVersion must be integer 1")
    require_string(value.get("campaignId"), "campaign.campaignId", errors)
    cases = value.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("campaign.cases must be a non-empty list")
        return {}, set()

    case_contracts: dict[str, dict[str, Any]] = {}
    fixture_refs: set[str] = set()
    for index, case in enumerate(cases):
        label = f"campaign.cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label} must be an object")
            continue
        case_id = case.get("id")
        if require_string(case_id, f"{label}.id", errors):
            if case_id in case_contracts:
                errors.append(f"campaign contains duplicate case id {case_id!r}")
        require_string(case.get("title"), f"{label}.title", errors)
        require_string(case.get("category"), f"{label}.category", errors)
        execution_risk = case.get("executionRisk")
        if not isinstance(execution_risk, str) or execution_risk not in EXECUTION_RISKS:
            errors.append(
                f"{label}.executionRisk must be one of {sorted(EXECUTION_RISKS)}"
            )
        validate_risk(case.get("risk"), case.get("priority"), label, errors)

        fixtures = case.get("fixtures")
        if require_string_list(fixtures, f"{label}.fixtures", errors):
            fixture_refs.update(fixtures)
        require_string_list(case.get("preconditions"), f"{label}.preconditions", errors)
        for field in ("action", "oracle"):
            content = case.get(field)
            if not isinstance(content, dict) or not content:
                errors.append(f"{label}.{field} must be a non-empty object")
        timeout = case.get("timeoutMs")
        if not is_integer(timeout) or timeout <= 0:
            errors.append(f"{label}.timeoutMs must be a positive integer")
        require_string_list(
            case.get("evidence"), f"{label}.evidence", errors, nonempty=True
        )

        recovery = case.get("recovery")
        if not isinstance(recovery, dict) or type(recovery.get("required")) is not bool:
            errors.append(f"{label}.recovery.required must be boolean")
        elif recovery["required"]:
            require_string(
                recovery.get("procedure"), f"{label}.recovery.procedure", errors
            )
            require_string(
                recovery.get("verification"),
                f"{label}.recovery.verification",
                errors,
            )
        elif isinstance(execution_risk, str) and execution_risk in {
            "reversible_mutation",
            "isolated_destructive",
            "external_side_effect",
        }:
            errors.append(f"{label}.recovery.required must be true for stateful cases")
        if isinstance(case_id, str) and case_id.strip():
            oracle = case.get("oracle")
            case_contracts[case_id] = {
                "executionRisk": execution_risk,
                "recoveryRequired": (
                    recovery.get("required") if isinstance(recovery, dict) else None
                ),
                "oracleDigest": (
                    oracle_digest(oracle)
                    if isinstance(oracle, dict) and oracle
                    else None
                ),
            }
    return case_contracts, fixture_refs


def validate_manifest(
    value: dict[str, Any], kit_root: Path, errors: list[str]
) -> set[str]:
    if value.get("schemaVersion") != 1:
        errors.append("fixtures-manifest.schemaVersion must be integer 1")
    generated_value = value.get("generatedDirectory")
    generated_ok = safe_relative(
        generated_value, "fixtures-manifest.generatedDirectory", errors
    )
    fixtures = value.get("fixtures")
    if not isinstance(fixtures, list):
        errors.append("fixtures-manifest.fixtures must be a list")
        fixtures = []

    ids: set[str] = set()
    filenames: set[str] = set()
    records: dict[str, dict[str, Any]] = {}
    for index, fixture in enumerate(fixtures):
        label = f"fixtures-manifest.fixtures[{index}]"
        if not isinstance(fixture, dict):
            errors.append(f"{label} must be an object")
            continue
        fixture_id = fixture.get("id")
        if require_string(fixture_id, f"{label}.id", errors):
            if fixture_id in ids:
                errors.append(f"fixtures-manifest contains duplicate id {fixture_id!r}")
            ids.add(fixture_id)
            records[fixture_id] = fixture
        filename = fixture.get("fileName")
        if safe_relative(filename, f"{label}.fileName", errors):
            if filename in filenames:
                errors.append(
                    f"fixtures-manifest contains duplicate fileName {filename!r}"
                )
            filenames.add(filename)
        require_string(fixture.get("kind"), f"{label}.kind", errors)
        expected_treatment = fixture.get("expectedTreatment")
        if (
            not isinstance(expected_treatment, str)
            or expected_treatment not in EXPECTED_TREATMENTS
        ):
            errors.append(
                f"{label}.expectedTreatment must be one of "
                f"{sorted(EXPECTED_TREATMENTS)}"
            )
        provenance = fixture.get("provenance")
        if not isinstance(provenance, dict):
            errors.append(f"{label}.provenance must be an object")
        else:
            if provenance.get("kind") not in PROVENANCE_KINDS:
                errors.append(
                    f"{label}.provenance.kind must be one of "
                    f"{sorted(PROVENANCE_KINDS)}"
                )
            safe_relative(
                provenance.get("source"), f"{label}.provenance.source", errors
            )
            require_string(
                provenance.get("reproduction"),
                f"{label}.provenance.reproduction",
                errors,
            )
        canaries = fixture.get("canaries")
        if require_string_list(
            canaries, f"{label}.canaries", errors, nonempty=True
        ) and isinstance(canaries, list):
            if len(canaries) > MAX_CANARIES_PER_FIXTURE:
                errors.append(
                    f"{label}.canaries exceeds {MAX_CANARIES_PER_FIXTURE} entries"
                )
            for canary_index, canary in enumerate(canaries):
                if len(canary) > MAX_CANARY_CHARS:
                    errors.append(
                        f"{label}.canaries[{canary_index}] exceeds "
                        f"{MAX_CANARY_CHARS} characters"
                    )
        if fixture.get("canaryEncoding") != "utf-8":
            errors.append(f"{label}.canaryEncoding must be 'utf-8'")
        if fixture.get("containsPrivateData") is not False:
            errors.append(f"{label}.containsPrivateData must be false")
        checksum = fixture.get("sha256")
        if (
            not isinstance(checksum, str)
            or re.fullmatch(r"[0-9a-f]{64}", checksum) is None
        ):
            errors.append(f"{label}.sha256 must be 64 lowercase hex characters")

    for fixture_id, fixture in records.items():
        duplicate = fixture.get("duplicateOf")
        if duplicate is not None and not isinstance(duplicate, str):
            errors.append(f"fixture {fixture_id!r} duplicateOf must be a string")
        elif duplicate is not None and duplicate not in records:
            errors.append(
                f"fixture {fixture_id!r} duplicateOf references unknown id {duplicate!r}"
            )
        elif duplicate == fixture_id:
            errors.append(f"fixture {fixture_id!r} cannot duplicate itself")

    if generated_ok:
        generated = kit_root / str(generated_value)
        if not generated.is_dir():
            errors.append(f"generated directory does not exist: {generated}")
        else:
            resolved_root = kit_root.resolve()
            resolved_generated = generated.resolve()
            if generated.is_symlink() or not resolved_generated.is_relative_to(
                resolved_root
            ):
                errors.append(
                    "generated directory must not be a symlink or escape the kit root"
                )
                return ids
            byte_cache: dict[str, bytes] = {}

            def fixture_bytes(filename: str) -> bytes:
                if filename not in byte_cache:
                    byte_cache[filename] = read_regular_file(
                        generated / filename,
                        resolved_generated,
                        MAX_FIXTURE_BYTES,
                    )
                return byte_cache[filename]

            entries: list[Path] = []
            traversal_truncated = False
            for path in generated.rglob("*"):
                if len(entries) >= MAX_GENERATED_ENTRIES:
                    errors.append(
                        f"generated directory exceeds {MAX_GENERATED_ENTRIES} entries"
                    )
                    traversal_truncated = True
                    break
                entries.append(path)
            file_entries = [path for path in entries if path.is_file()]
            if len(file_entries) > MAX_GENERATED_FILES:
                errors.append(
                    f"generated directory exceeds {MAX_GENERATED_FILES} files"
                )
            unsafe_entries: set[Path] = set()
            for path in entries:
                try:
                    if path.is_symlink() or not path.resolve().is_relative_to(
                        resolved_generated
                    ):
                        unsafe_entries.add(path)
                except OSError:
                    unsafe_entries.add(path)
            for path in unsafe_entries:
                errors.append(
                    "generated entry must not be a symlink or escape the generated "
                    f"root: {path.relative_to(generated).as_posix()}"
                )
            safe_files = [path for path in file_entries if path not in unsafe_entries]
            total_generated_bytes = sum(path.stat().st_size for path in safe_files)
            generated_within_limits = (
                not traversal_truncated
                and len(file_entries) <= MAX_GENERATED_FILES
                and total_generated_bytes <= MAX_GENERATED_BYTES
            )
            if total_generated_bytes > MAX_GENERATED_BYTES:
                errors.append(
                    f"generated directory exceeds {MAX_GENERATED_BYTES} total bytes"
                )
            oversized_files: set[Path] = set()
            for path in safe_files:
                if path.stat().st_size > MAX_FIXTURE_BYTES:
                    oversized_files.add(path)
                    errors.append(
                        "generated fixture exceeds size limit: "
                        f"{path.relative_to(generated).as_posix()}"
                    )
            actual = {
                path.relative_to(generated).as_posix()
                for path in entries
                if path.is_file() and path not in unsafe_entries
            }
            if actual != filenames:
                missing = sorted(filenames - actual)
                extra = sorted(actual - filenames)
                if missing:
                    errors.append(f"generated files missing from disk: {missing}")
                if extra:
                    errors.append(f"generated files absent from manifest: {extra}")
            for fixture_id, fixture in records.items():
                filename = fixture.get("fileName")
                if not isinstance(filename, str) or filename not in actual:
                    continue
                if not generated_within_limits or generated / filename in oversized_files:
                    continue
                try:
                    data = fixture_bytes(filename)
                except (OSError, ValueError) as error:
                    errors.append(
                        f"fixture {fixture_id!r} could not be read safely: {error}"
                    )
                    continue
                checksum = fixture.get("sha256")
                if checksum and hashlib.sha256(data).hexdigest() != checksum:
                    errors.append(f"fixture {fixture_id!r} sha256 does not match")
                if fixture.get("canaryEncoding") == "utf-8":
                    text = data.decode("utf-8", errors="replace")
                    find_sensitive_content(
                        text,
                        f"fixture {fixture_id!r}",
                        errors,
                        subject="fixture",
                    )
                    canaries = fixture.get("canaries")
                    for canary in list(
                        item
                        for item in (canaries if isinstance(canaries, list) else [])
                        if isinstance(item, str) and len(item) <= MAX_CANARY_CHARS
                    )[:MAX_CANARIES_PER_FIXTURE]:
                        if canary not in text:
                            errors.append(
                                f"fixture {fixture_id!r} is missing canary {canary!r}"
                            )
                duplicate = fixture.get("duplicateOf")
                if isinstance(duplicate, str) and duplicate in records:
                    original_name = records[duplicate].get("fileName")
                    if isinstance(original_name, str) and original_name in actual:
                        try:
                            original_data = fixture_bytes(original_name)
                        except (OSError, ValueError) as error:
                            errors.append(
                                f"fixture {duplicate!r} could not be read safely: {error}"
                            )
                            continue
                        if data != original_data:
                            errors.append(
                                f"fixture {fixture_id!r} is not byte-identical to {duplicate!r}"
                            )
    return ids


def validate_preflight(value: dict[str, Any], errors: list[str]) -> None:
    if value.get("schemaVersion") != 1:
        errors.append("preflight.schemaVersion must be integer 1")
    status = value.get("status")
    if not isinstance(status, str) or status not in {"passed", "blocked"}:
        errors.append("preflight.status must be 'passed' or 'blocked'")
    checks = value.get("checks")
    failed_checks = 0
    if not isinstance(checks, list) or not checks:
        errors.append("preflight.checks must be a non-empty list")
    else:
        for index, check in enumerate(checks):
            label = f"preflight.checks[{index}]"
            if not isinstance(check, dict):
                errors.append(f"{label} must be an object")
                continue
            require_string(check.get("condition"), f"{label}.condition", errors)
            if check.get("status") not in {"passed", "failed"}:
                errors.append(f"{label}.status must be 'passed' or 'failed'")
            elif check.get("status") == "failed":
                failed_checks += 1
            require_string(check.get("evidence"), f"{label}.evidence", errors)
    blockers = value.get("blockers")
    if not isinstance(blockers, list):
        errors.append("preflight.blockers must be a list")
    else:
        for index, blocker in enumerate(blockers):
            label = f"preflight.blockers[{index}]"
            if not isinstance(blocker, dict):
                errors.append(f"{label} must be an object")
                continue
            require_string(blocker.get("condition"), f"{label}.condition", errors)
            require_string(blocker.get("reason"), f"{label}.reason", errors)
        if status == "blocked" and not blockers:
            errors.append("blocked preflight must contain at least one blocker")
        elif status == "passed" and blockers:
            errors.append("passed preflight cannot contain blockers")
    if status == "passed" and failed_checks:
        errors.append("passed preflight cannot contain failed checks")
    if status == "blocked" and isinstance(checks, list) and checks and not failed_checks:
        errors.append("blocked preflight must contain at least one failed check")


def find_sensitive_content(
    value: object,
    path: str,
    errors: list[str],
    *,
    subject: str = "evidence",
) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = re.sub(r"[^a-z]", "", str(key).lower())
            if normalized in SENSITIVE_KEYS:
                errors.append(f"{subject} contains sensitive key at {path}.{key}")
            find_sensitive_content(child, f"{path}.{key}", errors, subject=subject)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            find_sensitive_content(child, f"{path}[{index}]", errors, subject=subject)
    elif isinstance(value, str) and (
        BEARER.search(value)
        or PRIVATE_KEY.search(value)
        or PROVIDER_TOKEN.search(value)
        or JWT.search(value)
    ):
        errors.append(f"{subject} contains secret-shaped content at {path}")


def validate_evidence(
    value: dict[str, Any],
    case_contracts: dict[str, dict[str, Any]],
    preflight_status: object,
    kit_root: Path,
    errors: list[str],
) -> None:
    if value.get("schemaVersion") != 1:
        errors.append("evidence.schemaVersion must be integer 1")
    records = value.get("records")
    if not isinstance(records, list):
        errors.append("evidence.records must be a list")
        return
    seen: set[str] = set()
    artifact_paths_seen: set[str] = set()
    artifact_reference_count = 0
    total_artifact_bytes = 0
    artifact_budget_exceeded = False
    for index, record in enumerate(records):
        label = f"evidence.records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{label} must be an object")
            continue
        case_id = record.get("caseId")
        if not isinstance(case_id, str):
            errors.append(f"{label}.caseId must be a string")
            contract = None
        elif case_id not in case_contracts:
            errors.append(f"{label}.caseId references unknown case {case_id!r}")
            contract = None
        elif case_id in seen:
            errors.append(f"evidence contains duplicate caseId {case_id!r}")
            contract = case_contracts[case_id]
        else:
            seen.add(case_id)
            contract = case_contracts[case_id]
        result = record.get("result")
        if not isinstance(result, str) or result not in RESULTS:
            errors.append(f"{label}.result must be one of {sorted(RESULTS)}")
        duration = record.get("durationMs")
        if not is_integer(duration) or duration < 0:
            errors.append(f"{label}.durationMs must be a non-negative integer")
        if record.get("sanitized") is not True:
            errors.append(f"{label}.sanitized must be true")
        observed = record.get("observed")
        if not isinstance(observed, dict) or not observed:
            errors.append(f"{label}.observed must be a non-empty object")
        artifacts = record.get("artifacts")
        if require_string_list(artifacts, f"{label}.artifacts", errors):
            for artifact_index, artifact in enumerate(artifacts):
                artifact_reference_count += 1
                artifact_label = f"{label}.artifacts[{artifact_index}]"
                if artifact_reference_count > MAX_ARTIFACT_REFERENCES:
                    errors.append(
                        f"evidence exceeds {MAX_ARTIFACT_REFERENCES} artifact references"
                    )
                    continue
                if not safe_relative(artifact, artifact_label, errors):
                    continue
                normalized_artifact = str(artifact).replace("\\", "/")
                if normalized_artifact in artifact_paths_seen:
                    errors.append(f"{artifact_label} duplicates an artifact reference")
                    continue
                artifact_paths_seen.add(normalized_artifact)
                if artifact_budget_exceeded:
                    continue
                artifact_path = kit_root / artifact
                if not normalized_artifact.startswith("evidence/"):
                    errors.append(f"{artifact_label} must be beneath evidence/")
                elif (
                    artifact_path.is_symlink()
                    or not artifact_path.is_file()
                    or not artifact_path.resolve().is_relative_to(
                        (kit_root / "evidence").resolve()
                    )
                ):
                    errors.append(
                        f"{artifact_label} must reference a contained regular file"
                    )
                else:
                    try:
                        artifact_data = read_regular_file(
                            artifact_path,
                            kit_root / "evidence",
                            MAX_ARTIFACT_BYTES,
                        )
                    except (OSError, ValueError) as error:
                        errors.append(f"{artifact_label} could not be read safely: {error}")
                        continue
                    total_artifact_bytes += len(artifact_data)
                    if total_artifact_bytes > MAX_TOTAL_ARTIFACT_BYTES:
                        errors.append(
                            "evidence artifacts exceed "
                            f"{MAX_TOTAL_ARTIFACT_BYTES} total bytes"
                        )
                        artifact_budget_exceeded = True
                        continue
                    find_sensitive_content(
                        artifact_data.decode("utf-8", errors="replace"),
                        artifact_label,
                        errors,
                    )
        mutations = record.get("mutations")
        if not isinstance(mutations, list):
            errors.append(f"{label}.mutations must be a list")
        recovery_status = record.get("recoveryStatus")
        if not isinstance(recovery_status, str) or recovery_status not in RECOVERY_STATUSES:
            errors.append(
                f"{label}.recoveryStatus must be one of {sorted(RECOVERY_STATUSES)}"
            )
        if contract and contract.get("recoveryRequired") is True:
            if isinstance(result, str) and result in {"pass", "fail"} and recovery_status not in {
                "recovered",
                "failed_recovery",
            }:
                errors.append(
                    f"{label}.recoveryStatus must record recovery outcome for an "
                    "executed stateful case"
                )
            if isinstance(result, str) and result in {"blocked", "not_run"} and recovery_status not in {
                "blocked",
                "pending",
            }:
                errors.append(
                    f"{label}.recoveryStatus must be blocked or pending for an "
                    "unexecuted stateful case"
                )
        if contract and isinstance(result, str) and result in {"pass", "fail"}:
            if preflight_status != "passed":
                errors.append(
                    f"{label}.result cannot be executed while preflight is not passed"
                )
            if not is_rfc3339(record.get("startedAt")):
                errors.append(
                    f"{label}.startedAt must be an RFC 3339 timestamp with timezone "
                    "when executed"
                )
            oracle_result = record.get("oracleResult")
            if not isinstance(oracle_result, dict):
                errors.append(f"{label}.oracleResult must be an object when executed")
            else:
                passed = oracle_result.get("passed")
                if type(passed) is not bool or passed != (result == "pass"):
                    errors.append(
                        f"{label}.oracleResult.passed must agree with result"
                    )
                require_string_list(
                    oracle_result.get("details"),
                    f"{label}.oracleResult.details",
                    errors,
                    nonempty=True,
                )
            if record.get("oracleDigest") != contract.get("oracleDigest"):
                errors.append(
                    f"{label}.oracleDigest must match the campaign oracle"
                )
    missing = sorted(set(case_contracts) - seen)
    if missing:
        errors.append(f"evidence is missing campaign cases: {missing}")
    find_sensitive_content(value, "evidence", errors)


def validate(kit_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    required = {
        "campaign": kit_root / "campaign.json",
        "fixtures-manifest": kit_root / "fixtures-manifest.json",
        "preflight": kit_root / "preflight.json",
        "evidence": kit_root / "evidence.json",
    }
    values = {
        name: load_object(path, kit_root, errors) for name, path in required.items()
    }
    case_contracts, fixture_refs = validate_campaign(values["campaign"], errors)
    try:
        fixture_ids = validate_manifest(values["fixtures-manifest"], kit_root, errors)
    except OSError as error:
        errors.append(f"fixtures-manifest filesystem inspection failed: {error}")
        fixture_ids = set()
    unknown_fixtures = sorted(fixture_refs - fixture_ids)
    if unknown_fixtures:
        errors.append(f"campaign references unknown fixtures: {unknown_fixtures}")
    validate_preflight(values["preflight"], errors)
    try:
        validate_evidence(
            values["evidence"],
            case_contracts,
            values["preflight"].get("status"),
            kit_root,
            errors,
        )
    except OSError as error:
        errors.append(f"evidence filesystem inspection failed: {error}")
    return {
        "status": "valid" if not errors else "invalid",
        "kit": str(kit_root),
        "caseCount": len(case_contracts),
        "fixtureCount": len(fixture_ids),
        "preflightStatus": values["preflight"].get("status"),
        "executionAuthorized": False,
        "executionResultsVerified": False,
        "validationScope": "structure_cross_record_semantics_and_filesystem_safety",
        "errors": errors,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a real-world edge-testing kit."
    )
    parser.add_argument("kit_directory", type=Path)
    parser.add_argument(
        "--oracle-digests",
        action="store_true",
        help="print canonical oracle digests from campaign.json",
    )
    args = parser.parse_args(argv[1:])
    kit_root = args.kit_directory.resolve()
    if args.oracle_digests:
        errors: list[str] = []
        campaign = load_object(kit_root / "campaign.json", kit_root, errors)
        contracts, _ = validate_campaign(campaign, errors)
        result = {
            "status": "valid" if not errors else "invalid",
            "oracleDigests": {
                case_id: contract["oracleDigest"]
                for case_id, contract in contracts.items()
                if contract.get("oracleDigest") is not None
            },
            "errors": errors,
        }
    else:
        result = validate(kit_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
