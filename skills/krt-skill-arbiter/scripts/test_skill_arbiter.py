#!/usr/bin/env python3
"""Contract tests for the Skill Arbiter portfolio checker."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
SCRIPTS = SKILL_ROOT / "scripts"


def run_script(name: str, *args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *(str(arg) for arg in args)],
        check=False,
        capture_output=True,
        text=True,
    )


class PortfolioContractTests(unittest.TestCase):
    @staticmethod
    def write_catalog(root: Path, *, safety_critical: bool) -> Path:
        catalog = root / "portfolio.json"
        catalog.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "skills": [
                        {
                            "id": "krt-safe-example",
                            "safety_critical": safety_critical,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return catalog

    def test_valid_fixture_passes_portfolio_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills" / "krt-safe-example"
            (skill / "agents").mkdir(parents=True)
            (skill / "references").mkdir()
            (root / "docs").mkdir()
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: krt-safe-example\n"
                "description: Test fixture.\n"
                "---\n\n"
                "# Safe Example\n\n"
                "Load `references/safety.md` before acting.\n",
                encoding="utf-8",
            )
            (skill / "agents" / "openai.yaml").write_text(
                'interface:\n'
                '  display_name: "krt-safe-example"\n'
                '  short_description: "Test fixture"\n'
                '  default_prompt: "Use krt-safe-example for this fixture."\n',
                encoding="utf-8",
            )
            (skill / "references" / "safety.md").write_text(
                "# Safety\n", encoding="utf-8"
            )
            (root / "docs" / "safety.md").write_text(
                "| Skill | Safety note |\n"
                "|---|---|\n"
                "| `krt-safe-example` | "
                "[`skills/krt-safe-example/references/safety.md`]"
                "(../skills/krt-safe-example/references/safety.md) |\n",
                encoding="utf-8",
            )

            catalog = self.write_catalog(root, safety_critical=True)
            result = run_script(
                "check_portfolio.py",
                "--repo-root",
                root,
                "--catalog",
                catalog,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["skill_count"], 1)
        self.assertEqual(payload["safety_critical_count"], 1)

    def test_default_catalog_validates_real_portfolio(self) -> None:
        result = run_script(
            "check_portfolio.py",
            "--repo-root",
            REPO_ROOT,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        catalog = json.loads(
            (SKILL_ROOT / "references" / "portfolio.json").read_text(encoding="utf-8")
        )["skills"]
        on_disk = [p for p in (REPO_ROOT / "skills").iterdir() if p.is_dir() and p.name.startswith("krt-")]
        self.assertEqual(payload["skill_count"], len(on_disk))
        self.assertEqual(
            sorted(payload["safety_critical_skills"]),
            sorted(item["id"] for item in catalog if item["safety_critical"]),
        )
        self.assertIn("krt-skill-arbiter", payload["safety_critical_skills"])

    def test_default_prompt_must_start_with_exact_canonical_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills" / "krt-safe-example"
            (skill / "agents").mkdir(parents=True)
            (root / "docs").mkdir()
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: krt-safe-example\n"
                "description: Test fixture.\n"
                "---\n\n"
                "# Safe Example\n",
                encoding="utf-8",
            )
            (skill / "agents" / "openai.yaml").write_text(
                'interface:\n'
                '  display_name: "krt-safe-example"\n'
                '  short_description: "Test fixture"\n'
                '  default_prompt: "Use $krt-safe-example for this fixture."\n',
                encoding="utf-8",
            )
            (root / "docs" / "safety.md").write_text(
                "# Safety\n", encoding="utf-8"
            )

            catalog = self.write_catalog(root, safety_critical=False)
            result = run_script(
                "check_portfolio.py",
                "--repo-root",
                root,
                "--catalog",
                catalog,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "default_prompt must start with 'Use krt-safe-example'",
            result.stderr,
        )

    def test_catalogued_critical_skill_requires_safety_wiring(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "skills" / "krt-safe-example"
            (skill / "agents").mkdir(parents=True)
            (root / "docs").mkdir()
            (skill / "SKILL.md").write_text(
                "---\n"
                "name: krt-safe-example\n"
                "description: Test fixture.\n"
                "---\n\n"
                "# Safe Example\n",
                encoding="utf-8",
            )
            (skill / "agents" / "openai.yaml").write_text(
                'interface:\n'
                '  display_name: "krt-safe-example"\n'
                '  short_description: "Test fixture"\n'
                '  default_prompt: "Use krt-safe-example fixture."\n',
                encoding="utf-8",
            )
            (root / "docs" / "safety.md").write_text(
                "# Safety\n",
                encoding="utf-8",
            )
            catalog = self.write_catalog(root, safety_critical=True)
            result = run_script(
                "check_portfolio.py",
                "--repo-root",
                root,
                "--catalog",
                catalog,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "safety-critical catalog entry requires references/safety.md",
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
