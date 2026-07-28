"""Bounded, offline DOCX package admission checks."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
import struct
import tempfile
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from xml.etree import ElementTree as ET


class PackageSafetyError(ValueError):
    """Raised when an OOXML package is unsafe for local processing."""


@dataclass(frozen=True)
class PackageLimits:
    max_package_bytes: int = 96 * 1024 * 1024
    max_central_directory_bytes: int = 8 * 1024 * 1024
    max_members: int = 1_000
    max_compressed_bytes: int = 64 * 1024 * 1024
    max_uncompressed_bytes: int = 256 * 1024 * 1024
    max_member_bytes: int = 64 * 1024 * 1024
    max_compression_ratio: int = 100
    min_ratio_member_bytes: int = 1024 * 1024

    @classmethod
    def from_environment(cls) -> "PackageLimits":
        values = {}
        for field in cls.__dataclass_fields__:
            setting = f"KRT_WORD_{field.upper()}"
            value = os.environ.get(setting)
            if value is None:
                continue
            try:
                parsed = int(value)
            except ValueError as error:
                raise PackageSafetyError(
                    f"package-safety:invalid-limit:{setting}"
                ) from error
            if parsed <= 0:
                raise PackageSafetyError(
                    f"package-safety:invalid-limit:{setting}"
                )
            values[field] = parsed
        return cls(**values)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _unsafe_name(name: str) -> bool:
    return (
        not name
        or "\x00" in name
        or "\\" in name
        or name.startswith("/")
        or bool(re.match(r"^[A-Za-z]:", name))
        or any(part in {"", ".", ".."} for part in name.rstrip("/").split("/"))
    )


def _blocked_part(name: str) -> str | None:
    normalized = name.casefold()
    if normalized in {"word/vbaproject.bin", "word/vbadata.xml"}:
        return "macros"
    if normalized.startswith("word/activex/"):
        return "activex"
    if normalized.startswith("word/embeddings/") or "oleobject" in normalized:
        return "ole-embeddings"
    return None


def _has_blocked_relationship(data: bytes) -> bool:
    try:
        root = ET.fromstring(data)
    except ET.ParseError as error:
        raise PackageSafetyError(
            "package-safety:invalid-relationships-xml"
        ) from error
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "Relationship":
            continue
        relationship_type = element.attrib.get("Type", "").casefold()
        target = element.attrib.get("Target", "")
        active_suffixes = (
            "/activexcontrol",
            "/afchunk",
            "/attachedtemplate",
            "/control",
            "/oleobject",
            "/package",
            "/vbaproject",
        )
        if relationship_type.endswith(active_suffixes):
            return True
        sensitive_targets = {
            "/custom-properties": re.compile(
                r"(?:^|/)docProps/custom\.xml$", re.IGNORECASE
            ),
            "/extended-properties": re.compile(
                r"(?:^|/)docProps/app\.xml$", re.IGNORECASE
            ),
            "/comments": re.compile(
                r"(?:^|/)comments\d*\.xml$", re.IGNORECASE
            ),
            "/commentsextended": re.compile(
                r"(?:^|/)commentsExtended\d*\.xml$", re.IGNORECASE
            ),
            "/commentsids": re.compile(
                r"(?:^|/)commentsIds\d*\.xml$", re.IGNORECASE
            ),
            "/commentsextensible": re.compile(
                r"(?:^|/)commentsExtensible\d*\.xml$", re.IGNORECASE
            ),
            "/people": re.compile(r"(?:^|/)people\d*\.xml$", re.IGNORECASE),
        }
        for suffix, expected in sensitive_targets.items():
            if relationship_type.endswith(suffix) and not expected.search(target):
                return True
        if element.attrib.get("TargetMode", "").casefold() != "external":
            continue
        if relationship_type.endswith("/hyperlink"):
            continue
        return True
    return False


def _validate_content_types(data: bytes) -> None:
    try:
        root = ET.fromstring(data)
    except ET.ParseError as error:
        raise PackageSafetyError(
            "package-safety:invalid-content-types-xml"
        ) from error
    declarations = [
        (
            element.attrib.get("ContentType", "").casefold(),
            element.attrib.get("PartName", ""),
        )
        for element in root
        if element.attrib.get("ContentType")
    ]
    content_types = [content_type for content_type, _part_name in declarations]
    blocked_tokens = ("macroenabled", "vbaproject", "activex", "oleobject")
    if any(
        token in content_type
        for content_type in content_types
        for token in blocked_tokens
    ):
        raise PackageSafetyError("package-safety:blocked-active-content-type")
    if not any(
        content_type.endswith(".document.main+xml")
        for content_type in content_types
    ):
        raise PackageSafetyError("package-safety:not-a-docx-content-type")
    for content_type, part_name in declarations:
        normalized_part = part_name.lstrip("/")
        if (
            "custom-properties" in content_type
            and normalized_part.casefold() != "docprops/custom.xml"
        ):
            raise PackageSafetyError(
                "package-safety:noncanonical-sensitive-part"
            )
        if (
            "extended-properties" in content_type
            and normalized_part.casefold() != "docprops/app.xml"
        ):
            raise PackageSafetyError(
                "package-safety:noncanonical-sensitive-part"
            )
        if "comments" in content_type and not re.fullmatch(
            r"word/comments(?:Extended|Ids|Extensible)?\d*\.xml",
            normalized_part,
            flags=re.IGNORECASE,
        ):
            raise PackageSafetyError(
                "package-safety:noncanonical-sensitive-part"
            )


def _preflight_archive_envelope(path: Path, limits: PackageLimits) -> None:
    try:
        physical_size = path.stat().st_size
        if physical_size > limits.max_package_bytes:
            raise PackageSafetyError("package-safety:physical-size-limit")
        with path.open("rb") as handle:
            tail_size = min(physical_size, 65_557)
            handle.seek(physical_size - tail_size)
            tail = handle.read(tail_size)
    except PackageSafetyError:
        raise
    except OSError as error:
        raise PackageSafetyError("package-safety:invalid-zip-package") from error

    marker = b"PK\x05\x06"
    index = tail.rfind(marker)
    if index < 0 or len(tail) - index < 22:
        raise PackageSafetyError("package-safety:missing-end-record")
    (
        _signature,
        disk_number,
        central_disk,
        entries_on_disk,
        entries_total,
        central_size,
        central_offset,
        comment_length,
    ) = struct.unpack_from("<4s4H2LH", tail, index)
    if disk_number or central_disk or entries_on_disk != entries_total:
        raise PackageSafetyError("package-safety:multi-disk-zip")
    if entries_total == 0xFFFF or central_size == 0xFFFFFFFF:
        raise PackageSafetyError("package-safety:zip64-not-supported")
    if entries_total > limits.max_members:
        raise PackageSafetyError("package-safety:member-count-limit")
    if central_size > limits.max_central_directory_bytes:
        raise PackageSafetyError("package-safety:central-directory-size-limit")
    end_record_offset = physical_size - tail_size + index
    if (
        end_record_offset + 22 + comment_length != physical_size
        or central_offset + central_size > end_record_offset
    ):
        raise PackageSafetyError("package-safety:invalid-end-record")


def preflight_docx(
    path: Path,
    *,
    limits: PackageLimits | None = None,
    require_docx_extension: bool = True,
) -> dict[str, int]:
    """Reject unsafe packages before any OOXML parser or renderer sees them."""
    limits = limits or PackageLimits.from_environment()
    if require_docx_extension and path.suffix.casefold() != ".docx":
        raise PackageSafetyError("package-safety:docx-extension-required")
    _preflight_archive_envelope(path, limits)
    try:
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            if len(members) > limits.max_members:
                raise PackageSafetyError("package-safety:member-count-limit")

            names: set[str] = set()
            members_by_name: dict[str, zipfile.ZipInfo] = {}
            compressed = 0
            uncompressed = 0
            for info in members:
                name = info.filename
                normalized = name.casefold()
                if _unsafe_name(name):
                    raise PackageSafetyError("package-safety:unsafe-member-name")
                if normalized in names:
                    raise PackageSafetyError("package-safety:duplicate-member")
                names.add(normalized)
                members_by_name[normalized] = info
                if info.flag_bits & 0x1:
                    raise PackageSafetyError("package-safety:encrypted-member")
                blocked = _blocked_part(name)
                if blocked:
                    raise PackageSafetyError(f"package-safety:blocked-{blocked}")
                if info.file_size > limits.max_member_bytes:
                    raise PackageSafetyError("package-safety:member-size-limit")
                compressed += info.compress_size
                uncompressed += info.file_size
                if compressed > limits.max_compressed_bytes:
                    raise PackageSafetyError("package-safety:compressed-size-limit")
                if uncompressed > limits.max_uncompressed_bytes:
                    raise PackageSafetyError("package-safety:uncompressed-size-limit")
                if info.file_size and info.compress_size == 0:
                    raise PackageSafetyError("package-safety:compression-ratio-limit")
                if (
                    info.file_size >= limits.min_ratio_member_bytes
                    and info.compress_size
                    and info.file_size / info.compress_size
                    > limits.max_compression_ratio
                ):
                    raise PackageSafetyError("package-safety:compression-ratio-limit")

            required = {"[content_types].xml", "word/document.xml"}
            if not required.issubset(names):
                raise PackageSafetyError("package-safety:not-a-docx-package")
            _validate_content_types(
                archive.read(members_by_name["[content_types].xml"])
            )
            for info in members:
                if (
                    info.filename.casefold().endswith(".rels")
                    and _has_blocked_relationship(archive.read(info))
                ):
                    raise PackageSafetyError("package-safety:blocked-relationship")
    except PackageSafetyError:
        raise
    except (OSError, zipfile.BadZipFile, RuntimeError) as error:
        raise PackageSafetyError("package-safety:invalid-zip-package") from error
    return {
        "members": len(members),
        "compressed_bytes": compressed,
        "uncompressed_bytes": uncompressed,
    }


@contextmanager
def admitted_docx(path: Path) -> Iterator[Path]:
    """Yield a private immutable snapshot admitted from one no-follow descriptor."""
    limits = PackageLimits.from_environment()
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise PackageSafetyError("package-safety:source-open-failed") from error
    temporary_path: Path | None = None
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise PackageSafetyError("package-safety:source-not-regular-file")
        if metadata.st_size > limits.max_package_bytes:
            raise PackageSafetyError("package-safety:physical-size-limit")
        with os.fdopen(descriptor, "rb", closefd=True) as source:
            descriptor = -1
            with tempfile.NamedTemporaryFile(
                prefix=f"krt-word-{path.stem}-",
                suffix=".docx",
                delete=False,
            ) as temporary:
                shutil.copyfileobj(source, temporary, length=1024 * 1024)
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_path = Path(temporary.name)
            final_metadata = os.fstat(source.fileno())
        if (
            final_metadata.st_size != metadata.st_size
            or final_metadata.st_mtime_ns != metadata.st_mtime_ns
            or final_metadata.st_ctime_ns != metadata.st_ctime_ns
            or temporary_path.stat().st_size != metadata.st_size
        ):
            raise PackageSafetyError("package-safety:source-changed-during-admission")
        preflight_docx(temporary_path, limits=limits)
        yield temporary_path
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
