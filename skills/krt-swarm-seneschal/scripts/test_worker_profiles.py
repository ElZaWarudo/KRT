#!/usr/bin/env python3
"""Tests for worker installation, discovery, and fail-closed behavior."""

from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
