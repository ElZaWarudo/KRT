#!/usr/bin/env python3
"""Fixture tests for merge authorization text validation."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(text: str, pr_number: int | None = 96, allow_generic_context: bool = False) -> tuple[int, dict]:
    command = [
        sys.executable,
        str(ROOT / "check_merge_authorization.py"),
        "--text",
        text,
    ]
    if pr_number is not None:
        command.extend(["--pr-number", str(pr_number)])
    if allow_generic_context:
        command.append("--allow-generic-context")

    completed = subprocess.run(
        command,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode, json.loads(completed.stdout)


class MergeAuthorizationTest(unittest.TestCase):
    def test_spanish_direct_authorization_allows(self) -> None:
        code, result = run("mergea la PR #96 ahora")
        self.assertEqual(code, 0, result)
        self.assertTrue(result["allowed"])

    def test_natural_equivalent_authorization_allows(self) -> None:
        code, result = run("puedes hacer merge de la PR 96")
        self.assertEqual(code, 0, result)
        self.assertTrue(result["allowed"])

    def test_contextual_pr_authorization_allows_when_expected_pr_is_known(self) -> None:
        code, result = run("mergea la pr")
        self.assertEqual(code, 0, result)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["summary"]["pr_references"], [96])
        self.assertTrue(result["summary"]["resolved_from_context"])

    def test_contextual_pull_request_authorization_allows_when_expected_pr_is_known(self) -> None:
        code, result = run("merge this pull request now")
        self.assertEqual(code, 0, result)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["summary"]["pr_references"], [96])
        self.assertTrue(result["summary"]["resolved_from_context"])

    def test_contextual_pr_authorization_blocks_without_expected_pr(self) -> None:
        code, result = run("mergea la pr", pr_number=None)
        self.assertNotEqual(code, 0)
        self.assertIn("missing-pr-reference", result["errors"])

    def test_generic_contextual_approval_allows_when_prompted_for_expected_pr(self) -> None:
        code, result = run("dale", allow_generic_context=True)
        self.assertEqual(code, 0, result)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["summary"]["pr_references"], [96])
        self.assertTrue(result["summary"]["has_generic_approval"])
        self.assertTrue(result["summary"]["resolved_from_generic_context"])

    def test_generic_contextual_approval_blocks_without_expected_pr(self) -> None:
        code, result = run("dale", pr_number=None, allow_generic_context=True)
        self.assertNotEqual(code, 0)
        self.assertIn("missing-pr-reference", result["errors"])

    def test_generic_plan_approval_blocks(self) -> None:
        code, result = run("aprobado, continua")
        self.assertNotEqual(code, 0)
        self.assertIn("missing-pr-reference", result["errors"])
        self.assertIn("missing-merge-intent", result["errors"])
        self.assertIn("generic-approval-is-not-merge-authorization", result["warnings"])

    def test_wrong_pr_blocks(self) -> None:
        code, result = run("mergea la PR #95 ahora")
        self.assertNotEqual(code, 0)
        self.assertIn("wrong-pr-reference:expected-96:found-95", result["errors"])

    def test_pr_reference_without_merge_intent_blocks(self) -> None:
        code, result = run("la PR #96 esta aprobada")
        self.assertNotEqual(code, 0)
        self.assertIn("missing-merge-intent", result["errors"])

    def test_multiple_pr_references_block(self) -> None:
        code, result = run("mergea la PR #96 y la PR #97")
        self.assertNotEqual(code, 0)
        self.assertIn("multiple-pr-references", result["errors"])


if __name__ == "__main__":
    unittest.main()
