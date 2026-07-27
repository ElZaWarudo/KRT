#!/usr/bin/env python3
"""End-to-end fixture tests for krt-word-illuminator scripts."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parent


def run_script(
    name: str, *args: str, env: dict[str, str] | None = None
) -> tuple[int, dict]:
    completed = subprocess.run(
        [sys.executable, str(ROOT / name), *args],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"{name} emitted invalid JSON\nstdout={completed.stdout}\nstderr={completed.stderr}"
        ) from exc
    return completed.returncode, payload


class WordIlluminatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(
            prefix="krt-word-illuminator-test-"
        )
        self.work = Path(self.temporary.name)
        self.request = self.work / "request.json"
        self.output = self.work / "report.docx"
        self.request.write_text(
            json.dumps(
                {
                    "document_type": "technical_report",
                    "objective": "Document the verified system architecture",
                    "title": "Architecture Report",
                    "subtitle": "Verified baseline",
                    "audience": "Engineering and management",
                    "language": "en",
                    "output": "report.docx",
                    "required_sections": ["Executive summary", "Architecture"],
                    "sources": [{"id": "requirements", "path": "requirements.md"}],
                    "document": {
                        "toc": True,
                        "header": "Architecture Report",
                        "footer": "Internal",
                        "page_numbers": True
                    },
                    "sections": [
                        {
                            "heading": "Executive summary",
                            "level": 1,
                            "blocks": [
                                {
                                    "type": "paragraph",
                                    "text": "The system uses a documented service boundary.",
                                    "provenance": "source",
                                    "source_ids": ["requirements"]
                                }
                            ]
                        },
                        {
                            "heading": "Architecture",
                            "level": 1,
                            "blocks": [
                                {
                                    "type": "table",
                                    "headers": ["Component", "Responsibility"],
                                    "rows": [["API", "Request handling"]],
                                    "caption": "Table 1. Components",
                                    "provenance": "source",
                                    "source_ids": ["requirements"]
                                },
                                {
                                    "type": "note",
                                    "text": "Implementation detail supplied by the user.",
                                    "provenance": "user"
                                }
                            ]
                        }
                    ],
                    "unverified_claims": []
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def create_document(self) -> dict:
        code, result = run_script("create_docx.py", str(self.request))
        self.assertEqual(code, 0, result)
        self.assertTrue(self.output.is_file())
        return result

    def visual_qa(self) -> Path:
        page_image = self.work / "page-1.png"
        page_image.write_bytes(b"fixture")
        render_report = self.work / "render-report.json"
        render_report.write_text(
            json.dumps(
                {
                    "document": str(self.output),
                    "pages": 1,
                    "page_images": [str(page_image)]
                }
            ),
            encoding="utf-8",
        )
        path = self.work / "visual-qa.json"
        path.write_text(
            json.dumps(
                {
                    "document": str(self.output),
                    "render_report": str(render_report),
                    "rendered_pages": 1,
                    "inspected_pages": [1],
                    "status": "passed",
                    "findings": []
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_create_inspect_and_validate(self) -> None:
        result = self.create_document()
        self.assertEqual(result["tables"], 1)
        self.assertEqual(result["visual_qa"], "pending_render_and_manual_inspection")

        code, inspection = run_script("inspect_docx.py", str(self.output))
        self.assertEqual(code, 0, inspection)
        self.assertEqual(inspection["tables"], 1)
        self.assertEqual(inspection["tables_with_repeating_header"], 1)
        self.assertEqual(
            [item["text"] for item in inspection["headings"]],
            ["Contents", "Executive summary", "Architecture"],
        )

        code, validation = run_script(
            "validate_docx.py",
            str(self.output),
            "--request",
            str(self.request),
        )
        self.assertEqual(code, 0, validation)
        self.assertTrue(validation["valid"])

        code, final_validation = run_script(
            "validate_docx.py",
            str(self.output),
            "--request",
            str(self.request),
            "--visual-qa",
            str(self.visual_qa()),
            "--final",
        )
        self.assertEqual(code, 0, final_validation)

    def test_edit_and_compare(self) -> None:
        self.create_document()
        patch = self.work / "patch.json"
        edited = self.work / "edited.docx"
        patch.write_text(
            json.dumps(
                {
                    "operations": [
                        {
                            "op": "replace_paragraph",
                            "old": "Implementation detail supplied by the user.",
                            "new": "Updated implementation detail."
                        },
                        {
                            "op": "insert_after_heading",
                            "heading": "Architecture",
                            "blocks": [
                                {
                                    "type": "paragraph",
                                    "text": "Inserted scope statement.",
                                    "provenance": "user"
                                }
                            ]
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        code, edit = run_script(
            "edit_docx.py",
            str(self.output),
            str(patch),
            "--output",
            str(edited),
        )
        self.assertEqual(code, 0, edit)
        code, comparison = run_script(
            "compare_docx.py", str(self.output), str(edited)
        )
        self.assertEqual(code, 0, comparison)
        self.assertTrue(comparison["changed"])
        self.assertTrue(comparison["text_diff"])

    def test_privacy_scrub(self) -> None:
        self.create_document()
        document = Document(str(self.output))
        document.core_properties.author = "Sensitive Author"
        document.core_properties.last_modified_by = "Sensitive Editor"
        commented = document.paragraphs[-1]
        document.add_comment(
            commented.runs,
            text="Working comment",
            author="Sensitive Reviewer",
            initials="SR",
        )
        document.save(self.output)
        clean = self.work / "clean.docx"
        code, result = run_script(
            "privacy_scrub.py",
            str(self.output),
            "--output",
            str(clean),
            "--remove-comments",
        )
        self.assertEqual(code, 0, result)
        self.assertEqual(result["before"]["comments"], 1)
        self.assertEqual(result["after"]["comments"], 0)
        self.assertEqual(result["after"]["core_properties"]["author"], "")
        self.assertEqual(result["after"]["core_properties"]["last_modified_by"], "")
        self.assertTrue(clean.is_file())

    def test_unknown_source_id_fails_creation(self) -> None:
        request = json.loads(self.request.read_text(encoding="utf-8"))
        request["sections"][0]["blocks"][0]["source_ids"] = ["missing"]
        self.request.write_text(json.dumps(request), encoding="utf-8")
        code, result = run_script("create_docx.py", str(self.request))
        self.assertNotEqual(code, 0)
        self.assertIn("Source grounding failed", result["error"])
        self.assertFalse(self.output.exists())

    def test_render_pipeline_records_pending_visual_qa(self) -> None:
        self.create_document()
        binary_dir = self.work / "bin"
        binary_dir.mkdir()
        libreoffice = binary_dir / "libreoffice"
        libreoffice.write_text(
            """#!/usr/bin/env python3
