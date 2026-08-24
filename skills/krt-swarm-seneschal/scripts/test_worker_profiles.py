#!/usr/bin/env python3
"""Tests for worker installation, discovery, and fail-closed behavior."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from check_worker_profiles import check_profiles
from install_worker_profiles import install_profiles


SKILL_ROOT = Path(__file__).resolve().parents[1]


def bundled(worker: str) -> Path:
    return SKILL_ROOT / "assets" / "codex-workers" / f"{worker}_worker.toml"


class WorkerProfileTest(unittest.TestCase):
    def test_bundled_profiles_validate_for_packaging(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=temp_root / "codex-home",
                allow_bundled=True,
            )

        self.assertTrue(result["allowed"], result["errors"])
        self.assertEqual(
            {entry["source"] for entry in result["workers"].values()},
            {"bundled-package"},
        )
        self.assertFalse(
            any(entry["runtime_discoverable"] for entry in result["workers"].values())
        )
        self.assertEqual(
            result["workers"]["spark"]["model_reasoning_effort"], "xhigh"
        )
        self.assertEqual(
            result["workers"]["luna"]["model_reasoning_effort"], "high"
        )
        self.assertEqual(
            result["workers"]["luna_xhigh"]["model_reasoning_effort"], "xhigh"
        )
        self.assertEqual(
            result["workers"]["luna_xhigh_discovery"]["sandbox_mode"],
            "read-only",
        )

    def test_bundled_only_profile_blocks_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=temp_root / "codex-home",
                requested_workers=["spark"],
            )

        self.assertFalse(result["allowed"])
        self.assertTrue(
            any("worker-profile-not-installed" in error for error in result["errors"])
        )

    def test_project_agent_wins(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repo_root = temp_root / "repo"
            project_agents = repo_root / ".codex" / "agents"
            project_agents.mkdir(parents=True)
            (project_agents / "spark_worker.toml").write_bytes(
                bundled("spark").read_bytes()
            )
            result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=repo_root,
                codex_home=temp_root / "codex-home",
                requested_workers=["spark"],
                model_class="spark",
            )

        self.assertTrue(result["allowed"], result["errors"])
        self.assertEqual(result["workers"]["spark"]["source"], "project-agent")

    def test_personal_agent_is_runtime_discoverable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            codex_home = temp_root / "codex-home"
            personal_agents = codex_home / "agents"
            personal_agents.mkdir(parents=True)
            (personal_agents / "luna_worker.toml").write_bytes(
                bundled("luna").read_bytes()
            )
            result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=codex_home,
                requested_workers=["luna"],
            )

        self.assertTrue(result["allowed"], result["errors"])
        self.assertEqual(result["workers"]["luna"]["source"], "user-agent")
        self.assertTrue(result["workers"]["luna"]["runtime_discoverable"])
        self.assertEqual(
            result["workers"]["luna"]["model_reasoning_effort"], "high"
        )

    def test_standard_luna_override_without_sandbox_mode_remains_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repo_root = temp_root / "repo"
            project_agents = repo_root / ".codex" / "agents"
            project_agents.mkdir(parents=True)
            profile = bundled("luna").read_text(encoding="utf-8").replace(
                'sandbox_mode = "workspace-write"\n',
                "",
            )
            (project_agents / "luna_worker.toml").write_text(
                profile, encoding="utf-8"
            )
            result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=repo_root,
                codex_home=temp_root / "codex-home",
                requested_workers=["luna"],
            )

        self.assertTrue(result["allowed"], result["errors"])
        self.assertIsNone(result["workers"]["luna"]["sandbox_mode"])

    def test_demanding_luna_profile_is_runtime_discoverable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repo_root = temp_root / "repo"
            project_agents = repo_root / ".codex" / "agents"
            project_agents.mkdir(parents=True)
            (project_agents / "luna_xhigh_worker.toml").write_bytes(
                bundled("luna_xhigh").read_bytes()
            )
            result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=repo_root,
                codex_home=temp_root / "codex-home",
                requested_workers=["luna_xhigh"],
                model_class="luna",
            )

        self.assertTrue(result["allowed"], result["errors"])
        self.assertEqual(result["workers"]["luna_xhigh"]["source"], "project-agent")
        self.assertEqual(
            result["workers"]["luna_xhigh"]["model_reasoning_effort"], "xhigh"
        )

    def test_deep_lane_requires_discovery_and_implementation_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=temp_root / "codex-home",
                lane="deep",
                model_class="luna",
                allow_bundled=True,
            )

        self.assertTrue(result["allowed"], result["errors"])
        self.assertEqual(
            set(result["workers"]),
            {"luna_xhigh_discovery", "luna_xhigh"},
        )

    def test_writable_discovery_override_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repo_root = temp_root / "repo"
            project_agents = repo_root / ".codex" / "agents"
            project_agents.mkdir(parents=True)
            profile = bundled("luna_xhigh_discovery").read_text(
                encoding="utf-8"
            ).replace('sandbox_mode = "read-only"', 'sandbox_mode = "workspace-write"')
            (project_agents / "luna_xhigh_discovery_worker.toml").write_text(
                profile, encoding="utf-8"
            )
            result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=repo_root,
                codex_home=temp_root / "codex-home",
                requested_workers=["luna_xhigh_discovery"],
            )

        self.assertFalse(result["allowed"])
        self.assertTrue(
            any("worker-profile-sandbox-mode-mismatch" in error for error in result["errors"])
        )

    def test_invalid_project_agent_blocks_instead_of_using_personal_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repo_root = temp_root / "repo"
            project_agents = repo_root / ".codex" / "agents"
            project_agents.mkdir(parents=True)
            (project_agents / "spark_worker.toml").write_text(
                'name = "wrong"\n', encoding="utf-8"
            )
            personal_agents = temp_root / "codex-home" / "agents"
            personal_agents.mkdir(parents=True)
            (personal_agents / "spark_worker.toml").write_bytes(
                bundled("spark").read_bytes()
            )
            result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=repo_root,
                codex_home=temp_root / "codex-home",
                requested_workers=["spark"],
            )

        self.assertFalse(result["allowed"])
        self.assertNotIn("spark", result["workers"])
        self.assertTrue(
            any("worker-profile-field-invalid" in error for error in result["errors"])
        )

    def test_reasoning_effort_override_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repo_root = temp_root / "repo"
            project_agents = repo_root / ".codex" / "agents"
            project_agents.mkdir(parents=True)
            profile = bundled("spark").read_text(encoding="utf-8").replace(
                'model_reasoning_effort = "xhigh"',
                'model_reasoning_effort = "high"',
            )
            (project_agents / "spark_worker.toml").write_text(
                profile, encoding="utf-8"
            )
            result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=repo_root,
                codex_home=temp_root / "codex-home",
                requested_workers=["spark"],
            )

        self.assertFalse(result["allowed"])
        self.assertTrue(
            any(
                "worker-profile-reasoning-effort-mismatch" in error
                for error in result["errors"]
            )
        )

    def test_model_override_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            repo_root = temp_root / "repo"
            project_agents = repo_root / ".codex" / "agents"
            project_agents.mkdir(parents=True)
            profile = bundled("luna_xhigh").read_text(encoding="utf-8").replace(
                'model = "gpt-5.6-luna"',
                'model = "gpt-5.3-codex-spark"',
            )
            (project_agents / "luna_xhigh_worker.toml").write_text(
                profile, encoding="utf-8"
            )
            result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=repo_root,
                codex_home=temp_root / "codex-home",
                requested_workers=["luna_xhigh"],
            )

        self.assertFalse(result["allowed"])
        self.assertTrue(
            any("worker-profile-model-mismatch" in error for error in result["errors"])
        )

    def test_lane_derives_worker_and_rejects_substitution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            allowed = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=temp_root / "codex-home",
                lane="deep",
                allow_bundled=True,
            )
            rejected = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=temp_root / "codex-home",
                requested_workers=["luna"],
                lane="deep",
                allow_bundled=True,
            )

        self.assertTrue(allowed["allowed"], allowed["errors"])
        self.assertEqual(
            set(allowed["workers"]),
            {"luna_xhigh_discovery", "luna_xhigh"},
        )
        self.assertFalse(rejected["allowed"])
        self.assertTrue(
            any("worker-lane-mismatch" in error for error in rejected["errors"])
        )

    def test_unknown_worker_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=temp_root / "codex-home",
                requested_workers=["unknown"],
            )

        self.assertFalse(result["allowed"])
        self.assertIn("worker-not-registered:unknown", result["errors"])

    def test_model_class_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=temp_root / "codex-home",
                requested_workers=["luna"],
                model_class="spark",
                allow_bundled=True,
            )

        self.assertFalse(result["allowed"])
        self.assertTrue(
            any("worker-model-class-mismatch" in error for error in result["errors"])
        )

    def test_installer_dry_run_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            codex_home = temp_root / "codex-home"
            result = install_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=codex_home,
                scope="user",
            )

            self.assertTrue(result["allowed"], result["errors"])
            self.assertFalse(result["applied"])
            self.assertFalse((codex_home / "agents").exists())

    def test_installer_makes_personal_agents_discoverable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            codex_home = temp_root / "codex-home"
            install_result = install_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=codex_home,
                scope="user",
                install=True,
            )
            check_result = check_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=codex_home,
            )

        self.assertTrue(install_result["allowed"], install_result["errors"])
        self.assertTrue(install_result["applied"])
        self.assertTrue(check_result["allowed"], check_result["errors"])
        self.assertEqual(
            {entry["source"] for entry in check_result["workers"].values()},
            {"user-agent"},
        )

    def test_installer_removes_legacy_luna_alias_with_replace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            codex_home = temp_root / "codex-home"
            personal_agents = codex_home / "agents"
            personal_agents.mkdir(parents=True)
            legacy = personal_agents / "luna-worker.toml"
            legacy_profile = bundled("luna").read_text(encoding="utf-8").replace(
                'model_reasoning_effort = "high"',
                'model_reasoning_effort = "max"',
            )
            legacy.write_text(legacy_profile, encoding="utf-8")

            result = install_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=codex_home,
                scope="user",
                requested_workers=["luna"],
                install=True,
                replace=True,
            )

            self.assertTrue(result["allowed"], result["errors"])
            self.assertFalse(legacy.exists())
            self.assertTrue((personal_agents / "luna_worker.toml").exists())

    def test_installer_preserves_customized_legacy_luna_alias(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            codex_home = temp_root / "codex-home"
            personal_agents = codex_home / "agents"
            personal_agents.mkdir(parents=True)
            legacy = personal_agents / "luna-worker.toml"
            customized = bundled("luna").read_text(encoding="utf-8").replace(
                "Work only on the delegated objective.",
                "Preserve these customized instructions.",
            )
            legacy.write_text(customized, encoding="utf-8")

            result = install_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=codex_home,
                scope="user",
                requested_workers=["luna"],
                install=True,
                replace=True,
            )

            self.assertFalse(result["allowed"])
            self.assertTrue(legacy.exists())

    def test_installer_preserves_differing_existing_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            codex_home = temp_root / "codex-home"
            personal_agents = codex_home / "agents"
            personal_agents.mkdir(parents=True)
            target = personal_agents / "spark_worker.toml"
            target.write_text('name = "custom"\n', encoding="utf-8")
            result = install_profiles(
                skill_dir=SKILL_ROOT,
                repo_root=temp_root / "repo",
                codex_home=codex_home,
                scope="user",
                requested_workers=["spark"],
                install=True,
            )

            self.assertFalse(result["allowed"])
            self.assertEqual(target.read_text(encoding="utf-8"), 'name = "custom"\n')

    def test_installer_rejects_missing_reasoning_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            skill_root = temp_root / "skill"
            assets = skill_root / "assets" / "codex-workers"
            shutil.copytree(SKILL_ROOT / "assets" / "codex-workers", assets)
            manifest_path = assets / "manifest.yaml"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            del manifest["workers"]["spark"]["expected_reasoning_effort"]
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result = install_profiles(
                skill_dir=skill_root,
                repo_root=temp_root / "repo",
                codex_home=temp_root / "codex-home",
                scope="user",
                requested_workers=["spark"],
            )

        self.assertFalse(result["allowed"])
        self.assertTrue(
            any("expected_reasoning_effort" in error for error in result["errors"])
        )


if __name__ == "__main__":
    unittest.main()
