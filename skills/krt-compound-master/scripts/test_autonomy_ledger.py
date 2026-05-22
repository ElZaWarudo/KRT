#!/usr/bin/env python3
"""Fixture tests for autonomy ledger validation."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHECK = ROOT / "check_autonomy_ledger.py"
FIXTURES = ROOT / "fixtures" / "autonomy-ledgers"
NOW = "2026-05-22T12:00:00Z"


def run_check(fixture: str, *extra: str) -> tuple[int, dict]:
    cmd = [
        sys.executable,
        str(CHECK),
        str(FIXTURES / fixture),
        "--mutation-class",
        "pr_merge",
        "--target",
        "repository=acme/widgets",
        "--target",
        "base_branch=main",
        "--target",
        "branch=feature/autonomous-flow",
        "--target",
        "head_branch=feature/autonomous-flow",
        "--target",
        "head_sha=abc123",
        "--target",
        "pr_number=42",
        "--target",
        "jira_key=KRT-42",
        "--now",
        NOW,
        *extra,
    ]
    completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
    return completed.returncode, json.loads(completed.stdout)


class AutonomyLedgerTest(unittest.TestCase):
    def test_active_ledger_allows_scoped_mutation(self) -> None:
        code, result = run_check("active.json")
        self.assertEqual(code, 0, result)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["mutation_class"], "pr_merge")

    def test_expired_ledger_blocks(self) -> None:
        code, result = run_check("expired.json")
        self.assertNotEqual(code, 0)
        self.assertIn("expired", result["block_reasons"])

    def test_revoked_ledger_blocks(self) -> None:
        code, result = run_check("revoked.json")
        self.assertNotEqual(code, 0)
        self.assertIn("ledger-not-active:revoked", result["block_reasons"])

    def test_scope_mismatch_blocks(self) -> None:
        code, result = run_check("active.json", "--target", "base_branch=develop")
        self.assertNotEqual(code, 0)
        self.assertIn("scope-mismatch:base_branch", result["block_reasons"])

    def test_missing_required_field_blocks(self) -> None:
        code, result = run_check("malformed.json")
        self.assertNotEqual(code, 0)
        self.assertTrue(any(reason.startswith("schema-error:missing:") for reason in result["block_reasons"]))

    def test_contract_hash_mismatch_blocks(self) -> None:
        code, result = run_check("active.json", "--expected-contract-hash", "not-the-hash")
        self.assertNotEqual(code, 0)
        self.assertIn("unexpected-contract-hash", result["block_reasons"])

    def test_audit_head_mismatch_blocks(self) -> None:
        code, result = run_check("active.json", "--expected-audit-head", "other-head")
        self.assertNotEqual(code, 0)
        self.assertIn("audit-chain-mismatch", result["block_reasons"])

    def test_missing_contract_hash_blocks(self) -> None:
        code, result = run_check("malformed.json")
        self.assertNotEqual(code, 0)
        self.assertIn("missing-contract-hash", result["block_reasons"])

    def test_issuer_without_approval_hash_blocks(self) -> None:
        code, result = run_check("issuer-only.json")
        self.assertNotEqual(code, 0)
        self.assertIn("missing-issuer-approval-binding", result["block_reasons"])

    def test_missing_required_target_blocks(self) -> None:
        cmd = [
            sys.executable,
            str(CHECK),
            str(FIXTURES / "active.json"),
            "--mutation-class",
            "pr_merge",
            "--target",
            "repository=acme/widgets",
            "--target",
            "base_branch=main",
            "--now",
            NOW,
        ]
        completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
        result = json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("missing-target:head_branch", result["block_reasons"])
        self.assertIn("missing-target:head_sha", result["block_reasons"])


if __name__ == "__main__":
    unittest.main()
