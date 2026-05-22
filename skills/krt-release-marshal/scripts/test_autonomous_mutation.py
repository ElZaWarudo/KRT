#!/usr/bin/env python3
"""Fixture tests for the autonomous mutation executor."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXECUTOR = ROOT / "autonomous_mutation.py"
FIXTURES = ROOT / "fixtures" / "github-autonomy"
LEDGER = ROOT.parents[1] / "krt-compound-master" / "scripts" / "fixtures" / "autonomy-ledgers" / "active.json"
NOW = "2026-05-22T12:00:00Z"
CONTRACT_HASH = "b74b94b95a17d325383b9d29a44fcd0c6830ddcec49f3a138d74d26b5d804968"


def run_executor(audit_dir: Path, state_file: str, *extra: str) -> tuple[int, dict]:
    cmd = [
        sys.executable,
        str(EXECUTOR),
        "--ledger",
        str(LEDGER),
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
        "--state-file",
        str(FIXTURES / state_file),
        "--audit-dir",
        str(audit_dir),
        "--now",
        NOW,
        *extra,
    ]
    completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
    return completed.returncode, json.loads(completed.stdout)


class AutonomousMutationTest(unittest.TestCase):
    def test_dry_run_records_audit_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, result = run_executor(Path(tmp), "merge_allowed.json")
            self.assertEqual(code, 0, result)
            self.assertTrue(result["allowed"])
            self.assertTrue((Path(tmp) / "HEAD").exists())
            events = list((Path(tmp) / "events").glob("*.json"))
            self.assertEqual(len(events), 2)

    def test_validator_failure_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, result = run_executor(Path(tmp), "merge_pending_check.json")
            self.assertNotEqual(code, 0)
            self.assertTrue(any(reason.startswith("required-check-not-green:test") for reason in result["block_reasons"]))

    def test_execute_requires_enforcement_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, result = run_executor(Path(tmp), "merge_allowed.json", "--execute", "--expected-contract-hash", CONTRACT_HASH)
            self.assertNotEqual(code, 0)
            self.assertIn("enforcement-boundary-unconfirmed", result["block_reasons"])

    def test_executor_blocks_without_state_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cmd = [
                sys.executable,
                str(EXECUTOR),
                "--ledger",
                str(LEDGER),
                "--mutation-class",
                "pr_merge",
                "--target",
                "repository=acme/widgets",
                "--target",
                "base_branch=main",
                "--target",
                "head_branch=feature/autonomous-flow",
                "--target",
                "head_sha=abc123",
                "--target",
                "pr_number=42",
                "--audit-dir",
                str(tmp),
                "--now",
                NOW,
            ]
            completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
            result = json.loads(completed.stdout)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("state-file-required", result["block_reasons"])

    def test_stale_ledger_audit_head_blocks_reuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, first = run_executor(Path(tmp), "merge_allowed.json")
            self.assertEqual(code, 0, first)
            code, second = run_executor(Path(tmp), "merge_allowed.json")
            self.assertNotEqual(code, 0)
            self.assertIn("audit-chain-mismatch", second["block_reasons"])


if __name__ == "__main__":
    unittest.main()
