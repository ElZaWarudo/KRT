#!/usr/bin/env python3
"""Tests for adaptive wave planning."""

from __future__ import annotations

import unittest

from plan_adaptive_wave import plan_adaptive_wave


def request(
    identifier: str,
    *,
    role: str = "implementer",
    owned_paths: list[str] | None = None,
    risk_surfaces: list[str] | None = None,
    blocked: bool = False,
) -> dict[str, object]:
    return {
        "id": identifier,
        "role": role,
        "priority": 1,
        "owned_paths": owned_paths or [],
        "risk_surfaces": risk_surfaces or [],
        "unresolved_dependencies": [],
        "blocked": blocked,
    }


class AdaptiveWaveTest(unittest.TestCase):
    def plan(self, **overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_version": 1,
            "total_slots": 8,
            "reserve_slots": 1,
            "role_caps": {},
            "scale_authorized": True,
            "review_capacity": 4,
            "wave_history": [],
            "requests": [],
        }
        value.update(overrides)
        return value

    def test_four_green_waves_raise_cap_but_overlap_is_rejected(self) -> None:
        history = [
            {
                "result": "green",
                "scope_violations": 0,
                "merge_conflicts": 0,
                "review_lagging": False,
            }
            for _ in range(4)
        ]
        result = plan_adaptive_wave(
            self.plan(
                wave_history=history,
                requests=[
                    request("one", owned_paths=["src/one.py"]),
                    request("two", owned_paths=["src/two.py"]),
                    request("overlap", owned_paths=["src/one.py"]),
                    request("three", owned_paths=["src/three.py"]),
                    request("four", owned_paths=["src/four.py"]),
                ],
            )
        )

        self.assertEqual(result["implementer_cap"], 4)
        self.assertEqual(len(result["allocation"]["admitted"]), 4)
        rejected = {item["id"]: item["reason"] for item in result["allocation"]["rejected"]}
        self.assertEqual(rejected["overlap"], "surface-overlap")

    def test_failed_wave_or_missing_authorization_prevents_scaling(self) -> None:
        green_history = [
            {
                "result": "green",
                "scope_violations": 0,
                "merge_conflicts": 0,
                "review_lagging": False,
            }
            for _ in range(4)
        ]
        unauthorized = plan_adaptive_wave(
            self.plan(
                scale_authorized=False,
                wave_history=green_history,
                requests=[request(str(index)) for index in range(4)],
            )
        )
        failed = plan_adaptive_wave(
            self.plan(
                wave_history=[*green_history, {"result": "failed"}],
                requests=[request("one"), request("two")],
            )
        )

        self.assertEqual(unauthorized["implementer_cap"], 2)
        self.assertIn("scale-not-authorized", unauthorized["cap_reasons"])
        self.assertEqual(failed["implementer_cap"], 1)

    def test_high_risk_surface_and_blockers_are_serialized(self) -> None:
        result = plan_adaptive_wave(
            self.plan(
                requests=[
                    request("auth-one", risk_surfaces=["auth"]),
                    request("auth-two", risk_surfaces=["auth"]),
                    request("blocked", blocked=True),
                    request("review", role="reviewer"),
                ]
            )
        )
        rejected = {item["id"]: item["reason"] for item in result["allocation"]["rejected"]}

        self.assertEqual(rejected["auth-two"], "surface-overlap")
        self.assertEqual(rejected["blocked"], "blocked-or-dependency")
        self.assertIn("review", {item["id"] for item in result["allocation"]["admitted"]})


if __name__ == "__main__":
    unittest.main()
