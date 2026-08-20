#!/usr/bin/env python3
"""Tests for deterministic Seneschal timing telemetry."""

from __future__ import annotations

import json
import multiprocessing
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from record_run_timing import record_timing


SCRIPT = Path(__file__).with_name("record_run_timing.py")


def record_concurrent(output: str, unit_id: str, start: object) -> None:
    """Write one distinct unit after all child processes are ready."""
    start.wait()
    record_timing(
        output=Path(output),
        run_id="run-concurrent",
        wave_id="wave-concurrent",
        unit_id=unit_id,
        lane="standard",
        worker_profile="luna",
        phases={"implementation": 10},
        context_bytes=100,
        verification_fingerprint=f"sha256:{unit_id}",
        review_rounds=0,
        fix_rounds=0,
        status="completed",
    )


class RunTimingTest(unittest.TestCase):
    def timing_args(self, output: Path, **overrides: object) -> dict[str, object]:
        values: dict[str, object] = {
            "output": output,
            "run_id": "run-1",
            "wave_id": "wave-1",
            "unit_id": "unit-1",
            "lane": "standard",
            "worker_profile": "luna",
            "phases": {},
            "context_bytes": 0,
            "verification_fingerprint": None,
            "review_rounds": 0,
            "fix_rounds": 0,
            "status": "planned",
        }
        values.update(overrides)
        return values

    def test_each_lane_records_manifest_owned_model_policy(self) -> None:
        routes = {
            "fast": ("spark", "spark", "xhigh"),
            "standard": ("luna", "luna", "high"),
            "deep": ("luna_xhigh", "luna", "xhigh"),
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "timing.json"
            for lane, (profile, model_class, effort) in routes.items():
                with self.subTest(lane=lane):
                    record = record_timing(
                        **self.timing_args(
                            output,
                            unit_id=f"unit-{lane}",
                            lane=lane,
                            worker_profile=profile,
                        )
                    )
                    self.assertEqual(record["worker_profile"], profile)
                    self.assertEqual(record["model_class"], model_class)
                    self.assertEqual(record["reasoning_effort"], effort)

    def test_record_is_created_and_phase_updates_are_merged(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "runs" / "timing.json"
            common = {
                "output": output,
                "run_id": "run-1",
                "wave_id": "wave-1",
                "unit_id": "unit-1",
                "lane": "standard",
                "worker_profile": "luna",
                "context_bytes": 2048,
                "verification_fingerprint": "sha256:abc",
                "review_rounds": 1,
                "fix_rounds": 0,
                "captured_at": "2026-08-19T10:00:00Z",
            }
            record_timing(
                **common,
                phases={"preflight": 20, "implementation": 80},
                status="running",
            )
            record = record_timing(
                **{
                    **common,
                    "context_bytes": None,
                    "verification_fingerprint": None,
                    "review_rounds": None,
                    "fix_rounds": None,
                    "captured_at": None,
                },
                phases={"verification": 30},
                status="completed",
            )
            document = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(document["schema_version"], 1)
        self.assertEqual(len(document["records"]), 1)
        self.assertEqual(record["total_duration_ms"], 130)
        self.assertEqual(
            record["phase_duration_ms"],
            {"preflight": 20, "implementation": 80, "verification": 30},
        )
        self.assertEqual(record["status"], "completed")
        self.assertEqual(record["context_bytes"], 2048)
        self.assertEqual(record["verification_fingerprint"], "sha256:abc")
        self.assertEqual(record["review_rounds"], 1)
        self.assertEqual(record["fix_rounds"], 0)

    def test_lane_profile_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "requires worker"):
                record_timing(
                    output=Path(temp_dir) / "timing.json",
                    run_id="run-1",
                    wave_id="wave-1",
                    unit_id="unit-1",
                    lane="fast",
                    worker_profile="luna",
                    phases={},
                    context_bytes=0,
                    verification_fingerprint=None,
                    review_rounds=0,
                    fix_rounds=0,
                    status="planned",
                )

    def test_negative_counters_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "timing.json"
            for field in ("context_bytes", "review_rounds", "fix_rounds"):
                with self.subTest(field=field):
                    with self.assertRaisesRegex(ValueError, "non-negative"):
                        record_timing(
                            **self.timing_args(output, **{field: -1})
                        )

    def test_malformed_document_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "timing.json"
            output.write_text(
                '{"schema_version": 2, "records": {}}', encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "schema_version 1"):
                record_timing(**self.timing_args(output))

    def test_unknown_and_negative_phases_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "timing.json"
            for phases in ({"unknown": 1}, {"review": -1}):
                with self.subTest(phases=phases):
                    with self.assertRaisesRegex(ValueError, "invalid phase"):
                        record_timing(
                            **self.timing_args(output, phases=phases)
                        )

    def test_cli_accepts_valid_phase_and_rejects_malformed_phase(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "timing.json"
            command = [
                sys.executable,
                str(SCRIPT),
                "--output",
                str(output),
                "--run-id",
                "run-cli",
                "--wave-id",
                "wave-cli",
                "--unit-id",
                "unit-cli",
                "--lane",
                "fast",
                "--worker-profile",
                "spark",
                "--status",
                "completed",
            ]
            valid = subprocess.run(
                [*command, "--phase", "verification=42"],
                check=False,
                capture_output=True,
                text=True,
            )
            malformed = subprocess.run(
                [*command, "--phase", "verification"],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertEqual(json.loads(valid.stdout)["total_duration_ms"], 42)
        self.assertNotEqual(malformed.returncode, 0)
        self.assertIn("phase must use NAME=MILLISECONDS", malformed.stderr)

    def test_concurrent_distinct_unit_updates_are_not_lost(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "timing.json"
            context = multiprocessing.get_context("spawn")
            start = context.Event()
            processes = [
                context.Process(
                    target=record_concurrent,
                    args=(str(output), f"unit-{index}", start),
                )
                for index in range(8)
            ]
            for process in processes:
                process.start()
            start.set()
            for process in processes:
                process.join(timeout=15)
                self.assertEqual(process.exitcode, 0)
            document = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(len(document["records"]), len(processes))
        self.assertEqual(
            {record["unit_id"] for record in document["records"]},
            {f"unit-{index}" for index in range(len(processes))},
        )

    def test_terminal_status_cannot_regress(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "timing.json"
            record_timing(
                **self.timing_args(output, status="completed")
            )
            with self.assertRaisesRegex(ValueError, "cannot transition"):
                record_timing(
                    **self.timing_args(output, status="running")
                )


if __name__ == "__main__":
    unittest.main()
