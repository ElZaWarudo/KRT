#!/usr/bin/env python3
"""Contract tests for bounded DOCX package admission."""

from __future__ import annotations

import sys
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lib.package_safety import (
    PackageLimits,
    PackageSafetyError,
    admitted_docx,
    preflight_docx,
)


def write_docx(path: Path, extra: dict[str, bytes] | None = None) -> None:
    parts = {
        "[Content_Types].xml": (
            b"<Types><Override PartName='/word/document.xml' "
            b"ContentType='application/vnd.openxmlformats-officedocument."
            b"wordprocessingml.document.main+xml'/></Types>"
        ),
        "word/document.xml": b"<w:document xmlns:w='urn:test'/>",
    }
    parts.update(extra or {})
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            archive.writestr(name, content)


class PackageSafetyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.work = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_safe_minimal_package_is_admitted(self) -> None:
        path = self.work / "safe.docx"
        write_docx(path)
        self.assertEqual(preflight_docx(path)["members"], 2)

    def test_admitted_snapshot_survives_source_replacement(self) -> None:
        source = self.work / "source.docx"
        replacement = self.work / "replacement.docx"
        write_docx(source)
        write_docx(replacement, {"word/extra.xml": b"replacement"})

        with admitted_docx(source) as snapshot:
            replacement.replace(source)
            with zipfile.ZipFile(snapshot) as archive:
                self.assertNotIn("word/extra.xml", archive.namelist())
            with zipfile.ZipFile(source) as archive:
                self.assertIn("word/extra.xml", archive.namelist())

    def test_admission_rejects_source_symlink(self) -> None:
        target = self.work / "target.docx"
        write_docx(target)
        link = self.work / "link.docx"
        link.symlink_to(target)

        with self.assertRaisesRegex(PackageSafetyError, "source-open-failed"):
            with admitted_docx(link):
                self.fail("symlink source should not be admitted")

    def test_external_relationship_is_rejected(self) -> None:
        path = self.work / "external.docx"
        write_docx(
            path,
            {
                "word/_rels/document.xml.rels": (
                    b"<Relationships><Relationship TargetMode='External' "
                    b"Target='https://example.invalid'/></Relationships>"
                )
            },
        )
        with self.assertRaisesRegex(PackageSafetyError, "blocked-relationship"):
            preflight_docx(path)

    def test_macro_part_is_rejected(self) -> None:
        path = self.work / "macro.docx"
        write_docx(path, {"word/vbaProject.bin": b"macro"})
        with self.assertRaisesRegex(PackageSafetyError, "blocked-macros"):
            preflight_docx(path)

    def test_macro_content_type_is_rejected_without_a_macro_part(self) -> None:
        path = self.work / "macro-content-type.docx"
        write_docx(
            path,
            {
                "[Content_Types].xml": (
                    b"<Types><Override PartName='/word/document.xml' "
                    b"ContentType='application/vnd.ms-word.document."
                    b"macroEnabled.main+xml'/></Types>"
                )
            },
        )
        with self.assertRaisesRegex(PackageSafetyError, "active-content-type"):
            preflight_docx(path)

    def test_encoded_external_relationship_is_rejected(self) -> None:
        path = self.work / "encoded-external.docx"
        write_docx(
            path,
            {
                "word/_rels/document.xml.rels": (
                    b"<Relationships><Relationship TargetMode='&#x45;xternal' "
                    b"Target='https://example.invalid'/></Relationships>"
                )
            },
        )
        with self.assertRaisesRegex(PackageSafetyError, "blocked-relationship"):
            preflight_docx(path)

    def test_external_hyperlink_relationship_is_allowed(self) -> None:
        path = self.work / "hyperlink.docx"
        write_docx(
            path,
            {
                "word/_rels/document.xml.rels": (
                    b"<Relationships><Relationship TargetMode='External' "
                    b"Type='http://schemas.openxmlformats.org/officeDocument/"
                    b"2006/relationships/hyperlink' "
                    b"Target='https://example.invalid'/></Relationships>"
                )
            },
        )
        self.assertEqual(preflight_docx(path)["members"], 3)

    def test_renamed_active_payload_is_rejected_by_relationship_type(self) -> None:
        for relationship_type in ("vbaProject", "oleObject", "activeXControl", "package"):
            with self.subTest(relationship_type=relationship_type):
                path = self.work / f"{relationship_type}.docx"
                write_docx(
                    path,
                    {
                        "word/payload.bin": b"active payload",
                        "word/_rels/document.xml.rels": (
                            b"<Relationships><Relationship "
                            b"Type='http://schemas.microsoft.com/office/2006/"
                            b"relationships/"
                            + relationship_type.encode()
                            + b"' Target='payload.bin'/></Relationships>"
                        ),
                    },
                )
                with self.assertRaisesRegex(
                    PackageSafetyError, "blocked-relationship"
                ):
                    preflight_docx(path)

    def test_renamed_sensitive_parts_are_rejected(self) -> None:
        for relationship_type, target in (
            ("comments", "private-review.xml"),
            ("custom-properties", "docProps/private.xml"),
            ("extended-properties", "docProps/private-app.xml"),
        ):
            with self.subTest(relationship_type=relationship_type):
                path = self.work / f"renamed-{relationship_type}.docx"
                write_docx(
                    path,
                    {
                        "_rels/.rels": (
                            b"<Relationships><Relationship Type='http://schemas."
                            b"openxmlformats.org/officeDocument/2006/relationships/"
                            + relationship_type.encode()
                            + b"' Target='"
                            + target.encode()
                            + b"'/></Relationships>"
                        ),
                        target: b"<private/>",
                    },
                )
                with self.assertRaisesRegex(
                    PackageSafetyError, "blocked-relationship"
                ):
                    preflight_docx(path)

    def test_small_highly_compressible_member_is_allowed(self) -> None:
        path = self.work / "compressible.docx"
        write_docx(path, {"word/long.xml": b"A" * 512_000})
        self.assertEqual(preflight_docx(path)["members"], 3)

    def test_member_and_ratio_limits_are_enforced(self) -> None:
        path = self.work / "ratio.docx"
        write_docx(path, {"word/media/fill.bin": b"A" * 4096})
        limits = PackageLimits(
            max_compression_ratio=2,
            min_ratio_member_bytes=1024,
        )
        with self.assertRaisesRegex(PackageSafetyError, "compression-ratio-limit"):
            preflight_docx(path, limits=limits)
        with self.assertRaisesRegex(PackageSafetyError, "member-count-limit"):
            preflight_docx(path, limits=PackageLimits(max_members=1))
        with self.assertRaisesRegex(PackageSafetyError, "member-size-limit"):
            preflight_docx(path, limits=PackageLimits(max_member_bytes=32))
        with self.assertRaisesRegex(PackageSafetyError, "physical-size-limit"):
            preflight_docx(path, limits=PackageLimits(max_package_bytes=32))

    def test_duplicate_and_unsafe_member_names_are_rejected(self) -> None:
        duplicate = self.work / "duplicate.docx"
        with zipfile.ZipFile(duplicate, "w") as archive:
            archive.writestr(
                "[Content_Types].xml",
                b"<Types><Override ContentType='application/vnd.openxmlformats-"
                b"officedocument.wordprocessingml.document.main+xml'/></Types>",
            )
            archive.writestr("word/document.xml", b"<document/>")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                archive.writestr("word/document.xml", b"<document/>")
        with self.assertRaisesRegex(PackageSafetyError, "duplicate-member"):
            preflight_docx(duplicate)

        traversal = self.work / "traversal.docx"
        write_docx(traversal, {"word/../outside.xml": b"blocked"})
        with self.assertRaisesRegex(PackageSafetyError, "unsafe-member-name"):
            preflight_docx(traversal)


if __name__ == "__main__":
    unittest.main()
