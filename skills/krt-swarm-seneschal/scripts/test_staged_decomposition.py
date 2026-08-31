#!/usr/bin/env python3
"""Tests for staged decomposition of coupled implementation units."""

from __future__ import annotations

import unittest

from plan_staged_decomposition import plan_staged_decomposition


def unit(
    identifier: str,
    paths: list[str],
    *,
    depends_on: list[str],
    generated_paths: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": identifier,
        "title": identifier.replace("-", " ").title(),
        "owned_paths": paths,
        "depends_on": depends_on,
        "focused_commands": [f"rtk pytest tests/{identifier}.py"] if paths else [],
        "generated_paths": generated_paths or [],
    }


class StagedDecompositionTest(unittest.TestCase):
    def plan(self) -> dict[str, object]:
        paths = [
            "src/agent_graph.py",
            "src/agent_process.py",
            "src/bus_contract.py",
            "src/codex_runtime.py",
            "tests/runtime_fixture.json",
            "src/journal.py",
            "tests/test_recovery.py",
            "src/commands.py",
            "generated/contracts.ts",
            "frontend/client.ts",
            "frontend/agent_lens.tsx",
            "src/integration.py",
        ]
        return {
            "schema_version": 1,
            "parent_unit_id": "codex-subagents",
            "parent_owned_paths": paths,
            "shared_api_paths": [
                "src/agent_graph.py",
                "src/agent_process.py",
                "src/bus_contract.py",
            ],
            "foundation": unit("foundation", paths[:3], depends_on=[]),
            "dependents": [
                unit("runtime", paths[3:5], depends_on=["foundation"]),
                unit("persistence", paths[5:7], depends_on=["foundation"]),
                unit(
                    "controls",
                    paths[7:10],
                    depends_on=["foundation"],
                    generated_paths=["generated/contracts.ts"],
                ),
                unit("agent-lens", paths[10:11], depends_on=["controls"]),
            ],
            "integration": unit(
                "integration",
                paths[11:],
                depends_on=["runtime", "persistence", "controls", "agent-lens"],
            ),
            "aggregate_commands": ["rtk test npm test"],
        }

    def test_compiles_serial_parallel_reconverging_waves(self) -> None:
        result = plan_staged_decomposition(self.plan())

        self.assertEqual(
            [wave["unit_ids"] for wave in result["waves"]],
            [
                ["foundation"],
                ["controls", "persistence", "runtime"],
                ["agent-lens"],
                ["integration"],
            ],
        )
        self.assertEqual(result["foundation_gate"]["required_status"], "release-ready")
        self.assertEqual(result["waves"][2]["requires_release_ready"], ["controls"])
        self.assertTrue(result["topology_hash"].startswith("sha256:"))

    def test_rejects_shared_api_outside_foundation(self) -> None:
        plan = self.plan()
        plan["shared_api_paths"] = ["src/codex_runtime.py"]

        with self.assertRaisesRegex(ValueError, "foundation must own"):
            plan_staged_decomposition(plan)

    def test_rejects_overlapping_or_unowned_paths(self) -> None:
        overlap = self.plan()
        overlap["dependents"][0]["owned_paths"].append("src/journal.py")
        missing = self.plan()
        missing["integration"]["owned_paths"] = []
        missing["integration"]["focused_commands"] = []

        with self.assertRaisesRegex(ValueError, "overlaps"):
            plan_staged_decomposition(overlap)
        with self.assertRaisesRegex(ValueError, "lack a staged owner"):
            plan_staged_decomposition(missing)

    def test_rejects_downstream_without_foundation_ancestry(self) -> None:
        plan = self.plan()
        plan["dependents"][0]["depends_on"] = []

        with self.assertRaisesRegex(ValueError, "does not descend from foundation"):
            plan_staged_decomposition(plan)

    def test_requires_integration_to_reconverge_all_dependents(self) -> None:
        plan = self.plan()
        plan["integration"]["depends_on"] = ["runtime", "persistence"]

        with self.assertRaisesRegex(ValueError, "every dependent"):
            plan_staged_decomposition(plan)


if __name__ == "__main__":
    unittest.main()
