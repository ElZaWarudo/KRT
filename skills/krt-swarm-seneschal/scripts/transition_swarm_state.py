#!/usr/bin/env python3
"""Apply optimistic, locked, recoverable transitions to queue and blocker state."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tempfile
from typing import Any

import yaml

from record_run_timing import document_lock
from materialize_approval_receipt import validate_receipt
from deterministic_artifacts import parse_timestamp


UNIT_TRANSITIONS = {
    "planned": {"ready", "blocked", "deferred"},
    "ready": {"running", "blocked", "deferred"},
    "running": {"review-gated", "blocked", "needs-fix", "split-required"},
    "review-gated": {"release-ready", "needs-fix", "blocked", "split-required"},
    "release-ready": {"handed-off", "needs-fix"},
    "needs-fix": {"running", "blocked", "deferred"},
    "blocked": {"planned", "ready", "deferred"},
    "deferred": {"planned", "ready"},
    "split-required": {"planned", "deferred"},
    "handed-off": {"merged"},
    "merged": set(),
}
BLOCKER_STATUSES = {"open", "answered", "superseded", "resolved"}


def state_digest(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _validate(queue: dict[str, Any], blockers: dict[str, Any]) -> None:
    if queue.get("schema_version") not in {1, 2} or not isinstance(queue.get("units"), dict):
        raise ValueError("queue state schema is invalid")
    gate = queue.get("documentation_gate")
    if not isinstance(gate, dict) or gate.get("status") not in {"draft", "in_review", "changes_requested", "approved"}:
        raise ValueError("documentation gate schema is invalid")
    for unit_id, unit in queue["units"].items():
        if not isinstance(unit_id, str) or not isinstance(unit, dict) or unit.get("status") not in UNIT_TRANSITIONS:
            raise ValueError("queue unit schema is invalid")
        if not isinstance(unit.get("blocked_by", []), list):
            raise ValueError("queue unit blocked_by must be a list")
    if blockers.get("schema_version") != 1 or not isinstance(blockers.get("blockers"), list):
        raise ValueError("blocker ledger schema is invalid")
    ids: list[str] = []
    for blocker in blockers["blockers"]:
        if not isinstance(blocker, dict) or not isinstance(blocker.get("id"), str) or blocker.get("status") not in BLOCKER_STATUSES:
            raise ValueError("blocker entry schema is invalid")
        ids.append(blocker["id"])
    if len(ids) != len(set(ids)):
        raise ValueError("blocker ids must be unique")
    open_refs: dict[str, set[str]] = {unit_id: set() for unit_id in queue["units"]}
    for blocker in blockers["blockers"]:
        if blocker["status"] != "open":
            continue
        affected = set(blocker.get("affected_units", []))
        if isinstance(blocker.get("unit_id"), str):
            affected.add(blocker["unit_id"])
        if any(unit_id not in queue["units"] for unit_id in affected):
            raise ValueError("open blocker references an unknown queue unit")
        for unit_id in affected:
            open_refs[unit_id].add(blocker["id"])
    for unit_id, unit in queue["units"].items():
        if set(unit.get("blocked_by", [])) != open_refs[unit_id]:
            raise ValueError("queue blocked_by disagrees with open blocker ledger")


def _receipt_path(repo_root: Path, raw_path: str) -> Path:
    relative = PurePosixPath(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("approval receipt path must be repo-relative")
    candidate = repo_root / relative
    if candidate.is_symlink():
        raise ValueError("approval receipt must not be a symlink")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(repo_root.resolve(strict=True))
    except (FileNotFoundError, ValueError) as exc:
        raise ValueError("approval receipt escapes or is missing") from exc
    return resolved


def _require_current_approval(queue: dict[str, Any], repo_root: Path | None) -> None:
    if repo_root is None:
        raise ValueError("approval-dependent transition requires repo_root")
    gate = queue["documentation_gate"]
    receipt_path = gate.get("approval_receipt")
    if gate.get("status") != "approved" or not isinstance(receipt_path, str):
        raise ValueError("documentation approval is missing")
    receipt = json.loads(_receipt_path(repo_root, receipt_path).read_text(encoding="utf-8"))
    validate_receipt(repo_root, receipt)
    if gate.get("approved_packet_digest") != receipt["packet_digest"]:
        raise ValueError("documentation approval receipt does not match queue state")
    if gate.get("approval_receipt_digest") != receipt["receipt_digest"]:
        raise ValueError("documentation approval provenance does not match queue state")


def _dump_yaml(value: dict[str, Any]) -> str:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True)


def _replace_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def transition_state(
    *, queue_path: Path, blockers_path: Path, transition: dict[str, Any],
    expected_queue_digest: str, expected_blockers_digest: str,
    repo_root: Path | None = None,
) -> dict[str, str]:
    lock_path = queue_path.parent / ".seneschal-state-transaction"
    with document_lock(lock_path):
        journal = lock_path.with_suffix(".json")
        if journal.exists():
            raise ValueError("unfinished state transaction requires trusted recovery; no state was mutated")
        if state_digest(queue_path) != expected_queue_digest:
            raise ValueError("queue digest changed; reload state before retrying")
        if state_digest(blockers_path) != expected_blockers_digest:
            raise ValueError("blockers digest changed; reload state before retrying")
        queue = _load_yaml(queue_path)
        blockers = _load_yaml(blockers_path)
        _validate(queue, blockers)
        operation = transition.get("operation")
        dirty_targets = ["queue"]
        if transition.get("schema_version") != 1:
            raise ValueError("transition schema_version must be 1")
        if operation == "approve-documentation":
            expected = {"schema_version", "operation", "receipt_path", "expected_approval_event_digest"}
            if set(transition) != expected or repo_root is None:
                raise ValueError("approve-documentation requires exact fields and repo_root")
            receipt_path = _receipt_path(repo_root, transition["receipt_path"])
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            validate_receipt(repo_root, receipt)
            if receipt["approval_event_digest"] != transition["expected_approval_event_digest"]:
                raise ValueError("approval receipt does not match trusted user-event handoff")
            gate = queue["documentation_gate"]
            if gate["status"] != "in_review":
                raise ValueError("documentation gate must be in_review before approval")
            approved_paths = gate.get("approval_artifacts", gate.get("source_artifacts"))
            if not isinstance(approved_paths, list) or sorted(approved_paths) != [item["path"] for item in receipt["artifacts"]]:
                raise ValueError("approval receipt does not cover the gate approval_artifacts")
            gate.update({
                "status": "approved",
                "approved_by": receipt["approved_by"],
                "approved_at": receipt["approved_at"],
                "approval_receipt": transition["receipt_path"],
                "approved_packet_digest": receipt["packet_digest"],
                "approval_receipt_digest": receipt["receipt_digest"],
            })
        elif operation == "documentation-status":
            expected = {"schema_version", "operation", "from", "to"}
            if set(transition) != expected:
                raise ValueError("documentation-status transition has missing or unknown fields")
            allowed = {
                "draft": {"in_review"},
                "in_review": {"changes_requested"},
                "changes_requested": {"in_review"},
            }
            gate = queue["documentation_gate"]
            if gate["status"] != transition["from"]:
                raise ValueError("documentation current status does not match transition precondition")
            if transition["to"] not in allowed.get(transition["from"], set()):
                raise ValueError("illegal documentation status transition")
            gate["status"] = transition["to"]
        elif operation == "unit-status":
            expected = {"schema_version", "operation", "unit_id", "from", "to"}
            if set(transition) != expected:
                raise ValueError("unit-status transition has missing or unknown fields")
            unit = queue["units"].get(transition["unit_id"])
            if not isinstance(unit, dict) or unit.get("status") != transition["from"]:
                raise ValueError("unit current status does not match transition precondition")
            if transition["to"] not in UNIT_TRANSITIONS[transition["from"]]:
                raise ValueError("illegal unit status transition")
            if transition["to"] in {"release-ready", "handed-off", "merged"}:
                raise ValueError("release lifecycle requires authoritative reconciliation, not unit-status")
            if transition["to"] in {"ready", "running"}:
                _require_current_approval(queue, repo_root)
                if unit.get("blocked_by"):
                    raise ValueError("unit has open blockers")
            unit["status"] = transition["to"]
        elif operation == "resolve-blocker":
            expected = {"schema_version", "operation", "blocker_id", "decided_at", "decided_by", "decision"}
            if set(transition) != expected:
                raise ValueError("resolve-blocker transition has missing or unknown fields")
            parse_timestamp(transition["decided_at"])
            if not all(isinstance(transition[key], str) and transition[key].strip() for key in ("decided_by", "decision")):
                raise ValueError("blocker resolution fields must be non-empty strings")
            blocker = next((item for item in blockers["blockers"] if item["id"] == transition["blocker_id"]), None)
            if blocker is None or blocker["status"] not in {"open", "answered"}:
                raise ValueError("blocker is not open or answered")
            blocker["status"] = "resolved"
            blocker["resolution"] = {
                "decided_at": transition["decided_at"],
                "decided_by": transition["decided_by"],
                "decision": transition["decision"],
            }
            dirty_targets = ["blockers", "queue"]
            for unit in queue["units"].values():
                refs = unit.get("blocked_by", [])
                if transition["blocker_id"] in refs:
                    unit["blocked_by"] = [ref for ref in refs if ref != transition["blocker_id"]]
                    if unit["status"] == "blocked" and not unit["blocked_by"]:
                        unit["status"] = "planned"
        else:
            raise ValueError("unsupported transition operation")
        _validate(queue, blockers)
        queue_text = _dump_yaml(queue)
        blocker_text = _dump_yaml(blockers)
        _replace_text(journal, json.dumps({
            "queue_path": str(queue_path.resolve()), "blockers_path": str(blockers_path.resolve()),
            "queue": queue_text, "blockers": blocker_text, "targets": dirty_targets,
        }, sort_keys=True))
        if "blockers" in dirty_targets:
            _replace_text(blockers_path, blocker_text)
        _replace_text(queue_path, queue_text)
        journal.unlink(missing_ok=True)
        return {"queue_digest": state_digest(queue_path), "blockers_digest": state_digest(blockers_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--blockers", type=Path, required=True)
    parser.add_argument("--transition", type=Path, required=True)
    parser.add_argument("--expected-queue-digest", required=True)
    parser.add_argument("--expected-blockers-digest", required=True)
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args()
    try:
        transition = json.loads(args.transition.read_text(encoding="utf-8"))
        if not isinstance(transition, dict):
            raise ValueError("transition must contain a JSON object")
        result = transition_state(
            queue_path=args.queue, blockers_path=args.blockers, transition=transition,
            expected_queue_digest=args.expected_queue_digest,
            expected_blockers_digest=args.expected_blockers_digest,
            repo_root=args.repo_root.resolve() if args.repo_root else None,
        )
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
