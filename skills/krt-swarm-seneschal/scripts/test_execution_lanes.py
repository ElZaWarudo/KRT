#!/usr/bin/env python3
"""Contract tests for fast, standard, and deep execution lanes."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ExecutionLaneContractTest(unittest.TestCase):
    def test_lane_routes_and_reasoning_are_explicit(self) -> None:
        lanes = (ROOT / "references" / "execution-lanes.md").read_text(
            encoding="utf-8"
        )
        rows = {
            cells[0].strip("`"): (cells[2].strip("`"), cells[3].strip("`"))
            for line in lanes.splitlines()
            if line.startswith("| `")
            for cells in ([cell.strip() for cell in line.strip("|").split("|")],)
        }
        expected = {
            "fast": ("spark", "xhigh"),
            "standard": ("luna", "high"),
            "deep": ("luna_xhigh", "xhigh"),
        }
        self.assertEqual(rows, expected)
        manifest = json.loads(
            (ROOT / "assets" / "codex-workers" / "manifest.yaml").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["lane_stages"]["fast"], ["spark"])
        self.assertEqual(manifest["lane_stages"]["standard"], ["luna"])
        self.assertEqual(
            manifest["lane_stages"]["deep"],
            ["luna_xhigh_discovery", "luna_xhigh"],
        )
        self.assertIn("Spark reasoning is intentionally fixed at `xhigh`", lanes)
        self.assertIn("default for normal work", lanes)
        self.assertIn(
            "admitted only by a concrete deep trigger", " ".join(lanes.split())
        )
        self.assertIn("Reasoning depth and execution duration are independent", lanes)
        self.assertIn("`deep_trigger: difficult` is invalid", lanes)

    def test_role_and_verification_admission_is_bounded(self) -> None:
        lanes = (ROOT / "references" / "execution-lanes.md").read_text(
            encoding="utf-8"
        )
        normalized = " ".join(lanes.split())
        for role in ("Planner", "Reviewer", "Fixer", "Integrator", "Documenter"):
            with self.subTest(role=role):
                self.assertIn(f"**{role}:**", lanes)
        self.assertIn(
            "The leaf worker runs only the exact contract-specific focused checks",
            normalized,
        )
        self.assertIn(
            "runs aggregate or CI-equivalent verification once", normalized
        )
        self.assertIn("fingerprint is unchanged", normalized)
        self.assertIn("Security Watch", normalized)
        self.assertIn("Security Sentinel Gate", normalized)

    def test_luna_contract_has_bounded_terminal_protocol(self) -> None:
        contracts = (ROOT / "references" / "subagent-contracts.md").read_text(
            encoding="utf-8"
        )
        profiles = (ROOT / "references" / "worker-profiles.md").read_text(
            encoding="utf-8"
        )
        for text in (contracts, profiles):
            with self.subTest(reference=text[:40]):
                self.assertIn("discovery_passes: 1", text)
                self.assertIn("extra_verification: forbidden", text)
                self.assertIn("max_elapsed_ms:", text)
                self.assertIn("grace_actions: 0", text)
                self.assertIn("aggregate_owner: root", text)

    def test_luna_supervision_is_sparse_and_profile_specific(self) -> None:
        supervision = (
            ROOT / "references" / "lightweight-supervision.md"
        ).read_text(encoding="utf-8")
        profiles = (ROOT / "references" / "worker-profiles.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("`luna` | `terminal-only`", supervision)
        self.assertIn("`luna_xhigh_discovery` | `read-only-discovery`", supervision)
        self.assertIn("exactly one terminal checkpoint", supervision)
        self.assertIn("Neither stage emits per-action telemetry", profiles)
        self.assertIn("diagnostic sample", profiles)

    def test_route_references_delegate_optional_role_admission(self) -> None:
        for name in (
            "autonomous-team-flow.md",
            "jira-team-flow.md",
            "parallel-dispatch-policy.md",
        ):
            with self.subTest(name=name):
                reference = (ROOT / "references" / name).read_text(encoding="utf-8")
                self.assertIn("execution-lanes.md", reference)


if __name__ == "__main__":
    unittest.main()
