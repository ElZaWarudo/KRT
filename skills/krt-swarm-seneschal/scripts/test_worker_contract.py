#!/usr/bin/env python3
"""Tests for executable worker contracts and cross-lane evaluation."""

from __future__ import annotations

import json
import shlex
import tempfile
import unittest
from pathlib import Path

from evaluate_worker_run import (
    TERMINAL_FIELDS,
    evaluate_worker_run,
    validate_worker_terminal,
)
from worker_contract import (
    TOP_LEVEL_FIELDS,
    TERMINAL_VALIDATOR,
    materialize_contract,
    preflight_contract_commands,
    terminal_validation_command,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PREFIX = shlex.join(["rtk", "python3", TERMINAL_VALIDATOR])
VALIDATOR_COMMAND = terminal_validation_command(
    "contract.json", "/tmp/run-1-unit-1-terminal.json"
)


class WorkerContractTest(unittest.TestCase):
    def draft(self, **overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_version": 1,
            "contract_id": "run-1:unit-1",
            "unit_id": "unit-1",
            "lane": "standard",
            "profile": "luna",
            "objective": "Update the service behavior.",
            "owned_files": ["src/service.py"],
            "required_context": ["tests/test_service.py"],
            "closed_decisions": ["Preserve the public API."],
            "forbidden_changes": ["Do not change public APIs."],
            "acceptance_criteria": [
                {"id": "AC-1", "description": "Focused behavior passes."}
            ],
            "commands": {
                "exact": ["rtk prettier --write src/service.py"],
                "read_only_prefixes": [
                    "rtk read",
                    "rtk grep",
                    VALIDATOR_PREFIX,
                ],
                "verification": {
                    "focused": ["rtk pytest tests/test_service.py"],
                    "natural": [],
                    "max_retries_per_command": 1,
                },
            },
            "execution_budget": {
                "discovery_passes": 1,
                "implementation_rounds": 1,
                "fix_rounds": 2,
                "review_rounds": 1,
                "extra_verification": "forbidden",
                "max_elapsed_ms": 60_000,
            },
            "supervision": {"mode": "terminal-only", "transition_after_ms": 15_000},
            "terminal_protocol": {
                "return_when": [
                    "acceptance_criteria_resolved",
                    "required_checks_attempted",
                    "state_reconciled",
                ],
                "grace_actions": 0,
            },
            "terminal_schema": "worker-terminal-v1",
            "required_certifications": ["reviewer"],
            "evidence_policy": {
                "minimum_command_trust": "self-reported",
                "changed_files_source": "root-diff",
            },
        }
        value.update(overrides)
        return value

    def terminal(self, **overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "status": "done",
            "phase": "closeout",
            "remaining_actions": [],
            "terminal_ready": True,
            "acceptance_criteria_resolved": True,
            "acceptance_evidence": [
                {
                    "criterion_id": "AC-1",
                    "status": "satisfied",
                    "evidence": "Focused test passed.",
                }
            ],
            "last_required_command": "rtk pytest tests/test_service.py",
            "verification": {
                "attempted": [
                    {
                        "command": "rtk pytest tests/test_service.py",
                        "attempts": 1,
                        "outcome": "passed",
                    }
                ],
                "skipped": [],
            },
            "verification_commands_run": ["rtk pytest tests/test_service.py"],
            "unowned_failures": [],
        }
        value.update(overrides)
        return value

    def observation(
        self, contract: dict[str, object], **overrides: object
    ) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_version": 1,
            "contract_hash": contract["contract_hash"],
            "worker_id": "implementer-1",
            "profile": "luna",
            "started_at_ms": 1_000,
            "changed_files": ["src/service.py"],
            "changed_files_source": "root-diff",
            "diff_digest": "sha256:observed-diff",
            "checkpoint_count": 0,
            "interventions_sent": [],
            "first_change_at_ms": 2_000,
            "last_required_command_finished_at_ms": 4_000,
            "returned_at_ms": 5_000,
            "phase_duration_ms": {"implementation": 2_000},
            "command_evidence": {
                "trust": "self-reported",
                "commands": [
                    {"command": "rtk read src/service.py", "kind": "read-only"},
                    {
                        "command": "rtk prettier --write src/service.py",
                        "kind": "exact",
                    },
                    {
                        "command": "rtk pytest tests/test_service.py",
                        "kind": "verification",
                    },
                    {
                        "command": VALIDATOR_COMMAND,
                        "kind": "read-only",
                    },
                ],
            },
            "terminal_validation_command": VALIDATOR_COMMAND,
            "terminal_validation_exit_code": 0,
            "certifications": [],
            "final": self.terminal(),
        }
        value.update(overrides)
        return value

    def certificate(self, contract: dict[str, object], **overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "role": "reviewer",
            "actor_id": "reviewer-1",
            "status": "passed",
            "contract_hash": contract["contract_hash"],
            "diff_digest": "sha256:diff",
            "findings": [],
        }
        value.update(overrides)
        return value

    def test_materialized_contract_has_stable_verified_hash(self) -> None:
        first = materialize_contract(self.draft())
        second = materialize_contract(self.draft())

        self.assertEqual(first["contract_hash"], second["contract_hash"])
        self.assertIs(validate_contract(first), first)

    def test_code_validators_track_published_schemas(self) -> None:
        contract_schema = json.loads(
            (ROOT / "references" / "worker-contract.schema.json").read_text(
                encoding="utf-8"
            )
        )
        terminal_schema = json.loads(
            (ROOT / "references" / "worker-terminal.schema.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(set(contract_schema["required"]), TOP_LEVEL_FIELDS)
        self.assertEqual(set(terminal_schema["required"]), TERMINAL_FIELDS)

    def test_contract_rejects_lane_profile_mismatch_and_tampering(self) -> None:
        with self.assertRaisesRegex(ValueError, "requires profile"):
            materialize_contract(self.draft(profile="spark"))
        contract = materialize_contract(self.draft())
        contract["objective"] = "Tampered"
        with self.assertRaisesRegex(ValueError, "contract_hash"):
            validate_contract(contract)

    def test_contract_requires_positive_elapsed_budget(self) -> None:
        budget = {**self.draft()["execution_budget"], "max_elapsed_ms": 0}
        with self.assertRaisesRegex(ValueError, "max_elapsed_ms must be positive"):
            materialize_contract(self.draft(execution_budget=budget))

    def test_command_preflight_rejects_wrong_package_working_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            backend = root / "backend"
            backend.mkdir()
            (backend / "package.json").write_text("{}", encoding="utf-8")
            tests = root / "tests"
            tests.mkdir()
            (tests / "test_service.py").write_text("", encoding="utf-8")
            base_commands = self.draft()["commands"]
            contract = materialize_contract(
                self.draft(commands={**base_commands, "exact": ["rtk npm test"]})
            )

            with self.assertRaisesRegex(ValueError, "no package.json"):
                preflight_contract_commands(contract, repo_root=root)

            contract = materialize_contract(
                self.draft(
                    commands={
                        **base_commands,
                        "exact": ["rtk npm --prefix backend test"],
                    }
                )
            )
            result = preflight_contract_commands(contract, repo_root=root)

        self.assertGreater(result["commands_checked"], 0)

    def test_command_preflight_rejects_missing_verification_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            contract = materialize_contract(self.draft(required_certifications=[]))

            with self.assertRaisesRegex(ValueError, "path does not exist"):
                preflight_contract_commands(contract, repo_root=root)

    def test_command_preflight_rejects_cwd_changes_and_chains(self) -> None:
        for command in ("rtk cd backend", "rtk pytest tests/ && rtk lint"):
            with self.subTest(command=command):
                base_commands = self.draft()["commands"]
                contract = materialize_contract(
                    self.draft(commands={**base_commands, "exact": [command]})
                )
                with self.assertRaisesRegex(
                    ValueError, "must not change cwd or chain"
                ):
                    preflight_contract_commands(contract, repo_root=Path.cwd())

    def test_valid_terminal_waits_for_independent_certification(self) -> None:
        contract = materialize_contract(self.draft())
        result = evaluate_worker_run(contract, self.observation(contract), now_ms=5_000)

        self.assertEqual(result["action"], "awaiting_certification")
        self.assertEqual(result["pending_certifications"], ["reviewer"])

    def test_independently_certified_terminal_completes(self) -> None:
        contract = materialize_contract(self.draft())
        observation = self.observation(
            contract,
            certifications=[
                self.certificate(contract, diff_digest="sha256:observed-diff")
            ],
        )
        result = evaluate_worker_run(contract, observation, now_ms=5_000)

        self.assertEqual(result["action"], "complete")
        self.assertEqual(result["evidence_trust"], "self-reported")
        self.assertEqual(result["metrics"]["acceptance_latency_ms"], 4_000)

    def test_certificate_must_bind_the_root_observed_diff(self) -> None:
        contract = materialize_contract(self.draft())
        observation = self.observation(
            contract, certifications=[self.certificate(contract)]
        )

        result = evaluate_worker_run(contract, observation, now_ms=5_000)

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("certification-diff-digest-mismatch", result["reasons"])

    def test_fast_and_deep_lanes_use_the_same_terminal_evaluator(self) -> None:
        fast = materialize_contract(
            self.draft(
                lane="fast",
                profile="spark",
                required_certifications=[],
            )
        )
        fast_result = evaluate_worker_run(
            fast, self.observation(fast, profile="spark"), now_ms=5_000
        )

        deep = materialize_contract(
            self.draft(
                lane="deep",
                profile="luna_xhigh",
                supervision={
                    "mode": "discovery-checkpoint",
                    "transition_after_ms": 15_000,
                },
                required_certifications=[],
            )
        )
        checkpoint = {
            "event": "discovery_complete",
            "discovery_complete_at_ms": 1_400,
            "edit_path_found": True,
            "planned_files": ["src/service.py"],
            "evidence_digest": (
                "edit src/service.py | symbol=Service.run; owned additive edit "
                "path confirmed; why=this file owns the behavior."
            ),
        }
        deep_result = evaluate_worker_run(
            deep,
            self.observation(
                deep,
                profile="luna_xhigh",
                checkpoint_count=1,
                checkpoint=checkpoint,
                discovery_returned_at_ms=1_500,
                implementation_started_at_ms=1_600,
                interventions_sent=["dispatch_implementation"],
            ),
            now_ms=5_000,
        )

        self.assertEqual(fast_result["action"], "complete")
        self.assertEqual(deep_result["action"], "complete")

    def test_scope_and_command_violations_fail_closed(self) -> None:
        contract = materialize_contract(self.draft(required_certifications=[]))
        observation = self.observation(contract, changed_files=["src/other.py"])
        observation["command_evidence"] = {
            "trust": "self-reported",
            "commands": [
                {"command": "rtk npm install", "kind": "exact"},
                {
                    "command": "rtk pytest tests/test_service.py",
                    "kind": "verification",
                },
            ],
        }
        result = evaluate_worker_run(contract, observation, now_ms=5_000)

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("changed-file-outside-contract", result["reasons"])
        self.assertIn("command-outside-contract", result["reasons"])
        self.assertIn("exact-command-count-mismatch", result["reasons"])

    def test_read_only_prefix_cannot_hide_a_command_chain(self) -> None:
        contract = materialize_contract(self.draft(required_certifications=[]))
        observation = self.observation(contract)
        observation["command_evidence"] = {
            "trust": "self-reported",
            "commands": [
                {
                    "command": "rtk read src/service.py && rtk npm install",
                    "kind": "read-only",
                },
                {
                    "command": "rtk prettier --write src/service.py",
                    "kind": "exact",
                },
                {
                    "command": "rtk pytest tests/test_service.py",
                    "kind": "verification",
                },
            ],
        }

        result = evaluate_worker_run(contract, observation, now_ms=5_000)

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("command-outside-contract", result["reasons"])

    def test_blocked_terminal_may_stop_before_exact_commands(self) -> None:
        contract = materialize_contract(self.draft())
        terminal = self.terminal(
            status="blocked",
            acceptance_criteria_resolved=False,
            acceptance_evidence=[
                {
                    "criterion_id": "AC-1",
                    "status": "not_satisfied",
                    "evidence": "Required external capability is unavailable.",
                }
            ],
        )
        observation = self.observation(contract, final=terminal)
        observation["command_evidence"] = {
            "trust": "self-reported",
            "commands": [
                {
                    "command": "rtk pytest tests/test_service.py",
                    "kind": "verification",
                },
                {
                    "command": VALIDATOR_COMMAND,
                    "kind": "read-only",
                },
            ],
        }

        result = evaluate_worker_run(contract, observation, now_ms=5_000)

        self.assertEqual(result["action"], "complete")
        self.assertEqual(result["terminal_status"], "blocked")
        self.assertEqual(result["pending_certifications"], [])
        self.assertIsNone(result["metrics"]["acceptance_latency_ms"])

    def test_runtime_audit_requirement_rejects_self_report(self) -> None:
        policy = {
            "minimum_command_trust": "runtime-audited",
            "changed_files_source": "root-diff",
        }
        contract = materialize_contract(
            self.draft(required_certifications=[], evidence_policy=policy)
        )
        result = evaluate_worker_run(contract, self.observation(contract), now_ms=5_000)

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("command-evidence-trust-too-low", result["reasons"])

    def test_late_terminal_exceeds_elapsed_budget(self) -> None:
        contract = materialize_contract(self.draft(required_certifications=[]))
        observation = self.observation(contract, returned_at_ms=70_001)

        result = evaluate_worker_run(contract, observation, now_ms=70_001)

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("execution-elapsed-budget-exceeded", result["reasons"])
        self.assertTrue(result["metrics"]["elapsed_budget_exhausted"])

    def test_terminal_validation_must_be_the_final_observed_command(self) -> None:
        contract = materialize_contract(self.draft(required_certifications=[]))
        observation = self.observation(contract)
        observation["command_evidence"]["commands"].append(
            {"command": "rtk read src/service.py", "kind": "read-only"}
        )

        result = evaluate_worker_run(contract, observation, now_ms=5_000)

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("terminal-validation-not-final-command", result["reasons"])

    def test_terminal_validation_must_match_envelope_paths_and_pass(self) -> None:
        contract = materialize_contract(self.draft(required_certifications=[]))
        wrong_path = self.observation(contract)
        wrong_path["command_evidence"]["commands"][-1]["command"] = (
            terminal_validation_command(
                "other.json", "/tmp/run-1-unit-1-terminal.json"
            )
        )
        failed = self.observation(contract, terminal_validation_exit_code=1)

        for observation in (wrong_path, failed):
            with self.subTest(observation=observation):
                result = evaluate_worker_run(contract, observation, now_ms=5_000)
                self.assertEqual(result["action"], "contract_violation")
                self.assertIn("terminal-validation-not-final-command", result["reasons"])

    def test_acceptance_evidence_must_map_every_criterion(self) -> None:
        contract = materialize_contract(self.draft(required_certifications=[]))
        result = evaluate_worker_run(
            contract,
            self.observation(contract, final=self.terminal(acceptance_evidence=[])),
            now_ms=5_000,
        )

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("acceptance-evidence-incomplete", result["reasons"])

    def test_terminal_schema_rejects_unknown_fields(self) -> None:
        contract = materialize_contract(self.draft(required_certifications=[]))
        result = evaluate_worker_run(
            contract,
            self.observation(contract, final=self.terminal(extra_claim=True)),
            now_ms=5_000,
        )

        self.assertEqual(result["action"], "contract_violation")
        self.assertIn("terminal-schema-unknown-fields", result["reasons"])

    def test_worker_side_terminal_validation_accepts_exact_shape(self) -> None:
        contract = materialize_contract(self.draft(required_certifications=[]))
        terminal = self.terminal()

        self.assertIs(validate_worker_terminal(contract, terminal), terminal)

    def test_worker_side_terminal_validation_rejects_common_protocol_errors(self) -> None:
        contract = materialize_contract(self.draft(required_certifications=[]))
        invalid_terminals = [
            self.terminal(phase="verification"),
            {key: value for key, value in self.terminal().items() if key != "unowned_failures"},
            self.terminal(verification_commands_run={"command": "rtk pytest tests/test_service.py"}),
        ]

        for terminal in invalid_terminals:
            with self.subTest(terminal=terminal):
                with self.assertRaisesRegex(ValueError, "invalid worker terminal"):
                    validate_worker_terminal(contract, terminal)


if __name__ == "__main__":
    unittest.main()
