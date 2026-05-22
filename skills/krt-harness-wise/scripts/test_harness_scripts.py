#!/usr/bin/env python3
"""Fixture tests for Harness Wise deterministic scripts."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"


def run_json(*args: str) -> tuple[int, dict]:
    completed = subprocess.run([sys.executable, *args], text=True, capture_output=True, check=False)
    return completed.returncode, json.loads(completed.stdout)


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


if __name__ == "__main__":
    unittest.main()
