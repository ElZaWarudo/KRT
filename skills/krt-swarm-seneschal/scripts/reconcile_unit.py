#!/usr/bin/env python3
"""Read-only evidence validation for the transactional release-ready gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

from deterministic_artifacts import canonical_sha256
from deterministic_validation import exact_object, non_empty_string, string_list
from evaluate_worker_run import _certification_state
from finding_registry import validate_registry
from verification_evidence import (
    _assert_fingerprint_matches_worktree,
    validate_evidence_record,
    validate_fingerprint,
)


def read_reference(root: Path, reference: Any) -> tuple[Path, bytes]:
    exact_object(reference, {"path", "digest"}, "evidence reference")
    raw = non_empty_string(reference["path"], "reference.path")
    path = Path(raw)
    if ".." in path.parts:
        raise ValueError("evidence path must not contain traversal")
    if not path.is_absolute():
        path = root / path
    if any(parent.is_symlink() for parent in (path, *path.parents)):
        raise ValueError("evidence path must not be a symlink")
    data = path.read_bytes()
    if reference["digest"] != "sha256:" + hashlib.sha256(data).hexdigest():
        raise ValueError("evidence reference digest mismatch")
    return path.resolve(), data


def validate_reconciliation(
    *, root: Path, queue: dict[str, Any], unit_id: str,
    evidence: dict[str, str],
) -> dict[str, Any]:
    """Validate root-owned artifacts; never execute evidence-supplied commands."""
    unit = queue["units"].get(unit_id)
    if not isinstance(unit, dict) or unit.get("status") != "review-gated":
        raise ValueError("reconcile-unit requires a review-gated unit")
    if unit.get("blocked_by"):
        raise ValueError("unit has open blockers")
    dependencies = string_list(unit.get("depends_on"), "depends_on", unique=True)
    for dependency in dependencies:
        prior = queue["units"].get(dependency)
        if dependency == unit_id or not isinstance(prior, dict) or (
            prior.get("status") not in {"release-ready", "handed-off", "merged"}
            or prior.get("blocked_by")
        ):
            raise ValueError("unit has unmet dependencies")
    policy = exact_object(unit.get("reconciliation_policy"), {
        "candidate_revision", "candidate_digest", "contract_hash", "worker_id",
        "required_certifications", "findings_registry",
    }, "reconciliation_policy")
    for key in ("candidate_digest", "contract_hash"):
        if not isinstance(policy[key], str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", policy[key]):
            raise ValueError(f"reconciliation_policy.{key} must be a SHA-256 digest")
    worker = non_empty_string(policy["worker_id"], "worker_id")
    roles = string_list(policy["required_certifications"], "required_certifications", unique=True)
    if "reviewer" not in roles or set(roles) - {"reviewer", "security-sentinel"}:
        raise ValueError("required certifications must include reviewer and only supported roles")
    execution = unit.get("execution", {})
    risk = unit.get("risk", {})
    if not isinstance(execution, dict) or not isinstance(risk, dict):
        raise ValueError("unit execution and risk must be mappings")
    triggers = execution.get("role_triggers", {})
    if not isinstance(triggers, dict):
        raise ValueError("unit role_triggers must be a mapping")
    if (triggers.get("security-sentinel") or risk.get("security", "unknown") != "low") and "security-sentinel" not in roles:
        raise ValueError("security certificate is required by unit risk or triggers")
    contract_hash = execution.get("worker_contract_hash")
    if contract_hash is not None and contract_hash != policy["contract_hash"]:
        raise ValueError("reconciliation contract does not match unit contract")

    observed: list[tuple[dict[str, str], bytes]] = []

    def read(ref: Any, *, document: bool = True) -> Any:
        _, data = read_reference(root, ref)
        observed.append((dict(ref), data))
        if not document:
            return data
        value = json.loads(data)
        if not isinstance(value, dict):
            raise ValueError("evidence must contain a JSON object")
        return value

    bundle = exact_object(read(evidence), {
        "schema_version", "unit_id", "candidate_revision", "fingerprint",
        "verification", "verification_logs", "certificates", "findings_registry",
    }, "reconciliation evidence")
    if bundle["schema_version"] != 1 or bundle["unit_id"] != unit_id:
        raise ValueError("reconciliation evidence unit or schema mismatch")
    revision = policy["candidate_revision"]
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", revision):
        raise ValueError("candidate_revision must be a full Git commit ID")

    def check_candidate() -> None:
        try:
            head = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "--verify", "HEAD^{commit}"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
        except subprocess.CalledProcessError as exc:
            raise ValueError("cannot resolve candidate revision") from exc
        if head != revision or bundle["candidate_revision"] != revision:
            raise ValueError("candidate revision mismatch")
        try:
            _assert_fingerprint_matches_worktree(root, fingerprint, require_complete_diff=True)
        except subprocess.CalledProcessError as exc:
            raise ValueError("cannot inspect complete candidate diff") from exc

    fingerprint = validate_fingerprint(read(bundle["fingerprint"]))
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", fingerprint["base_revision"]):
        raise ValueError("fingerprint base_revision must be a full Git commit ID")
    candidate_digest = canonical_sha256({
        "candidate_revision": revision, "fingerprint": fingerprint["fingerprint"],
    })
    if candidate_digest != policy["candidate_digest"]:
        raise ValueError("candidate digest mismatch")
    check_candidate()
    verification = validate_evidence_record(read(bundle["verification"]))
    if verification["result"] != "passed" or any(
        verification[key] != fingerprint[key]
        for key in ("fingerprint", "base_revision", "changed_paths", "commands")
    ):
        raise ValueError("passing verification does not cover candidate")
    logs = bundle["verification_logs"]
    if not isinstance(logs, list) or len(logs) != len(fingerprint["commands"]):
        raise ValueError("verification log coverage is incomplete")
    log_paths = []
    for ref in logs:
        read(ref, document=False)
        log_paths.append(str((root / Path(ref["path"])).resolve()))
    recorded_paths = [str((root / Path(path)).resolve()) for path in verification["evidence"]]
    if log_paths != recorded_paths:
        raise ValueError("verification logs do not match evidence record")

    refs = bundle["certificates"]
    if not isinstance(refs, list):
        raise ValueError("certificates must be a list")
    certificates = [read(ref) for ref in refs]
    reasons, pending, findings = _certification_state(
        {"contract_hash": policy["contract_hash"], "required_certifications": roles},
        {"worker_id": worker, "diff_digest": candidate_digest, "certifications": certificates},
    )
    if reasons or pending or any(cert.get("status") != "passed" for cert in certificates):
        raise ValueError(f"independent certificates rejected: {reasons + pending}")
    if any(findings.values()):
        raise ValueError("certificates contain unresolved actionable findings")
    if bundle["findings_registry"] != policy["findings_registry"]:
        raise ValueError("findings registry does not match trusted unit policy")
    registry = validate_registry(read(bundle["findings_registry"]))
    if registry["contract_hash"] != policy["contract_hash"] or registry["diff_digest"] != candidate_digest:
        raise ValueError("findings registry candidate binding mismatch")
    for finding in registry["findings"]:
        if finding["status"] not in {"fixed", "rejected"} or (
            finding["status"] == "fixed"
            and finding["resolution"]["resolved_diff_digest"] != candidate_digest
        ):
            raise ValueError("registry contains unresolved actionable findings")
    # Detect edits during validation before the caller writes its transaction journal.
    for ref, data in observed:
        if read_reference(root, ref)[1] != data:
            raise ValueError("reconciliation evidence changed during validation")
    check_candidate()
    return {
        "evidence": evidence, "candidate_revision": revision,
        "candidate_digest": candidate_digest, "fingerprint": fingerprint["fingerprint"],
        "verification_record_digest": verification["record_digest"],
        "findings_registry_digest": registry["registry_digest"],
        "accepted_artifacts": [ref for ref, _ in observed],
    }
