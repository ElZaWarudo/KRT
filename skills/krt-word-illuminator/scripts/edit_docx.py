#!/usr/bin/env python3
"""Apply guarded structural patches to an existing DOCX."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import zipfile
from contextlib import ExitStack
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
from lib.path_safety import atomic_publish_file, resolve_output_path  # noqa: E402
from lib.package_safety import admitted_docx  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("patch", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def package_parts(path: Path) -> set[str]:
    with zipfile.ZipFile(path) as archive:
        return set(archive.namelist())


def replace_paragraph(document: object, operation: dict) -> dict:
    matches = [
        paragraph
        for paragraph in iter_all_paragraphs(document)
        if paragraph.text == operation["old"]
    ]
    if not matches:
        raise ValueError("No exact paragraph match for the requested text")
    if len(matches) > 1 and not operation.get("all", False):
        raise ValueError(
            f"Ambiguous paragraph replacement ({len(matches)} matches)"
        )
    targets = matches if operation.get("all", False) else matches[:1]
    for paragraph in targets:
        # Assigning paragraph.text recreates its runs, silently dropping
        # character formatting, hyperlinks, fields, drawings, and references.
        # This narrow operation only supports a single plain-text run so its
        # formatting can be retained by updating that run in place.
        semantic_nodes = paragraph._p.xpath(
            ".//w:hyperlink | .//w:fldChar | .//w:instrText | .//w:drawing | "
            ".//w:br | .//w:tab | .//w:footnoteReference | "
            ".//w:endnoteReference | .//w:commentReference | "
            ".//w:commentRangeStart | .//w:commentRangeEnd | "
            ".//w:bookmarkStart | .//w:bookmarkEnd | .//w:sdt | .//w:smartTag"
        )
        if (
            len(paragraph.runs) != 1
            or paragraph.runs[0].text != paragraph.text
            or semantic_nodes
        ):
            raise ValueError(
                "replace_paragraph supports only simple single-run text "
                "paragraphs; use a structural edit for formatted or inline content"
            )
        paragraph.runs[0].text = operation["new"]
    return {
        "op": operation["op"],
        "matches": len(targets),
        "formatting_preserved": True,
    }


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
            f"Expected one requested heading; found {len(matches)}"
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
    admissions = ExitStack()
    try:
        source_path = args.document.absolute()
        patch_path = args.patch.resolve()
        output = resolve_output_path(args.output, label="Output path")
        if not source_path.is_file():
            raise FileNotFoundError(f"Document not found: {source_path}")
        if output == source_path:
            raise ValueError("Editing in place is not supported; choose a new output path")
        if output.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing output: {output}")

        patch = load_json(patch_path)
        validate_json(patch, SKILL_DIR / "schemas" / "document-patch.schema.json")
        source = admissions.enter_context(admitted_docx(source_path))
        before = inspect_docx(source)
        if before["package"]["insertions"] or before["package"]["deletions"]:
            raise ValueError(
                "Basic editing is disabled for documents with tracked changes; "
                "use a specialized reviewed OOXML workflow"
            )
        before_parts = package_parts(source)
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
        with tempfile.NamedTemporaryFile(
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".docx",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
        try:
            document.save(temporary_path)
            after = inspect_docx(temporary_path)
            removed_parts = sorted(before_parts - package_parts(temporary_path))
            if removed_parts:
                raise ValueError(
                    "Edit removed package parts outside the requested scope "
                    f"({len(removed_parts)} parts)"
                )
            atomic_publish_file(
                temporary_path,
                output,
                overwrite=args.overwrite,
                label="edited DOCX",
            )
        finally:
            if temporary_path.exists():
                temporary_path.unlink()
        report = {
            "input": str(source_path),
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
    finally:
        admissions.close()


if __name__ == "__main__":
    raise SystemExit(main())
