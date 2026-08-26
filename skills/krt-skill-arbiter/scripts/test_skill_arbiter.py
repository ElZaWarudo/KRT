#!/usr/bin/env python3
"""Contract tests for the deterministic Skill Arbiter utilities."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from functools import cache
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
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


@cache
def corpus_identity() -> dict[str, object]:
    checked = run_script("check_corpus.py", CASES, EXPECTATIONS)
    if checked.returncode != 0:
        raise AssertionError(checked.stderr)
    payload = json.loads(checked.stdout)
    return {
        "schema_version": 1,
        "corpus_version": payload["corpus_version"],
        "corpus_digest": payload["corpus_digest"],
    }


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

    def test_routing_expectation_requires_skill(self) -> None:
        cases = json.loads(CASES.read_text(encoding="utf-8"))
        expectations = json.loads(EXPECTATIONS.read_text(encoding="utf-8"))
        routing_id = next(
            case["id"]
            for case in cases["cases"]
            if case["category"] == "routing"
        )
        next(
            item
            for item in expectations["expectations"]
            if item["id"] == routing_id
        )["expected_skill"] = None

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "expectations.json"
            path.write_text(json.dumps(expectations), encoding="utf-8")
            result = run_script("check_corpus.py", CASES, path)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("routing expected_skill must be a KRT ID", result.stderr)

    def test_negative_trigger_expectation_requires_null_skill(self) -> None:
        cases = json.loads(CASES.read_text(encoding="utf-8"))
        expectations = json.loads(EXPECTATIONS.read_text(encoding="utf-8"))
        negative_id = next(
            case["id"]
            for case in cases["cases"]
            if case["category"] == "negative-trigger"
        )
        next(
            item
            for item in expectations["expectations"]
            if item["id"] == negative_id
        )["expected_skill"] = "krt-security-sentinel"

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "expectations.json"
            path.write_text(json.dumps(expectations), encoding="utf-8")
            result = run_script("check_corpus.py", CASES, path)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "negative-trigger expected_skill must be null",
            result.stderr,
        )


class ScoreRunTests(unittest.TestCase):
    def test_score_preserves_inconclusive_results(self) -> None:
        results = {
            **corpus_identity(),
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
            **corpus_identity(),
            "results": [{"case_id": "not-in-the-corpus", "status": "pass"}],
        }

        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "results.json"
            result_path.write_text(json.dumps(results), encoding="utf-8")
            result = run_script("score_run.py", result_path, CASES)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown case_id", result.stderr)

    def test_score_rejects_mismatched_corpus_identity(self) -> None:
        results = {
            **corpus_identity(),
            "corpus_version": "old-corpus",
            "results": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "results.json"
            result_path.write_text(json.dumps(results), encoding="utf-8")
            result = run_script("score_run.py", result_path, CASES)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("corpus_version does not match", result.stderr)

    def test_score_rejects_mismatched_digest(self) -> None:
        results = {
            **corpus_identity(),
            "corpus_digest": "0" * 64,
            "results": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "results.json"
            result_path.write_text(json.dumps(results), encoding="utf-8")
            result = run_script("score_run.py", result_path, CASES)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("corpus_digest does not match", result.stderr)

    def test_score_rejects_boolean_schema_version(self) -> None:
        results = {
            **corpus_identity(),
            "schema_version": True,
            "results": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "results.json"
            result_path.write_text(json.dumps(results), encoding="utf-8")
            result = run_script("score_run.py", result_path, CASES)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("schema_version must be integer 1", result.stderr)

    def test_score_rejects_duplicate_and_invalid_status(self) -> None:
        results = {
            **corpus_identity(),
            "results": [
                {"case_id": "routing-security-review", "status": "pass"},
                {"case_id": "routing-security-review", "status": "unknown"},
                {"case_id": "routing-repo-health", "status": "unknown"},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            result_path = Path(directory) / "results.json"
            result_path.write_text(json.dumps(results), encoding="utf-8")
            result = run_script("score_run.py", result_path, CASES)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate case_id", result.stderr)
        self.assertIn("status must be pass, fail, or inconclusive", result.stderr)


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
        self.assertEqual(payload["skill_count"], 28)
        self.assertEqual(payload["safety_critical_count"], 21)
        self.assertIn("krt-document-forge", payload["safety_critical_skills"])
        self.assertIn("krt-real-world-edge-testing", payload["safety_critical_skills"])
        self.assertIn("krt-skill-arbiter", payload["safety_critical_skills"])
        self.assertIn("krt-word-illuminator", payload["safety_critical_skills"])

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
