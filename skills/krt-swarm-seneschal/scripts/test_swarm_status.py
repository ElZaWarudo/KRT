#!/usr/bin/env python3
"""Tests for the compact derived swarm status panel."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from render_swarm_status import build_snapshot, load_structured, render_text


class SwarmStatusTest(unittest.TestCase):
    def test_panel_derives_wave_gates_blockers_slots_and_evidence(self) -> None:
        queue = {
            "documentation_gate": {"status": "approved"},
            "units": {
                "one": {"status": "release-ready"},
                "two": {"status": "running"},
                "three": {"status": "review-gated"},
                "four": {"status": "blocked"},
            },
            "wave_history": [
                {
                    "id": "wave-4",
                    "selected_units": ["one", "two", "three", "four"],
                    "result": "running",
                    "aggregate_verification": {
                        "result": "passed",
                        "fingerprint": "sha256:1234567890abcdef",
                    },
                    "gates": {"scope": "passed", "state": "current"},
                }
            ],
        }
        blockers = {
            "blockers": [
                {"status": "open", "risk": "high"},
                {"status": "resolved", "risk": "high"},
            ]
        }
        evidence = {"records": [{"result": "passed"}, {"result": "failed"}]}
        allocation = {
            "allocation": {
                "admitted": [{"id": "impl"}, {"id": "review"}],
                "usable_slots": 7,
                "reserve_slots": 1,
            }
        }

        snapshot = build_snapshot(
            queue=queue,
            blockers=blockers,
            evidence=evidence,
            allocation=allocation,
        )
        rendered = render_text(snapshot)

        self.assertEqual(snapshot["wave"]["completed"], 1)
        self.assertEqual(snapshot["blockers"], {"open": 1, "high_risk": 1})
        self.assertEqual(snapshot["slots"], {"active": 2, "usable": 7, "reserved": 1})
        self.assertIn("Wave wave-4", rendered)
        self.assertIn("verification=passed", rendered)

    def test_panel_rejects_stale_wave_unit_projection(self) -> None:
        with self.assertRaisesRegex(ValueError, "inconsistent"):
            build_snapshot(
                queue={
                    "units": {"one": {"status": "ready"}},
                    "wave_history": [{"id": "wave", "selected_units": ["missing"]}],
                },
                blockers={"blockers": []},
                evidence={"records": []},
                allocation={},
            )

    def test_panel_loads_canonical_yaml_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "queue-state.yaml"
            path.write_text(
                "schema_version: 2\nunits:\n  one:\n    status: ready\n",
                encoding="utf-8",
            )
            loaded = load_structured(path, default={})

        self.assertEqual(loaded["units"]["one"]["status"], "ready")


if __name__ == "__main__":
    unittest.main()
