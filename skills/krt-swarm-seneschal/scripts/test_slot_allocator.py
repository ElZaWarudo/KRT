#!/usr/bin/env python3
"""Tests for functional Seneschal slot allocation."""

from __future__ import annotations

import unittest

from allocate_worker_slots import allocate_slots


class SlotAllocatorTest(unittest.TestCase):
    def test_capacity_reserve_and_role_caps_are_enforced(self) -> None:
        plan = {
            "schema_version": 1,
            "total_slots": 8,
            "reserve_slots": 1,
            "role_caps": {},
            "requests": [
                {"id": "impl-1", "role": "implementer", "priority": 1},
                {"id": "impl-2", "role": "implementer", "priority": 1},
                {"id": "impl-3", "role": "implementer", "priority": 1},
                {"id": "review-1", "role": "reviewer", "priority": 1},
                {"id": "review-2", "role": "reviewer", "priority": 1},
                {"id": "security-1", "role": "security", "priority": 1},
                {"id": "ci-1", "role": "ci-platform", "priority": 1},
                {"id": "integrate-1", "role": "integrator", "priority": 1},
                {"id": "docs-1", "role": "documenter", "priority": 1},
            ],
        }

        result = allocate_slots(plan)

        self.assertEqual(len(result["admitted"]), 7)
        self.assertEqual(result["reserve_slots"], 1)
        rejected = {item["id"]: item["reason"] for item in result["rejected"]}
        self.assertEqual(rejected["impl-3"], "role-cap")
        self.assertEqual(rejected["docs-1"], "capacity-reserved")
        self.assertEqual(result["active_by_role"]["implementer"], 2)

    def test_invalid_or_duplicate_requests_are_rejected(self) -> None:
        plan = {
            "schema_version": 1,
            "total_slots": 4,
            "reserve_slots": 1,
            "role_caps": {},
            "requests": [
                {"id": "same", "role": "implementer", "priority": 1},
                {"id": "same", "role": "reviewer", "priority": 1},
            ],
        }
        with self.assertRaisesRegex(ValueError, "unique"):
            allocate_slots(plan)


if __name__ == "__main__":
    unittest.main()
