#!/usr/bin/env python3
"""Focused checks for the Muse Code worker boundary."""

from __future__ import annotations

import json
from pathlib import Path
from subprocess import CompletedProcess
import tempfile
import unittest
from unittest.mock import patch

from run_muse_implementer import MODEL, REQUIRED_FLAGS, run_muse, validate_terminal

GOOD_TERMINAL = {
    "status": "done",
    "summary": "Fixed the off-by-one in pagination.",
    "changed_files": ["src/pager.py"],
    "checks": [{"command": "pytest tests/test_pager.py", "result": "passed"}],
    "blockers": [],
}


class MuseImplementerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "worker"
        self.workspace.mkdir()
        (self.workspace / ".git").write_text("gitdir: elsewhere", encoding="utf-8")
        self.assignment = self.root / "assignment.md"
        self.assignment.write_text("Fix pagination. Own src/pager.py. Check: pytest tests/test_pager.py\n")
        self.terminal_path = self.root / "terminal.json"
        self.log_path = self.root / "run.jsonl"

    def call(self, **overrides):
        kwargs = dict(
            assignment_path=self.assignment, workspace=self.workspace,
            terminal_path=self.terminal_path, log_path=self.log_path, max_model_steps=5,
        )
        kwargs.update(overrides)
        return run_muse(**kwargs)

    def fake_run(self, terminal: object | None):
        def run(argv, **kwargs):
            if argv[1:3] == ["exec", "--help"]:
                return CompletedProcess(argv, 0, " ".join(REQUIRED_FLAGS), "")
            self.assertIn(MODEL, argv)
            self.assertEqual(argv[argv.index("--workspace") + 1], str(self.workspace))
            self.assertEqual(argv[argv.index("--approval-mode") + 1], "never")
            if terminal is not None:
                self.terminal_path.write_text(json.dumps(terminal), encoding="utf-8")
            return CompletedProcess(argv, 0, "", "")
        return run

    def patched(self, terminal: object | None):
        return (
            patch("run_muse_implementer.shutil.which", return_value="/bin/muse"),
            patch("run_muse_implementer.subprocess.run", side_effect=self.fake_run(terminal)),
        )

    def test_rejects_log_inside_worker_workspace(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside the worker worktree"):
            self.call(log_path=self.workspace / "run.jsonl")

    def test_rejects_reused_terminal_path(self) -> None:
        self.terminal_path.write_text("{}")
        with self.assertRaisesRegex(ValueError, "fresh paths"):
            self.call()

    def test_missing_muse_is_a_dispatch_blocker(self) -> None:
        with patch("run_muse_implementer.shutil.which", return_value=None):
            with self.assertRaisesRegex(ValueError, "unavailable"):
                self.call()

    def test_requires_terminal_artifact(self) -> None:
        which, run = self.patched(None)
        with which, run, self.assertRaisesRegex(RuntimeError, "terminal artifact"):
            self.call()

    def test_rejects_invalid_terminal(self) -> None:
        which, run = self.patched({"status": "blocked", "summary": "x", "changed_files": [],
                                   "checks": [], "blockers": []})
        with which, run, self.assertRaisesRegex(RuntimeError, "requires at least one blocker"):
            self.call()

    def test_success_returns_only_diagnostic_evidence(self) -> None:
        which, run = self.patched(GOOD_TERMINAL)
        with which, run:
            result = self.call()
        self.assertEqual(result["model"], MODEL)
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["command_trust"], "self-reported")
        self.assertEqual(result["readiness"], "requires-caller-diff-inspection-and-verification")

    def test_validate_terminal_flags_bad_check_result(self) -> None:
        bad = dict(GOOD_TERMINAL, checks=[{"command": "pytest", "result": "green"}])
        self.assertTrue(validate_terminal(bad))
        self.assertEqual(validate_terminal(GOOD_TERMINAL), [])


if __name__ == "__main__":
    unittest.main()
