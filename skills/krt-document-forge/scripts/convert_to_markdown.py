#!/usr/bin/env python3
"""Convert PDF and DOCX files into harness-ready Markdown."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import venv
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}
NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
RELATIONSHIP_NAMESPACE = "http://schemas.openxmlformats.org/package/2006/relationships"
PYTHON_DEPENDENCIES = {
    "pdf": ["pypdf", "pdfplumber"],
    "pdf-images": ["PyMuPDF"],
}
DEFAULT_VENV = Path(".krt/document-forge/venv")


class ConversionError(Exception):
    pass


@dataclass
class ConversionResult:
    source: Path
    output: Path | None
    method: str | None
    status: str
    message: str
    assets: list[Path]
    source_sha256: str | None = None
    output_sha256: str | None = None


def slugify(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    value = re.sub(r"-{2,}", "-", value).strip("-._")
    return value or "document"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def qname(name: str) -> str:
    prefix, local = name.split(":", 1)
    return f"{{{NAMESPACES[prefix]}}}{local}"


def local_venv_site_packages(venv_dir: Path) -> Path:
    version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    return venv_dir / "lib" / version / "site-packages"


def ensure_python_dependencies(groups: Iterable[str], venv_dir: Path) -> None:
    packages: list[str] = []
    for group in groups:
        packages.extend(PYTHON_DEPENDENCIES.get(group, []))
    if not packages:
        return

    site_packages = local_venv_site_packages(venv_dir)
    if not site_packages.exists():
        venv.EnvBuilder(with_pip=True).create(venv_dir)

    python = venv_dir / ("Scripts" if os.name == "nt" else "bin") / "python"
    subprocess.run(
        [str(python), "-m", "pip", "install", "--upgrade", *packages],
        check=True,
    )
    sys.path.insert(0, str(site_packages))


def add_local_venv_to_path(venv_dir: Path) -> None:
    site_packages = local_venv_site_packages(venv_dir)
    if site_packages.exists() and str(site_packages) not in sys.path:
        sys.path.insert(0, str(site_packages))


def default_images_dir(output_dir: Path) -> Path:
    if output_dir.name == "sources":
        return output_dir.parent / "images"
    return output_dir / "images"


def expected_output_path(source: Path, output_dir: Path) -> Path:
    return output_dir / f"{slugify(source.stem)}.md"


def source_image_dir(source: Path, image_dir: Path) -> Path:
    return image_dir / slugify(source.stem)


def markdown_link(output: Path, asset: Path) -> str:
    return os.path.relpath(asset, output.parent).replace(os.sep, "/")


def remove_existing_assets(source: Path, image_dir: Path) -> None:
    target = source_image_dir(source, image_dir)
    if target.exists():
        shutil.rmtree(target)


def xml_text(element: ET.Element) -> str:
    parts: list[str] = []
    for node in element.iter():
        if node.tag == qname("w:t") and node.text:
            parts.append(node.text)
        elif node.tag == qname("w:tab"):
            parts.append("\t")
        elif node.tag in {qname("w:br"), qname("w:cr")}:
            parts.append("\n")
    return "".join(parts).strip()


def read_docx_styles(archive: zipfile.ZipFile) -> dict[str, str]:
    try:
        raw = archive.read("word/styles.xml")
    except KeyError:
        return {}

    root = ET.fromstring(raw)
    styles: dict[str, str] = {}
    for style in root.findall("w:style", NAMESPACES):
        style_id = style.attrib.get(qname("w:styleId"))
        name = style.find("w:name", NAMESPACES)
        if style_id and name is not None:
            styles[style_id] = name.attrib.get(qname("w:val"), style_id)
    return styles


def read_docx_relationships(archive: zipfile.ZipFile) -> dict[str, str]:
    try:
        raw = archive.read("word/_rels/document.xml.rels")
    except KeyError:
        return {}

    root = ET.fromstring(raw)
    relationships: dict[str, str] = {}
    for relationship in root.findall(f"{{{RELATIONSHIP_NAMESPACE}}}Relationship"):
        relationship_id = relationship.attrib.get("Id")
        target = relationship.attrib.get("Target")
        relationship_type = relationship.attrib.get("Type", "")
        if relationship_id and target and relationship_type.endswith("/image"):
            relationships[relationship_id] = target
    return relationships


def paragraph_style(paragraph: ET.Element, styles: dict[str, str]) -> str | None:
    style = paragraph.find("w:pPr/w:pStyle", NAMESPACES)
    if style is None:
        return None
    style_id = style.attrib.get(qname("w:val"))
    if not style_id:
        return None
    return styles.get(style_id, style_id)


def heading_level(style_name: str | None) -> int | None:
    if not style_name:
        return None
    normalized = style_name.lower().replace(" ", "")
    match = re.search(r"(heading|titulo|título)([1-6])", normalized)
    if match:
        return int(match.group(2))
    return None


def is_list_paragraph(paragraph: ET.Element) -> bool:
    return paragraph.find("w:pPr/w:numPr", NAMESPACES) is not None


def image_relationship_ids(element: ET.Element) -> list[str]:
    relationship_ids: list[str] = []
    for image in element.findall(".//a:blip", NAMESPACES):
        relationship_id = image.attrib.get(qname("r:embed"))
        if relationship_id:
            relationship_ids.append(relationship_id)
    return relationship_ids


def docx_target_path(target: str) -> str:
    normalized = target.lstrip("/")
    if normalized.startswith("word/"):
        return normalized
    return f"word/{normalized}"


def save_docx_images(
    archive: zipfile.ZipFile,
    relationship_ids: Iterable[str],
    relationships: dict[str, str],
    image_dir: Path,
    output: Path,
    source_slug: str,
    start_index: int,
) -> tuple[list[str], list[Path], int]:
    blocks: list[str] = []
    assets: list[Path] = []
    image_dir.mkdir(parents=True, exist_ok=True)
    index = start_index

    for relationship_id in relationship_ids:
        target = relationships.get(relationship_id)
        if not target:
            continue
        archive_path = docx_target_path(target)
        try:
            data = archive.read(archive_path)
        except KeyError:
            continue

        extension = Path(target).suffix or ".bin"
        index += 1
        asset = image_dir / f"{source_slug}-image-{index:03d}{extension}"
        asset.write_bytes(data)
        assets.append(asset)
        blocks.append(f"![{source_slug} image {index:03d}]({markdown_link(output, asset)})")

    return blocks, assets, index


def docx_table_to_markdown(table: ET.Element) -> str:
    rows: list[list[str]] = []
    for row in table.findall("w:tr", NAMESPACES):
        cells = []
        for cell in row.findall("w:tc", NAMESPACES):
            cell_text = " ".join(
                xml_text(paragraph)
                for paragraph in cell.findall("w:p", NAMESPACES)
                if xml_text(paragraph)
            )
            cells.append(cell_text.replace("|", "\\|"))
        if cells:
            rows.append(cells)

    if not rows:
        return ""

    width = max(len(row) for row in rows)
    padded = [row + [""] * (width - len(row)) for row in rows]
    header = padded[0]
    separator = ["---"] * width
    body = padded[1:] or [[""] * width]

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def extract_docx(path: Path, output: Path, image_dir: Path | None) -> tuple[str, str, list[Path]]:
    try:
        with zipfile.ZipFile(path) as archive:
            styles = read_docx_styles(archive)
            relationships = read_docx_relationships(archive)
            root = ET.fromstring(archive.read("word/document.xml"))

            body = root.find("w:body", NAMESPACES)
            if body is None:
                raise ConversionError("DOCX document body was not found")

            blocks: list[str] = []
            assets: list[Path] = []
            image_index = 0
            source_slug = slugify(path.stem)
            source_image_dir = image_dir / source_slug if image_dir else None

            for child in body:
                if child.tag == qname("w:p"):
                    text = xml_text(child)
                    if text:
                        level = heading_level(paragraph_style(child, styles))
                        if level:
                            blocks.append(f"{'#' * min(level + 1, 6)} {text}")
                        elif is_list_paragraph(child):
                            blocks.append(f"- {text}")
                        else:
                            blocks.append(text)
                    if source_image_dir:
                        image_blocks, image_assets, image_index = save_docx_images(
                            archive,
                            image_relationship_ids(child),
                            relationships,
                            source_image_dir,
                            output,
                            source_slug,
                            image_index,
                        )
                        blocks.extend(image_blocks)
                        assets.extend(image_assets)
                elif child.tag == qname("w:tbl"):
                    table = docx_table_to_markdown(child)
                    if table:
                        blocks.append(table)
                    if source_image_dir:
                        image_blocks, image_assets, image_index = save_docx_images(
                            archive,
                            image_relationship_ids(child),
                            relationships,
                            source_image_dir,
                            output,
                            source_slug,
                            image_index,
                        )
                        blocks.extend(image_blocks)
                        assets.extend(image_assets)
    except (KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        raise ConversionError(f"cannot read DOCX structure: {exc}") from exc

    text = "\n\n".join(blocks).strip()
    if not text and not assets:
        raise ConversionError("DOCX extraction produced no readable text")
    return text, "docx-stdlib", assets


def extract_pdf_with_pdftotext(path: Path) -> str | None:
    if shutil.which("pdftotext") is None:
        return None
    completed = subprocess.run(
        ["pdftotext", "-layout", str(path), "-"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise ConversionError(completed.stderr.strip() or "pdftotext failed")
    return completed.stdout.strip()


def extract_pdf_with_pypdf(path: Path) -> str | None:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        return None

    reader = PdfReader(str(path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(f"<!-- page: {index} -->\n\n{text}")
    return "\n\n".join(pages).strip()


def extract_pdf_with_pdfplumber(path: Path) -> str | None:
    try:
        import pdfplumber  # type: ignore
    except ImportError:
        return None

    pages = []
    with pdfplumber.open(path) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            text = (page.extract_text(layout=True) or "").strip()
            if text:
                pages.append(f"<!-- page: {index} -->\n\n{text}")
    return "\n\n".join(pages).strip()


def extract_pdf_images(path: Path, image_dir: Path, output: Path) -> tuple[list[str], list[Path], str | None]:
    try:
        import fitz  # type: ignore
    except ImportError:
        return [], [], "PDF image extraction skipped: PyMuPDF is not installed; rerun with --install-missing"

    source_slug = slugify(path.stem)
    source_image_dir = image_dir / source_slug
    source_image_dir.mkdir(parents=True, exist_ok=True)
    blocks: list[str] = []
    assets: list[Path] = []
    image_index = 0

    try:
        with fitz.open(path) as document:
            for page_index in range(len(document)):
                page = document[page_index]
                for image_info in page.get_images(full=True):
                    xref = image_info[0]
                    image = document.extract_image(xref)
                    data = image.get("image")
                    if not data:
                        continue
                    extension = "." + image.get("ext", "bin").lstrip(".")
                    image_index += 1
                    asset = source_image_dir / (
                        f"{source_slug}-page-{page_index + 1:03d}-image-{image_index:03d}{extension}"
                    )
                    asset.write_bytes(data)
                    assets.append(asset)
                    blocks.append(
                        f"![{source_slug} page {page_index + 1} image {image_index:03d}]"
                        f"({markdown_link(output, asset)})"
                    )
    except Exception as exc:
        return blocks, assets, f"PDF image extraction failed: {exc}"

    return blocks, assets, None


def extract_pdf(path: Path) -> tuple[str, str]:
    extractors = [
        ("pdftotext", extract_pdf_with_pdftotext),
        ("pypdf", extract_pdf_with_pypdf),
        ("pdfplumber", extract_pdf_with_pdfplumber),
    ]
    missing: list[str] = []
    failures: list[str] = []
    for method, extractor in extractors:
        try:
            text = extractor(path)
        except Exception as exc:
            failures.append(f"{method}: {exc}")
            continue
        if text is None:
            missing.append(method)
            continue
        if text:
            return text, method

    if len(missing) == len(extractors):
        raise ConversionError(
            "no PDF text extractor available; install Poppler pdftotext, pypdf, or pdfplumber"
        )
    detail = f" Extractor failures: {'; '.join(failures)}" if failures else ""
    raise ConversionError(
        f"PDF extraction produced no readable text. If the content is graphical, rerun with --extract-images "
        f"to reference embedded images as assets.{detail}"
    )


def markdown_document(source: Path, source_type: str, method: str, body: str) -> str:
    converted_at = utc_now()
    title = source.stem.replace("_", " ").replace("-", " ").strip() or source.name
    frontmatter = {
        "source_path": str(source),
        "source_type": source_type,
        "converted_at": converted_at,
        "converter": "krt-document-forge",
        "conversion_method": method,
    }
    lines = ["---"]
    lines.extend(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in frontmatter.items())
    lines.extend(["---", "", f"# {title}", "", body.strip(), ""])
    return "\n".join(lines)


def collect_inputs(paths: Iterable[Path], recursive: bool) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            iterator = path.rglob("*") if recursive else path.iterdir()
            files.extend(item for item in iterator if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS)
        elif path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)
        elif path.exists():
            raise ConversionError(f"unsupported input type: {path}")
        else:
            raise ConversionError(f"input not found: {path}")
    return sorted(set(files))


def convert_file(
    source: Path,
    output_dir: Path,
    image_dir: Path | None,
    overwrite: bool,
    extract_images: bool,
    clean_assets: bool,
) -> ConversionResult:
    output = expected_output_path(source, output_dir)
    source_hash = sha256_file(source)
    if output.exists() and not overwrite:
        return ConversionResult(
            source,
            output,
            None,
            "skipped",
            "output exists; pass --overwrite to replace",
            [],
            source_hash,
            sha256_file(output),
        )

    try:
        assets: list[Path] = []
        warnings: list[str] = []
        if clean_assets and extract_images and image_dir:
            remove_existing_assets(source, image_dir)

        if source.suffix.lower() == ".docx":
            body, method, assets = extract_docx(source, output, image_dir if extract_images else None)
            source_type = "docx"
        elif source.suffix.lower() == ".pdf":
            body, method = extract_pdf(source)
            source_type = "pdf"
            if extract_images and image_dir:
                image_blocks, image_assets, image_warning = extract_pdf_images(source, image_dir, output)
                if image_blocks:
                    body = "\n\n".join([body, "## Extracted Images", *image_blocks]).strip()
                    method = f"{method}+pymupdf-images"
                assets.extend(image_assets)
                if image_warning:
                    warnings.append(image_warning)
        else:
            raise ConversionError(f"unsupported extension: {source.suffix}")

        output_dir.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown_document(source, source_type, method, body), encoding="utf-8")
        message = "ok" if not warnings else "ok; " + "; ".join(warnings)
        return ConversionResult(source, output, method, "converted", message, assets, source_hash, sha256_file(output))
    except ConversionError as exc:
        return ConversionResult(source, output, None, "failed", str(exc), [], source_hash, None)


def result_payload(result: ConversionResult) -> dict[str, object]:
    return {
        "source": str(result.source),
        "source_sha256": result.source_sha256,
        "output": str(result.output) if result.output else None,
        "output_sha256": result.output_sha256,
        "method": result.method,
        "status": result.status,
        "message": result.message,
        "assets": [
            {
                "path": str(asset),
                "sha256": sha256_file(asset) if asset.exists() else None,
            }
            for asset in result.assets
        ],
    }


def manifest_payload(
    results: list[ConversionResult],
    output_dir: Path,
    image_dir: Path,
    extract_images: bool,
) -> dict[str, object]:
    return {
        "schema_version": 2,
        "generated_at": utc_now(),
        "converter": "krt-document-forge",
        "output_dir": str(output_dir),
        "images_dir": str(image_dir),
        "extract_images": extract_images,
        "files": [result_payload(result) for result in results],
    }


def load_manifest(path: Path | None) -> dict[str, dict[str, object]]:
    if not path:
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConversionError(f"cannot read manifest: {exc}") from exc

    entries = raw.get("files", raw) if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        raise ConversionError("manifest must be a list or an object with a files list")

    by_source: dict[str, dict[str, object]] = {}
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get("source"), str):
            by_source[str(entry["source"])] = entry
    return by_source


def markdown_image_links(markdown: str) -> list[str]:
    links = []
    for match in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", markdown):
        link = match.group(1).strip()
        if link and not re.match(r"^(https?:|data:|#)", link):
            links.append(link.split("#", 1)[0])
    return links


def check_file(source: Path, output_dir: Path, manifest_entry: dict[str, object] | None) -> ConversionResult:
    output = expected_output_path(source, output_dir)
    source_hash = sha256_file(source) if source.exists() else None
    output_hash = sha256_file(output) if output.exists() else None
    failures: list[str] = []
    assets: list[Path] = []

    if not output.exists():
        failures.append("output Markdown is missing")
    elif output.stat().st_size == 0:
        failures.append("output Markdown is empty")
    else:
        markdown = output.read_text(encoding="utf-8")
        for link in markdown_image_links(markdown):
            asset = (output.parent / link).resolve()
            assets.append(asset)
            if not asset.exists():
                failures.append(f"linked image is missing: {link}")

    if manifest_entry:
        if manifest_entry.get("source_sha256") and manifest_entry.get("source_sha256") != source_hash:
            failures.append("source hash differs from manifest")
        if manifest_entry.get("output_sha256") and manifest_entry.get("output_sha256") != output_hash:
            failures.append("output hash differs from manifest")
        for asset_entry in manifest_entry.get("assets", []):
            if isinstance(asset_entry, str):
                asset = Path(asset_entry)
                expected_hash = None
            elif isinstance(asset_entry, dict) and isinstance(asset_entry.get("path"), str):
                asset = Path(str(asset_entry["path"]))
                expected_hash = asset_entry.get("sha256")
            else:
                continue
            if asset not in assets:
                assets.append(asset)
            if not asset.exists():
                failures.append(f"manifest asset is missing: {asset}")
            elif expected_hash and expected_hash != sha256_file(asset):
                failures.append(f"manifest asset hash differs: {asset}")

    status = "failed" if failures else "checked"
    message = "; ".join(failures) if failures else "ok"
    return ConversionResult(source, output, None, status, message, assets, source_hash, output_hash)


def check_artifacts(files: list[Path], output_dir: Path, manifest: Path | None) -> list[ConversionResult]:
    manifest_by_source = load_manifest(manifest)
    return [
        check_file(source, output_dir, manifest_by_source.get(str(source)))
        for source in files
    ]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="PDF/DOCX files or directories to convert")
    parser.add_argument("--output-dir", type=Path, default=Path("docs/harnesses/sources"))
    parser.add_argument("--images-dir", type=Path, help="image asset directory; defaults beside the output sources")
    parser.add_argument("--recursive", action="store_true", help="recurse into input directories")
    parser.add_argument("--overwrite", action="store_true", help="replace existing generated Markdown")
    parser.add_argument("--extract-images", action="store_true", help="extract embedded images and link them from Markdown")
    parser.add_argument("--clean-assets", action="store_true", help="remove old image assets for each source before regenerating")
    parser.add_argument("--check", action="store_true", help="validate existing Markdown, image links, and manifest hashes")
    parser.add_argument("--install-missing", action="store_true", help="install optional Python extractors into a local venv")
    parser.add_argument("--dependency-venv", type=Path, default=DEFAULT_VENV, help="local venv for --install-missing")
    parser.add_argument("--manifest", type=Path, help="optional JSON summary path")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        files = collect_inputs(args.inputs, args.recursive)
    except ConversionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if not files:
        print("ERROR: no supported .pdf or .docx files found", file=sys.stderr)
        return 2

    image_dir = args.images_dir or default_images_dir(args.output_dir)
    if args.check:
        try:
            results = check_artifacts(files, args.output_dir, args.manifest)
        except ConversionError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        payload = manifest_payload(results, args.output_dir, image_dir, args.extract_images)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 1 if any(result.status == "failed" for result in results) else 0

    add_local_venv_to_path(args.dependency_venv)
    if args.install_missing:
        groups = []
        if any(path.suffix.lower() == ".pdf" for path in files):
            groups.append("pdf")
        if args.extract_images and any(path.suffix.lower() == ".pdf" for path in files):
            groups.append("pdf-images")
        try:
            ensure_python_dependencies(groups, args.dependency_venv)
        except subprocess.CalledProcessError as exc:
            print(f"ERROR: dependency installation failed: {exc}", file=sys.stderr)
            return 2

    results = [
        convert_file(path, args.output_dir, image_dir, args.overwrite, args.extract_images, args.clean_assets)
        for path in files
    ]
    payload = manifest_payload(results, args.output_dir, image_dir, args.extract_images)

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 1 if any(result.status == "failed" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
