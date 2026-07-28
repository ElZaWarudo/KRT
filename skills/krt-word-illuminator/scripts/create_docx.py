#!/usr/bin/env python3
"""Create a professional DOCX from a grounded JSON request."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from lib.worddoc import (  # noqa: E402
    audit_request_grounding,
    create_from_request,
    inspect_docx,
    load_json,
    redact_inspection,
    resolve_request_path,
    validate_json,
)
from lib.path_safety import atomic_publish_files, resolve_output_path  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--allow-source-reference-issues",
        action="store_true",
        help="Create despite missing or unknown source IDs; report remains non-passing.",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve_output(args: argparse.Namespace, request: dict) -> Path:
    if args.output:
        return resolve_output_path(args.output, label="Output path")
    resolved = resolve_request_path(
        str(request["output"]),
        args.request.resolve().parent,
        label="Request output",
    )
    return resolve_output_path(resolved, label="Request output")


def main() -> int:
    args = parse_args()
    try:
        request_path = args.request.resolve()
        request = load_json(request_path)
        validate_json(request, SKILL_DIR / "schemas" / "document-request.schema.json")
        output = resolve_output(args, request)
        report_path = (
            resolve_output_path(args.report, label="Report path")
            if args.report
            else resolve_output_path(
                output.with_suffix(".creation-report.json"),
                label="Creation report path",
            )
        )

        if output.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing output: {output}")
        if report_path.exists() and not args.overwrite:
            raise FileExistsError(
                f"Refusing to overwrite existing report: {report_path}"
            )
        if output.suffix.lower() != ".docx":
            raise ValueError("Output must use the .docx extension")

        section_names = {section["heading"].strip().casefold() for section in request["sections"]}
        missing_sections = [
            name
            for name in request.get("required_sections", [])
            if name.strip().casefold() not in section_names
        ]
        if missing_sections:
            raise ValueError(f"Missing required sections: {', '.join(missing_sections)}")

        grounding = audit_request_grounding(request)
        if grounding["source_reference_issues"] and not args.allow_source_reference_issues:
            raise ValueError(
                "Source grounding failed; use valid source_ids or explicitly allow issues"
            )

        document = create_from_request(request, request_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".docx",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
        report_temporary_path: Path | None = None
        try:
            document.save(temporary_path)
            inspection = inspect_docx(temporary_path)
            inspection["path"] = str(output)
            report = {
                "output": str(output),
                "status": (
                    "created_with_grounding_issues"
                    if grounding["source_reference_issues"]
                    else "created"
                ),
                "document_type": request["document_type"],
                "sections": len(request["sections"]),
                "tables": inspection["tables"],
                "figures": inspection["inline_figures"],
                "grounding": {
                    "provenance_counts": grounding["provenance_counts"],
                    "source_reference_issue_count": len(
                        grounding["source_reference_issues"]
                    ),
                    "unclassified_block_count": len(
                        grounding["unclassified_blocks"]
                    ),
                    "unverified_claim_count": len(grounding["unverified_claims"]),
                },
                "structural_inspection": redact_inspection(inspection),
                "visual_qa": "pending_render_and_manual_inspection",
            }
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=report_path.parent,
                prefix=f".{report_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as report_temporary:
                report_temporary.write(
                    json.dumps(report, indent=2, ensure_ascii=False) + "\n"
                )
                report_temporary.flush()
                os.fsync(report_temporary.fileno())
                report_temporary_path = Path(report_temporary.name)
            atomic_publish_files(
                (
                    (temporary_path, output, "DOCX output"),
                    (
                        report_temporary_path,
                        report_path,
                        "creation report",
                    ),
                ),
                overwrite=args.overwrite,
            )
        finally:
            if temporary_path.exists():
                temporary_path.unlink()
            if (
                report_temporary_path is not None
                and report_temporary_path.exists()
            ):
                report_temporary_path.unlink()
        report["report"] = str(report_path)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if not grounding["source_reference_issues"] else 1
    except Exception as exc:
        print(
            json.dumps(
                {"error": str(exc), "request": str(args.request)},
                ensure_ascii=False,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
