#!/usr/bin/env python3
"""Fixture tests for autonomous GitHub validators."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures" / "github-autonomy"


def run(script: str, mutation: str, fixture: str, *extra: str) -> tuple[int, dict]:
    cmd = [
        sys.executable,
        str(ROOT / script),
        "--mutation-class",
        mutation,
        "--fixture",
        str(FIXTURES / fixture),
        "--target",
        "repository=acme/widgets",
        "--target",
        "base_branch=main",
        "--target",
        "head_branch=feature/autonomous-flow",
        *extra,
    ]
    completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
    return completed.returncode, json.loads(completed.stdout)


class GitHubAutonomyTest(unittest.TestCase):
    def test_merge_allowed(self) -> None:
        code, result = run("check_merge_eligibility.py", "pr_merge", "merge_allowed.json", "--current-actor", "codex-agent")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["live_state_summary"]["action"], "merge")

    def test_stale_approval_blocks(self) -> None:
        code, result = run("check_merge_eligibility.py", "pr_merge", "merge_stale_approval.json")
        self.assertNotEqual(code, 0)
        self.assertIn("current-head-human-approval-missing", result["block_reasons"])

    def test_pending_check_blocks(self) -> None:
        code, result = run("check_merge_eligibility.py", "pr_merge", "merge_pending_check.json")
        self.assertNotEqual(code, 0)
        self.assertTrue(any(reason.startswith("required-check-not-green:test") for reason in result["block_reasons"]))

    def test_failed_completed_check_blocks(self) -> None:
        code, result = run("check_merge_eligibility.py", "pr_merge", "merge_failed_completed_check.json")
        self.assertNotEqual(code, 0)
        self.assertIn("required-check-not-green:test:FAILURE", result["block_reasons"])

    def test_non_approved_review_decision_blocks(self) -> None:
        code, result = run("check_merge_eligibility.py", "pr_merge", "merge_review_required.json")
        self.assertNotEqual(code, 0)
        self.assertIn("review-decision-not-approved:REVIEW_REQUIRED", result["block_reasons"])

    def test_merge_queue_is_distinct_mutation(self) -> None:
        code, result = run("check_merge_eligibility.py", "pr_merge", "merge_queue_required.json")
        self.assertNotEqual(code, 0)
        self.assertIn("merge-queue-required", result["block_reasons"])
        code, result = run("check_merge_eligibility.py", "pr_merge_queue", "merge_queue_required.json")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["live_state_summary"]["action"], "enqueue")

    def test_pr_duplicate_blocks_create(self) -> None:
        code, result = run("check_pr_mutation.py", "pr_create", "pr_create_duplicate.json")
        self.assertNotEqual(code, 0)
        self.assertIn("duplicate-open-pr", result["block_reasons"])

    def test_pr_ready_allows_valid_fixture(self) -> None:
        code, result = run("check_pr_mutation.py", "pr_ready", "pr_create_valid.json")
        self.assertEqual(code, 0, result)

    def test_branch_force_requires_ledger_enablement(self) -> None:
        code, result = run("check_branch_mutation.py", "branch_force_push", "branch_valid.json", "--target", "branch=feature/autonomous-flow")
        self.assertNotEqual(code, 0)
        self.assertIn("force-with-lease-not-ledger-enabled", result["block_reasons"])

    def test_reviewer_noop_is_allowed(self) -> None:
        code, result = run("check_reviewer_request.py", "reviewer_request", "reviewer_noop.json")
        self.assertEqual(code, 0, result)
        self.assertIn("reviewer-already-requested", result["warnings"])

    def test_stack_after_parent_merge_requires_refresh(self) -> None:
        code, result = run("check_stack_state.py", "pr_merge", "stack_after_parent_merge.json")
        self.assertNotEqual(code, 0)
        self.assertIn("downstream-retarget-required", result["block_reasons"])
        self.assertIn("downstream-approvals-stale", result["block_reasons"])


if __name__ == "__main__":
    unittest.main()
