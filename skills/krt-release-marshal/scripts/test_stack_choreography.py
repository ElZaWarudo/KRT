#!/usr/bin/env python3
"""Tests for stacked-PR choreography checks."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(*args: str) -> tuple[int, dict]:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "check_stack_choreography.py"), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode, json.loads(completed.stdout)


class StackChoreographyTest(unittest.TestCase):
    def test_squash_stack_requires_refresh_plan_before_parent_merge(self) -> None:
        code, result = run(
            "--parent-merge-method",
            "squash",
            "--parent-branch",
            "fix/frontend-build",
            "--child-branch",
            "feat/public-dpp-integrity",
            "--child-base",
            "fix/frontend-build",
            "--final-base",
            "spike/frontend",
        )
        self.assertNotEqual(code, 0)
        self.assertIn("downstream-refresh-plan-required-for-squash", result["block_reasons"])

    def test_squash_stack_allows_merge_plan_when_refresh_is_planned(self) -> None:
        code, result = run(
            "--parent-merge-method",
            "squash",
            "--parent-branch",
            "fix/frontend-build",
            "--child-branch",
            "feat/public-dpp-integrity",
            "--child-base",
            "fix/frontend-build",
            "--final-base",
            "spike/frontend",
            "--refresh-planned",
        )
        self.assertEqual(code, 0, result)

    def test_squash_stack_requires_child_refresh_after_parent_merge(self) -> None:
        code, result = run(
            "--parent-merge-method",
            "squash",
            "--parent-state",
            "merged",
            "--parent-branch",
            "fix/frontend-build",
            "--child-branch",
            "feat/public-dpp-integrity",
            "--child-base",
            "fix/frontend-build",
            "--final-base",
            "spike/frontend",
        )
        self.assertNotEqual(code, 0)
        self.assertIn("downstream-refresh-required-after-squash-merge", result["block_reasons"])

    def test_squash_stack_blocks_deleted_parent_before_child_refresh(self) -> None:
        code, result = run(
            "--parent-merge-method",
            "squash",
            "--parent-state",
            "merged",
            "--parent-branch",
            "fix/frontend-build",
            "--child-branch",
            "feat/public-dpp-integrity",
            "--child-base",
            "fix/frontend-build",
            "--final-base",
            "spike/frontend",
            "--parent-branch-deleted",
        )
        self.assertNotEqual(code, 0)
        self.assertIn("parent-branch-deleted-before-child-refresh", result["block_reasons"])

    def test_squash_stack_requires_fresh_approvals_and_checks_after_refresh(self) -> None:
        code, result = run(
            "--parent-merge-method",
            "squash",
            "--parent-state",
            "merged",
            "--parent-branch",
            "fix/frontend-build",
            "--child-branch",
            "feat/public-dpp-integrity",
            "--child-base",
            "fix/frontend-build",
            "--final-base",
            "spike/frontend",
            "--child-rebased-onto-final-base",
        )
        self.assertNotEqual(code, 0)
        self.assertIn("downstream-approvals-stale", result["block_reasons"])
        self.assertIn("downstream-checks-stale", result["block_reasons"])

    def test_squash_stack_passes_after_refresh_and_revalidation(self) -> None:
        code, result = run(
            "--parent-merge-method",
            "squash",
            "--parent-state",
            "merged",
            "--parent-branch",
            "fix/frontend-build",
            "--child-branch",
            "feat/public-dpp-integrity",
            "--child-base",
            "fix/frontend-build",
            "--final-base",
            "spike/frontend",
            "--child-rebased-onto-final-base",
            "--approvals-refreshed",
            "--checks-refreshed",
        )
        self.assertEqual(code, 0, result)


if __name__ == "__main__":
    unittest.main()
