#!/usr/bin/env python3
"""Contract tests for Swarm authority and resume state."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


class SwarmAuthorityContractTest(unittest.TestCase):
    def test_public_skill_surface_stays_bounded_and_four_operation(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        operation_section = skill.split("## Four Operations", 1)[1].split(
            "## Operating Model", 1
        )[0]
        operations = set(
            re.findall(r"^\| `([a-z]+)` \|", operation_section, re.MULTILINE)
        )

        self.assertLessEqual(len(skill.splitlines()), 160)
        self.assertLessEqual(len(skill), 10_000)
        self.assertEqual(operations, {"plan", "dispatch", "reconcile", "status"})
        self.assertIn("references/lightweight-dispatch.md", skill)
        self.assertIn("references/executable-worker-contracts.md", skill)
        self.assertIn("references/safety.md", skill)

    def test_skill_is_explicit_only(self) -> None:
        metadata = yaml.safe_load(
            (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        )

        self.assertIs(metadata["policy"]["allow_implicit_invocation"], False)
        self.assertTrue(
            metadata["interface"]["default_prompt"].startswith(
                "Use krt-swarm-seneschal"
            )
        )

    def test_autonomous_flow_uses_compound_json_v1_as_only_authority(self) -> None:
        flow = (ROOT / "references" / "autonomous-team-flow.md").read_text(encoding="utf-8")
        self.assertIn("../../krt-compound-master/references/autonomy-ledger-schema.md", flow)
        self.assertIn("check_autonomy_ledger.py", flow)
        self.assertIn("JSON", flow)
        self.assertNotIn("allowed_mutation_classes:", flow)
        self.assertNotIn("denied_without_review:", flow)

    def test_resume_state_is_a_non_authoritative_snapshot(self) -> None:
        schema = (ROOT / "references" / "queue-state-schema.md").read_text(encoding="utf-8")
        self.assertIn("schema_version: 2", schema)
        self.assertIn("authority: false", schema)
        self.assertIn("schema_version: 1", schema)
        self.assertIn("contract_hash:", schema)
        self.assertIn("latest_audit_event:", schema)
        self.assertIn("captured_at:", schema)
        self.assertNotIn("<run>.yaml", schema)

    def test_general_jira_flow_has_no_cloud_default(self) -> None:
        paths = [
            ROOT / "SKILL.md",
            ROOT / "references" / "autonomous-team-flow.md",
            ROOT / "references" / "blocker-ledger.md",
            ROOT / "references" / "gates-and-reconciliation.md",
            ROOT / "references" / "jira-seeding.md",
            ROOT / "references" / "jira-team-flow.md",
            ROOT / "references" / "queue-and-dispatch.md",
            ROOT / "references" / "queue-state-schema.md",
            ROOT / "references" / "swarm-protocol.md",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        forbidden = [
            "Jira Cloud queues",
            "Run Jira Cloud backlog",
            "Seed Jira Cloud",
            "use Jira Cloud backlog source",
            "Jira Cloud is the default Jira posture",
            "`krt-jira-cloud-scribe` is the default Jira integration role",
            "read active Jira Cloud issues through `krt-jira-cloud-scribe`",
            "execute only mutation classes covered by the autonomy ledger through `krt-jira-cloud-scribe`",
        ]
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, combined)
        self.assertIn("selected Jira provider skill", combined)

        adapter_markers = ("`cloud` ->", "`cloud` selects")
        for path in paths:
            for line in path.read_text(encoding="utf-8").splitlines():
                if "Jira Cloud" in line or "krt-jira-cloud-scribe" in line:
                    with self.subTest(path=path, line=line):
                        self.assertTrue(any(marker in line for marker in adapter_markers))


if __name__ == "__main__":
    unittest.main()
