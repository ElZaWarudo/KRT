#!/usr/bin/env python3
"""Tests for deterministic commit guardrails."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class CommitGuardTest(unittest.TestCase):
    def test_guard_creates_ignore_and_proves_secret_path_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)

            completed = subprocess.run(
                [sys.executable, str(ROOT / "ensure_krt_env_ignore.py"), "--root", str(root)],
                text=True,
                capture_output=True,
                check=False,
            )
            data = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(data["ok"])
            self.assertTrue(data["changed"])
            self.assertEqual((root / ".krt/env/.gitignore").read_text(encoding="utf-8"), "*\n!.gitignore\n!*.example\n")

            ignored = subprocess.run(
                ["git", "check-ignore", "-q", ".krt/env/jira-scribe.env"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(ignored.returncode, 0)

    def test_guard_blocks_if_secret_path_is_tracked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            secret = root / ".krt/env/jira-scribe.env"
            secret.parent.mkdir(parents=True)
            secret.write_text("JIRA_API_TOKEN=tracked\n", encoding="utf-8")
            subprocess.run(["git", "add", "-f", ".krt/env/jira-scribe.env"], cwd=root, text=True, check=True)

            completed = subprocess.run(
                [sys.executable, str(ROOT / "ensure_krt_env_ignore.py"), "--root", str(root)],
                text=True,
                capture_output=True,
                check=False,
            )
            data = json.loads(completed.stdout)

            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(data["ok"])
            self.assertIn("secret-env-tracked:.krt/env/jira-scribe.env", data["block_reasons"])

    def test_create_approved_commit_commits_exact_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "agent@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Agent"], cwd=root, check=True)
            (root / "README.md").write_text("hello\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "create_approved_commit.py"),
                    "--root",
                    str(root),
                    "--message",
                    "docs(readme): add project overview",
                    "--path",
                    "README.md",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            data = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(data["ok"])
            self.assertEqual(data["committed_paths"], ["README.md"])
            log = subprocess.run(["git", "log", "-1", "--pretty=%s"], cwd=root, text=True, capture_output=True, check=True)
            self.assertEqual(log.stdout.strip(), "docs(readme): add project overview")

    def test_create_approved_commit_blocks_dirty_index_before_staging(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "agent@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Agent"], cwd=root, check=True)
            (root / "README.md").write_text("hello\n", encoding="utf-8")
            (root / "notes.md").write_text("secret extra\n", encoding="utf-8")
            subprocess.run(["git", "add", "notes.md"], cwd=root, check=True)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "create_approved_commit.py"),
                    "--root",
                    str(root),
                    "--message",
                    "docs(readme): add project overview",
                    "--path",
                    "README.md",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            data = json.loads(completed.stdout)

            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(data["ok"])
            self.assertIn("index-not-clean", data["block_reasons"])
            self.assertEqual(data["staged_paths"], ["notes.md"])

    def test_create_approved_commit_can_reset_index_when_approved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "agent@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Agent"], cwd=root, check=True)
            (root / "README.md").write_text("hello\n", encoding="utf-8")
            (root / "notes.md").write_text("staged first\n", encoding="utf-8")
            subprocess.run(["git", "add", "notes.md"], cwd=root, check=True)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "create_approved_commit.py"),
                    "--root",
                    str(root),
                    "--message",
                    "docs(readme): add project overview",
                    "--path",
                    "README.md",
                    "--reset-index-approved",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            data = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(data["ok"])
            self.assertTrue(data["reset_index"])
            self.assertEqual(data["previous_staged_count"], 1)
            self.assertEqual(data["committed_paths"], ["README.md"])
            status = subprocess.run(["git", "status", "--short"], cwd=root, text=True, capture_output=True, check=True)
            self.assertIn("?? notes.md", status.stdout)

    def test_create_approved_commit_blocks_secret_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "agent@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Agent"], cwd=root, check=True)
            secret = root / ".krt/env/jira-scribe.env"
            secret.parent.mkdir(parents=True)
            secret.write_text("JIRA_API_TOKEN=real-token\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "create_approved_commit.py"),
                    "--root",
                    str(root),
                    "--message",
                    "chore(config): add jira setup",
                    "--path",
                    ".krt/env/jira-scribe.env",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            data = json.loads(completed.stdout)

            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(data["ok"])
            self.assertIn("secret-env-path-planned:.krt/env/jira-scribe.env", data["block_reasons"])

    def test_create_approved_commit_blocks_secret_like_assignment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "agent@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Agent"], cwd=root, check=True)
            (root / "config.example").write_text("JIRA_API_TOKEN=real-token\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "create_approved_commit.py"),
                    "--root",
                    str(root),
                    "--message",
                    "docs(config): add jira example",
                    "--path",
                    "config.example",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            data = json.loads(completed.stdout)

            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(data["ok"])
            self.assertIn("secret-like-env-assignment:JIRA_API_TOKEN", data["block_reasons"])

    def test_create_approved_commit_allows_non_secret_project_key_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "agent@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Agent"], cwd=root, check=True)
            (root / ".krt/env").mkdir(parents=True)
            (root / ".krt/env/jira-scribe.env.example").write_text(
                "JIRA_PROJECT_KEY=KRT\nJIRA_API_TOKEN=replace-with-token\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "create_approved_commit.py"),
                    "--root",
                    str(root),
                    "--message",
                    "docs(config): add jira env example",
                    "--path",
                    ".krt/env/jira-scribe.env.example",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            data = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(data["ok"])
            self.assertEqual(data["committed_paths"], [".krt/env/jira-scribe.env.example"])

    def test_create_approved_commit_allows_dotenv_example_placeholders(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            subprocess.run(["git", "config", "user.email", "agent@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Agent"], cwd=root, check=True)
            (root / ".env.example").write_text(
                "JIRA_HOST=jira.example.com\nJIRA_PROJECT_KEY=KRT\nJIRA_API_TOKEN=replace-with-token\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "create_approved_commit.py"),
                    "--root",
                    str(root),
                    "--message",
                    "docs(config): add env example",
                    "--path",
                    ".env.example",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            data = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(data["ok"])
            self.assertEqual(data["committed_paths"], [".env.example"])

    def test_create_approved_commit_blocks_bad_message_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            (root / "README.md").write_text("hello\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "create_approved_commit.py"),
                    "--root",
                    str(root),
                    "--message",
                    "Update README.",
                    "--path",
                    "README.md",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            data = json.loads(completed.stdout)

            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(data["ok"])
            self.assertIn("commit-message-format", data["block_reasons"])


if __name__ == "__main__":
    unittest.main()
