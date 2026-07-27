#!/usr/bin/env python3
"""Fixture tests for Harness Wise deterministic scripts."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"


def run_json(*args: str) -> tuple[int, dict]:
    completed = subprocess.run([sys.executable, *args], text=True, capture_output=True, check=False)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {
            "allowed": False,
            "errors": [f"invalid-json-output:{completed.stderr.strip()}"],
            "warnings": [],
        }
    return completed.returncode, payload


class HarnessScriptTest(unittest.TestCase):
    def test_check_valid_harness(self) -> None:
        code, result = run_json(str(ROOT / "check_harness.py"), str(FIXTURES / "harnesses" / "valid.md"))
        self.assertEqual(code, 0, result)
        self.assertTrue(result["allowed"])

    def test_missing_frontmatter_blocks(self) -> None:
        code, result = run_json(str(ROOT / "check_harness.py"), str(FIXTURES / "harnesses" / "no-frontmatter.md"))
        self.assertNotEqual(code, 0)
        self.assertIn("missing-frontmatter", result["errors"])

    def test_missing_sections_block(self) -> None:
        code, result = run_json(str(ROOT / "check_harness.py"), str(FIXTURES / "harnesses" / "missing-sections.md"))
        self.assertNotEqual(code, 0)
        self.assertTrue(any(error.startswith("missing-section:") for error in result["errors"]))

    def test_absolute_path_blocks(self) -> None:
        code, result = run_json(str(ROOT / "check_harness.py"), str(FIXTURES / "harnesses" / "absolute-path.md"))
        self.assertNotEqual(code, 0)
        self.assertTrue(any(error.startswith("absolute-path:") for error in result["errors"]))

    def test_self_reference_blocks(self) -> None:
        code, result = run_json(str(ROOT / "check_harness.py"), str(FIXTURES / "harnesses" / "self-reference.md"))
        self.assertNotEqual(code, 0)
        self.assertIn("self-reference:krt-harness-wise", result["errors"])

    def test_overbroad_read_warns(self) -> None:
        code, result = run_json(str(ROOT / "check_harness.py"), str(FIXTURES / "harnesses" / "overbroad.md"))
        self.assertEqual(code, 0, result)
        self.assertIn("overbroad-read-instruction", result["warnings"])

    def test_find_agent_init_detects_project_context(self) -> None:
        code, result = run_json(str(ROOT / "find_agent_init.py"), "--root", str(FIXTURES / "valid_project"))
        self.assertEqual(code, 0, result)
        paths = [entry["path"] for entry in result["paths"]]
        self.assertIn("AGENTS.md", paths)
        self.assertIn(".codex", paths)

    def test_find_agent_init_warns_when_missing(self) -> None:
        code, result = run_json(str(ROOT / "find_agent_init.py"), "--root", str(FIXTURES / "missing_init"))
        self.assertEqual(code, 0, result)
        self.assertIn("no-agent-initialization-context-found", result["warnings"])

    def test_find_harness_prefers_matching_candidate(self) -> None:
        code, result = run_json(
            str(ROOT / "find_harness.py"),
            "--root",
            str(FIXTURES / "valid_project"),
            "--task",
            "invoice export",
        )
        self.assertEqual(code, 0, result)
        self.assertEqual(result["summary"]["best"], "docs/harnesses/invoice-export.md")

    def test_find_harness_blocks_missing_explicit_path(self) -> None:
        code, result = run_json(
            str(ROOT / "find_harness.py"),
            "--root",
            str(FIXTURES / "valid_project"),
            "--harness",
            "docs/harnesses/missing.md",
        )
        self.assertNotEqual(code, 0)
        self.assertIn("harness-not-found:docs/harnesses/missing.md", result["errors"])

    def test_find_harness_blocks_absolute_explicit_path(self) -> None:
        code, result = run_json(
            str(ROOT / "find_harness.py"),
            "--root",
            str(FIXTURES / "valid_project"),
            "--harness",
            "/tmp/harness.md",
        )
        self.assertNotEqual(code, 0)
        self.assertIn("harness-path-must-be-repo-relative:/tmp/harness.md", result["errors"])

    def test_find_harness_blocks_parent_escape(self) -> None:
        code, result = run_json(
            str(ROOT / "find_harness.py"),
            "--root",
            str(FIXTURES / "valid_project"),
            "--harness",
            "../harness.md",
        )
        self.assertNotEqual(code, 0)
        self.assertIn("harness-path-must-be-repo-relative:../harness.md", result["errors"])

    def test_sensitive_staged_summary_is_blocked_without_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.prepare_evidence_root(Path(directory))
            destination = root / "docs" / "harnesses" / "summaries" / "sensitive.md"

            code, result = run_json(
                str(ROOT / "promote_evidence.py"),
                "docs/harnesses/staging/sensitive.md",
                "--sidecar",
                "docs/harnesses/provenance/sensitive.json",
                "--root",
                str(root),
            )

            self.assertNotEqual(code, 0)
            self.assertFalse(result["allowed"])
            self.assertTrue(any(error.startswith("publication-safety:") for error in result["errors"]))
            self.assertFalse(destination.exists())

    def test_clean_staged_summary_is_promoted_identically_and_rescanned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.prepare_evidence_root(Path(directory))
            source = root / "docs" / "harnesses" / "staging" / "clean.md"
            destination = root / "docs" / "harnesses" / "summaries" / "clean.md"

            code, result = run_json(
                str(ROOT / "promote_evidence.py"),
                "docs/harnesses/staging/clean.md",
                "--sidecar",
                "docs/harnesses/provenance/clean.json",
                "--root",
                str(root),
            )

            self.assertEqual(code, 0, result)
            self.assertTrue(result["allowed"])
            self.assertEqual(result["summary"]["destination_rescan"], "passed")
            self.assertEqual(destination.read_bytes(), source.read_bytes())

    def test_promotion_blocks_destination_escape_and_implicit_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.prepare_evidence_root(Path(directory))
            summaries = root / "docs" / "harnesses" / "summaries"
            summaries.mkdir(parents=True)
            existing = summaries / "clean.md"
            existing.write_text("existing\n", encoding="utf-8")

            escape_code, escape = run_json(
                str(ROOT / "promote_evidence.py"),
                "docs/harnesses/staging/clean.md",
                "--sidecar",
                "docs/harnesses/provenance/clean.json",
                "--destination",
                "../escaped.md",
                "--root",
                str(root),
            )
            overwrite_code, overwrite = run_json(
                str(ROOT / "promote_evidence.py"),
                "docs/harnesses/staging/clean.md",
                "--sidecar",
                "docs/harnesses/provenance/clean.json",
                "--root",
                str(root),
            )
            explicit_code, explicit = run_json(
                str(ROOT / "promote_evidence.py"),
                "docs/harnesses/staging/clean.md",
                "--sidecar",
                "docs/harnesses/provenance/clean.json",
                "--root",
                str(root),
                "--overwrite",
            )

            self.assertNotEqual(escape_code, 0)
            self.assertIn("destination-must-be-under:docs/harnesses/summaries", escape["errors"])
            self.assertNotEqual(overwrite_code, 0)
            self.assertIn("destination-exists:docs/harnesses/summaries/clean.md", overwrite["errors"])
            self.assertEqual(explicit_code, 0, explicit)
            self.assertEqual(existing.read_bytes(), (root / "docs/harnesses/staging/clean.md").read_bytes())
            self.assertFalse((root / "docs" / "harnesses" / "escaped.md").exists())

    def test_unaccepted_sidecar_warning_blocks_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.prepare_evidence_root(Path(directory))
            sidecar = root / "docs" / "harnesses" / "provenance" / "clean.json"
            payload = json.loads(sidecar.read_text(encoding="utf-8"))
            payload["warnings"] = ["table-layout-uncertain"]
            sidecar.write_text(json.dumps(payload), encoding="utf-8")

            code, result = run_json(
                str(ROOT / "check_evidence.py"),
                "docs/harnesses/staging/clean.md",
                "--sidecar",
                "docs/harnesses/provenance/clean.json",
                "--root",
                str(root),
            )

            self.assertNotEqual(code, 0)
            self.assertIn("unaccepted-warning:table-layout-uncertain", result["errors"])

            payload["warning_decisions"] = {
                "table-layout-uncertain": "Accepted: no tabular values are required."
            }
            sidecar.write_text(json.dumps(payload), encoding="utf-8")
            accepted_code, accepted = run_json(
                str(ROOT / "check_evidence.py"),
                "docs/harnesses/staging/clean.md",
                "--sidecar",
                "docs/harnesses/provenance/clean.json",
                "--root",
                str(root),
            )
            self.assertEqual(accepted_code, 0, accepted)

    def test_sidecar_requires_explicit_publication_classification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self.prepare_evidence_root(Path(directory))
            sidecar = root / "docs" / "harnesses" / "provenance" / "clean.json"
            payload = json.loads(sidecar.read_text(encoding="utf-8"))
            for field in ("classification", "redaction_status", "publication_rationale"):
                payload.pop(field, None)
            sidecar.write_text(json.dumps(payload), encoding="utf-8")

            code, result = run_json(
                str(ROOT / "check_evidence.py"),
                "docs/harnesses/staging/clean.md",
                "--sidecar",
                "docs/harnesses/provenance/clean.json",
                "--root",
                str(root),
            )

            self.assertNotEqual(code, 0)
            self.assertIn("invalid-classification:expected-public-internal-confidential-restricted-unknown", result["errors"])
            self.assertIn("redaction-status-must-be-completed", result["errors"])
            self.assertIn("publication-rationale-required", result["errors"])

    def test_publication_check_blocks_sensitive_value_classes(self) -> None:
        cases = {
            "secret-like-assignment": "token=super-secret-value",
            "pii-like-value": "DNI: 12345678Z",
            "email": "person@example.com",
            "phone-like-value": "+34 612 345 678",
            "iban-like-value": "ES9121000418450200051332",
            "private-url": "https://portal.internal/customer",
            "source-hash-or-raw-digest": "a" * 64,
            "generated-source-fallback-reference": "docs/harnesses/sources/private.md",
            "absolute-source-path": "/home/operator/contracts/client.docx",
            "windows-absolute-source-path": r"C:\clients\private\client.docx",
            "source-metadata": "source_path=private/client.docx",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = self.prepare_evidence_root(Path(directory))
            summary = root / "docs" / "harnesses" / "staging" / "clean.md"
            baseline = summary.read_text(encoding="utf-8")
            for expected, value in cases.items():
                with self.subTest(expected=expected):
                    summary.write_text(f"{baseline}\n{value}\n", encoding="utf-8")
                    code, result = run_json(
                        str(ROOT / "check_evidence.py"),
                        "docs/harnesses/staging/clean.md",
                        "--sidecar",
                        "docs/harnesses/provenance/clean.json",
                        "--root",
                        str(root),
                    )
                    self.assertNotEqual(code, 0)
                    self.assertIn(f"publication-safety:{expected}", result["errors"])

    @staticmethod
    def prepare_evidence_root(root: Path) -> Path:
        harnesses = root / "docs" / "harnesses"
        shutil.copytree(FIXTURES / "evidence" / "staging", harnesses / "staging")
        shutil.copytree(FIXTURES / "evidence" / "provenance", harnesses / "provenance")
        return root


if __name__ == "__main__":
    unittest.main()
