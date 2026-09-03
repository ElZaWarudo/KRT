#!/usr/bin/env python3
"""Tests for the root-owned review finding registry."""

from __future__ import annotations

import unittest
from pathlib import Path
import tempfile

from deterministic_artifacts import write_exclusive_atomic
from finding_registry import (
    _registry_lock,
    ingest_findings,
    new_registry,
    record_finding_feedback,
    resolve_finding,
    validate_finding_verdict,
    validate_registry,
)


def finding() -> dict[str, object]:
    return {
        "severity": "p1",
        "principle": "correctness",
        "rule_id": "malformed-import",
        "observation": "Malformed imports bypass validation.",
        "impact": "Invalid data reaches persistence.",
        "recommendation": "Validate before persistence.",
        "evidence": ["src/imports.py:42"],
    }


class FindingRegistryTest(unittest.TestCase):
    def registry(self) -> dict[str, object]:
        return new_registry(
            registry_id="review-run-1",
            contract_hash="sha256:contract",
            diff_digest="sha256:diff",
        )

    def submission(self, reporter: str = "reviewer-one") -> dict[str, object]:
        return {
            "contract_hash": "sha256:contract",
            "diff_digest": "sha256:diff",
            "review_plan_hash": "sha256:plan",
            "surface_id": "backend",
            "reporter_id": reporter,
            "findings": [finding()],
        }

    def ingest(self, registry: dict[str, object], reporter: str = "reviewer-one") -> dict[str, object]:
        return ingest_findings(
            registry,
            self.submission(reporter),
            expected_digest=registry["registry_digest"],
        )

    def test_ingest_assigns_stable_id_and_exact_duplicate_is_idempotent(self) -> None:
        first = self.ingest(self.registry())
        identifier = first["findings"][0]["id"]
        second = self.ingest(first, reporter="reviewer-two")

        self.assertRegex(identifier, r"^F-[0-9A-F]{8}$")
        self.assertEqual(len(second["findings"]), 1)
        self.assertEqual(second["findings"][0]["id"], identifier)
        self.assertEqual(second["findings"][0]["reporters"], ["reviewer-one", "reviewer-two"])
        validate_registry(second)

    def test_same_reporter_retry_does_not_advance_registry(self) -> None:
        first = self.ingest(self.registry())
        second = self.ingest(first)

        self.assertEqual(second["revision"], first["revision"])
        self.assertEqual(second["registry_digest"], first["registry_digest"])

    def test_exact_dedup_spans_surfaces_but_semantic_disagreement_does_not(self) -> None:
        first = self.ingest(self.registry())
        duplicate = self.submission("reviewer-two")
        duplicate["surface_id"] = "security"
        merged = ingest_findings(
            first, duplicate, expected_digest=first["registry_digest"]
        )
        self.assertEqual(len(merged["findings"]), 1)
        self.assertEqual(merged["findings"][0]["surface_ids"], ["backend", "security"])

        disagreement = self.submission("reviewer-three")
        disagreement["findings"][0]["severity"] = "p0"
        separate = ingest_findings(
            merged, disagreement, expected_digest=merged["registry_digest"]
        )
        self.assertEqual(len(separate["findings"]), 2)
        self.assertEqual(
            {item["severity"] for item in separate["findings"]}, {"p0", "p1"}
        )

    def test_mutation_requires_expected_registry_digest(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected digest"):
            ingest_findings(
                self.registry(), self.submission(), expected_digest="sha256:stale"
            )

    def test_feedback_is_preserved_without_replacing_the_finding(self) -> None:
        registry = self.ingest(self.registry())
        original_digest = registry["registry_digest"]
        identifier = registry["findings"][0]["id"]
        challenged = record_finding_feedback(
            registry,
            {
                "finding_id": identifier,
                "actor_id": "reviewer-two",
                "action": "challenge",
                "rationale": "The guard may run earlier.",
                "evidence": ["src/guard.py:10"],
            },
            expected_digest=registry["registry_digest"],
        )

        self.assertEqual(challenged["findings"][0]["status"], "proposed")
        self.assertEqual(len(challenged["findings"][0]["feedback"]), 1)
        self.assertEqual(registry["registry_digest"], original_digest)
        self.assertEqual(registry["findings"][0]["feedback"], [])
        validate_registry(registry)

    def test_corroborating_feedback_uses_the_same_digest_guard(self) -> None:
        registry = self.ingest(self.registry())
        identifier = registry["findings"][0]["id"]
        feedback = {
            "finding_id": identifier,
            "actor_id": "reviewer-two",
            "action": "corroborate",
            "rationale": "The focused test reproduces the defect.",
            "evidence": ["tests/imports.py:8"],
        }
        result = record_finding_feedback(
            registry,
            feedback,
            expected_digest=registry["registry_digest"],
        )
        feedback["evidence"].append("tests/later.py:1")

        self.assertEqual(result["findings"][0]["feedback"][0]["action"], "corroborate")
        self.assertEqual(
            result["findings"][0]["feedback"][0]["evidence"],
            ["tests/imports.py:8"],
        )

    def test_ingest_detaches_submission_evidence(self) -> None:
        registry = self.registry()
        submission = self.submission()
        result = ingest_findings(
            registry, submission, expected_digest=registry["registry_digest"]
        )
        submission["findings"][0]["evidence"].append("src/later.py:1")

        self.assertEqual(result["findings"][0]["evidence"], ["src/imports.py:42"])
        validate_registry(result)

    def test_reporter_cannot_validate_own_finding(self) -> None:
        registry = self.ingest(self.registry())
        identifier = registry["findings"][0]["id"]
        verdict = {
            "finding_id": identifier,
            "validator_id": "reviewer-one",
            "verdict": "confirmed",
            "evidence": ["tests/imports.py:5"],
            "revised_severity": None,
            "revised_observation": None,
            "revised_impact": None,
            "revised_recommendation": None,
        }

        with self.assertRaisesRegex(ValueError, "reporter"):
            validate_finding_verdict(
                registry, verdict, expected_digest=registry["registry_digest"]
            )

    def test_revised_validation_and_resolution_preserve_lifecycle(self) -> None:
        registry = self.ingest(self.registry())
        identifier = registry["findings"][0]["id"]
        validated = validate_finding_verdict(
            registry,
            {
                "finding_id": identifier,
                "validator_id": "validator-one",
                "verdict": "revised",
                "evidence": ["tests/imports.py:5"],
                "revised_severity": "p2",
                "revised_observation": "Only one import path bypasses validation.",
                "revised_impact": "One malformed input can reach persistence.",
                "revised_recommendation": "Guard that import path.",
            },
            expected_digest=registry["registry_digest"],
        )
        resolved = resolve_finding(
            validated,
            {
                "finding_id": identifier,
                "resolver_id": "fixer-one",
                "resolution": "fixed",
                "evidence": ["tests/imports.py::test_malformed"],
                "resolved_diff_digest": "sha256:fixed-diff",
            },
            expected_digest=validated["registry_digest"],
        )

        self.assertEqual(resolved["findings"][0]["status"], "fixed")
        self.assertEqual(resolved["findings"][0]["severity"], "p1")
        self.assertEqual(
            resolved["findings"][0]["validation"]["revised_finding"]["severity"],
            "p2",
        )

    def test_revision_preserves_original_fingerprint_identity(self) -> None:
        registry = self.ingest(self.registry())
        identifier = registry["findings"][0]["id"]
        revised = validate_finding_verdict(
            registry,
            {
                "finding_id": identifier,
                "validator_id": "validator-one",
                "verdict": "revised",
                "evidence": ["tests/imports.py:5"],
                "revised_severity": "p2",
                "revised_observation": "Only one import path bypasses validation.",
                "revised_impact": "One malformed input can reach persistence.",
                "revised_recommendation": "Guard that import path.",
            },
            expected_digest=registry["registry_digest"],
        )
        retried = self.ingest(revised)
        self.assertEqual(retried["registry_digest"], revised["registry_digest"])

        submission = self.submission("reviewer-two")
        submission["findings"][0].update(
            severity="p2",
            observation="Only one import path bypasses validation.",
            impact="One malformed input can reach persistence.",
            recommendation="Guard that import path.",
        )
        separate = ingest_findings(
            retried, submission, expected_digest=retried["registry_digest"]
        )
        self.assertEqual(len(separate["findings"]), 2)

    def test_resolution_rejects_malformed_digest_without_mutating_input(self) -> None:
        registry = self.ingest(self.registry())
        identifier = registry["findings"][0]["id"]
        validated = validate_finding_verdict(
            registry,
            {
                "finding_id": identifier,
                "validator_id": "validator-one",
                "verdict": "confirmed",
                "evidence": ["tests/imports.py:5"],
                "revised_severity": None,
                "revised_observation": None,
                "revised_impact": None,
                "revised_recommendation": None,
            },
            expected_digest=registry["registry_digest"],
        )
        original_digest = validated["registry_digest"]
        with self.assertRaisesRegex(ValueError, "must use sha256"):
            resolve_finding(
                validated,
                {
                    "finding_id": identifier,
                    "resolver_id": "fixer-one",
                    "resolution": "fixed",
                    "evidence": ["tests/imports.py::test_malformed"],
                    "resolved_diff_digest": "not-a-digest",
                },
                expected_digest=original_digest,
            )
        self.assertEqual(validated["registry_digest"], original_digest)
        self.assertIsNone(validated["findings"][0]["resolution"])

    def test_exclusive_atomic_create_never_replaces_existing_registry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            write_exclusive_atomic(path, {"value": "first"})
            with self.assertRaises(FileExistsError):
                write_exclusive_atomic(path, {"value": "second"})
            self.assertIn("first", path.read_text(encoding="utf-8"))

    def test_registry_lock_is_available_on_the_current_platform(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"

            with _registry_lock(path):
                self.assertTrue(path.with_name(".registry.json.lock").is_file())


if __name__ == "__main__":
    unittest.main()
