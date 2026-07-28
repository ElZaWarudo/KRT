#!/usr/bin/env python3
"""Tests for the non-mutating runtime preflight."""

from __future__ import annotations

import json
import subprocess
import sys
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


if __name__ == "__main__":
    unittest.main()
