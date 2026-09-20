#!/usr/bin/env python3
"""Tests for locked, validated Seneschal state transitions."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from materialize_approval_receipt import materialize_receipt
from transition_swarm_state import _load_yaml, _validate, state_digest, transition_state
from verification_evidence import write_atomic

APPROVAL_EVENT_DIGEST = "sha256:" + "a" * 64
EXECUTION_READY_EVENT_DIGEST = "sha256:" + "b" * 64
REPO_ROOT = Path(__file__).resolve().parents[3]

class SwarmStateTransitionTest(unittest.TestCase):
    def test_checked_in_empty_state_pair_satisfies_transition_validator(self) -> None:
        queue = _load_yaml(REPO_ROOT / "docs" / "swarm" / "queue-state.yaml")
        blockers = _load_yaml(REPO_ROOT / "docs" / "swarm" / "blockers.yaml")

        _validate(queue, blockers)

        self.assertEqual(queue["documentation_gate"]["status"], "draft")
        self.assertIsNone(queue["jira"]["provider"])
        self.assertEqual(queue["units"], {})

    def fixtures(self, root: Path) -> tuple[Path, Path]:
        queue = root / "queue.yaml"
        blockers = root / "blockers.yaml"
        queue.write_text(yaml.safe_dump({
            "schema_version": 2,
            "documentation_gate": {"status": "approved"},
            "units": {"unit-1": {"status": "blocked", "blocked_by": ["BLK-1"]}},
        }), encoding="utf-8")
        blockers.write_text(yaml.safe_dump({
            "schema_version": 1,
            "blockers": [{
                "id": "BLK-1", "status": "open", "affected_units": ["unit-1"],
                "resolution": {"decided_at": None, "decided_by": None, "decision": None},
            }],
        }), encoding="utf-8")
        return queue, blockers

    def approve(self, root: Path, queue: Path, blockers: Path) -> dict[str, object]:
        (root / "plan.md").write_text("reviewed", encoding="utf-8")
        queue_state = yaml.safe_load(queue.read_text(encoding="utf-8"))
        queue_state["documentation_gate"] = {
            "status": "in_review", "approval_artifacts": ["plan.md"]
        }
        queue.write_text(yaml.safe_dump(queue_state), encoding="utf-8")
        receipt = materialize_receipt(
            repo_root=root, source_artifacts=["plan.md"], approved_by="user",
            approved_at="2026-08-25T08:00:00Z",
            approval_event_digest=APPROVAL_EVENT_DIGEST,
        )
        write_atomic(root / "receipt.json", receipt)
        transition_state(
            queue_path=queue, blockers_path=blockers, repo_root=root,
            transition={"schema_version": 1, "operation": "approve-documentation", "receipt_path": "receipt.json", "expected_approval_event_digest": APPROVAL_EVENT_DIGEST},
            expected_queue_digest=state_digest(queue), expected_blockers_digest=state_digest(blockers),
        )
        return receipt

    def test_resolve_blocker_updates_both_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            queue, blockers = self.fixtures(Path(temp_dir))
            transition_state(
                queue_path=queue,
                blockers_path=blockers,
                transition={
                    "schema_version": 1,
                    "operation": "resolve-blocker",
                    "blocker_id": "BLK-1",
                    "decided_at": "2026-08-25T08:00:00Z",
                    "decided_by": "user",
                    "decision": "Proceed.",
                },
                expected_queue_digest=state_digest(queue),
                expected_blockers_digest=state_digest(blockers),
            )
            queue_state = yaml.safe_load(queue.read_text(encoding="utf-8"))
            blocker_state = yaml.safe_load(blockers.read_text(encoding="utf-8"))

        self.assertEqual(blocker_state["blockers"][0]["status"], "resolved")
        self.assertEqual(queue_state["units"]["unit-1"]["status"], "planned")
        self.assertEqual(queue_state["units"]["unit-1"]["blocked_by"], [])

    def test_stale_writer_and_illegal_transition_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            queue, blockers = self.fixtures(Path(temp_dir))
            with self.assertRaisesRegex(ValueError, "queue digest"):
                transition_state(
                    queue_path=queue,
                    blockers_path=blockers,
                    transition={"schema_version": 1, "operation": "unit-status", "unit_id": "unit-1", "from": "blocked", "to": "planned"},
                    expected_queue_digest="sha256:stale",
                    expected_blockers_digest=state_digest(blockers),
                )
            with self.assertRaisesRegex(ValueError, "illegal unit status transition"):
                transition_state(
                    queue_path=queue,
                    blockers_path=blockers,
                    transition={"schema_version": 1, "operation": "unit-status", "unit_id": "unit-1", "from": "blocked", "to": "release-ready"},
                    expected_queue_digest=state_digest(queue),
                    expected_blockers_digest=state_digest(blockers),
                )

    def test_documentation_approval_uses_a_current_content_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            queue, blockers = self.fixtures(root)
            receipt = self.approve(root, queue, blockers)
            gate = yaml.safe_load(queue.read_text(encoding="utf-8"))["documentation_gate"]

        self.assertEqual(gate["status"], "approved")
        self.assertEqual(gate["approved_packet_digest"], receipt["packet_digest"])

    def test_reopen_documentation_invalidates_approval_and_allows_renewal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            queue, blockers = self.fixtures(root)
            old_receipt = self.approve(root, queue, blockers)
            old_receipt_bytes = (root / "receipt.json").read_bytes()
            blocker_bytes = blockers.read_bytes()

            def apply(transition: dict[str, object], **digests: str) -> None:
                transition_state(
                    queue_path=queue, blockers_path=blockers, repo_root=root,
                    transition={"schema_version": 1, **transition},
                    expected_queue_digest=digests.get("queue", state_digest(queue)),
                    expected_blockers_digest=digests.get("blockers", state_digest(blockers)),
                )

            def reject(transition: dict[str, object], error: str, **digests: str) -> None:
                before = {path: path.read_bytes() for path in root.iterdir() if path.is_file()}
                with self.assertRaisesRegex(ValueError, error):
                    apply(transition, **digests)
                self.assertEqual(before, {path: path.read_bytes() for path in root.iterdir() if path.is_file()})

            reopen = {"operation": "documentation-status", "from": "approved", "to": "in_review"}
            reject(reopen, "queue digest", queue="sha256:stale")
            reject(reopen, "blockers digest", blockers="sha256:stale")
            reject({**reopen, "from": "draft"}, "current status")
            reject({**reopen, "to": "draft"}, "illegal documentation")
            journal = root / ".seneschal-state-transaction.json"
            journal.write_text("{}", encoding="utf-8")
            reject(reopen, "unfinished state transaction")
            journal.unlink()
            (root / "plan.md").write_text("reconciled", encoding="utf-8")
            apply(reopen)
            self.assertEqual(_load_yaml(queue)["documentation_gate"], {
                "status": "in_review", "approval_artifacts": ["plan.md"],
            })
            self.assertEqual(blockers.read_bytes(), blocker_bytes)
            self.assertEqual((root / "receipt.json").read_bytes(), old_receipt_bytes)
            reject({"operation": "unit-status", "unit_id": "unit-1", "from": "blocked", "to": "ready"}, "approval is missing")
            approval = {"operation": "approve-documentation", "receipt_path": "receipt.json", "expected_approval_event_digest": APPROVAL_EVENT_DIGEST}
            reject(approval, "digest mismatch")
            new_event = "sha256:" + "c" * 64
            receipt = materialize_receipt(
                repo_root=root, source_artifacts=["plan.md"], approved_by="user",
                approved_at="2026-09-05T08:00:00Z", approval_event_digest=new_event,
            )
            write_atomic(root / "renewed.json", receipt)
            approval["receipt_path"] = "renewed.json"
            reject(approval, "trusted user-event handoff")
            (root / "other.md").write_text("other", encoding="utf-8")
            other = materialize_receipt(
                repo_root=root, source_artifacts=["other.md"], approved_by="user",
                approved_at="2026-09-05T08:00:00Z", approval_event_digest=new_event,
            )
            write_atomic(root / "other.json", other)
            approval["expected_approval_event_digest"] = new_event
            reject({**approval, "receipt_path": "other.json"}, "does not cover")
            apply(approval)
            gate = _load_yaml(queue)["documentation_gate"]
            self.assertEqual(gate["status"], "approved")
            self.assertEqual(gate["approval_receipt"], "renewed.json")
            self.assertEqual(gate["approval_receipt_digest"], receipt["receipt_digest"])
            self.assertNotEqual(gate["approved_packet_digest"], old_receipt["packet_digest"])
            self.assertEqual(blockers.read_bytes(), blocker_bytes)
            apply({"operation": "resolve-blocker", "blocker_id": "BLK-1", "decided_at": "2026-09-05T08:01:00Z", "decided_by": "user", "decision": "Proceed."})
            apply({"operation": "unit-status", "unit_id": "unit-1", "from": "planned", "to": "ready"})
            self.assertEqual(_load_yaml(queue)["units"]["unit-1"]["status"], "ready")

    def test_open_blocker_prevents_ready_transition(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            queue, blockers = self.fixtures(root)
            self.approve(root, queue, blockers)

            with self.assertRaisesRegex(ValueError, "open blockers"):
                transition_state(
                    queue_path=queue, blockers_path=blockers, repo_root=root,
                    transition={"schema_version": 1, "operation": "unit-status", "unit_id": "unit-1", "from": "blocked", "to": "ready"},
                    expected_queue_digest=state_digest(queue), expected_blockers_digest=state_digest(blockers),
                )

    def test_changed_approved_artifact_prevents_execution_transition(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            queue, blockers = self.fixtures(root)
            self.approve(root, queue, blockers)
            transition_state(
                queue_path=queue, blockers_path=blockers,
                transition={"schema_version": 1, "operation": "resolve-blocker", "blocker_id": "BLK-1", "decided_at": "2026-08-25T08:01:00Z", "decided_by": "user", "decision": "Proceed."},
                expected_queue_digest=state_digest(queue), expected_blockers_digest=state_digest(blockers),
            )
            (root / "plan.md").write_text("changed", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                transition_state(
                    queue_path=queue, blockers_path=blockers, repo_root=root,
                    transition={"schema_version": 1, "operation": "unit-status", "unit_id": "unit-1", "from": "planned", "to": "ready"},
                    expected_queue_digest=state_digest(queue), expected_blockers_digest=state_digest(blockers),
                )

    def test_execution_ready_exemption_allows_ready_without_packet_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            queue, blockers = self.fixtures(root)
            queue_state = yaml.safe_load(queue.read_text(encoding="utf-8"))
            queue_state["documentation_gate"] = {"status": "draft"}
            queue_state["units"]["unit-1"].update({
                "status": "planned",
                "blocked_by": [],
                "documentation_gate_exemption": {
                    "basis": "explicit-execution-ready-unit",
                    "authorization_event_digest": EXECUTION_READY_EVENT_DIGEST,
                },
            })
            queue.write_text(yaml.safe_dump(queue_state), encoding="utf-8")
            blockers.write_text(yaml.safe_dump({
                "schema_version": 1,
                "blockers": [],
            }), encoding="utf-8")

            transition_state(
                queue_path=queue,
                blockers_path=blockers,
                transition={
                    "schema_version": 1,
                    "operation": "unit-status",
                    "unit_id": "unit-1",
                    "from": "planned",
                    "to": "ready",
                    "expected_authorization_event_digest": EXECUTION_READY_EVENT_DIGEST,
                },
                expected_queue_digest=state_digest(queue),
                expected_blockers_digest=state_digest(blockers),
            )

            result = yaml.safe_load(queue.read_text(encoding="utf-8"))

        self.assertEqual(result["units"]["unit-1"]["status"], "ready")

    def test_execution_ready_exemption_must_match_trusted_event_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            queue, blockers = self.fixtures(root)
            queue_state = yaml.safe_load(queue.read_text(encoding="utf-8"))
            queue_state["documentation_gate"] = {"status": "draft"}
            queue_state["units"]["unit-1"].update({
                "status": "planned",
                "blocked_by": [],
                "documentation_gate_exemption": {
                    "basis": "explicit-execution-ready-unit",
                    "authorization_event_digest": EXECUTION_READY_EVENT_DIGEST,
                },
            })
            queue.write_text(yaml.safe_dump(queue_state), encoding="utf-8")
            blockers.write_text(yaml.safe_dump({
                "schema_version": 1,
                "blockers": [],
            }), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "trusted user-event handoff"):
                transition_state(
                    queue_path=queue,
                    blockers_path=blockers,
                    transition={
                        "schema_version": 1,
                        "operation": "unit-status",
                        "unit_id": "unit-1",
                        "from": "planned",
                        "to": "ready",
                        "expected_authorization_event_digest": "sha256:" + "c" * 64,
                    },
                    expected_queue_digest=state_digest(queue),
                    expected_blockers_digest=state_digest(blockers),
                )

    def test_execution_ready_exemption_requires_trusted_event_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            queue, blockers = self.fixtures(root)
            queue_state = yaml.safe_load(queue.read_text(encoding="utf-8"))
            queue_state["units"]["unit-1"]["documentation_gate_exemption"] = {
                "basis": "explicit-execution-ready-unit",
                "authorization_event_digest": "sha256:guess",
            }
            queue.write_text(yaml.safe_dump(queue_state), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "exemption schema"):
                transition_state(
                    queue_path=queue,
                    blockers_path=blockers,
                    transition={
                        "schema_version": 1,
                        "operation": "unit-status",
                        "unit_id": "unit-1",
                        "from": "blocked",
                        "to": "planned",
                    },
                    expected_queue_digest=state_digest(queue),
                    expected_blockers_digest=state_digest(blockers),
                )

    def test_generic_transition_refuses_every_release_lifecycle_edge(self) -> None:
        for source, target in (
            ("review-gated", "release-ready"),
            ("release-ready", "handed-off"),
            ("handed-off", "merged"),
        ):
            with self.subTest(source=source, target=target), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                queue, blockers = self.fixtures(root)
                queue_state = yaml.safe_load(queue.read_text(encoding="utf-8"))
                queue_state["units"]["unit-1"]["status"] = source
                queue.write_text(yaml.safe_dump(queue_state), encoding="utf-8")

                with self.assertRaisesRegex(ValueError, "authoritative reconciliation"):
                    transition_state(
                        queue_path=queue, blockers_path=blockers,
                        transition={"schema_version": 1, "operation": "unit-status", "unit_id": "unit-1", "from": source, "to": target},
                        expected_queue_digest=state_digest(queue), expected_blockers_digest=state_digest(blockers),
                    )


if __name__ == "__main__":
    unittest.main()