import sys
from pathlib import Path
output = Path(sys.argv[sys.argv.index("--outdir") + 1])
source = Path(sys.argv[-1])
(output / f"{source.stem}.pdf").write_bytes(b"%PDF-1.4 fixture")
""",
            encoding="utf-8",
        )
        pdftoppm = binary_dir / "pdftoppm"
        pdftoppm.write_text(
            """#!/usr/bin/env python3
import sys
from pathlib import Path
from PIL import Image
prefix = Path(sys.argv[-1])
Image.new("RGB", (100, 140), "white").save(f"{prefix}-1.png")
""",
            encoding="utf-8",
        )
        libreoffice.chmod(0o755)
        pdftoppm.chmod(0o755)
        environment = dict(os.environ)
        environment["PATH"] = f"{binary_dir}{os.pathsep}{environment['PATH']}"
        render_dir = self.work / "render"
        code, result = run_script(
            "render_docx.py",
            str(self.output),
            "--output-dir",
            str(render_dir),
            env=environment,
        )
        self.assertEqual(code, 0, result)
        self.assertEqual(result["pages"], 1)
        self.assertEqual(result["visual_qa"], "pending_manual_inspection")
        self.assertTrue((render_dir / "page-1.png").is_file())
        self.assertTrue((render_dir / "render-report.json").is_file())

    def test_bundled_template_preserves_single_page_field(self) -> None:
        template = (
            ROOT.parent / "assets" / "templates" / "professional-report.docx"
        ).resolve()
        self.assertTrue(template.is_file())
        request = json.loads(self.request.read_text(encoding="utf-8"))
        request["template"] = str(template)
        request["output"] = "templated.docx"
        request["document"] = {"toc": False}
        self.request.write_text(json.dumps(request), encoding="utf-8")
        output = self.work / "templated.docx"
        code, result = run_script("create_docx.py", str(self.request))
        self.assertEqual(code, 0, result)
        code, inspection = run_script("inspect_docx.py", str(output))
        self.assertEqual(code, 0, inspection)
        self.assertEqual(inspection["package"]["fields"], 1)

    def test_ambiguous_edit_fails(self) -> None:
        document = Document()
        document.add_paragraph("Repeated")
        document.add_paragraph("Repeated")
        source = self.work / "ambiguous.docx"
        document.save(source)
        patch = self.work / "ambiguous.json"
        patch.write_text(
            json.dumps(
                {
                    "operations": [
                        {
                            "op": "replace_paragraph",
                            "old": "Repeated",
                            "new": "Changed"
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        code, result = run_script(
            "edit_docx.py",
            str(source),
            str(patch),
            "--output",
            str(self.work / "ambiguous-edited.docx"),
        )
        self.assertNotEqual(code, 0)
        self.assertIn("Ambiguous paragraph replacement", result["error"])


if __name__ == "__main__":
    unittest.main()
