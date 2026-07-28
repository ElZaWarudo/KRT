#!/usr/bin/env python3
"""Scrub personal DOCX metadata and optionally remove comments."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from contextlib import ExitStack
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from lib.ooxml import scrub_package  # noqa: E402
from lib.package_safety import admitted_docx  # noqa: E402
from lib.path_safety import resolve_output_path  # noqa: E402
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
    admissions = ExitStack()
    try:
        source_path = args.document.absolute()
        output = resolve_output_path(args.output, label="Output path")
        if not source_path.is_file():
            raise FileNotFoundError(f"Document not found: {source_path}")
        if source_path == output:
            raise ValueError("Privacy scrub requires a distinct output path")
        if output.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing output: {output}")

        source = admissions.enter_context(admitted_docx(source_path))
        before = inspect_docx(source)
        package_result = scrub_package(
            source,
            output,
            remove_comments=args.remove_comments,
            remove_custom_properties=not args.keep_custom_properties,
            overwrite=args.overwrite,
        )
        with zipfile.ZipFile(output) as archive:
            bad_member = archive.testzip()
            if bad_member:
                raise RuntimeError(f"Corrupt output member: {bad_member}")
        after = inspect_docx(output)
        before_core = before["core_properties"]
        after_core = after["core_properties"]
        personal_core_fields = (
            "author",
            "comments",
            "created",
            "keywords",
            "last_modified_by",
            "modified",
        )
        report = {
            "input": str(source_path),
            "output": str(output),
            "package": package_result,
            "before": {
                "populated_personal_metadata_fields": sorted(
                    key
                    for key in personal_core_fields
                    if before_core.get(key)
                ),
                "comments": before["package"]["comments"],
                "comment_personal_metadata": before["package"][
                    "comment_personal_metadata"
                ],
                "extended_personal_metadata": before["package"][
                    "extended_personal_metadata"
                ],
                "possible_pii": before["possible_pii"],
                "zip_metadata": before["package"]["zip_metadata"],
            },
            "after": {
                "populated_personal_metadata_fields": sorted(
                    key
                    for key in personal_core_fields
                    if after_core.get(key)
                ),
                "comments": after["package"]["comments"],
                "comment_personal_metadata": after["package"][
                    "comment_personal_metadata"
                ],
                "extended_personal_metadata": after["package"][
                    "extended_personal_metadata"
                ],
                "possible_pii": after["possible_pii"],
                "zip_metadata": after["package"]["zip_metadata"],
            },
            "content_pii_removed": False,
            "visual_qa": "pending_render_and_manual_inspection",
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
