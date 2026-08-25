#!/usr/bin/env python3
"""Tests for deterministic verification fingerprints and evidence reuse."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from verification_evidence import (
    compute_fingerprint,
    decide_reuse,
    load_registry,
    record_evidence,
    validate_fingerprint,
)


class VerificationEvidenceTest(unittest.TestCase):
    def test_fingerprint_is_stable_and_content_sensitive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "a.txt").write_text("alpha", encoding="utf-8")
            (root / "b.txt").write_text("beta", encoding="utf-8")
            first = compute_fingerprint(
                repo_root=root,
                base_revision="abc123",
                changed_paths=["b.txt", "a.txt"],
                commands=["rtk pytest tests/", "rtk lint"],
            )
            second = compute_fingerprint(
                repo_root=root,
                base_revision="abc123",
                changed_paths=["a.txt", "b.txt"],
                commands=["rtk pytest tests/", "rtk lint"],
            )
            (root / "a.txt").write_text("changed", encoding="utf-8")
            changed = compute_fingerprint(
                repo_root=root,
                base_revision="abc123",
                changed_paths=["a.txt", "b.txt"],
                commands=["rtk pytest tests/", "rtk lint"],
            )

        self.assertEqual(first["fingerprint"], second["fingerprint"])
        self.assertNotEqual(first["fingerprint"], changed["fingerprint"])
        self.assertIs(validate_fingerprint(first), first)

    def test_exact_passing_fingerprint_is_reused_until_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry_path = root / "evidence.json"
            (root / "a.txt").write_text("alpha", encoding="utf-8")
            fingerprint = compute_fingerprint(
                repo_root=root,
                base_revision="abc123",
                changed_paths=["a.txt"],
                commands=["rtk pytest tests/"],
            )
            record_evidence(
                registry_path=registry_path,
                fingerprint=fingerprint,
                result="passed",
                evidence=["logs/aggregate.txt"],
                captured_at="2026-08-25T08:00:00Z",
            )
            registry = load_registry(registry_path)
            reusable = decide_reuse(
                registry=registry,
                fingerprint=fingerprint,
                now="2026-08-25T08:30:00Z",
                max_age_seconds=3_600,
            )
            stale = decide_reuse(
                registry=registry,
                fingerprint=fingerprint,
                now="2026-08-25T10:00:01Z",
                max_age_seconds=3_600,
            )

        self.assertEqual(reusable["action"], "reuse")
        self.assertEqual(stale, {"action": "run", "reason": "evidence-stale", "record": reusable["record"]})

    def test_failed_or_missing_evidence_requires_run(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry_path = root / "evidence.json"
            (root / "a.txt").write_text("alpha", encoding="utf-8")
            fingerprint = compute_fingerprint(
                repo_root=root,
                base_revision="abc123",
                changed_paths=["a.txt"],
                commands=["rtk pytest tests/"],
            )
            missing = decide_reuse(
                registry=load_registry(registry_path),
                fingerprint=fingerprint,
                now="2026-08-25T08:00:00Z",
                max_age_seconds=3_600,
            )
            record_evidence(
                registry_path=registry_path,
                fingerprint=fingerprint,
                result="failed",
                evidence=["logs/failure.txt"],
                captured_at="2026-08-25T08:00:00Z",
            )
            failed = decide_reuse(
                registry=load_registry(registry_path),
                fingerprint=fingerprint,
                now="2026-08-25T08:01:00Z",
                max_age_seconds=3_600,
            )

        self.assertEqual(missing["reason"], "evidence-missing")
        self.assertEqual(failed["reason"], "prior-evidence-failed")

    def test_malformed_registry_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            registry_path = Path(temp_dir) / "evidence.json"
            registry_path.write_text(
                '{"schema_version": 1, "records": [{"result": "passed"}]}',
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "evidence record"):
                load_registry(registry_path)


if __name__ == "__main__":
    unittest.main()
