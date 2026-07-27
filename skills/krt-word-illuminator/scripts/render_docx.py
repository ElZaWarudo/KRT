#!/usr/bin/env python3
"""Render DOCX to PDF and one PNG per page for mandatory visual QA."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=144)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--check-tools", action="store_true")
    return parser.parse_args()


def find_renderer() -> str | None:
    return shutil.which("libreoffice") or shutil.which("soffice")


def rasterize_with_pdftoppm(pdf: Path, output_dir: Path, dpi: int) -> list[Path]:
    command = shutil.which("pdftoppm")
    if not command:
        return []
    prefix = output_dir / "page"
    subprocess.run(
        [command, "-png", "-r", str(dpi), str(pdf), str(prefix)],
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted(output_dir.glob("page-*.png"), key=lambda item: int(item.stem.split("-")[-1]))


def rasterize_with_fitz(pdf: Path, output_dir: Path, dpi: int) -> list[Path]:
    try:
        import fitz
    except ImportError:
        return []
    scale = dpi / 72
    matrix = fitz.Matrix(scale, scale)
    pages = []
    with fitz.open(pdf) as document:
        for index, page in enumerate(document, start=1):
            output = output_dir / f"page-{index}.png"
            page.get_pixmap(matrix=matrix, alpha=False).save(output)
            pages.append(output)
    return pages


def main() -> int:
    args = parse_args()
    renderer = find_renderer()
    pdftoppm = shutil.which("pdftoppm")
    try:
        import fitz  # noqa: F401

        fitz_available = True
    except ImportError:
        fitz_available = False

    tools = {
        "libreoffice": renderer,
        "pdftoppm": pdftoppm,
        "pymupdf": fitz_available,
    }
    if args.check_tools:
        print(json.dumps({"tools": tools}, indent=2))
        return 0 if renderer and (pdftoppm or fitz_available) else 1

    try:
        source = args.document.resolve()
        output_dir = args.output_dir.resolve()
        if not source.is_file():
            raise FileNotFoundError(f"Document not found: {source}")
        if not renderer:
            raise RuntimeError("LibreOffice/soffice is required for DOCX rendering")
        if not (pdftoppm or fitz_available):
            raise RuntimeError("pdftoppm or PyMuPDF is required for PNG page rendering")
        if output_dir.exists() and any(output_dir.iterdir()) and not args.overwrite:
            raise FileExistsError(
                f"Output directory is not empty; use --overwrite: {output_dir}"
            )
        output_dir.mkdir(parents=True, exist_ok=True)
        if args.overwrite:
            for old in output_dir.glob("page-*.png"):
                old.unlink()
            for old in (output_dir / "render-report.json", output_dir / f"{source.stem}.pdf"):
                if old.exists():
                    old.unlink()

        with tempfile.TemporaryDirectory(prefix="krt-word-render-") as temporary:
            temp_dir = Path(temporary)
            completed = subprocess.run(
                [
                    renderer,
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(temp_dir),
                    str(source),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )
            pdf = temp_dir / f"{source.stem}.pdf"
            if completed.returncode != 0 or not pdf.is_file():
                raise RuntimeError(
                    "LibreOffice conversion failed: "
                    + (completed.stderr.strip() or completed.stdout.strip())
                )
            final_pdf = output_dir / pdf.name
            shutil.copy2(pdf, final_pdf)

        pages = rasterize_with_pdftoppm(final_pdf, output_dir, args.dpi)
        rasterizer = "pdftoppm"
        if not pages:
            pages = rasterize_with_fitz(final_pdf, output_dir, args.dpi)
            rasterizer = "PyMuPDF"
        if not pages:
            raise RuntimeError("PDF rasterization produced no pages")

        report = {
            "document": str(source),
            "pdf": str(final_pdf),
            "pages": len(pages),
            "page_images": [str(path) for path in pages],
            "dpi": args.dpi,
            "renderer": renderer,
            "rasterizer": rasterizer,
            "visual_qa": "pending_manual_inspection",
            "required_inspected_pages": list(range(1, len(pages) + 1)),
        }
        report_path = output_dir / "render-report.json"
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        report["report"] = str(report_path)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc), "tools": tools}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

