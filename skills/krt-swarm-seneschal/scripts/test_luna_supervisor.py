#!/usr/bin/env python3
"""Tests for the lightweight Luna supervision state machine."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from evaluate_luna_run import evaluate_run


SCRIPT = Path(__file__).with_name("evaluate_luna_run.py")


class LunaSupervisorTest(unittest.TestCase):
    def observation(self, **overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_version": 1,
            "profile": "luna_xhigh",
            "started_at_ms": 1_000,
            "owned_files": ["src/service.py"],
            "checkpoint_count": 0,
            "verification_manifest": {
                "focused": ["pytest tests/test_service.py"],
                "natural": ["pytest tests/"],
                "max_retries_per_command": 1,
            },
            "interventions_sent": [],
        }
        value.update(overrides)
        return value

    def terminal_result(self, **overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "status": "done",
            "phase": "closeout",
            "remaining_actions": [],
            "terminal_ready": True,
            "acceptance_criteria_resolved": True,
            "last_required_command": "pytest tests/",
            "verification": {
                "attempted": [
                    {
                        "command": "pytest tests/test_service.py",
                        "attempts": 1,
                        "outcome": "passed",
                    },
                    {
                        "command": "pytest tests/",
                        "attempts": 1,
                        "outcome": "passed",
                    },
                ],
                "skipped": [],
            },
            "verification_commands_run": [
                "pytest tests/test_service.py",
                "pytest tests/",
            ],
            "unowned_failures": [],
        }
        value.update(overrides)
        return value

    def test_xhigh_transitions_when_checkpoint_stalls_before_first_change(self) -> None:
        result = evaluate_run(
            self.observation(
                checkpoint_count=1,
                checkpoint={
                    "discovery_complete_at_ms": 5_000,
                    "edit_path_found": True,
                    "planned_files": ["src/service.py"],
                }
            ),
            now_ms=20_000,
            transition_after_ms=10_000,
        )

        self.assertEqual(result["action"], "transition_to_implementation")
        self.assertEqual(result["metrics"]["root_interventions"], 0)

    def test_xhigh_does_not_repeat_sent_transition(self) -> None:
        result = evaluate_run(
            self.observation(
                checkpoint_count=1,
                checkpoint={
                    "discovery_complete_at_ms": 5_000,
                    "edit_path_found": True,
                    "planned_files": ["src/service.py"],
                },
                interventions_sent=["transition_to_implementation"],
            ),
            now_ms=20_000,
            transition_after_ms=10_000,
        )

        self.assertEqual(result["action"], "continue")
        self.assertEqual(result["metrics"]["root_interventions"], 1)

    def test_xhigh_returns_when_discovery_finds_no_safe_edit_path(self) -> None:
        result = evaluate_run(
            self.observation(
                checkpoint_count=1,
                checkpoint={
                    "discovery_complete_at_ms": 5_000,
                    "edit_path_found": False,
                    "planned_files": [],
                }
            ),
            now_ms=5_001,
        )

        self.assertEqual(result["action"], "return_needs_review")

    def test_standard_luna_has_no_live_checkpoint_requirement(self) -> None:
        result = evaluate_run(
            self.observation(profile="luna"),
            now_ms=20_000,
        )

        self.assertEqual(result["action"], "continue")

    def test_standard_luna_rejects_live_checkpoint(self) -> None:
        result = evaluate_run(
            self.observation(
                profile="luna",
                checkpoint_count=1,
                checkpoint={
                    "discovery_complete_at_ms": 5_000,
                    "edit_path_found": True,
                    "planned_files": ["src/service.py"],
                },
            ),
            now_ms=20_000,
        )

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("unexpected-checkpoint", result["reasons"])

    def test_terminal_ready_without_return_requires_immediate_return(self) -> None:
        result = evaluate_run(
            self.observation(
                checkpoint_count=1,
                checkpoint={
                    "discovery_complete_at_ms": 5_000,
                    "edit_path_found": True,
                    "planned_files": ["src/service.py"],
                },
                final=self.terminal_result(),
                last_required_command_finished_at_ms=30_000,
            ),
            now_ms=30_001,
        )

        self.assertEqual(result["action"], "return_now")

    def test_returned_run_calculates_closeout_metrics(self) -> None:
        result = evaluate_run(
            self.observation(
                checkpoint_count=1,
                checkpoint={
                    "discovery_complete_at_ms": 5_000,
                    "edit_path_found": True,
                    "planned_files": ["src/service.py"],
                },
                first_change_at_ms=7_000,
                phase_duration_ms={"discovery": 4_000, "implementation": 8_000},
                last_required_command_finished_at_ms=30_000,
                returned_at_ms=31_000,
                final=self.terminal_result(),
            ),
            now_ms=31_000,
        )

        self.assertEqual(result["action"], "complete")
        self.assertEqual(result["metrics"]["time_to_first_change_ms"], 6_000)
        self.assertEqual(result["metrics"]["discovery_implementation_ratio"], 0.5)
        self.assertEqual(
            result["metrics"]["last_required_command_to_return_ms"], 1_000
        )
        self.assertEqual(result["metrics"]["out_of_manifest_commands"], 0)

    def test_unmanifested_verification_is_a_contract_violation(self) -> None:
        result = evaluate_run(
            self.observation(
                returned_at_ms=31_000,
                checkpoint_count=1,
                checkpoint={
                    "discovery_complete_at_ms": 5_000,
                    "edit_path_found": True,
                    "planned_files": ["src/service.py"],
                },
                final=self.terminal_result(
                    last_required_command="npm run ci",
                    verification={
                        "attempted": [
                            {
                                "command": "npm run ci",
                                "attempts": 1,
                                "outcome": "passed",
                            }
                        ],
                        "skipped": [],
                    },
                    verification_commands_run=["npm run ci"],
                ),
            ),
            now_ms=31_000,
        )

        self.assertEqual(result["action"], "contract_violation")
        self.assertEqual(result["metrics"]["out_of_manifest_commands"], 1)
        self.assertIn("verification-command-outside-manifest", result["reasons"])

    def test_invalid_terminal_shape_is_a_contract_violation(self) -> None:
        result = evaluate_run(
            self.observation(
                returned_at_ms=31_000,
                checkpoint_count=1,
                checkpoint={
                    "discovery_complete_at_ms": 5_000,
                    "edit_path_found": True,
                    "planned_files": ["src/service.py"],
                },
                final=self.terminal_result(
                    phase="verification",
                    remaining_actions=["one more check"],
                    last_required_command=None,
                    verification={
                        "attempted": [],
                        "skipped": [
                            {
                                "command": "pytest tests/test_service.py",
                                "reason": "verification phase did not finish",
                            },
                            {
                                "command": "pytest tests/",
                                "reason": "verification phase did not finish",
                            },
                        ],
                    },
                    verification_commands_run=[],
                ),
            ),
            now_ms=31_000,
        )

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("invalid-terminal-shape", result["reasons"])

    def test_terminal_result_must_account_for_every_manifest_command(self) -> None:
        result = evaluate_run(
            self.observation(
                profile="luna",
                returned_at_ms=31_000,
                final=self.terminal_result(
                    last_required_command=None,
                    verification={"attempted": [], "skipped": []},
                    verification_commands_run=[],
                ),
            ),
            now_ms=31_000,
        )

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("verification-manifest-incomplete", result["reasons"])

    def test_concretely_skipped_manifest_command_is_accounted_for(self) -> None:
        result = evaluate_run(
            self.observation(
                profile="luna",
                returned_at_ms=31_000,
                final=self.terminal_result(
                    status="needs_review",
                    acceptance_criteria_resolved=False,
                    last_required_command="pytest tests/test_service.py",
                    verification={
                        "attempted": [
                            {
                                "command": "pytest tests/test_service.py",
                                "attempts": 1,
                                "outcome": "passed",
                            }
                        ],
                        "skipped": [
                            {
                                "command": "pytest tests/",
                                "reason": "dependency unavailable",
                            }
                        ],
                    },
                    verification_commands_run=["pytest tests/test_service.py"],
                ),
            ),
            now_ms=31_000,
        )

        self.assertEqual(result["action"], "complete")
        self.assertEqual(result["terminal_status"], "needs_review")

    def test_retry_limit_and_last_required_command_are_enforced(self) -> None:
        result = evaluate_run(
            self.observation(
                profile="luna",
                returned_at_ms=31_000,
                final=self.terminal_result(
                    last_required_command="pytest tests/test_service.py",
                    verification={
                        "attempted": [
                            {
                                "command": "pytest tests/test_service.py",
                                "attempts": 3,
                                "outcome": "passed",
                            },
                            {
                                "command": "pytest tests/",
                                "attempts": 1,
                                "outcome": "passed",
                            },
                        ],
                        "skipped": [],
                    },
                    verification_commands_run=[
                        "pytest tests/test_service.py",
                        "pytest tests/test_service.py",
                        "pytest tests/test_service.py",
                        "pytest tests/",
                    ],
                ),
            ),
            now_ms=31_000,
        )

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("verification-retry-limit-exceeded", result["reasons"])
        self.assertIn("invalid-last-required-command", result["reasons"])

    def test_verification_commands_follow_manifest_order(self) -> None:
        result = evaluate_run(
            self.observation(
                profile="luna",
                returned_at_ms=31_000,
                final=self.terminal_result(
                    last_required_command="pytest tests/test_service.py",
                    verification_commands_run=[
                        "pytest tests/",
                        "pytest tests/test_service.py",
                    ],
                ),
            ),
            now_ms=31_000,
        )

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("verification-command-order-invalid", result["reasons"])

    def test_done_rejects_unresolved_acceptance_or_unowned_failures(self) -> None:
        result = evaluate_run(
            self.observation(
                profile="luna",
                returned_at_ms=31_000,
                final=self.terminal_result(
                    acceptance_criteria_resolved=False,
                    unowned_failures=["legacy failure"],
                ),
            ),
            now_ms=31_000,
        )

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("acceptance-criteria-unresolved", result["reasons"])
        self.assertIn("done-with-unowned-failures", result["reasons"])

    def test_xhigh_terminal_result_requires_exactly_one_checkpoint(self) -> None:
        result = evaluate_run(
            self.observation(returned_at_ms=31_000, final=self.terminal_result()),
            now_ms=31_000,
        )

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("invalid-checkpoint-count", result["reasons"])

    def test_xhigh_checkpoint_requires_nonempty_owned_planned_files(self) -> None:
        for checkpoint_count, planned_files, expected_reason in (
            (1, [], "checkpoint-missing-planned-files"),
            (1, ["src/unowned.py"], "checkpoint-plans-unowned-file"),
            (2, ["src/service.py"], "invalid-checkpoint-count"),
        ):
            with self.subTest(
                checkpoint_count=checkpoint_count, planned_files=planned_files
            ):
                result = evaluate_run(
                    self.observation(
                        checkpoint_count=checkpoint_count,
                        checkpoint={
                            "discovery_complete_at_ms": 5_000,
                            "edit_path_found": True,
                            "planned_files": planned_files,
                        },
                    ),
                    now_ms=20_000,
                )

                self.assertEqual(result["action"], "contract_violation")
                self.assertIn(expected_reason, result["reasons"])

    def test_checkpoint_without_edit_path_rejects_planned_files(self) -> None:
        result = evaluate_run(
            self.observation(
                checkpoint_count=1,
                checkpoint={
                    "discovery_complete_at_ms": 5_000,
                    "edit_path_found": False,
                    "planned_files": ["src/service.py"],
                },
            ),
            now_ms=5_001,
        )

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("checkpoint-has-unexpected-planned-files", result["reasons"])

    def test_reversed_timestamps_are_contract_violations(self) -> None:
        for overrides in (
            {"first_change_at_ms": 999},
            {"last_required_command_finished_at_ms": 32_000},
            {
                "last_required_command_finished_at_ms": 30_000,
                "returned_at_ms": 29_000,
                "final": self.terminal_result(),
            },
        ):
            with self.subTest(overrides=overrides):
                value = {
                    "profile": "luna",
                    "returned_at_ms": 31_000,
                    "final": self.terminal_result(),
                    **overrides,
                }
                result = evaluate_run(self.observation(**value), now_ms=31_000)

                self.assertEqual(result["action"], "contract_violation")
                self.assertIn("invalid-timestamp-order", result["reasons"])

    def test_cli_accepts_observation_on_stdin(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--now-ms", "20000"],
            input=json.dumps(
                self.observation(
                    checkpoint_count=1,
                    checkpoint={
                        "discovery_complete_at_ms": 5_000,
                        "edit_path_found": True,
                        "planned_files": ["src/service.py"],
                    }
                )
            ),
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout)["action"], "transition_to_implementation"
        )


if __name__ == "__main__":
    unittest.main()
