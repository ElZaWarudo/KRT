#!/usr/bin/env python3
"""Tests for baseline-bound worker patch export."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from export_worker_patch import export_worker_patch


class ExportWorkerPatchTest(unittest.TestCase):
    def make_repo(self, root: Path) -> str:
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
        (root / "foundation.txt").write_text("base\n", encoding="utf-8")
        (root / "worker.txt").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
        return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()

    def metadata(self, base: str, tree: str, owned: list[str]) -> dict[str, object]:
        return {
            "workspace_id": "run-worker",
            "worker_id": "worker",
            "unit_id": "runtime",
            "role": "implementer",
            "base_revision": base,
            "baseline_tree": tree,
            "dependency_patch_hashes": ["sha256:foundation"],
            "owned_paths": owned,
            "contract_hash": "sha256:contract",
        }

    def test_exports_only_worker_delta_and_patch_applies_to_same_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "worker"
            base = self.make_repo(root)
            (root / "foundation.txt").write_text("dependency\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "foundation.txt"], check=True)
            tree = subprocess.run(["git", "-C", str(root), "write-tree"], check=True, capture_output=True, text=True).stdout.strip()
            (root / "worker.txt").write_text("worker\n", encoding="utf-8")
            (root / "new.txt").write_text("new\n", encoding="utf-8")

            patch, manifest = export_worker_patch(root, self.metadata(base, tree, ["worker.txt", "new.txt"]))

            target = Path(temp_dir) / "target"
            subprocess.run(["git", "clone", "-q", str(root), str(target)], check=True)
            (target / "foundation.txt").write_text("dependency\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(target), "add", "foundation.txt"], check=True)
            patch_path = Path(temp_dir) / "worker.patch"
            patch_path.write_bytes(patch)
            subprocess.run(["git", "-C", str(target), "apply", "--index", str(patch_path)], check=True)

            self.assertEqual(manifest["changed_files"][0]["path"], "new.txt")
            self.assertEqual({entry["path"] for entry in manifest["changed_files"]}, {"new.txt", "worker.txt"})
            self.assertEqual((target / "foundation.txt").read_text(encoding="utf-8"), "dependency\n")
            self.assertEqual((target / "worker.txt").read_text(encoding="utf-8"), "worker\n")
            self.assertEqual((target / "new.txt").read_text(encoding="utf-8"), "new\n")

    def test_rejects_unowned_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base = self.make_repo(root)
            tree = subprocess.run(["git", "-C", str(root), "write-tree"], check=True, capture_output=True, text=True).stdout.strip()
            (root / "worker.txt").write_text("changed\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "unowned"):
                export_worker_patch(root, self.metadata(base, tree, []))


if __name__ == "__main__":
    unittest.main()
