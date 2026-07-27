#!/usr/bin/env python3
"""Validate a private staged summary and its provenance sidecar."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Any

from publication_safety import scan_publication


STAGING_DIR = Path("docs/harnesses/staging")
PROVENANCE_DIR = Path("docs/harnesses/provenance")
CLASSIFICATIONS = {"public", "internal", "confidential", "restricted", "unknown"}


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def opaque_provenance_id(value: object) -> bool:
    if not isinstance(value, str) or not value.startswith("prov-"):
        return False
    try:
        identifier = uuid.UUID(value.removeprefix("prov-"))
    except ValueError:
        return False
    return identifier.version == 4 and str(identifier) == value.removeprefix("prov-")


def scoped_path(root: Path, raw: str, scope: Path, label: str) -> tuple[Path | None, str | None]:
    requested = Path(raw)
    if requested.is_absolute():
        return None, f"{label}-must-be-under:{scope.as_posix()}"
    expected_root = (root / scope).resolve()
    candidate = (root / requested).resolve()
    try:
        candidate.relative_to(expected_root)
    except ValueError:
        return None, f"{label}-must-be-under:{scope.as_posix()}"
    return candidate, None


def check_evidence(
    root: Path,
    summary_arg: str,
    sidecar_arg: str,
) -> tuple[dict[str, Any], Path | None, Path | None, bytes | None]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    summary_path, summary_scope_error = scoped_path(root, summary_arg, STAGING_DIR, "summary")
    sidecar_path, sidecar_scope_error = scoped_path(root, sidecar_arg, PROVENANCE_DIR, "sidecar")
    errors.extend(error for error in (summary_scope_error, sidecar_scope_error) if error)

    if summary_path and summary_path.suffix.lower() != ".md":
        errors.append("summary-must-be-markdown")
    if sidecar_path and sidecar_path.suffix.lower() != ".json":
        errors.append("sidecar-must-be-json")
    if summary_path and not summary_path.is_file():
        errors.append(f"summary-not-found:{summary_arg}")
    if sidecar_path and not sidecar_path.is_file():
        errors.append(f"sidecar-not-found:{sidecar_arg}")

    summary_bytes: bytes | None = None
    summary_text = ""
    sidecar: dict[str, Any] = {}
    if not errors and summary_path and sidecar_path:
        try:
            summary_bytes = summary_path.read_bytes()
            summary_text = summary_bytes.decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"summary-unreadable:{exc}")
        try:
            loaded = json.loads(sidecar_path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                raise ValueError("sidecar must be a JSON object")
            sidecar = loaded
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"sidecar-unreadable:{exc}")

    provenance_id: object = None
    if summary_text:
        frontmatter = parse_frontmatter(summary_text)
        provenance_id = frontmatter.get("provenance_id")
        if not opaque_provenance_id(provenance_id):
            errors.append("invalid-provenance-id:expected-random-uuid4")
        if sidecar.get("provenance_id") != provenance_id:
            errors.append("provenance-id-mismatch")

        findings = scan_publication(summary_text)
        errors.extend(f"publication-safety:{code}" for code in findings["blocking"])
        warnings.extend(f"publication-safety:{code}" for code in findings["warnings"])

    declared_warnings = sidecar.get("warnings", [])
    decisions = sidecar.get("warning_decisions", {})
    if sidecar.get("classification") not in CLASSIFICATIONS:
        errors.append("invalid-classification:expected-public-internal-confidential-restricted-unknown")
    if sidecar.get("redaction_status") != "completed":
        errors.append("redaction-status-must-be-completed")
    rationale = sidecar.get("publication_rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        errors.append("publication-rationale-required")
    if not isinstance(declared_warnings, list) or not all(
        isinstance(item, str) and item.strip() for item in declared_warnings
    ):
        errors.append("sidecar-warnings-must-be-string-list")
        declared_warnings = []
    if not isinstance(decisions, dict):
        errors.append("sidecar-warning-decisions-must-be-object")
        decisions = {}

    warning_codes = [*declared_warnings, *warnings]
    for warning in sorted(set(warning_codes)):
        decision = decisions.get(warning)
        if not isinstance(decision, str) or not decision.strip():
            errors.append(f"unaccepted-warning:{warning}")

    result = {
        "allowed": not errors,
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warning_codes)),
        "summary": {
            "staged_summary": summary_arg,
            "sidecar": sidecar_arg,
            "provenance_id": provenance_id,
        },
        "paths": [summary_arg, sidecar_arg],
    }
    return result, summary_path, sidecar_path, summary_bytes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", help="repo-relative Markdown under docs/harnesses/staging")
    parser.add_argument("--sidecar", required=True, help="repo-relative JSON under docs/harnesses/provenance")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    result, _, _, _ = check_evidence(args.root, args.summary, args.sidecar)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
