#!/usr/bin/env python3
"""Tests for root-owned worker diff observation."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from capture_worker_observation import observe_diff


class CaptureWorkerObservationTest(unittest.TestCase):
    def test_digest_changes_with_observed_content_and_includes_untracked_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
            (root / "tracked.txt").write_text("before", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "tracked.txt"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
            (root / "tracked.txt").write_text("after", encoding="utf-8")
            (root / "new.txt").write_text("new", encoding="utf-8")

            first = observe_diff(root, "HEAD")
            (root / "tracked.txt").write_text("after two", encoding="utf-8")
            second = observe_diff(root, "HEAD")

        self.assertEqual(first["changed_files"], ["new.txt", "tracked.txt"])
        self.assertEqual(first["changed_files_source"], "root-diff")
        self.assertNotEqual(first["diff_digest"], second["diff_digest"])


if __name__ == "__main__":
    unittest.main()
