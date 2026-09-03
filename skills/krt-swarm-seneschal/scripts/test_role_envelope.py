#!/usr/bin/env python3
"""Tests for executable Reviewer and Fixer envelopes."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from persist_role_terminal import persist_role_terminal
from plan_review_wave import plan_review_wave
from render_role_envelope import render_role_envelope


class RoleEnvelopeTest(unittest.TestCase):
    def test_reviewer_envelope_uses_concrete_paths_and_optional_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            workspace = root / "workspace"
            artifacts = root / "artifacts"
            workspace.mkdir()
            artifacts.mkdir()
            assignment = artifacts / "review-plan.json"
            plan = plan_review_wave({
                "schema_version": 2,
                "assurance_tier": "high",
                "contract_hash": "sha256:contract",
                "diff_digest": "sha256:diff",
                "changed_paths": ["src/example.py"],
                "reviewer_capacity": 1,
                "surfaces": [{
                    "id": "backend",
                    "reviewer_role": "reviewer",
                    "owned_paths": ["src/example.py"],
                    "risk_boundaries": ["input", "output"],
                    "cross_cutting": False,
                    "priority": 0,
                }],
            })
            assignment.write_text(json.dumps(plan), encoding="utf-8")

            envelope = render_role_envelope(
                role="reviewer",
                actor_id="reviewer-one",
                assignment_path=assignment,
                workspace_root=workspace,
                terminal_path=artifacts / "terminal.json",
                surface_id="backend",
                recovery_path=artifacts / "recovery.json",
            )

            self.assertEqual(envelope["role"], "reviewer")
            self.assertEqual(envelope["actor_id"], "reviewer-one")
            self.assertEqual(envelope["surface_id"], "backend")
            self.assertTrue(Path(envelope["assignment_path"]).is_absolute())
            self.assertIn("validate_review_terminal.py", envelope["terminal_validation_command"])
            self.assertIn("Do not send heartbeat messages", envelope["prompt"])
            self.assertIn("never certifies review", envelope["prompt"])

    def test_fixer_envelope_rejects_recovery_and_workspace_terminal(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            workspace = root / "workspace"
            artifacts = root / "artifacts"
            workspace.mkdir()
            artifacts.mkdir()
            assignment = artifacts / "fixer-assignment.json"
            assignment.write_text(json.dumps({
                "contract_hash": "sha256:contract",
                "registry_digest": "sha256:registry",
                "finding_ids": ["F-ONE"],
                "owned_paths": ["src/service.py"],
                "verification_commands": ["rtk pytest tests/test_service.py"],
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "reviewer"):
                render_role_envelope(
                    role="fixer",
                    actor_id="fixer-one",
                    assignment_path=assignment,
                    workspace_root=workspace,
                    terminal_path=artifacts / "terminal.json",
                    recovery_path=artifacts / "recovery.json",
                )
            with self.assertRaisesRegex(ValueError, "outside"):
                render_role_envelope(
                    role="fixer",
                    actor_id="fixer-one",
                    assignment_path=assignment,
                    workspace_root=workspace,
                    terminal_path=workspace / "terminal.json",
                )

    def test_validated_terminal_is_persisted_once(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            plan = plan_review_wave({
                "schema_version": 2,
                "assurance_tier": "high",
                "contract_hash": "sha256:contract",
                "diff_digest": "sha256:diff",
                "changed_paths": ["src/example.py"],
                "reviewer_capacity": 1,
                "surfaces": [{
                    "id": "backend",
                    "reviewer_role": "reviewer",
                    "owned_paths": ["src/example.py"],
                    "risk_boundaries": ["input"],
                    "cross_cutting": False,
                    "priority": 0,
                }],
            })
            plan_path = root / "plan.json"
            terminal_path = root / "candidate.json"
            durable_path = root / "accepted.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            terminal_path.write_text(json.dumps({
                "contract_hash": "sha256:contract",
                "diff_digest": "sha256:diff",
                "review_plan_hash": plan["review_plan_hash"],
                "reviewer_id": "reviewer-one",
                "surface_id": "backend",
                "risk_boundaries_checked": ["input"],
                "findings": [],
                "finding_feedback": [],
                "suppressed_speculative_count": 0,
                "stop_reason": "coverage-complete",
            }), encoding="utf-8")

            receipt = persist_role_terminal(
                role="reviewer",
                expected_actor_id="reviewer-one",
                assignment_path=plan_path,
                input_path=terminal_path,
                output_path=durable_path,
            )

            self.assertTrue(receipt["valid"])
            self.assertTrue(durable_path.exists())
            with self.assertRaises(FileExistsError):
                persist_role_terminal(
                    role="reviewer",
                    expected_actor_id="reviewer-one",
                    assignment_path=plan_path,
                    input_path=terminal_path,
                    output_path=durable_path,
                )

    def test_persistence_rejects_actor_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw).resolve()
            assignment = {
                "contract_hash": "sha256:contract",
                "registry_digest": "sha256:registry",
                "finding_ids": ["F-ONE"],
                "owned_paths": ["src/service.py"],
                "verification_commands": ["rtk pytest tests/test_service.py"],
            }
            terminal = {
                "contract_hash": "sha256:contract",
                "registry_digest": "sha256:registry",
                "fixer_id": "wrong-fixer",
                "finding_changes": [{
                    "finding_id": "F-ONE",
                    "changed_paths": ["src/service.py"],
                    "verification_commands": ["rtk pytest tests/test_service.py"],
                }],
                "blockers": [],
                "stop_reason": "mapping-complete",
            }
            assignment_path = root / "assignment.json"
            terminal_path = root / "candidate.json"
            assignment_path.write_text(json.dumps(assignment), encoding="utf-8")
            terminal_path.write_text(json.dumps(terminal), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "actor ID"):
                persist_role_terminal(
                    role="fixer",
                    expected_actor_id="fixer-one",
                    assignment_path=assignment_path,
                    input_path=terminal_path,
                    output_path=root / "accepted.json",
                )


if __name__ == "__main__":
    unittest.main()
