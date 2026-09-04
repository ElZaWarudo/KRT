#!/usr/bin/env python3
"""Tests for guarded Seneschal worktree cleanup."""

from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from cleanup_worker_workspaces import reconcile_cleanup


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class CleanupWorkerWorkspacesTest(unittest.TestCase):
    def fixture(
        self,
        root: Path,
        *,
        name: str = "worker",
        attached: bool = True,
    ) -> tuple[Path, Path, Path, dict[str, object]]:
        repo = root / "repo"
        parent = root / "worktrees"
        workspace = parent / "run-1" / name
        artifact = root / "artifacts" / f"{name}.patch"
        repo.mkdir()
        artifact.parent.mkdir()
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "test@example.com")
        git(repo, "config", "user.name", "Test")
        (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
        git(repo, "add", "tracked.txt")
        git(repo, "commit", "-qm", "base")
        workspace.parent.mkdir(parents=True)
        branch = f"seneschal/run-1/{name}" if attached else None
        if branch:
            git(repo, "worktree", "add", "-q", "-b", branch, str(workspace), "HEAD")
        else:
            git(repo, "worktree", "add", "-q", "--detach", str(workspace), "HEAD")
        (workspace / "tracked.txt").write_text("changed\n", encoding="utf-8")
        artifact.write_text("durable patch\n", encoding="utf-8")
        registry = {
            "schema_version": 1,
            "entries": [{
                "workspace_id": f"run-1-{name}",
                "run_id": "run-1",
                "path": str(workspace),
                "branch": branch,
                "lifecycle_status": "cleanup-ready",
                "preserve_for_diagnosis": False,
                "durable_artifacts": [{"path": str(artifact), "sha256": digest(artifact)}],
            }],
        }
        return repo, parent, workspace, registry

    def test_dry_run_reports_without_removing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, parent, workspace, registry = self.fixture(Path(temp_dir))

            result = reconcile_cleanup(repo_root=repo, worktree_parent=parent, registry=registry, apply=False)

            self.assertEqual(result["would_remove"], ["run-1-worker"])
            self.assertTrue(workspace.exists())
            self.assertIn("seneschal/run-1/worker", git(repo, "branch", "--format=%(refname:short)"))

    def test_apply_removes_dirty_worktree_and_merged_temporary_branch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, parent, workspace, registry = self.fixture(Path(temp_dir))

            result = reconcile_cleanup(repo_root=repo, worktree_parent=parent, registry=registry, apply=True)

            self.assertEqual(result["removed"], ["run-1-worker"])
            self.assertFalse(workspace.exists())
            self.assertNotIn("seneschal/run-1/worker", git(repo, "branch", "--format=%(refname:short)"))

    def test_apply_removes_detached_mutable_worktree_without_creating_a_branch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo, parent, workspace, registry = self.fixture(Path(temp_dir), attached=False)

            result = reconcile_cleanup(repo_root=repo, worktree_parent=parent, registry=registry, apply=True)

            self.assertEqual(result["removed"], ["run-1-worker"])
            self.assertFalse(workspace.exists())
            self.assertNotIn("seneschal/", git(repo, "branch", "--format=%(refname:short)"))

    def test_preserves_active_and_unregistered_worktrees(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo, parent, workspace, registry = self.fixture(root)
            registry["entries"][0]["lifecycle_status"] = "active"
            unregistered = parent / "run-2" / "worker"
            unregistered.parent.mkdir(parents=True)
            git(repo, "worktree", "add", "-q", "-b", "seneschal/run-2/worker", str(unregistered), "HEAD")

            result = reconcile_cleanup(repo_root=repo, worktree_parent=parent, registry=registry, apply=True)

            self.assertTrue(workspace.exists())
            self.assertTrue(unregistered.exists())
            self.assertEqual(result["retained"][0]["reasons"], ["status=active"])
            self.assertIn(os.path.normcase(str(unregistered.resolve())), result["unregistered_worktrees"])
            self.assertIn("seneschal/run-2/worker", result["unregistered_branches"])

    def test_rejects_cleanup_path_outside_run_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo, parent, _, registry = self.fixture(root)
            registry["entries"][0]["path"] = str(root / "outside")

            with self.assertRaisesRegex(ValueError, "run-specific worktree parent"):
                reconcile_cleanup(repo_root=repo, worktree_parent=parent, registry=registry, apply=False)

    def test_preserves_workspace_when_artifact_hash_has_changed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo, parent, workspace, registry = self.fixture(root)
            artifact = Path(registry["entries"][0]["durable_artifacts"][0]["path"])
            artifact.write_text("tampered\n", encoding="utf-8")

            result = reconcile_cleanup(repo_root=repo, worktree_parent=parent, registry=registry, apply=True)

            self.assertTrue(workspace.exists())
            self.assertIn("artifact-hash-mismatch", result["retained"][0]["reasons"][0])

    def test_retries_branch_only_cleanup_after_worktree_was_already_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo, parent, workspace, registry = self.fixture(root)
            git(repo, "worktree", "remove", "--force", str(workspace))

            result = reconcile_cleanup(repo_root=repo, worktree_parent=parent, registry=registry, apply=True)

            self.assertEqual(result["removed"], ["run-1-worker"])
            self.assertNotIn("seneschal/run-1/worker", git(repo, "branch", "--format=%(refname:short)"))

    def test_reports_fully_absent_workspace_as_already_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo, parent, workspace, registry = self.fixture(root, attached=False)
            git(repo, "worktree", "remove", "--force", str(workspace))

            result = reconcile_cleanup(repo_root=repo, worktree_parent=parent, registry=registry, apply=True)

            self.assertEqual(result["already_removed"], ["run-1-worker"])


if __name__ == "__main__":
    unittest.main()
