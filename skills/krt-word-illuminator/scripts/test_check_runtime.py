#!/usr/bin/env python3
"""Tests for the non-mutating runtime preflight."""

from __future__ import annotations

import json
import subprocess
import os
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("check_runtime.py")


class RuntimePreflightTests(unittest.TestCase):
    def test_core_preflight_reports_machine_readable_status(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            check=False,
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0 if payload["ready"] else 1)
        self.assertIn("python-docx", payload["python_modules"])
        self.assertIn("jsonschema", payload["python_modules"])
        self.assertFalse(payload["installation_performed"])

    def test_render_preflight_never_claims_installation(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--require-render"],
            check=False,
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0 if payload["ready"] else 1)
        self.assertEqual(
            payload["ready"],
            payload["core_ready"] and payload["render_ready"],
        )
        self.assertFalse(payload["installation_performed"])

    def test_detects_tool_that_only_accepts_short_version_flag(self) -> None:
        # Poppler's pdftoppm exits 1 on --version and 0 on -v.
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "pdftoppm"
            fake.write_text('#!/bin/sh\n[ "$1" = "-v" ] && exit 0\nexit 1\n')
            fake.chmod(0o755)
            env = dict(os.environ, PATH=f"{tmp}{os.pathsep}{os.environ['PATH']}")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--require-render"],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["tools"]["pdftoppm"], str(fake))


if __name__ == "__main__":
    unittest.main()
