#!/usr/bin/env python3
"""Build the bundled neutral professional-report DOCX template."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from docx import Document

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from lib.worddoc import configure_document, ensure_styles, set_core_properties  # noqa: E402
from lib.path_safety import atomic_publish_file, resolve_output_path  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=SKILL_DIR / "assets" / "templates" / "professional-report.docx",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output = resolve_output_path(args.output, label="Template output path")
        if output.exists() and not args.overwrite:
            raise FileExistsError(f"Refusing to overwrite existing template: {output}")
        document = Document()
        ensure_styles(document, normalize_builtins=True)
        configure_document(
            document,
            {
                "page_size": "A4",
                "header": "",
                "footer": "",
                "page_numbers": True,
            },
            preserve_template_layout=False,
        )
        set_core_properties(
            document,
            {
                "title": "Professional report template",
                "subject": "Neutral KRT DOCX template",
                "author": "",
                "keywords": "",
                "comments": "",
            },
        )
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
            atomic_publish_file(
                temporary_path,
                output,
                overwrite=args.overwrite,
                label="template",
            )
        finally:
            if temporary_path.exists():
                temporary_path.unlink()
        print(json.dumps({"output": str(output), "status": "created"}, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
