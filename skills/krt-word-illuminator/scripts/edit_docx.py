#!/usr/bin/env python3
"""Apply guarded structural patches to an existing DOCX."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from docx import Document

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from lib.worddoc import (  # noqa: E402
    add_block,
    add_sections,
    inspect_docx,
    iter_all_paragraphs,
    load_json,
    paragraph_heading_level,
    set_core_properties,
    validate_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("patch", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def replace_paragraph(document: object, operation: dict) -> dict:
    matches = [
        paragraph
        for paragraph in iter_all_paragraphs(document)
        if paragraph.text == operation["old"]
    ]
    if not matches:
        raise ValueError(f"No exact paragraph match for: {operation['old']!r}")
    if len(matches) > 1 and not operation.get("all", False):
        raise ValueError(
            f"Ambiguous paragraph replacement ({len(matches)} matches): "
            f"{operation['old']!r}"
        )
    targets = matches if operation.get("all", False) else matches[:1]
    for paragraph in targets:
        paragraph.text = operation["new"]
    return {"op": operation["op"], "matches": len(targets)}


def insert_after_heading(
    document: object,
    operation: dict,
    *,
    base_dir: Path,
) -> dict:
    matches = [
        paragraph
        for paragraph in document.paragraphs
        if paragraph.text == operation["heading"]
        and paragraph_heading_level(paragraph) is not None
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one heading named {operation['heading']!r}; found {len(matches)}"
        )
    if any(block.get("type") == "section_break" for block in operation["blocks"]):
        raise ValueError("Section breaks are not supported in heading-relative insertion")

    elements = []
    for block in operation["blocks"]:
        elements.extend(add_block(document, block, base_dir=base_dir))
    anchor = matches[0]._p
    for element in elements:
        anchor.addnext(element)
        anchor = element
    return {"op": operation["op"], "heading": operation["heading"], "blocks": len(elements)}


def main() -> int:
    args = parse_args()
    try:
        source = args.document.resolve()
        patch_path = args.patch.resolve()
        output = args.output.resolve()
        if not source.is_file():
            raise FileNotFoundError(f"Document not found: {source}")
        if output == source:
            raise ValueError("Editing in place is not supported; choose a new output path")
        if output.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing output: {output}")

        patch = load_json(patch_path)
        validate_json(patch, SKILL_DIR / "schemas" / "document-patch.schema.json")
        before = inspect_docx(source)
        document = Document(str(source))
        operations = []

        for operation in patch["operations"]:
            kind = operation["op"]
            if kind == "replace_paragraph":
                operations.append(replace_paragraph(document, operation))
            elif kind == "insert_after_heading":
                operations.append(
                    insert_after_heading(document, operation, base_dir=patch_path.parent)
                )
            elif kind == "append_sections":
                elements = add_sections(
                    document, operation["sections"], base_dir=patch_path.parent
                )
                operations.append({"op": kind, "elements": len(elements)})
            elif kind == "set_core_properties":
                set_core_properties(document, operation["properties"])
                operations.append(
                    {"op": kind, "properties": sorted(operation["properties"])}
                )
            else:  # pragma: no cover - schema guards this
                raise ValueError(f"Unsupported operation: {kind}")

        output.parent.mkdir(parents=True, exist_ok=True)
        document.save(output)
        after = inspect_docx(output)
        report = {
            "input": str(source),
            "output": str(output),
            "operations": operations,
            "before_sha256": before["sha256"],
            "after_sha256": after["sha256"],
            "visual_qa": "pending_render_and_manual_inspection",
            "comparison_required": True,
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

