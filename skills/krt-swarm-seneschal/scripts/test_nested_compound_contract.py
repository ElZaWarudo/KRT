#!/usr/bin/env python3
"""Contract tests for Seneschal-nested Compound Master flows."""

from __future__ import annotations

import unittest
from pathlib import Path


SWARM_ROOT = Path(__file__).resolve().parents[1]
COMPOUND_ROOT = SWARM_ROOT.parent / "krt-compound-master"


class NestedCompoundContractTest(unittest.TestCase):
    def test_seneschal_routes_nested_flows_through_compound_master(self) -> None:
        skill = (SWARM_ROOT / "SKILL.md").read_text(encoding="utf-8")
        nesting = (
            SWARM_ROOT / "references" / "compound-master-nesting.md"
        ).read_text(encoding="utf-8")

        self.assertIn("references/compound-master-nesting.md", skill)
        self.assertIn("interaction: brokered", nesting)
        self.assertIn("state_path:", nesting)
        self.assertIn("Decision Broker", nesting)
        self.assertIn("artifact-planning wave", nesting)
        self.assertIn("For an execution wave", nesting)
        self.assertIn("krt-release-marshal", nesting)

    def test_compound_master_supports_isolated_nested_runs(self) -> None:
        skill = (COMPOUND_ROOT / "SKILL.md").read_text(encoding="utf-8")
        nesting = (
            COMPOUND_ROOT / "references" / "nested-orchestration.md"
        ).read_text(encoding="utf-8")
        execution = (
            COMPOUND_ROOT / "references" / "execution-flow.md"
        ).read_text(encoding="utf-8")

        self.assertIn("orchestrator:standalone|seneschal", skill)
        self.assertIn("state-path:<repo-relative-path>", skill)
        self.assertIn("interaction:direct|brokered", skill)
        self.assertIn("docs/orchestration/compound-master/<run-id>/state.md", nesting)
        self.assertIn("ce-unified-plan/v1", nesting)
        self.assertIn("Do not invoke the\nroadmap generator", nesting)
        self.assertIn("Do not invoke `krt-release-marshal`", nesting)
        self.assertIn("do not ask the user directly", nesting)
        self.assertIn("return the release-ready context to the parent", execution)

    def test_queue_projects_but_does_not_own_compound_state(self) -> None:
        schema = (
            SWARM_ROOT / "references" / "queue-state-schema.md"
        ).read_text(encoding="utf-8")

        self.assertIn("schema_version: 2", schema)
        self.assertIn("compound_runs:", schema)
        self.assertIn("shared_revision:", schema)
        self.assertIn("artifact_revision:", schema)
        self.assertIn("child state path as authority", schema)

    def test_decisions_are_persisted_before_children_resume(self) -> None:
        blockers = (
            SWARM_ROOT / "references" / "blocker-ledger.md"
        ).read_text(encoding="utf-8")
        worker_contract = (
            SWARM_ROOT / "references" / "subagent-contracts.md"
        ).read_text(encoding="utf-8")

        self.assertIn("canonical_target:", blockers)
        self.assertIn("Persist the decision", blockers)
        self.assertIn("Decision requests:", worker_contract)
        self.assertIn("Do not ask the user directly", worker_contract)


if __name__ == "__main__":
    unittest.main()
