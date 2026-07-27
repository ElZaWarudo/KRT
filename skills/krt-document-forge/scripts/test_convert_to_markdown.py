#!/usr/bin/env python3
"""Focused contract tests for Document Forge."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("convert_to_markdown.py")
SPEC = importlib.util.spec_from_file_location("convert_to_markdown", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class DocumentForgeContractTest(unittest.TestCase):
    def test_default_summary_dir_is_private_staging(self) -> None:
        output_dir = Path("docs/harnesses/sources")
        self.assertEqual(
            MODULE.default_summary_dir(output_dir),
            Path("docs/harnesses/staging"),
        )

    def test_staged_summary_uses_opaque_provenance_without_source_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / "sources" / "brief.md"
            summary = root / "staging" / "brief.md"
            output.parent.mkdir()
            summary.parent.mkdir()
            output.write_text("# Private conversion\n", encoding="utf-8")
            summary.write_text(
                "---\n"
                "summary_type: harness-ready\n"
                "provenance_id: prov-550e8400-e29b-41d4-a716-446655440000\n"
                "---\n\n"
                "# Sanitized brief\n",
                encoding="utf-8",
            )

            self.assertEqual(MODULE.validate_summary(summary), [])


if __name__ == "__main__":
    unittest.main()
