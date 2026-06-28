#!/usr/bin/env python3
"""Fixture tests for autonomous Jira validators."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures" / "jira-autonomy"
SECRET_ENV_CONTENT = "\n".join(
    [
        "JIRA_CLOUD_HOST=example.atlassian.net",
        "JIRA_CLOUD_EMAIL=bot@example.com",
        "JIRA_CLOUD_" "API_TOKEN=token",
        "JIRA_CLOUD_PROJECT_KEY=KRT",
        "",
        "# Optional",
        "JIRA_CLOUD_BOARD_ID=12",
        "",
    ]
)


def run(script: str, mutation: str, fixture: str, *extra: str) -> tuple[int, dict]:
    cmd = [
        sys.executable,
        str(ROOT / script),
        "--mutation-class",
        mutation,
        "--fixture",
        str(FIXTURES / fixture),
        "--target",
        "jira_project=KRT",
        "--target",
        "jira_key=KRT-42",
        "--target",
        "pr_url=https://github.com/acme/widgets/pull/42",
        *extra,
    ]
    completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
    return completed.returncode, json.loads(completed.stdout)


class JiraAutonomyTest(unittest.TestCase):
    def write_secret_env(self, root: Path) -> None:
        (root / ".krt/env/jira-cloud-scribe.env").write_text(SECRET_ENV_CONTENT, encoding="utf-8")

    def test_check_jira_env_reports_not_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)

            completed = subprocess.run(
                [sys.executable, str(ROOT / "check_jira_env.py"), "--root", str(root)],
                text=True,
                capture_output=True,
                check=False,
            )
            result = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertFalse(result["ok"])
            self.assertEqual(result["diagnosis"], "jira-env-not-configured")
            self.assertIn("JIRA_CLOUD_HOST", result["missing_required_vars"])

    def test_check_jira_env_reports_secret_file_not_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            subprocess.run(
                [sys.executable, str(ROOT / "setup_jira_env.py"), "--root", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )
            self.write_secret_env(root)

            completed = subprocess.run(
                [sys.executable, str(ROOT / "check_jira_env.py"), "--root", str(root), "--no-auto-load"],
                text=True,
                capture_output=True,
                check=False,
            )
            result = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertFalse(result["ok"])
            self.assertEqual(result["diagnosis"], "env-file-present-but-not-loaded")
            self.assertTrue(result["project_files"]["secret_env_exists"])

    def test_check_jira_env_auto_loads_secret_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            subprocess.run(
                [sys.executable, str(ROOT / "setup_jira_env.py"), "--root", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )
            self.write_secret_env(root)

            completed = subprocess.run(
                [sys.executable, str(ROOT / "check_jira_env.py"), "--root", str(root)],
                text=True,
                capture_output=True,
                check=False,
            )
            result = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(result["ok"])
            self.assertEqual(result["diagnosis"], "ready")
            self.assertEqual(
                result["auto_loaded_vars"],
                [
                    "JIRA_CLOUD_HOST",
                    "JIRA_CLOUD_EMAIL",
                    "JIRA_CLOUD_API_TOKEN",
                    "JIRA_CLOUD_PROJECT_KEY",
                    "JIRA_CLOUD_BOARD_ID",
                ],
            )

    def test_check_jira_env_strict_fails_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)

            completed = subprocess.run(
                [sys.executable, str(ROOT / "check_jira_env.py"), "--root", str(root), "--strict"],
                text=True,
                capture_output=True,
                check=False,
            )
            result = json.loads(completed.stdout)

            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(result["ok"])

    def test_check_jira_env_rejects_vars_without_project_secret_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            env = os.environ.copy()
            env["JIRA_CLOUD_HOST"] = "example.atlassian.net"
            env["JIRA_CLOUD_EMAIL"] = "bot@example.com"
            env["JIRA_CLOUD_API_TOKEN"] = "token"
            env["JIRA_CLOUD_PROJECT_KEY"] = "KRT"

            completed = subprocess.run(
                [sys.executable, str(ROOT / "check_jira_env.py"), "--root", str(root)],
                text=True,
                capture_output=True,
                check=False,
                env=env,
            )
            result = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertFalse(result["ok"])
            self.assertEqual(result["diagnosis"], "env-loaded-without-project-secret-file")

    def test_run_with_jira_env_executes_command_with_loaded_vars(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            subprocess.run(
                [sys.executable, str(ROOT / "setup_jira_env.py"), "--root", str(root)],
                text=True,
                capture_output=True,
                check=True,
            )
            self.write_secret_env(root)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "run_with_jira_env.py"),
                    "--root",
                    str(root),
                    "--",
                    sys.executable,
                    "-c",
                    (
                        "import json, os; print(json.dumps({"
                        "'host': os.environ.get('JIRA_CLOUD_HOST'), "
                        "'project': os.environ.get('JIRA_CLOUD_PROJECT_KEY'), "
                        "'email': os.environ.get('JIRA_CLOUD_EMAIL')}))"
                    ),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertEqual(result["host"], "example.atlassian.net")
            self.assertEqual(result["project"], "KRT")
            self.assertEqual(result["email"], "bot@example.com")

    def test_spanish_text_accepts_semantic_copy(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "check_jira_text.py"), "--text", "Crear una tarea para validar el flujo con auditoria"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)

    def test_spanish_text_rejects_operational_ids(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "check_jira_text.py"), "--text", "feat: RDM-001 RU1 merge PR"],
            text=True,
            capture_output=True,
            check=False,
        )
        result = json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        self.assertTrue(any(reason.startswith("forbidden-pattern:") for reason in result["block_reasons"]))

    def test_issue_payload_validates(self) -> None:
        code, result = run("check_jira_issue_mutation.py", "jira_create", "issue_valid.json")
        self.assertEqual(code, 0, result)

    def test_issue_bad_text_blocks(self) -> None:
        code, result = run("check_jira_issue_mutation.py", "jira_create", "issue_bad_text.json")
        self.assertNotEqual(code, 0)
        self.assertTrue(any(reason.startswith("summary:") for reason in result["block_reasons"]))

    def test_backlink_existing_is_noop(self) -> None:
        code, result = run("check_jira_binding.py", "jira_backlink", "binding_existing.json")
        self.assertEqual(code, 0, result)
        self.assertIn("backlink-already-present", result["warnings"])

    def test_conflicting_backlink_blocks(self) -> None:
        code, result = run("check_jira_binding.py", "jira_backlink", "binding_conflict.json")
        self.assertNotEqual(code, 0)
        self.assertIn("jira-linked-to-different-pr", result["block_reasons"])

    def test_backlink_requires_pr_url(self) -> None:
        cmd = [
            sys.executable,
            str(ROOT / "check_jira_binding.py"),
            "--mutation-class",
            "jira_backlink",
            "--fixture",
            str(FIXTURES / "binding_existing.json"),
            "--target",
            "jira_key=KRT-42",
        ]
        completed = subprocess.run(cmd, text=True, capture_output=True, check=False)
        result = json.loads(completed.stdout)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("missing-pr-url", result["block_reasons"])

    def test_review_transition_requires_exact_transition(self) -> None:
        code, result = run("check_jira_transition.py", "jira_transition_review", "transition_review.json")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["live_state_summary"]["action"], "transition:21")

    def test_done_transition_requires_merged_pr(self) -> None:
        code, result = run("check_jira_transition.py", "jira_transition_done", "transition_done.json")
        self.assertEqual(code, 0, result)

    def test_multiple_done_transitions_block(self) -> None:
        code, result = run("check_jira_transition.py", "jira_transition_done", "transition_multiple_done.json")
        self.assertNotEqual(code, 0)
        self.assertIn("multiple-done-transitions", result["block_reasons"])

    def test_already_done_is_noop_success(self) -> None:
        code, result = run("check_jira_transition.py", "jira_transition_done", "transition_already_done.json")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["live_state_summary"]["action"], "noop-already-done")

    def test_already_done_without_pr_binding_blocks(self) -> None:
        code, result = run("check_jira_transition.py", "jira_transition_done", "transition_already_done_unbound.json")
        self.assertNotEqual(code, 0)
        self.assertIn("pr-remote-link-missing-or-mismatch", result["block_reasons"])

    def test_setup_jira_env_creates_ignored_secret_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)

            completed = subprocess.run(
                [sys.executable, str(ROOT / "setup_jira_env.py"), "--root", str(root)],
                text=True,
                capture_output=True,
                check=False,
            )
            result = json.loads(completed.stdout)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(result["ok"])
            self.assertTrue((root / ".krt/env/.gitignore").exists())
            self.assertTrue((root / ".krt/env/jira-cloud-scribe.env").exists())
            self.assertTrue((root / ".krt/env/jira-cloud-scribe.env.example").exists())

            ignored = subprocess.run(
                ["git", "check-ignore", "-q", ".krt/env/jira-cloud-scribe.env"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(ignored.returncode, 0)

    def test_setup_jira_env_blocks_tracked_secret_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, text=True, capture_output=True, check=True)
            secret = root / ".krt/env/jira-cloud-scribe.env"
            secret.parent.mkdir(parents=True)
            secret.write_text("JIRA_CLOUD_" "API_TOKEN=already-tracked\n", encoding="utf-8")
            subprocess.run(["git", "add", "-f", ".krt/env/jira-cloud-scribe.env"], cwd=root, text=True, check=True)

            completed = subprocess.run(
                [sys.executable, str(ROOT / "setup_jira_env.py"), "--root", str(root)],
                text=True,
                capture_output=True,
                check=False,
            )
            result = json.loads(completed.stdout)

            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse(result["ok"])
            self.assertEqual(result["reason"], "secret-env-already-tracked")


if __name__ == "__main__":
    unittest.main()
