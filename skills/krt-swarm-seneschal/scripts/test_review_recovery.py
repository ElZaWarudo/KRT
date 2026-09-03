#!/usr/bin/env python3
"""Tests for non-certifying review recovery artifacts."""

from __future__ import annotations

import unittest

from plan_review_wave import plan_review_wave
from validate_review_recovery import validate_review_recovery


class ReviewRecoveryTest(unittest.TestCase):
    def plan(self) -> dict[str, object]:
        return plan_review_wave({
            "schema_version": 2,
            "assurance_tier": "high",
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

    def recovery(self, **overrides: object) -> dict[str, object]:
        plan = self.plan()
        value: dict[str, object] = {
            "schema_version": 1,
            "contract_hash": "sha256:contract",
            "diff_digest": "sha256:diff",
            "review_plan_hash": plan["review_plan_hash"],
            "reviewer_id": "reviewer-one",
            "surface_id": "backend",
            "risk_boundaries_checked": ["input"],
            "candidate_findings": [],
            "candidate_feedback": [],
            "stop_reason": "interrupted",
            "certifies_review": False,
        }
        value.update(overrides)
        return value

    def test_accepts_partial_coverage_without_certification(self) -> None:
        result = validate_review_recovery(self.plan(), self.recovery())
        self.assertTrue(result["valid"])
        self.assertFalse(result["certifies_review"])
        self.assertEqual(result["checked_boundary_count"], 1)

    def test_rejects_unassigned_boundary_or_certification(self) -> None:
        with self.assertRaisesRegex(ValueError, "unassigned"):
            validate_review_recovery(
                self.plan(), self.recovery(risk_boundaries_checked=["other"])
            )
        with self.assertRaisesRegex(ValueError, "certifies_review"):
            validate_review_recovery(
                self.plan(), self.recovery(certifies_review=True)
            )


if __name__ == "__main__":
    unittest.main()
