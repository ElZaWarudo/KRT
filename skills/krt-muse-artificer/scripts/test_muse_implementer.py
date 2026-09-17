#!/usr/bin/env python3
"""Focused checks for the external Muse Implementer boundary."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from run_muse_implementer import MODEL, run_muse

SENESCHAL_DIR = Path(__file__).resolve().parents[2] / "krt-swarm-seneschal"
SENESCHAL_SCRIPTS = SENESCHAL_DIR / "scripts"
sys.path.insert(0, str(SENESCHAL_SCRIPTS))
from worker_contract import materialize_contract


class MuseImplementerTest(unittest.TestCase):
    def setUp(self) -> None:
        from test_worker_contract import WorkerContractTest

        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "worker"
        self.workspace.mkdir()
        (self.workspace / ".git").write_text("gitdir: elsewhere", encoding="utf-8")
        contract = materialize_contract(
            WorkerContractTest().draft(profile="muse_contributor")
        )
        self.contract_path = self.root / "contract.json"
        self.contract_path.write_text(json.dumps(contract), encoding="utf-8")
        self.terminal_path = self.root / "terminal.json"
        self.log_path = self.root / "run.jsonl"

    def test_rejects_log_inside_worker_workspace(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside the worker worktree"):
            run_muse(
                seneschal_skill_dir=SENESCHAL_DIR,
                contract_path=self.contract_path, workspace=self.workspace,
                terminal_path=self.terminal_path,
                log_path=self.workspace / "run.jsonl", max_model_steps=5,
            )

    def test_invokes_exact_model_and_requires_terminal_artifact(self) -> None:
        from subprocess import CompletedProcess

        def fake_run(argv, **kwargs):
            if argv[1:3] == ["exec", "--help"]:
                return CompletedProcess(argv, 0, " ".join((
                    "--json", "--prompt-file", "--workspace", "--model",
                    "--max-model-steps", "--approval-mode", "--user-input-auto-resolve",
                    "--disable-web-tools", "--no-foreign-personal-context",
                    "--trust-workspace",
                )), "")
            self.assertIn(MODEL, argv)
            self.assertEqual(argv[argv.index("--workspace") + 1], str(self.workspace))
            self.assertIn("--trust-workspace", argv)
            return CompletedProcess(argv, 0, "", "")

        with patch("run_muse_implementer.shutil.which", return_value="/bin/muse"), patch(
            "run_muse_implementer.subprocess.run", side_effect=fake_run
        ):
            with self.assertRaisesRegex(RuntimeError, "terminal artifact"):
                run_muse(
                    seneschal_skill_dir=SENESCHAL_DIR,
                    contract_path=self.contract_path, workspace=self.workspace,
                    terminal_path=self.terminal_path,
                    log_path=self.log_path, max_model_steps=5,
                )

    def test_success_returns_only_diagnostic_evidence(self) -> None:
        from subprocess import CompletedProcess
        from test_worker_contract import WorkerContractTest

        def fake_run(argv, **kwargs):
            if argv[1:3] == ["exec", "--help"]:
                return CompletedProcess(argv, 0, " ".join((
                    "--json", "--prompt-file", "--workspace", "--model",
                    "--max-model-steps", "--approval-mode", "--user-input-auto-resolve",
                    "--disable-web-tools", "--no-foreign-personal-context",
                    "--trust-workspace",
                )), "")
            if argv[1] == "exec":
                self.terminal_path.write_text(
                    json.dumps(WorkerContractTest().terminal()), encoding="utf-8"
                )
            return CompletedProcess(argv, 0, "", "")

        with patch("run_muse_implementer.shutil.which", return_value="/bin/muse"), patch(
            "run_muse_implementer.subprocess.run", side_effect=fake_run
        ):
            result = run_muse(
                seneschal_skill_dir=SENESCHAL_DIR,
                contract_path=self.contract_path, workspace=self.workspace,
                terminal_path=self.terminal_path, log_path=self.log_path,
                max_model_steps=5,
            )
        self.assertEqual(result["model"], MODEL)
        self.assertEqual(result["command_trust"], "self-reported")
        self.assertEqual(result["readiness"], "requires-root-observation-and-verification")


if __name__ == "__main__":
    unittest.main()
