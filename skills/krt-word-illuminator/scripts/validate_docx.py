#!/usr/bin/env python3
"""Validate DOCX structure, grounding, accessibility, privacy, and visual QA."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from docx import Document
from docx.oxml.ns import qn

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from lib.worddoc import (  # noqa: E402
    audit_request_grounding,
    inspect_docx,
    iter_all_paragraphs,
    load_json,
    paragraph_heading_level,
    validate_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--visual-qa", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--final", action="store_true")
    parser.add_argument("--privacy", action="store_true")
    parser.add_argument("--strict-warnings", action="store_true")
    parser.add_argument("--allow-pending", action="store_true")
    return parser.parse_args()


def issue(code: str, message: str, **details: Any) -> dict[str, Any]:
    value: dict[str, Any] = {"code": code, "message": message}
    value.update(details)
    return value


def normalize_heading(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def _resolve_from(base: Path, value: str) -> Path:
    result = Path(value)
    return result.resolve() if result.is_absolute() else (base / result).resolve()


def validate_visual_qa(
    path: Path, document: Path
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    data = load_json(path)
    validate_json(data, SKILL_DIR / "schemas" / "visual-qa.schema.json")
    errors = []
    qa_document = _resolve_from(path.parent, data["document"])
    if qa_document != document.resolve():
        errors.append(
            issue(
                "visual-document-mismatch",
                "Visual QA refers to a different document",
                expected=str(document.resolve()),
                actual=str(qa_document),
            )
        )

    render_report_path = _resolve_from(path.parent, data["render_report"])
    if not render_report_path.is_file():
        errors.append(
            issue(
                "missing-render-report",
                "Visual QA render report does not exist",
                path=str(render_report_path),
            )
        )
        render_report = {}
    else:
        render_report = load_json(render_report_path)
        rendered_document = _resolve_from(
            render_report_path.parent, str(render_report.get("document", ""))
        )
        if rendered_document != document.resolve():
            errors.append(
                issue(
                    "render-document-mismatch",
                    "Render report refers to a different document",
                    expected=str(document.resolve()),
                    actual=str(rendered_document),
                )
            )
        if render_report.get("pages") != data["rendered_pages"]:
            errors.append(
                issue(
                    "render-page-count-mismatch",
                    "Visual QA page count differs from render report",
                    qa_pages=data["rendered_pages"],
                    report_pages=render_report.get("pages"),
                )
            )
        missing_images = [
            value
            for value in render_report.get("page_images", [])
            if not _resolve_from(render_report_path.parent, str(value)).is_file()
        ]
        if missing_images:
            errors.append(
                issue(
                    "missing-rendered-page-images",
                    "Rendered page images listed in the report are missing",
                    images=missing_images,
                )
            )

    expected = set(range(1, data["rendered_pages"] + 1))
    inspected = set(data["inspected_pages"])
    if inspected != expected:
        errors.append(
            issue(
                "visual-pages-incomplete",
                "Every rendered page must be inspected",
                missing=sorted(expected - inspected),
                unexpected=sorted(inspected - expected),
            )
        )
    blocking = [
        finding
        for finding in data["findings"]
        if finding["severity"] == "blocking" and not finding["resolved"]
    ]
    if blocking:
        errors.append(
            issue(
                "visual-blocking-findings",
                "Blocking visual findings remain unresolved",
                count=len(blocking),
            )
        )
    if data["status"] != "passed":
        errors.append(
            issue("visual-qa-not-passed", "Visual QA status must be passed")
        )
    return data, errors


def main() -> int:
    args = parse_args()
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    visual_qa = None
    unverified_claims: list[str] = []
    try:
        source = args.document.resolve()
        if not source.is_file():
            raise FileNotFoundError(f"Document not found: {source}")
        inspection = inspect_docx(source)
        document = Document(str(source))

        titles = [
            paragraph
            for paragraph in document.paragraphs
            if paragraph.style and paragraph.style.name == "Title" and paragraph.text.strip()
        ]
        if not titles:
            errors.append(issue("missing-title", "No non-empty Title paragraph found"))

        previous_level = 0
        for heading in inspection["headings"]:
            level = heading["level"]
            if previous_level and level > previous_level + 1:
                errors.append(
                    issue(
                        "heading-level-skip",
                        f"Heading level jumps from {previous_level} to {level}",
                        heading=heading["text"],
                    )
                )
            previous_level = level

        paragraph_texts = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if len(paragraph.text.strip()) >= 40
        ]
        duplicates = [text for text, count in Counter(paragraph_texts).items() if count > 1]
        if duplicates:
            warnings.append(
                issue(
                    "duplicate-paragraphs",
                    "Long duplicate paragraphs detected",
                    count=len(duplicates),
                    samples=duplicates[:5],
                )
            )

        empty_spacers = 0
        direct_runs = 0
        total_runs = 0
        for paragraph in document.paragraphs:
            if not paragraph.text.strip():
                has_semantic_content = bool(
                    paragraph._p.xpath(".//w:drawing | .//w:br | .//w:fldChar")
                )
                if not has_semantic_content:
                    empty_spacers += 1
        for paragraph in iter_all_paragraphs(document):
            for run in paragraph.runs:
                total_runs += 1
                properties = run._r.find(qn("w:rPr"))
                if properties is not None and len(properties):
                    direct_runs += 1
        if empty_spacers:
            warnings.append(
                issue(
                    "empty-spacing-paragraphs",
                    "Empty paragraphs may be used for visual spacing",
                    count=empty_spacers,
                )
            )
        direct_ratio = round(direct_runs / total_runs, 4) if total_runs else 0
        if direct_ratio > 0.25:
            warnings.append(
                issue(
                    "excess-direct-formatting",
                    "More than 25% of runs contain direct formatting",
                    ratio=direct_ratio,
                )
            )

        if inspection["tables"] != inspection["tables_with_repeating_header"]:
            errors.append(
                issue(
                    "table-header-not-repeated",
                    "Every table must mark its first row as a repeating header",
                    tables=inspection["tables"],
                    compliant=inspection["tables_with_repeating_header"],
                )
            )
        if inspection["inline_figures"] != inspection["figures_with_alt_text"]:
            errors.append(
                issue(
                    "missing-figure-alt-text",
                    "Every inline figure must have alternative text",
                    figures=inspection["inline_figures"],
                    compliant=inspection["figures_with_alt_text"],
                )
            )

        placeholders = inspection["placeholders"]
        accidental = {
            key: value
            for key, value in placeholders.items()
            if key != "pending-confirmation"
        }
        if accidental:
            errors.append(
                issue(
                    "accidental-placeholders",
                    "Unresolved TODO, XXX, or template variables remain",
                    placeholders=accidental,
                )
            )
        if placeholders.get("pending-confirmation") and not args.allow_pending:
            errors.append(
                issue(
                    "pending-confirmation",
                    "Pending confirmations remain in the document",
                    count=placeholders["pending-confirmation"],
                )
            )

        if args.request:
            request = load_json(args.request.resolve())
            validate_json(
                request, SKILL_DIR / "schemas" / "document-request.schema.json"
            )
            required = {
                normalize_heading(value)
                for value in request.get("required_sections", [])
            }
            actual = {
                normalize_heading(item["text"]) for item in inspection["headings"]
            }
            missing = sorted(required - actual)
            if missing:
                errors.append(
                    issue(
                        "missing-required-sections",
                        "Required sections are absent",
                        sections=missing,
                    )
                )
            grounding = audit_request_grounding(request)
            if grounding["source_reference_issues"]:
                errors.append(
                    issue(
                        "source-reference-issues",
                        "Source-backed blocks have missing or unknown source IDs",
                        details=grounding["source_reference_issues"],
                    )
                )
            if grounding["unclassified_blocks"]:
                warnings.append(
                    issue(
                        "unclassified-content",
                        "Content blocks lack provenance classification",
                        details=grounding["unclassified_blocks"],
                    )
                )
            unverified_claims = grounding["unverified_claims"]
            if unverified_claims and not args.allow_pending:
                errors.append(
                    issue(
                        "unverified-claims",
                        "Unverified claims remain",
                        claims=unverified_claims,
                    )
                )

        if args.final:
            package = inspection["package"]
            if package["comments"]:
                errors.append(
                    issue("comments-remain", "Comments remain in the final document")
                )
            if package["insertions"] or package["deletions"]:
                errors.append(
                    issue(
                        "tracked-changes-remain",
                        "Tracked insertions or deletions remain in the final document",
                        insertions=package["insertions"],
                        deletions=package["deletions"],
                    )
                )

        if args.privacy:
            properties = inspection["core_properties"]
            personal = {
                key: properties[key]
                for key in ("author", "last_modified_by")
                if properties.get(key)
            }
            if personal:
                errors.append(
                    issue(
                        "personal-metadata",
                        "Personal author metadata remains",
                        properties=personal,
                    )
                )
            if inspection["package"]["custom_properties"]:
                warnings.append(
                    issue(
                        "custom-properties",
                        "Custom document properties remain",
                    )
                )
            if inspection["possible_pii"]:
                warnings.append(
                    issue(
                        "possible-pii",
                        "Possible personal data appears in document content",
                        matches=inspection["possible_pii"],
                    )
                )

        if args.visual_qa:
            visual_qa, visual_errors = validate_visual_qa(
                args.visual_qa.resolve(), source
            )
            errors.extend(visual_errors)
        elif args.final:
            errors.append(
                issue(
                    "missing-visual-qa",
                    "Final validation requires a visual QA report",
                )
            )

        valid = not errors and not (args.strict_warnings and warnings)
        report = {
            "document": str(source),
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "metrics": {
                "paragraphs": inspection["paragraphs"],
                "headings": len(inspection["headings"]),
                "tables": inspection["tables"],
                "figures": inspection["inline_figures"],
                "sections": len(inspection["sections"]),
                "direct_formatting_ratio": direct_ratio,
                "empty_spacing_paragraphs": empty_spacers,
            },
            "visual_qa": visual_qa,
            "unverified_claims": unverified_claims,
        }
        validate_json(
            report, SKILL_DIR / "schemas" / "validation-report.schema.json"
        )
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if valid else 1
    except Exception as exc:
        print(
            json.dumps(
                {
                    "document": str(args.document),
                    "valid": False,
                    "errors": [issue("validation-exception", str(exc))],
                    "warnings": warnings,
                    "metrics": {},
                    "visual_qa": visual_qa,
                    "unverified_claims": unverified_claims,
                },
                ensure_ascii=False,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
