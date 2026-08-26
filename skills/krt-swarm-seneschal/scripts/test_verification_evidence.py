#!/usr/bin/env python3
"""Tests for deterministic verification fingerprints and evidence reuse."""

from __future__ import annotations

import tempfile
import subprocess
import json
import sys
import unittest
from pathlib import Path

from verification_evidence import (
    compute_fingerprint,
    decide_reuse,
    execute_and_record,
    load_registry,
    record_evidence,
    validate_fingerprint,
    write_atomic,
)


class VerificationEvidenceTest(unittest.TestCase):
    def init_git(self, root: Path) -> None:
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)

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
                repo_root=root,
                registry=registry,
                fingerprint=fingerprint,
                expected_fingerprint=fingerprint["fingerprint"],
                expected_record_digest=registry["records"][0]["record_digest"],
                now="2026-08-25T08:30:00Z",
                max_age_seconds=3_600,
                require_complete_diff=False,
            )
            stale = decide_reuse(
                repo_root=root,
                registry=registry,
                fingerprint=fingerprint,
                expected_fingerprint=fingerprint["fingerprint"],
                expected_record_digest=registry["records"][0]["record_digest"],
                now="2026-08-25T10:00:01Z",
                max_age_seconds=3_600,
                require_complete_diff=False,
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
                repo_root=root,
                registry=load_registry(registry_path),
                fingerprint=fingerprint,
                expected_fingerprint=fingerprint["fingerprint"],
                now="2026-08-25T08:00:00Z",
                max_age_seconds=3_600,
                require_complete_diff=False,
            )
            record_evidence(
                registry_path=registry_path,
                fingerprint=fingerprint,
                result="failed",
                evidence=["logs/failure.txt"],
                captured_at="2026-08-25T08:00:00Z",
            )
            failed = decide_reuse(
                repo_root=root,
                registry=(failed_registry := load_registry(registry_path)),
                fingerprint=fingerprint,
                expected_fingerprint=fingerprint["fingerprint"],
                expected_record_digest=failed_registry["records"][0]["record_digest"],
                now="2026-08-25T08:01:00Z",
                max_age_seconds=3_600,
                require_complete_diff=False,
            )

        self.assertEqual(missing["reason"], "evidence-missing")
        self.assertEqual(failed["reason"], "prior-evidence-failed")

    def test_execution_result_is_derived_from_observed_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry_path = root / "evidence.json"
            (root / "a.txt").write_text("alpha", encoding="utf-8")
            fingerprint = compute_fingerprint(
                repo_root=root,
                base_revision="abc123",
                changed_paths=["a.txt"],
                commands=["python3 -c 'raise SystemExit(7)'"],
            )

            record = execute_and_record(
                repo_root=root,
                registry_path=registry_path,
                fingerprint=fingerprint,
                expected_fingerprint=fingerprint["fingerprint"],
                evidence_dir=root / "logs",
                captured_at="2026-08-25T08:00:00Z",
                require_complete_diff=False,
            )

        self.assertEqual(record["result"], "failed")
        self.assertTrue(any("exit-7" in item for item in record["evidence"]))

    def test_execution_rejects_stale_fingerprint_content(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "a.txt").write_text("alpha", encoding="utf-8")
            fingerprint = compute_fingerprint(
                repo_root=root,
                base_revision="abc123",
                changed_paths=["a.txt"],
                commands=["python3 -c 'print(1)'"],
            )
            (root / "a.txt").write_text("tampered", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "no longer matches"):
                execute_and_record(
                    repo_root=root,
                    registry_path=root / "evidence.json",
                    fingerprint=fingerprint,
                    expected_fingerprint=fingerprint["fingerprint"],
                    evidence_dir=root / "logs",
                    captured_at="2026-08-25T08:00:00Z",
                    require_complete_diff=False,
                )

    def test_reuse_rejects_live_content_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry_path = root / "evidence.json"
            (root / "a.txt").write_text("alpha", encoding="utf-8")
            fingerprint = compute_fingerprint(
                repo_root=root, base_revision="abc123", changed_paths=["a.txt"],
                commands=["python3 -c 'print(1)'"],
            )
            record_evidence(
                registry_path=registry_path, fingerprint=fingerprint, result="passed",
                evidence=["log"], captured_at="2026-08-25T08:00:00Z",
            )
            (root / "a.txt").write_text("changed", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "no longer matches"):
                decide_reuse(
                    repo_root=root, registry=load_registry(registry_path),
                    fingerprint=fingerprint, now="2026-08-25T08:01:00Z",
                    expected_fingerprint=fingerprint["fingerprint"],
                    max_age_seconds=3_600, require_complete_diff=False,
                )

    def test_execution_rejects_a_command_created_unlisted_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as log_dir:
            root = Path(temp_dir)
            self.init_git(root)
            (root / "a.txt").write_text("base", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "a.txt"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
            (root / "a.txt").write_text("changed", encoding="utf-8")
            fingerprint = compute_fingerprint(
                repo_root=root, base_revision="HEAD", changed_paths=["a.txt"],
                commands=["python3 -c 'from pathlib import Path; Path(\"new.txt\").write_text(\"x\")'"],
            )

            with self.assertRaisesRegex(ValueError, "complete root-observed diff"):
                execute_and_record(
                    repo_root=root, registry_path=Path(log_dir) / "evidence.json",
                    fingerprint=fingerprint, evidence_dir=Path(log_dir),
                    expected_fingerprint=fingerprint["fingerprint"],
                    captured_at="2026-08-25T08:00:00Z",
                )

    def test_fingerprint_rejects_symlinked_parent_escape(self) -> None:
        with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as outside_dir:
            root = Path(root_dir)
            outside = Path(outside_dir)
            (outside / "secret.txt").write_text("secret", encoding="utf-8")
            (root / "link").symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "escapes repo_root"):
                compute_fingerprint(
                    repo_root=root, base_revision="abc123",
                    changed_paths=["link/secret.txt"], commands=["python3 -c 'print(1)'"],
                )

    def test_run_and_decide_cli_wire_trusted_digests(self) -> None:
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as evidence_root:
            root = Path(repo_dir)
            evidence = Path(evidence_root)
            self.init_git(root)
            (root / "a.txt").write_text("base", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "a.txt"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)
            (root / "a.txt").write_text("changed", encoding="utf-8")
            fingerprint = compute_fingerprint(
                repo_root=root, base_revision="HEAD", changed_paths=["a.txt"],
                commands=["python3 -c 'print(1)'"],
            )
            fingerprint_path = evidence / "fingerprint.json"
            registry_path = evidence / "registry.json"
            write_atomic(fingerprint_path, fingerprint)
            script = Path(__file__).with_name("verification_evidence.py")
            run = subprocess.run([
                sys.executable, str(script), "run", "--repo-root", str(root),
                "--registry", str(registry_path), "--fingerprint", str(fingerprint_path),
                "--evidence-dir", str(evidence / "logs"), "--expected-fingerprint",
                fingerprint["fingerprint"], "--timeout-seconds", "30",
            ], check=True, text=True, stdout=subprocess.PIPE)
            record = json.loads(run.stdout)
            decide = subprocess.run([
                sys.executable, str(script), "decide", "--repo-root", str(root),
                "--registry", str(registry_path), "--fingerprint", str(fingerprint_path),
                "--expected-fingerprint", fingerprint["fingerprint"],
                "--expected-record-digest", record["record_digest"],
                "--max-age-seconds", "3600",
            ], check=True, text=True, stdout=subprocess.PIPE)

        self.assertEqual(json.loads(decide.stdout)["action"], "reuse")

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
