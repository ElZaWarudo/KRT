#!/usr/bin/env python3
"""Scrub personal DOCX metadata and optionally remove comments."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

from docx import Document

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from lib.ooxml import scrub_package  # noqa: E402
from lib.worddoc import inspect_docx  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--remove-comments", action="store_true")
    parser.add_argument("--keep-custom-properties", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        source = args.document.resolve()
        output = args.output.resolve()
        if not source.is_file():
            raise FileNotFoundError(f"Document not found: {source}")
        if source == output:
            raise ValueError("Privacy scrub requires a distinct output path")
        if output.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing output: {output}")

        before = inspect_docx(source)
        package_result = scrub_package(
            source,
            output,
            remove_comments=args.remove_comments,
            remove_custom_properties=not args.keep_custom_properties,
        )
        with zipfile.ZipFile(output) as archive:
            bad_member = archive.testzip()
            if bad_member:
                raise RuntimeError(f"Corrupt output member: {bad_member}")
        Document(str(output))
        after = inspect_docx(output)
        report = {
            "input": str(source),
            "output": str(output),
            "package": package_result,
            "before": {
                "core_properties": before["core_properties"],
                "comments": before["package"]["comments"],
                "possible_pii": before["possible_pii"],
            },
            "after": {
                "core_properties": after["core_properties"],
                "comments": after["package"]["comments"],
                "possible_pii": after["possible_pii"],
            },
            "content_pii_removed": False,
            "visual_qa": "pending_render_and_manual_inspection",
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

