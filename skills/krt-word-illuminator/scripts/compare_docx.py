#!/usr/bin/env python3
"""Compare two DOCX files textually, structurally, and optionally visually."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

from docx import Document

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from lib.worddoc import inspect_docx, iter_all_paragraphs  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--before-render-dir", type=Path)
    parser.add_argument("--after-render-dir", type=Path)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def package_parts(path: Path) -> set[str]:
    with zipfile.ZipFile(path) as archive:
        return set(archive.namelist())


def page_number(path: Path) -> int:
    try:
        return int(path.stem.split("-")[-1])
    except ValueError:
        return 0


def image_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def visual_comparison(before_dir: Path, after_dir: Path) -> dict[str, Any]:
    before_pages = sorted(before_dir.glob("page-*.png"), key=page_number)
    after_pages = sorted(after_dir.glob("page-*.png"), key=page_number)
    pages = []
    try:
        from PIL import Image, ImageChops, ImageStat
    except ImportError:
        Image = None

    for index in range(max(len(before_pages), len(after_pages))):
        before = before_pages[index] if index < len(before_pages) else None
        after = after_pages[index] if index < len(after_pages) else None
        item: dict[str, Any] = {
            "page": index + 1,
            "before": str(before) if before else None,
            "after": str(after) if after else None,
            "changed": True,
        }
        if before and after:
            item["changed"] = image_digest(before) != image_digest(after)
            if Image is not None:
                with Image.open(before).convert("RGB") as left, Image.open(after).convert(
                    "RGB"
                ) as right:
                    item["dimensions_before"] = list(left.size)
                    item["dimensions_after"] = list(right.size)
                    if left.size == right.size:
                        difference = ImageChops.difference(left, right)
                        mean = ImageStat.Stat(difference).mean
                        item["mean_pixel_difference"] = round(sum(mean) / len(mean), 4)
        pages.append(item)
    return {
        "before_pages": len(before_pages),
        "after_pages": len(after_pages),
        "pages": pages,
        "manual_visual_review_required": True,
    }


def main() -> int:
    args = parse_args()
    try:
        before_path = args.before.resolve()
        after_path = args.after.resolve()
        for path in (before_path, after_path):
            if not path.is_file():
                raise FileNotFoundError(f"Document not found: {path}")

        before_doc = Document(str(before_path))
        after_doc = Document(str(after_path))
        before_lines = [paragraph.text for paragraph in iter_all_paragraphs(before_doc)]
        after_lines = [paragraph.text for paragraph in iter_all_paragraphs(after_doc)]
        diff = list(
            difflib.unified_diff(
                before_lines,
                after_lines,
                fromfile=str(before_path),
                tofile=str(after_path),
                lineterm="",
            )
        )

        before_inspection = inspect_docx(before_path)
        after_inspection = inspect_docx(after_path)
        before_parts = package_parts(before_path)
        after_parts = package_parts(after_path)
        metrics = {}
        for key in (
            "paragraphs",
            "tables",
            "table_rows",
            "inline_figures",
        ):
            if before_inspection[key] != after_inspection[key]:
                metrics[key] = {
                    "before": before_inspection[key],
                    "after": after_inspection[key],
                }

        report: dict[str, Any] = {
            "before": str(before_path),
            "after": str(after_path),
            "changed": before_inspection["sha256"] != after_inspection["sha256"],
            "text_diff": diff,
            "structure_changes": metrics,
            "heading_changes": {
                "before": before_inspection["headings"],
                "after": after_inspection["headings"],
            },
            "style_usage_changes": {
                "before": before_inspection["style_usage"],
                "after": after_inspection["style_usage"],
            },
            "package_parts_added": sorted(after_parts - before_parts),
            "package_parts_removed": sorted(before_parts - after_parts),
            "visual": None,
        }
        if args.before_render_dir or args.after_render_dir:
            if not (args.before_render_dir and args.after_render_dir):
                raise ValueError("Both render directories are required for visual comparison")
            report["visual"] = visual_comparison(
                args.before_render_dir.resolve(),
                args.after_render_dir.resolve(),
            )
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

