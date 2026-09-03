#!/usr/bin/env python3
"""Tests for conservative verification failure classification."""

from __future__ import annotations

import unittest

from classify_verification_result import classify_verification_result


class VerificationClassificationTest(unittest.TestCase):
    def document(self, **overrides: object) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_version": 1,
            "command": "rtk pytest tests/test_service.py",
            "current": {"exit_code": 1, "failure_fingerprint": "sha256:failure"},
            "baseline": {
                "attempted": True,
                "source_revision": "abc123",
                "exit_code": 0,
                "failure_fingerprint": None,
            },
            "environment": {"dependencies_available": True, "evidence": []},
            "owned_surface_changed": True,
        }
        value.update(overrides)
        return value

    def test_baseline_pass_makes_current_failure_a_regression(self) -> None:
        result = classify_verification_result(self.document())
        self.assertEqual(result["classification"], "regression")

    def test_missing_dependencies_are_environment_not_baseline(self) -> None:
        document = self.document(
            baseline={
                "attempted": False,
                "source_revision": None,
                "exit_code": None,
                "failure_fingerprint": None,
            },
            environment={
                "dependencies_available": False,
                "evidence": ["node_modules directory is absent"],
            },
        )
        result = classify_verification_result(document)
        self.assertEqual(result["classification"], "environment_failure")

    def test_baseline_requires_matching_failure_and_unchanged_owned_surface(self) -> None:
        baseline = {
            "attempted": True,
            "source_revision": "abc123",
            "exit_code": 1,
            "failure_fingerprint": "sha256:failure",
        }
        result = classify_verification_result(
            self.document(baseline=baseline, owned_surface_changed=False)
        )
        self.assertEqual(result["classification"], "baseline_failure")
        result = classify_verification_result(
            self.document(baseline=baseline, owned_surface_changed=True)
        )
        self.assertEqual(result["classification"], "unclassified_failure")

    def test_missing_dependency_claim_requires_evidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "environment evidence"):
            classify_verification_result(
                self.document(
                    environment={"dependencies_available": False, "evidence": []}
                )
            )

    def test_dependency_availability_rejects_integer_aliases(self) -> None:
        with self.assertRaisesRegex(ValueError, "true, false, or null"):
            classify_verification_result(
                self.document(
                    environment={"dependencies_available": 1, "evidence": []}
                )
            )


if __name__ == "__main__":
    unittest.main()
