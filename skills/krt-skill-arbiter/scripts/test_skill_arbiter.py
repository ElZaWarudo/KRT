#!/usr/bin/env python3
"""Contract tests for the deterministic Skill Arbiter utilities."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
CASES = SKILL_ROOT / "references" / "cases.json"
EXPECTATIONS = SKILL_ROOT / "references" / "expectations.json"


def run_script(name: str, *args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *(str(arg) for arg in args)],
        check=False,
        capture_output=True,
        text=True,
    )


class CorpusContractTests(unittest.TestCase):
    def test_bundled_corpus_is_valid(self) -> None:
        result = run_script("check_corpus.py", CASES, EXPECTATIONS)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["case_count"], 12)
        self.assertEqual(
            payload["categories"],
            {
                "fallback": 2,
                "negative-trigger": 2,
                "outcome": 2,
                "permissions": 2,
                "restart": 2,
                "routing": 2,
            },
        )

    def test_routing_case_cannot_reveal_target_skill(self) -> None:
        cases = json.loads(CASES.read_text(encoding="utf-8"))
        routing_case = next(
            case for case in cases["cases"] if case["evaluation_mode"] == "routing"
        )
        routing_case["target_skill"] = "krt-security-sentinel"

        with tempfile.TemporaryDirectory() as directory:
            invalid_cases = Path(directory) / "cases.json"
            invalid_cases.write_text(json.dumps(cases), encoding="utf-8")
            result = run_script("check_corpus.py", invalid_cases, EXPECTATIONS)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must not expose target_skill", result.stderr)

    def test_capability_target_must_exist_in_skills_root(self) -> None:
        cases = json.loads(CASES.read_text(encoding="utf-8"))
        capability_case = next(
            case
            for case in cases["cases"]
            if case["evaluation_mode"] == "capability"
        )
        capability_case["target_skill"] = "krt-missing-skill"
        capability_case["prompt"] = (
            "Use krt-missing-skill to exercise this capability case."
        )

        with tempfile.TemporaryDirectory() as directory:
            invalid_cases = Path(directory) / "cases.json"
            invalid_cases.write_text(json.dumps(cases), encoding="utf-8")
            result = run_script(
                "check_corpus.py",
                invalid_cases,
                EXPECTATIONS,
                "--skills-root",
                SKILL_ROOT.parent,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("target_skill does not exist", result.stderr)


class ScoreRunTests(unittest.TestCase):
    def test_score_preserves_inconclusive_results(self) -> None:
        results = {
            "run_id": "test-run",
            "results": [
                {"case_id": "routing-security-review", "status": "pass"},
                {"case_id": "routing-repo-health", "status": "fail"},
                {
                    "case_id": "negative-no-security-for-style",
                    "status": "inconclusive",
                },
            ],
        }

        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "results.json"
            result_path.write_text(json.dumps(results), encoding="utf-8")
            result = run_script("score_run.py", result_path, CASES)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["counts"], {"fail": 1, "inconclusive": 1, "pass": 1})
        self.assertEqual(payload["submitted"], 3)
        self.assertEqual(payload["corpus_coverage"], 0.25)
        self.assertEqual(payload["conclusive_pass_rate"], 0.5)

    def test_score_rejects_unknown_case(self) -> None:
        results = {
            "results": [{"case_id": "not-in-the-corpus", "status": "pass"}],
        }

        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "results.json"
            result_path.write_text(json.dumps(results), encoding="utf-8")
            result = run_script("score_run.py", result_path, CASES)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown case_id", result.stderr)


class PortfolioContractTests(unittest.TestCase):
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

            result = run_script("check_portfolio.py", "--repo-root", root)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["skill_count"], 1)
        self.assertEqual(payload["safety_critical_count"], 1)

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

            result = run_script("check_portfolio.py", "--repo-root", root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "default_prompt must start with 'Use krt-safe-example'",
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
