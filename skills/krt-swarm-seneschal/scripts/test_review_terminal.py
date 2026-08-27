#!/usr/bin/env python3
"""Tests for deterministic review-terminal validation."""

from __future__ import annotations

import unittest

from plan_review_wave import plan_review_wave
from validate_review_terminal import validate_review_terminal


def finding(severity: str = "p1", *, suffix: str = "one") -> dict[str, object]:
    return {
        "severity": severity,
        "principle": "correctness",
        "rule_id": f"rule-{suffix}",
        "observation": "Observed behavior",
        "impact": "Concrete impact",
        "recommendation": "Bounded correction",
        "evidence": [f"src/example.py:{suffix}"],
    }


class ReviewTerminalTest(unittest.TestCase):
    def plan(self) -> dict[str, object]:
        return plan_review_wave({
            "schema_version": 1,
            "contract_hash": "sha256:contract",
            "diff_digest": "sha256:diff",
            "changed_paths": ["src/example.py"],
            "reviewer_capacity": 1,
            "surfaces": [{
                "id": "backend",
                "reviewer_role": "reviewer",
                "owned_paths": ["src/example.py"],
                "risk_boundaries": ["input", "output"],
                "cross_cutting": False,
                "priority": 0,
            }],
        })

    def terminal(self, **overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "contract_hash": "sha256:contract",
            "diff_digest": "sha256:diff",
            "review_plan_hash": self.plan()["review_plan_hash"],
            "reviewer_id": "reviewer-one",
            "surface_id": "backend",
            "risk_boundaries_checked": ["input", "output"],
            "findings": [],
            "finding_feedback": [],
            "suppressed_speculative_count": 0,
            "stop_reason": "coverage-complete",
        }
        value.update(overrides)
        return value

    def test_accepts_complete_coverage_and_uncapped_p0_p1(self) -> None:
        findings = [finding("p0", suffix=str(index)) for index in range(4)]
        findings.extend(finding("p1", suffix=f"p1-{index}") for index in range(4))

        result = validate_review_terminal(
            self.plan(), self.terminal(findings=findings)
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["finding_counts"]["p0"], 4)
        self.assertEqual(result["finding_counts"]["p1"], 4)

    def test_rejects_incomplete_or_duplicate_boundary_coverage(self) -> None:
        with self.assertRaisesRegex(ValueError, "coverage"):
            validate_review_terminal(
                self.plan(), self.terminal(risk_boundaries_checked=["input"])
            )
        with self.assertRaisesRegex(ValueError, "coverage"):
            validate_review_terminal(
                self.plan(),
                self.terminal(risk_boundaries_checked=["input", "output", "output"]),
            )

    def test_caps_only_actionable_p2_findings(self) -> None:
        with self.assertRaisesRegex(ValueError, "three actionable p2"):
            validate_review_terminal(
                self.plan(),
                self.terminal(
                    findings=[finding("p2", suffix=str(index)) for index in range(4)]
                ),
            )

    def test_rejects_p3_and_speculative_evidence_free_findings(self) -> None:
        invalid = finding("p1")
        invalid["severity"] = "p3"
        with self.assertRaisesRegex(ValueError, "severity"):
            validate_review_terminal(self.plan(), self.terminal(findings=[invalid]))
        invalid = finding("p2")
        invalid["evidence"] = []
        with self.assertRaisesRegex(ValueError, "evidence"):
            validate_review_terminal(self.plan(), self.terminal(findings=[invalid]))

    def test_hashes_and_stop_reason_are_contract_bound(self) -> None:
        with self.assertRaisesRegex(ValueError, "diff_digest"):
            validate_review_terminal(
                self.plan(), self.terminal(diff_digest="sha256:other")
            )
        with self.assertRaisesRegex(ValueError, "stop_reason"):
            validate_review_terminal(
                self.plan(), self.terminal(stop_reason="finding-budget")
            )

    def test_accepts_canonical_feedback_and_queued_assignments(self) -> None:
        plan = plan_review_wave({
            "schema_version": 1,
            "contract_hash": "sha256:contract",
            "diff_digest": "sha256:diff",
            "changed_paths": ["src/example.py", "src/queued.py"],
            "reviewer_capacity": 1,
            "surfaces": [
                {
                    "id": "backend",
                    "reviewer_role": "reviewer",
                    "owned_paths": ["src/example.py"],
                    "risk_boundaries": ["input", "output"],
                    "cross_cutting": False,
                    "priority": 0,
                },
                {
                    "id": "queued",
                    "reviewer_role": "reviewer",
                    "owned_paths": ["src/queued.py"],
                    "risk_boundaries": ["queue"],
                    "cross_cutting": False,
                    "priority": 1,
                },
            ],
        })
        terminal = self.terminal(
            review_plan_hash=plan["review_plan_hash"],
            surface_id="queued",
            risk_boundaries_checked=["queue"],
            finding_feedback=[{
                "finding_id": "F-1234ABCD",
                "action": "challenge",
                "rationale": "An upstream guard may cover this path.",
                "evidence": ["src/guard.py:10"],
            }],
        )

        result = validate_review_terminal(plan, terminal)

        self.assertEqual(result["surface_id"], "queued")
        self.assertEqual(result["finding_feedback_count"], 1)

    def test_rejects_a_tampered_review_plan_hash(self) -> None:
        plan = self.plan()
        plan["review_plan_hash"] = "sha256:tampered"
        with self.assertRaisesRegex(ValueError, "plan hash"):
            validate_review_terminal(
                plan, self.terminal(review_plan_hash="sha256:tampered")
            )


if __name__ == "__main__":
    unittest.main()
