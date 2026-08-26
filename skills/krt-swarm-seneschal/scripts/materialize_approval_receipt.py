#!/usr/bin/env python3
"""Materialize and validate documentation approvals bound to artifact content."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

from deterministic_artifacts import canonical_sha256, file_sha256, parse_timestamp, write_atomic


SCHEMA_VERSION = 1


def _artifact_entries(repo_root: Path, source_artifacts: list[str]) -> list[dict[str, str]]:
    if not source_artifacts or len(source_artifacts) != len(set(source_artifacts)):
        raise ValueError("source_artifacts must be a non-empty unique list")
    entries: list[dict[str, str]] = []
    for raw_path in sorted(source_artifacts):
        relative = PurePosixPath(raw_path)
        if relative.is_absolute() or ".." in relative.parts or not raw_path:
            raise ValueError(f"artifact path must be repo-relative: {raw_path}")
        path = repo_root / relative
        try:
            path.resolve(strict=True).relative_to(repo_root.resolve(strict=True))
        except (FileNotFoundError, ValueError) as exc:
            raise ValueError(f"approval artifact escapes or is missing: {raw_path}") from exc
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"approval artifact must be a regular file: {raw_path}")
        entries.append(
            {"path": raw_path, "digest": file_sha256(path)}
        )
    return entries


def materialize_receipt(
    *, repo_root: Path, source_artifacts: list[str], approved_by: str, approved_at: str,
    approval_event_digest: str,
) -> dict[str, Any]:
    if not approved_by.strip():
        raise ValueError("approved_by must be non-empty")
    parse_timestamp(approved_at)
    if re.fullmatch(r"sha256:[0-9a-f]{64}", approval_event_digest) is None:
        raise ValueError("approval_event_digest must be a trusted lowercase SHA-256 handoff")
    artifacts = _artifact_entries(repo_root, source_artifacts)
    packet_payload = {"schema_version": SCHEMA_VERSION, "artifacts": artifacts}
    receipt = {
        **packet_payload,
        "packet_digest": canonical_sha256(packet_payload),
        "approved_by": approved_by,
        "approved_at": approved_at,
        "approval_event_digest": approval_event_digest,
    }
    receipt["receipt_digest"] = canonical_sha256(receipt)
    return receipt


def validate_receipt(repo_root: Path, receipt: Any) -> dict[str, Any]:
    expected = {"schema_version", "artifacts", "packet_digest", "approved_by", "approved_at", "approval_event_digest", "receipt_digest"}
    if not isinstance(receipt, dict) or set(receipt) != expected:
        raise ValueError("approval receipt has missing or unknown fields")
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("approval receipt schema_version is invalid")
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("approval receipt artifacts must be a list")
    paths = [item.get("path") for item in artifacts if isinstance(item, dict)]
    if len(paths) != len(artifacts) or not all(isinstance(path, str) for path in paths):
        raise ValueError("approval receipt artifact entry is invalid")
    current = _artifact_entries(repo_root, paths)
    if current != artifacts:
        raise ValueError("approval artifact digest mismatch; approval is stale")
    packet_payload = {"schema_version": SCHEMA_VERSION, "artifacts": artifacts}
    expected_digest = canonical_sha256(packet_payload)
    if receipt.get("packet_digest") != expected_digest:
        raise ValueError("approval packet digest is invalid")
    if not isinstance(receipt.get("approved_by"), str) or not receipt["approved_by"].strip():
        raise ValueError("approval receipt approved_by is invalid")
    if not isinstance(receipt.get("approved_at"), str):
        raise ValueError("approval receipt approved_at is invalid")
    parse_timestamp(receipt["approved_at"])
    if not isinstance(receipt.get("approval_event_digest"), str) or re.fullmatch(r"sha256:[0-9a-f]{64}", receipt["approval_event_digest"]) is None:
        raise ValueError("approval receipt event digest is invalid")
    unsigned = {key: value for key, value in receipt.items() if key != "receipt_digest"}
    if receipt.get("receipt_digest") != canonical_sha256(unsigned):
        raise ValueError("approval receipt digest is invalid")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--artifact", action="append", required=True)
    parser.add_argument("--approved-by", required=True)
    parser.add_argument("--approved-at", required=True)
    parser.add_argument("--expected-approval-event-digest", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = materialize_receipt(
            repo_root=args.repo_root.resolve(),
            source_artifacts=args.artifact,
            approved_by=args.approved_by,
            approved_at=args.approved_at,
            approval_event_digest=args.expected_approval_event_digest,
        )
        write_atomic(args.output, receipt)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    json.dump(receipt, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
