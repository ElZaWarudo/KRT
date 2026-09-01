#!/usr/bin/env python3
"""Tests for the Council cognitive-load overlay gate."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("check_cognitive_overlay.py")


def bundle() -> dict:
    return {
        "context": {
            "cognitive_load_requested": False,
            "workload_comparison_required": False,
        },
        "evaluators": [
            {"evaluator": f"{number:02d}", "findings": []}
            for number in range(1, 13)
        ],
    }


def finding(
    finding_id: str,
    *,
    severity: str = "P2",
    factor: str = "M",
    flow: str = "FLOW-01",
    profile: str = "ROLE-01",
    sensitivity: str = "none",
) -> dict:
    return {
        "id": finding_id,
        "severity": severity,
        "affected": [flow, profile],
        "cognitive_load": {
            "factors": [factor],
            "profile": profile,
            "rationale": "The target user must retain hidden state during the task.",
            "claim_basis": "heuristic",
            "profile_sensitivity": sensitivity,
            "court_referral": "candidate",
        },
    }


def run(value: dict) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "bundle.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(path)],
            check=False,
            capture_output=True,
            text=True,
        )


class CognitiveOverlayTests(unittest.TestCase):
    def test_all_twelve_empty_outputs_are_valid_without_referral(self) -> None:
        result = run(bundle())

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["evaluator_count"], 12)
        self.assertEqual(payload["finding_count"], 0)
        self.assertFalse(payload["court_required"])

    def test_missing_evaluator_is_invalid(self) -> None:
        value = bundle()
        value["evaluators"].pop()

        result = run(value)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing evaluators: 12", result.stderr)

    def test_missing_overlay_is_invalid(self) -> None:
        value = bundle()
        value["evaluators"][0]["findings"] = [
            {"id": "POL-01-001", "severity": "P2", "affected": ["FLOW-01"]}
        ]

        result = run(value)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing cognitive_load object", result.stderr)

    def test_two_independent_matching_signals_require_court(self) -> None:
        value = bundle()
        value["evaluators"][0]["findings"] = [finding("POL-01-001")]
        value["evaluators"][1]["findings"] = [finding("POL-02-001")]

        result = run(value)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["court_required"])
        repeated = next(
            item for item in payload["triggers"] if item["type"] == "repeated-signal"
        )
        self.assertEqual(repeated["evaluators"], ["01", "02"])

    def test_p1_cognitive_finding_requires_court(self) -> None:
        value = bundle()
        value["evaluators"][0]["findings"] = [
            finding("POL-01-001", severity="P1")
        ]

        result = run(value)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["court_required"])
        self.assertIn(
            "high-severity-cognitive-finding",
            {item["type"] for item in payload["triggers"]},
        )

    def test_profile_reversal_requires_court(self) -> None:
        value = bundle()
        value["evaluators"][0]["findings"] = [
            finding("POL-01-001", sensitivity="possible-reversal")
        ]

        result = run(value)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["court_required"])
        self.assertIn(
            "profile-reversal",
            {item["type"] for item in payload["triggers"]},
        )

    def test_explicit_request_requires_court_without_findings(self) -> None:
        value = bundle()
        value["context"]["cognitive_load_requested"] = True

        result = run(value)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["court_required"])
        self.assertEqual(payload["triggers"], [{"type": "explicit-request"}])


if __name__ == "__main__":
    unittest.main()
