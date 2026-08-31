#!/usr/bin/env python3
"""Tests for root-owned worker diff observation."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from capture_worker_observation import observe_diff


class CaptureWorkerObservationTest(unittest.TestCase):
    def make_repo(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
        (root / "tracked.txt").write_text("before", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "tracked.txt"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)

    def test_digest_changes_with_observed_content_and_includes_untracked_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_repo(root)
            (root / "tracked.txt").write_text("after", encoding="utf-8")
            (root / "new.txt").write_text("new", encoding="utf-8")

            first = observe_diff(root, "HEAD")
            (root / "tracked.txt").write_text("after two", encoding="utf-8")
            second = observe_diff(root, "HEAD")

        self.assertEqual(first["changed_files"], ["new.txt", "tracked.txt"])
        self.assertEqual(first["changed_files_source"], "root-diff")
        self.assertNotEqual(first["diff_digest"], second["diff_digest"])

    def test_sealed_index_excludes_inherited_dependency_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_repo(root)
            (root / "tracked.txt").write_text("dependency baseline", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "tracked.txt"], check=True)
            baseline_tree = subprocess.run(
                ["git", "-C", str(root), "write-tree"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            (root / "worker.txt").write_text("worker change", encoding="utf-8")

            result = observe_diff(root, "HEAD", baseline_tree)

        self.assertEqual(result["changed_files"], ["worker.txt"])
        self.assertEqual(result["changed_files_source"], "root-diff")
        self.assertEqual(result["diff_basis"], "worktree-vs-index")
        self.assertEqual(result["baseline_tree"], baseline_tree)

    def test_rejects_worker_index_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self.make_repo(root)
            baseline_tree = subprocess.run(
                ["git", "-C", str(root), "write-tree"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            (root / "staged-by-worker.txt").write_text("forbidden", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "staged-by-worker.txt"], check=True)

            with self.assertRaisesRegex(ValueError, "worker index changed"):
                observe_diff(root, "HEAD", baseline_tree)


if __name__ == "__main__":
    unittest.main()
