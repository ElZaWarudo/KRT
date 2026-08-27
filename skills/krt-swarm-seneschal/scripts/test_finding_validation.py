#!/usr/bin/env python3
"""Tests for targeted finding validation evaluation."""

from __future__ import annotations

import unittest

from evaluate_finding_validation import evaluate_finding_validation
from finding_registry import ingest_findings, new_registry, validate_finding_verdict


def raw_finding(severity: str = "p1") -> dict[str, object]:
    return {
        "severity": severity,
        "principle": "correctness",
        "rule_id": "empty-array",
        "observation": "Empty arrays are rejected.",
        "impact": "Valid empty input fails.",
        "recommendation": "Accept an empty array.",
        "evidence": ["src/parser.py:10"],
    }


class FindingValidationTest(unittest.TestCase):
    def proposed(self) -> dict[str, object]:
        registry = new_registry(
            registry_id="review-run",
            contract_hash="sha256:contract",
            diff_digest="sha256:diff",
        )
        return ingest_findings(
            registry,
            {
                "contract_hash": "sha256:contract",
                "diff_digest": "sha256:diff",
                "review_plan_hash": "sha256:plan",
                "surface_id": "backend",
                "reporter_id": "reviewer-one",
                "findings": [raw_finding()],
            },
            expected_digest=registry["registry_digest"],
        )

    def validated(self, verdict: str = "confirmed") -> dict[str, object]:
        registry = self.proposed()
        finding_id = registry["findings"][0]["id"]
        return validate_finding_verdict(
            registry,
            {
                "finding_id": finding_id,
                "validator_id": "validator-one",
                "verdict": verdict,
                "evidence": ["tests/parser.py:20"],
                "revised_severity": None,
                "revised_observation": None,
                "revised_impact": None,
                "revised_recommendation": None,
            },
            expected_digest=registry["registry_digest"],
        )

    def batch(self, registry: dict[str, object], **overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "contract_hash": "sha256:contract",
            "diff_digest": "sha256:diff",
            "validator_id": "validator-one",
            "finding_ids": [registry["findings"][0]["id"]],
            "allow_new_critical": True,
            "new_critical_findings": [],
        }
        value.update(overrides)
        return value

    def test_confirms_targeted_actionable_finding(self) -> None:
        registry = self.validated()
        result = evaluate_finding_validation(registry, self.batch(registry))

        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["actionable_finding_ids"], self.batch(registry)["finding_ids"])

    def test_unvalidated_or_wrong_validator_fails_closed(self) -> None:
        proposed = self.proposed()
        with self.assertRaisesRegex(ValueError, "lacks validation"):
            evaluate_finding_validation(proposed, self.batch(proposed))
        validated = self.validated()
        with self.assertRaisesRegex(ValueError, "validator mismatch"):
            evaluate_finding_validation(
                validated, self.batch(validated, validator_id="validator-two")
            )

    def test_targeted_validator_can_raise_only_new_p0_or_p1(self) -> None:
        registry = self.validated()
        with self.assertRaisesRegex(ValueError, "only new p0 or p1"):
            evaluate_finding_validation(
                registry,
                self.batch(registry, new_critical_findings=[raw_finding("p2")]),
            )
        result = evaluate_finding_validation(
            registry,
            self.batch(registry, new_critical_findings=[raw_finding("p0")]),
        )
        self.assertEqual(result["new_critical_findings"][0]["severity"], "p0")

    def test_rejected_finding_is_not_actionable(self) -> None:
        registry = self.validated("rejected")
        result = evaluate_finding_validation(registry, self.batch(registry))

        self.assertEqual(result["actionable_finding_ids"], [])
        self.assertEqual(result["rejected_finding_ids"], self.batch(registry)["finding_ids"])

    def test_empty_batch_completes_only_when_no_findings_need_validation(self) -> None:
        empty = new_registry(
            registry_id="clean-review",
            contract_hash="sha256:contract",
            diff_digest="sha256:diff",
        )
        batch = {
            "contract_hash": "sha256:contract",
            "diff_digest": "sha256:diff",
            "validator_id": "validator-one",
            "finding_ids": [],
            "allow_new_critical": True,
            "new_critical_findings": [],
        }

        self.assertEqual(evaluate_finding_validation(empty, batch)["status"], "complete")
        with self.assertRaisesRegex(ValueError, "cannot omit proposed"):
            evaluate_finding_validation(self.proposed(), batch)


if __name__ == "__main__":
    unittest.main()
