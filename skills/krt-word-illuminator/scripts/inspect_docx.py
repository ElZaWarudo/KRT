#!/usr/bin/env python3
"""Inspect a DOCX package and emit a structural JSON report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from lib.path_safety import atomic_write_text  # noqa: E402
from lib.worddoc import inspect_docx, redact_inspection  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--include-content",
        action="store_true",
        help="Include heading, header, footer, and metadata values in protected output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.document.is_file():
        print(json.dumps({"error": f"Document not found: {args.document}"}))
        return 2
    try:
        report = inspect_docx(args.document.absolute())
        if not args.include_content:
            report = redact_inspection(report)
        if args.report:
            atomic_write_text(
                args.report,
                json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                overwrite=args.overwrite,
                label="inspection report",
            )
    except Exception as exc:
        print(json.dumps({"error": str(exc), "document": str(args.document)}))
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
