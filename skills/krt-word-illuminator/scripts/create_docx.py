#!/usr/bin/env python3
"""Create a professional DOCX from a grounded JSON request."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from lib.worddoc import (  # noqa: E402
    audit_request_grounding,
    create_from_request,
    inspect_docx,
    load_json,
    validate_json,
)


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
        return args.output.resolve()
    output = Path(request["output"])
    if not output.is_absolute():
        output = args.request.resolve().parent / output
    return output


def main() -> int:
    args = parse_args()
    try:
        request_path = args.request.resolve()
        request = load_json(request_path)
        validate_json(request, SKILL_DIR / "schemas" / "document-request.schema.json")
        output = resolve_output(args, request)
        report_path = (
            args.report.resolve()
            if args.report
            else output.with_suffix(".creation-report.json")
        )

        if output.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing output: {output}")
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
        document.save(output)
        inspection = inspect_docx(output)
        report = {
            "output": str(output),
            "status": (
                "created_with_grounding_issues"
                if grounding["source_reference_issues"]
                else "created"
            ),
            "objective": request["objective"],
            "document_type": request["document_type"],
            "sections": len(request["sections"]),
            "tables": inspection["tables"],
            "figures": inspection["inline_figures"],
            "grounding": grounding,
            "structural_inspection": inspection,
            "visual_qa": "pending_render_and_manual_inspection",
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
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

