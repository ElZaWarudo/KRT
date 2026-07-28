#!/usr/bin/env python3
"""Render DOCX to PDF and one PNG per page for mandatory visual QA."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SKILL_DIR))

from lib.package_safety import admitted_docx, sha256_file  # noqa: E402
from lib.path_safety import resolve_output_path  # noqa: E402

RENDER_MARKER = ".krt-word-render.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=144)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--check-tools", action="store_true")
    parser.add_argument(
        "--allow-networked-render",
        action="store_true",
        help="Allow a non-final preview when network namespace isolation is unavailable.",
    )
    return parser.parse_args()


def find_renderer() -> str | None:
    return shutil.which("libreoffice") or shutil.which("soffice")


def network_isolation_prefix() -> list[str] | None:
    unshare = shutil.which("unshare")
    if not unshare:
        return None
    candidates = [
        [unshare, "--net", "--"],
        [unshare, "--user", "--map-root-user", "--net", "--"],
    ]
    for prefix in candidates:
        try:
            completed = subprocess.run(
                [*prefix, "true"],
                check=False,
                capture_output=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if completed.returncode == 0:
            return prefix
    return None


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


def publish_render_directory(
    staging: Path,
    output_dir: Path,
    *,
    overwrite: bool,
) -> None:
    """Publish a complete render set, restoring prior evidence on swap failure."""
    validate_managed_render_directory(staging)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    backup: Path | None = None
    if output_dir.exists():
        if not output_dir.is_dir():
            raise ValueError("Render output path exists and is not a directory")
        if not overwrite:
            raise FileExistsError(
                f"Render output directory already exists; use --overwrite: {output_dir}"
            )
        validate_managed_render_directory(output_dir)
        backup = Path(
            tempfile.mkdtemp(
                dir=output_dir.parent,
                prefix=f".{output_dir.name}.previous.",
            )
        )
        backup.rmdir()
        output_dir.replace(backup)
    try:
        staging.replace(output_dir)
    except Exception:
        if backup is not None and not output_dir.exists():
            backup.replace(output_dir)
        raise
    if backup is not None:
        shutil.rmtree(backup)


def write_render_marker(directory: Path) -> None:
    managed_files = sorted(
        path.name
        for path in directory.iterdir()
        if path.is_file() and path.name != RENDER_MARKER
    )
    marker = {
        "format": "krt-word-render-directory",
        "version": 1,
        "managed_files": managed_files,
    }
    (directory / RENDER_MARKER).write_text(
        json.dumps(marker, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def validate_managed_render_directory(directory: Path) -> None:
    marker_path = directory / RENDER_MARKER
    if not marker_path.is_file() or marker_path.is_symlink():
        raise ValueError(
            "Refusing to replace a directory not owned by krt-word-illuminator"
        )
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("Render directory ownership marker is invalid") from error
    managed_files = marker.get("managed_files")
    if (
        marker.get("format") != "krt-word-render-directory"
        or marker.get("version") != 1
        or not isinstance(managed_files, list)
        or not all(
            isinstance(name, str)
            and name
            and name == Path(name).name
            and name != RENDER_MARKER
            for name in managed_files
        )
        or len(set(managed_files)) != len(managed_files)
    ):
        raise ValueError("Render directory ownership marker is invalid")
    actual_entries = {path.name for path in directory.iterdir()}
    expected_entries = {RENDER_MARKER, *managed_files}
    if actual_entries != expected_entries or any(
        not (directory / name).is_file()
        or (directory / name).is_symlink()
        for name in managed_files
    ):
        raise ValueError(
            "Refusing to replace render directory with unknown or unsafe entries"
        )


def main() -> int:
    args = parse_args()
    renderer = find_renderer()
    pdftoppm = shutil.which("pdftoppm")
    isolation_prefix = network_isolation_prefix()
    try:
        import fitz  # noqa: F401

        fitz_available = True
    except ImportError:
        fitz_available = False

    tools = {
        "libreoffice": renderer,
        "pdftoppm": pdftoppm,
        "pymupdf": fitz_available,
        "network_isolation": bool(isolation_prefix),
    }
    if args.check_tools:
        print(json.dumps({"tools": tools}, indent=2))
        return (
            0
            if renderer and (pdftoppm or fitz_available) and isolation_prefix
            else 1
        )

    try:
        source_path = args.document.absolute()
        output_dir = resolve_output_path(
            args.output_dir, label="Render output directory"
        )
        if not source_path.is_file():
            raise FileNotFoundError(f"Document not found: {source_path}")
        if not renderer:
            raise RuntimeError("LibreOffice/soffice is required for DOCX rendering")
        if not (pdftoppm or fitz_available):
            raise RuntimeError("pdftoppm or PyMuPDF is required for PNG page rendering")
        if not isolation_prefix and not args.allow_networked_render:
            raise RuntimeError(
                "Network-isolated rendering is unavailable; use "
                "--allow-networked-render only for a non-final preview"
            )
        if output_dir.exists() and not args.overwrite:
            raise FileExistsError(
                f"Render output directory already exists; use --overwrite: {output_dir}"
            )
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        with admitted_docx(source_path) as source, tempfile.TemporaryDirectory(
            dir=output_dir.parent,
            prefix=f".{output_dir.name}.staging.",
        ) as staging_value:
            document_sha256 = sha256_file(source)
            staging = Path(staging_value)
            runtime_dir = staging / ".runtime"
            runtime_dir.mkdir()
            profile_dir = runtime_dir / "libreoffice-profile"
            profile_dir.mkdir()
            runtime_home = runtime_dir / "home"
            runtime_home.mkdir()
            command = [
                renderer,
                f"-env:UserInstallation={profile_dir.as_uri()}",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(runtime_dir),
                str(source),
            ]
            if isolation_prefix:
                command = [*isolation_prefix, *command]
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
                env={
                    "HOME": str(runtime_home),
                    "LANG": os.environ.get("LANG", "C.UTF-8"),
                    "LC_ALL": os.environ.get("LC_ALL", "C.UTF-8"),
                    "PATH": os.environ.get("PATH", ""),
                    "TMPDIR": str(runtime_dir),
                },
            )
            rendered_pdf = runtime_dir / f"{source.stem}.pdf"
            if completed.returncode != 0 or not rendered_pdf.is_file():
                raise RuntimeError(
                    f"LibreOffice conversion failed (exit {completed.returncode})"
                )
            final_pdf = staging / "document.pdf"
            shutil.copy2(rendered_pdf, final_pdf)
            pages = rasterize_with_pdftoppm(final_pdf, staging, args.dpi)
            rasterizer = "pdftoppm"
            if not pages:
                pages = rasterize_with_fitz(final_pdf, staging, args.dpi)
                rasterizer = "PyMuPDF"
            if not pages:
                raise RuntimeError("PDF rasterization produced no pages")
            shutil.rmtree(runtime_dir)

            report = {
                "document_sha256": document_sha256,
                "pdf": final_pdf.name,
                "pdf_sha256": sha256_file(final_pdf),
                "pages": len(pages),
                "page_images": [path.name for path in pages],
                "page_image_sha256": {
                    path.name: sha256_file(path) for path in pages
                },
                "dpi": args.dpi,
                "renderer": Path(renderer).name,
                "rasterizer": rasterizer,
                "network_isolation": bool(isolation_prefix),
                "network_isolation_method": (
                    "unshare-network-namespace"
                    if isolation_prefix
                    else "explicit-networked-preview"
                ),
                "network_isolation_evidence": "producer-asserted",
                "visual_qa": "pending_manual_inspection",
                "required_inspected_pages": list(range(1, len(pages) + 1)),
            }
            report_path = staging / "render-report.json"
            report_path.write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            write_render_marker(staging)
            publish_render_directory(
                staging,
                output_dir,
                overwrite=args.overwrite,
            )

        report["report"] = "render-report.json"
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc), "tools": tools}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
