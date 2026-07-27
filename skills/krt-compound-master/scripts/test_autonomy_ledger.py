#!/usr/bin/env python3
"""Fixture tests for autonomy ledger validation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CHECK = ROOT / "check_autonomy_ledger.py"
FIXTURES = ROOT / "fixtures" / "autonomy-ledgers"
NOW = "2026-05-22T12:00:00Z"


def run_check_path(ledger: Path, *extra: str) -> tuple[int, dict]:
    cmd = [
        sys.executable,
        str(CHECK),
        str(ledger),
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


def run_check(fixture: str, *extra: str) -> tuple[int, dict]:
    return run_check_path(FIXTURES / fixture, *extra)


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

    def test_unsupported_schema_version_blocks(self) -> None:
        code, result = run_check("unsupported-version.json")
        self.assertNotEqual(code, 0)
        self.assertIn("schema-error:unsupported-version:2", result["block_reasons"])

    def test_boolean_schema_version_blocks(self) -> None:
        ledger = json.loads((FIXTURES / "active.json").read_text(encoding="utf-8"))
        ledger["schema_version"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "boolean-version.json"
            path.write_text(json.dumps(ledger), encoding="utf-8")
            code, result = run_check_path(path)

        self.assertNotEqual(code, 0)
        self.assertIn(
            "schema-error:unsupported-version:True",
            result["block_reasons"],
        )


class RuntimeRoleContractTest(unittest.TestCase):
    def test_current_compound_review_roles_are_canonical(self) -> None:
        role_contract = (ROOT.parent / "references" / "role-and-runtime.md").read_text(encoding="utf-8")
        self.assertIn("| `document_review` | `ce-doc-review` |", role_contract)
        self.assertIn("| `code_review` | `ce-code-review` |", role_contract)
        self.assertNotIn("| `document_review` | `document-review` |", role_contract)
        self.assertNotIn("| `code_review` | `ce-review` |", role_contract)

    def test_code_review_uses_current_report_only_agent_mode(self) -> None:
        review_contract = (ROOT.parent / "references" / "review-security-ci.md").read_text(encoding="utf-8")
        self.assertIn('Skill("<code_review>", "mode:agent ', review_contract)
        self.assertIn("route every correction through the work loop", review_contract)
        self.assertNotIn("mode:autofix", review_contract)
        self.assertNotIn("mode:report-only", review_contract)


if __name__ == "__main__":
    unittest.main()
