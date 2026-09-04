#!/usr/bin/env python3
"""Tests for role-aware worktree planning."""

from __future__ import annotations

import unittest

from plan_worker_workspaces import plan_worker_workspaces


def invocation(identifier: str, role: str, *, depends_on: list[str] | None = None, candidates: list[str] | None = None, paths: list[str] | None = None) -> dict[str, object]:
    return {
        "id": identifier,
        "unit_id": identifier.split("-")[0],
        "role": role,
        "depends_on": depends_on or [],
        "candidate_invocations": candidates or [],
        "owned_paths": paths or [],
    }


class WorkerWorkspacePlanTest(unittest.TestCase):
    def plan(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "run_id": "codex-agents",
            "base_revision": "0123456789abcdef",
            "worktree_parent": "/tmp/seneschal-worktrees",
            "invocations": [
                invocation("plan", "planner"),
                invocation("foundation-discovery", "discovery"),
                invocation("foundation-build", "implementer", paths=["src/contracts.py"]),
                invocation("runtime-build", "implementer", depends_on=["foundation-build"], paths=["src/runtime.py"]),
                invocation("persistence-build", "implementer", depends_on=["foundation-build"], paths=["src/journal.py"]),
                invocation("runtime-review", "reviewer", candidates=["runtime-build"]),
                invocation("security-review", "security-reviewer", candidates=["persistence-build"]),
                invocation("finding-validation", "targeted-validator", candidates=["runtime-build"]),
                invocation("runtime-fix", "fixer", candidates=["runtime-build"], paths=["src/runtime.py"]),
                invocation("compound", "compound-master", depends_on=["foundation-build"], paths=["docs/work-package.md"]),
                invocation("docs", "documenter", depends_on=["runtime-fix", "persistence-build"], paths=["docs/agents.md"]),
                invocation("integration", "integrator", depends_on=["runtime-fix", "persistence-build", "compound", "docs"], paths=["src/glue.py"]),
                invocation("aggregate", "ci-validator", candidates=["integration"]),
            ],
        }

    def test_assigns_unique_role_aware_worktrees(self) -> None:
        result = plan_worker_workspaces(self.plan())
        workspaces = {item["invocation_id"]: item for item in result["workspaces"]}

        self.assertEqual(len({item["path"] for item in workspaces.values()}), len(workspaces))
        self.assertEqual(workspaces["runtime-build"]["mode"], "mutable")
        self.assertTrue(workspaces["runtime-build"]["detached"])
        self.assertIsNone(workspaces["runtime-build"]["branch"])
        self.assertTrue(workspaces["runtime-fix"]["detached"])
        self.assertIsNone(workspaces["runtime-fix"]["branch"])
        self.assertEqual(workspaces["runtime-review"]["mode"], "read-only")
        self.assertTrue(workspaces["runtime-review"]["detached"])
        self.assertEqual(workspaces["aggregate"]["mode"], "disposable-verification")
        self.assertEqual(workspaces["finding-validation"]["mode"], "disposable-verification")
        self.assertEqual(workspaces["compound"]["mode"], "mutable")
        self.assertEqual(result["consolidation_invocation"], "integration")
        self.assertFalse(workspaces["integration"]["detached"])
        self.assertEqual(workspaces["integration"]["branch"], "seneschal/codex-agents/integration")
        self.assertEqual(
            [item["branch"] for item in workspaces.values() if item["branch"]],
            ["seneschal/codex-agents/integration"],
        )
        self.assertLess(result["patch_application_order"].index("foundation-build"), result["patch_application_order"].index("runtime-build"))
        self.assertLess(result["patch_application_order"].index("runtime-fix"), result["patch_application_order"].index("integration"))
        self.assertTrue(result["workspace_plan_hash"].startswith("sha256:"))

    def test_rejects_mutable_ownership_for_read_only_role(self) -> None:
        plan = self.plan()
        reviewer = next(item for item in plan["invocations"] if item["role"] == "reviewer")
        reviewer["owned_paths"] = ["src/runtime.py"]

        with self.assertRaisesRegex(ValueError, "must not own"):
            plan_worker_workspaces(plan)

    def test_can_keep_integrator_detached_when_release_does_not_need_a_branch(self) -> None:
        plan = self.plan()
        plan["integration_branch"] = False

        result = plan_worker_workspaces(plan)
        integration = next(item for item in result["workspaces"] if item["role"] == "integrator")

        self.assertIsNone(result["integration_branch"])
        self.assertIsNone(integration["branch"])
        self.assertTrue(integration["detached"])

    def test_requires_exactly_one_consolidation_workspace(self) -> None:
        plan = self.plan()
        plan["invocations"] = [item for item in plan["invocations"] if item["role"] != "integrator"]

        with self.assertRaisesRegex(ValueError, "exactly one integrator"):
            plan_worker_workspaces(plan)

    def test_rejects_unknown_candidate_or_dependency(self) -> None:
        plan = self.plan()
        reviewer = next(item for item in plan["invocations"] if item["role"] == "reviewer")
        reviewer["candidate_invocations"] = ["missing"]

        with self.assertRaisesRegex(ValueError, "unknown invocations"):
            plan_worker_workspaces(plan)

    def test_rejects_dependency_cycle(self) -> None:
        plan = self.plan()
        plan["invocations"][2]["depends_on"] = ["runtime-build"]

        with self.assertRaisesRegex(ValueError, "contains a cycle"):
            plan_worker_workspaces(plan)

    def test_rejects_mutable_result_outside_consolidation_ancestry(self) -> None:
        plan = self.plan()
        integration = next(item for item in plan["invocations"] if item["role"] == "integrator")
        integration["depends_on"].remove("compound")

        with self.assertRaisesRegex(ValueError, "do not feed consolidation"):
            plan_worker_workspaces(plan)


if __name__ == "__main__":
    unittest.main()
