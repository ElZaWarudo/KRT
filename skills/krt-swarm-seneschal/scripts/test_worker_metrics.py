#!/usr/bin/env python3
"""Tests for worker-profile metric summaries."""

from __future__ import annotations

import unittest

from summarize_worker_metrics import summarize


class WorkerMetricsTest(unittest.TestCase):
    def test_records_are_grouped_by_profile_and_evidence_trust(self) -> None:
        records = []
        for acceptance, scope in ((100, 0), (300, 1)):
            records.append(
                {
                    "worker_profile": "luna",
                    "evidence_trust": "self-reported",
                    "status": "completed",
                    "acceptance_latency_ms": acceptance,
                    "discovery_implementation_ratio": 0.25,
                    "time_to_first_change_ms": 20,
                    "total_duration_ms": acceptance,
                    "fix_rounds": 1,
                    "out_of_manifest_commands": 0,
                    "repeated_verification_commands": 1,
                    "review_findings_p0": 0,
                    "review_findings_p1": 1,
                    "review_findings_p2": 0,
                    "scope_violations": scope,
                }
            )
        records.append(
            {
                **records[0],
                "worker_profile": "luna_xhigh",
                "evidence_trust": "runtime-audited",
            }
        )

        result = summarize({"schema_version": 1, "records": records})

        self.assertEqual(len(result["groups"]), 2)
        luna = next(
            group for group in result["groups"] if group["worker_profile"] == "luna"
        )
        self.assertEqual(luna["samples"], 2)
        self.assertEqual(luna["median_acceptance_latency_ms"], 200)
        self.assertEqual(luna["total_scope_violations"], 1)
        self.assertEqual(luna["total_review_findings_p1"], 2)

    def test_invalid_timing_document_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "schema_version"):
            summarize({"schema_version": 2, "records": {}})


if __name__ == "__main__":
    unittest.main()
