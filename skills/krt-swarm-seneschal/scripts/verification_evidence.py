#!/usr/bin/env python3
"""Compute wave fingerprints and manage reusable aggregate verification evidence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tempfile
from typing import Any

from record_run_timing import document_lock


SCHEMA_VERSION = 1
RESULTS = {"passed", "failed"}


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def parse_timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_relative_path(path: str) -> PurePosixPath:
    candidate = PurePosixPath(path)
    if not path or candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("changed paths must be non-empty repo-relative paths")
    return candidate


def compute_fingerprint(
    *, repo_root: Path, base_revision: str, changed_paths: list[str], commands: list[str]
) -> dict[str, Any]:
    if not isinstance(base_revision, str) or not base_revision.strip():
        raise ValueError("base_revision must be a non-empty string")
    if not changed_paths or len(changed_paths) != len(set(changed_paths)):
        raise ValueError("changed_paths must be non-empty and unique")
    if (
        not commands
        or any(not isinstance(command, str) or not command for command in commands)
        or len(commands) != len(set(commands))
    ):
        raise ValueError("commands must be a non-empty ordered unique list")
    path_entries: list[dict[str, str]] = []
    for raw_path in sorted(changed_paths):
        relative = validate_relative_path(raw_path)
        path = repo_root / relative
        if path.is_symlink():
            digest = f"symlink:{os.readlink(path)}"
        elif path.is_file():
            digest = f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"
        elif path.exists():
            raise ValueError(f"changed path is not a file: {raw_path}")
        else:
            digest = "deleted"
        path_entries.append({"path": raw_path, "digest": digest})
    payload = {
        "schema_version": SCHEMA_VERSION,
        "base_revision": base_revision,
        "changed_paths": path_entries,
        "commands": commands,
    }
    return {
        **payload,
        "fingerprint": f"sha256:{hashlib.sha256(canonical_json(payload)).hexdigest()}",
    }


def validate_fingerprint(document: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "schema_version",
        "base_revision",
        "changed_paths",
        "commands",
        "fingerprint",
    }
    if not isinstance(document, dict) or set(document) != expected:
        raise ValueError("fingerprint document has missing or unknown fields")
    rebuilt_payload = {key: document[key] for key in expected - {"fingerprint"}}
    expected_hash = f"sha256:{hashlib.sha256(canonical_json(rebuilt_payload)).hexdigest()}"
    if document.get("schema_version") != SCHEMA_VERSION or document.get("fingerprint") != expected_hash:
        raise ValueError("fingerprint document is invalid or has been modified")
    if not isinstance(document.get("base_revision"), str) or not document["base_revision"]:
        raise ValueError("fingerprint base_revision is invalid")
    changed_paths = document.get("changed_paths")
    commands = document.get("commands")
    if not isinstance(changed_paths, list) or not isinstance(commands, list):
        raise ValueError("fingerprint paths and commands must be lists")
    if not changed_paths or not commands or len(commands) != len(set(commands)) or any(
        not isinstance(command, str) or not command for command in commands
    ):
        raise ValueError("fingerprint paths and commands are invalid")
    normalized_paths: list[str] = []
    for entry in changed_paths:
        if not isinstance(entry, dict) or set(entry) != {"path", "digest"}:
            raise ValueError("fingerprint changed path entry is invalid")
        path = entry.get("path")
        digest = entry.get("digest")
        if not isinstance(path, str) or not isinstance(digest, str) or not digest:
            raise ValueError("fingerprint changed path entry is invalid")
        validate_relative_path(path)
        normalized_paths.append(path)
    if normalized_paths != sorted(set(normalized_paths)):
        raise ValueError("fingerprint changed paths must be sorted and unique")
    return document


def load_registry(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"schema_version": SCHEMA_VERSION, "records": []}
    if document.get("schema_version") != SCHEMA_VERSION or not isinstance(document.get("records"), list):
        raise ValueError("evidence registry must use schema_version 1 and records[]")
    for record in document["records"]:
        validate_evidence_record(record)
    return document


def validate_evidence_record(record: Any) -> dict[str, Any]:
    expected = {
        "fingerprint",
        "base_revision",
        "changed_paths",
        "commands",
        "result",
        "captured_at",
        "evidence",
    }
    if not isinstance(record, dict) or set(record) != expected:
        raise ValueError("evidence record has missing or unknown fields")
    if record.get("result") not in RESULTS:
        raise ValueError("evidence record result is invalid")
    if not isinstance(record.get("fingerprint"), str) or not record["fingerprint"].startswith("sha256:"):
        raise ValueError("evidence record fingerprint is invalid")
    if not isinstance(record.get("base_revision"), str) or not record["base_revision"]:
        raise ValueError("evidence record base_revision is invalid")
    if not isinstance(record.get("changed_paths"), list) or not isinstance(record.get("commands"), list):
        raise ValueError("evidence record paths and commands are invalid")
    if not isinstance(record.get("captured_at"), str):
        raise ValueError("evidence record captured_at is invalid")
    parse_timestamp(record["captured_at"])
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence or any(
        not isinstance(item, str) or not item for item in evidence
    ):
        raise ValueError("evidence record references are invalid")
    return record


def write_atomic(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(document, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def record_evidence(
    *,
    registry_path: Path,
    fingerprint: dict[str, Any],
    result: str,
    evidence: list[str],
    captured_at: str,
) -> dict[str, Any]:
    validate_fingerprint(fingerprint)
    if result not in RESULTS:
        raise ValueError("result must be passed or failed")
    if not evidence or any(not isinstance(item, str) or not item for item in evidence):
        raise ValueError("evidence must contain at least one non-empty reference")
    parse_timestamp(captured_at)
    record = {
        "fingerprint": fingerprint["fingerprint"],
        "base_revision": fingerprint["base_revision"],
        "changed_paths": fingerprint["changed_paths"],
        "commands": fingerprint["commands"],
        "result": result,
        "captured_at": captured_at,
        "evidence": evidence,
    }
    validate_evidence_record(record)
    with document_lock(registry_path):
        registry = load_registry(registry_path)
        registry["records"] = [
            item
            for item in registry["records"]
            if item.get("fingerprint") != fingerprint["fingerprint"]
        ]
        registry["records"].append(record)
        registry["records"].sort(key=lambda item: item["fingerprint"])
        write_atomic(registry_path, registry)
    return record


def decide_reuse(
    *,
    registry: dict[str, Any],
    fingerprint: dict[str, Any],
    now: str,
    max_age_seconds: int,
) -> dict[str, Any]:
    validate_fingerprint(fingerprint)
    if not isinstance(max_age_seconds, int) or isinstance(max_age_seconds, bool) or max_age_seconds < 0:
        raise ValueError("max_age_seconds must be a non-negative integer")
    now_value = parse_timestamp(now)
    matches = [
        record
        for record in registry.get("records", [])
        if isinstance(record, dict) and record.get("fingerprint") == fingerprint["fingerprint"]
    ]
    if not matches:
        return {"action": "run", "reason": "evidence-missing", "record": None}
    record = matches[-1]
    validate_evidence_record(record)
    if (
        record["base_revision"] != fingerprint["base_revision"]
        or record["changed_paths"] != fingerprint["changed_paths"]
        or record["commands"] != fingerprint["commands"]
    ):
        raise ValueError("evidence record does not match its fingerprint inputs")
    if record.get("result") != "passed":
        return {"action": "run", "reason": "prior-evidence-failed", "record": record}
    captured_at = record.get("captured_at")
    if not isinstance(captured_at, str):
        raise ValueError("evidence record captured_at is invalid")
    age_seconds = int((now_value - parse_timestamp(captured_at)).total_seconds())
    if age_seconds < 0:
        raise ValueError("evidence record is from the future")
    if age_seconds > max_age_seconds:
        return {"action": "run", "reason": "evidence-stale", "record": record}
    return {
        "action": "reuse",
        "reason": "exact-passing-fingerprint",
        "age_seconds": age_seconds,
        "record": record,
    }


def load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    compute = subparsers.add_parser("compute")
    compute.add_argument("--repo-root", type=Path, required=True)
    compute.add_argument("--base-revision", required=True)
    compute.add_argument("--path", action="append", required=True)
    compute.add_argument("--verification-command", action="append", required=True)
    compute.add_argument("--output", type=Path)
    record = subparsers.add_parser("record")
    record.add_argument("--registry", type=Path, required=True)
    record.add_argument("--fingerprint", type=Path, required=True)
    record.add_argument("--result", choices=sorted(RESULTS), required=True)
    record.add_argument("--evidence", action="append", required=True)
    record.add_argument("--captured-at", default=None)
    decide = subparsers.add_parser("decide")
    decide.add_argument("--registry", type=Path, required=True)
    decide.add_argument("--fingerprint", type=Path, required=True)
    decide.add_argument("--now", default=None)
    decide.add_argument("--max-age-seconds", type=int, required=True)
    args = parser.parse_args()
    try:
        if args.command == "compute":
            result = compute_fingerprint(
                repo_root=args.repo_root,
                base_revision=args.base_revision,
                changed_paths=args.path,
                commands=args.verification_command,
            )
            if args.output:
                write_atomic(args.output, result)
        elif args.command == "record":
            result = record_evidence(
                registry_path=args.registry,
                fingerprint=load_json_object(args.fingerprint),
                result=args.result,
                evidence=args.evidence,
                captured_at=args.captured_at or utc_now(),
            )
        else:
            result = decide_reuse(
                registry=load_registry(args.registry),
                fingerprint=load_json_object(args.fingerprint),
                now=args.now or utc_now(),
                max_age_seconds=args.max_age_seconds,
            )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
