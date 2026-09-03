#!/usr/bin/env python3
"""Tests for deterministic review-surface planning."""

from __future__ import annotations

import unittest

from plan_review_wave import plan_review_wave


def surface(
    identifier: str,
    paths: list[str],
    *,
    cross_cutting: bool = False,
    role: str = "reviewer",
    priority: int = 1,
) -> dict[str, object]:
    return {
        "id": identifier,
        "reviewer_role": role,
        "owned_paths": paths,
        "risk_boundaries": [f"{identifier}-boundary"],
        "cross_cutting": cross_cutting,
        "priority": priority,
    }


class ReviewWaveTest(unittest.TestCase):
    def plan(self, **overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_version": 2,
            "assurance_tier": "high",
            "contract_hash": "sha256:contract",
            "diff_digest": "sha256:diff",
            "changed_paths": ["src/api.py", "src/ui.ts"],
            "reviewer_capacity": 3,
            "surfaces": [
                surface("backend", ["src/api.py"]),
                surface("frontend", ["src/ui.ts"]),
            ],
        }
        value.update(overrides)
        return value

    def test_partitions_primary_surfaces_and_requests_validation_wave(self) -> None:
        result = plan_review_wave(self.plan())

        self.assertTrue(result["coverage_complete"])
        self.assertTrue(result["validation_wave_required"])
        self.assertFalse(result["approval_required"])
        self.assertEqual(
            [assignment["id"] for assignment in result["assignments"]],
            ["backend", "frontend"],
        )
        self.assertTrue(result["review_plan_hash"].startswith("sha256:"))

    def test_cross_cutting_security_overlap_is_explicitly_allowed(self) -> None:
        result = plan_review_wave(
            self.plan(
                surfaces=[
                    surface("backend", ["src/api.py"]),
                    surface("frontend", ["src/ui.ts"]),
                    surface(
                        "security",
                        ["src/api.py", "src/ui.ts"],
                        cross_cutting=True,
                        role="security-sentinel",
                    ),
                ]
            )
        )

        self.assertTrue(result["coverage_complete"])
        self.assertEqual(len(result["assignments"]), 3)

    def test_uncovered_or_overlapping_primary_paths_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "lack a primary"):
            plan_review_wave(self.plan(surfaces=[surface("backend", ["src/api.py"])]))
        with self.assertRaisesRegex(ValueError, "overlap"):
            plan_review_wave(
                self.plan(
                    surfaces=[
                        surface("one", ["src/api.py", "src/ui.ts"]),
                        surface("two", ["src/ui.ts"]),
                    ]
                )
            )

    def test_capacity_queues_excess_reviewers_without_claiming_complete_coverage(self) -> None:
        result = plan_review_wave(
            self.plan(
                reviewer_capacity=1,
                surfaces=[
                    surface("backend", ["src/api.py"], priority=0),
                    surface("frontend", ["src/ui.ts"], priority=1),
                ],
            )
        )

        self.assertFalse(result["coverage_complete"])
        self.assertTrue(result["validation_wave_required"])
        self.assertEqual(result["queued"][0]["reason"], "reviewer-capacity")
        self.assertEqual(result["queued"][0]["assignment"]["id"], "frontend")
        self.assertEqual(
            result["queued"][0]["assignment"]["risk_boundaries"],
            ["frontend-boundary"],
        )

    def test_input_order_does_not_change_hash(self) -> None:
        left = plan_review_wave(self.plan())
        right = plan_review_wave(
            self.plan(
                changed_paths=["src/ui.ts", "src/api.py"],
                surfaces=[
                    surface("frontend", ["src/ui.ts"]),
                    surface("backend", ["src/api.py"]),
                ],
            )
        )

        self.assertEqual(left["review_plan_hash"], right["review_plan_hash"])

    def test_low_and_medium_assurance_bypass_coordinated_review(self) -> None:
        for tier in ("low", "medium"):
            with self.subTest(tier=tier):
                with self.assertRaisesRegex(ValueError, "high or critical"):
                    plan_review_wave(self.plan(assurance_tier=tier))

    def test_critical_assurance_requires_approval(self) -> None:
        result = plan_review_wave(self.plan(assurance_tier="critical"))

        self.assertTrue(result["validation_wave_required"])
        self.assertTrue(result["approval_required"])

    def test_critical_assurance_requires_a_review_council(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least two"):
            plan_review_wave(
                self.plan(
                    assurance_tier="critical",
                    changed_paths=["src/api.py"],
                    surfaces=[surface("backend", ["src/api.py"])],
                )
            )

    def test_schema_one_requires_migration(self) -> None:
        with self.assertRaisesRegex(ValueError, "schema_version must be 2"):
            plan_review_wave(self.plan(schema_version=1))


if __name__ == "__main__":
    unittest.main()
