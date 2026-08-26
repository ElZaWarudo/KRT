#!/usr/bin/env python3
"""Tests for adaptive wave planning."""

from __future__ import annotations

import unittest
import hashlib

from plan_adaptive_wave import plan_adaptive_wave
from verification_evidence import canonical_json


def scale_authorization(authorized: bool) -> dict[str, object]:
    value: dict[str, object] = {
        "authorization_id": "user-approval-1",
        "authorized": authorized,
        "authorized_by": "user",
        "max_implementers": 4 if authorized else 2,
    }
    value["authorization_digest"] = f"sha256:{hashlib.sha256(canonical_json(value)).hexdigest()}"
    return value


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
            "scale_authorization": scale_authorization(True),
            "review_capacity": 4,
            "wave_history": [],
            "requests": [],
        }
        value.update(overrides)
        return value

    def execute(self, plan: dict[str, object]) -> dict[str, object]:
        authorization = plan["scale_authorization"]
        assert isinstance(authorization, dict)
        digest = authorization["authorization_digest"]
        assert isinstance(digest, str)
        return plan_adaptive_wave(
            plan, expected_scale_authorization_digest=digest
        )

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
        result = self.execute(
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
        unauthorized = self.execute(
            self.plan(
                scale_authorization=scale_authorization(False),
                wave_history=green_history,
                requests=[request(str(index)) for index in range(4)],
            )
        )
        failed = self.execute(
            self.plan(
                wave_history=[*green_history, {"result": "failed"}],
                requests=[request("one"), request("two")],
            )
        )

        self.assertEqual(unauthorized["implementer_cap"], 2)
        self.assertIn("scale-not-authorized", unauthorized["cap_reasons"])
        self.assertEqual(failed["implementer_cap"], 1)

    def test_high_risk_surface_and_blockers_are_serialized(self) -> None:
        result = self.execute(
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

    def test_scale_authorization_cannot_be_changed_without_invalidating_digest(self) -> None:
        authorization = scale_authorization(True)
        authorization["max_implementers"] = 8

        with self.assertRaisesRegex(ValueError, "digest"):
            plan_adaptive_wave(
                self.plan(scale_authorization=authorization),
                expected_scale_authorization_digest=scale_authorization(True)["authorization_digest"],
            )

    def test_self_consistent_authorization_without_trusted_handoff_is_rejected(self) -> None:
        forged = scale_authorization(True)
        forged["authorization_id"] = "forged"
        unsigned = {key: value for key, value in forged.items() if key != "authorization_digest"}
        forged["authorization_digest"] = f"sha256:{hashlib.sha256(canonical_json(unsigned)).hexdigest()}"

        with self.assertRaisesRegex(ValueError, "trusted handoff"):
            plan_adaptive_wave(
                self.plan(scale_authorization=forged),
                expected_scale_authorization_digest=scale_authorization(True)["authorization_digest"],
            )


if __name__ == "__main__":
    unittest.main()
