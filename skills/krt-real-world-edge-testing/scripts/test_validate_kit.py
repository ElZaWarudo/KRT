#!/usr/bin/env python3
"""Focused tests for the real-world edge-testing kit validator."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
STARTER = SKILL_ROOT / "assets" / "starter-kit"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import validate_kit as validator  # noqa: E402


validate = validator.validate


class ValidateKitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.kit = Path(self.temporary.name) / "edge-tests"
        shutil.copytree(STARTER, self.kit)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def read(self, name: str) -> dict:
        return json.loads((self.kit / name).read_text(encoding="utf-8"))

    def write(self, name: str, value: dict) -> None:
        (self.kit / name).write_text(
            json.dumps(value, indent=2) + "\n", encoding="utf-8"
        )

    def error_text(self) -> str:
        return "\n".join(validate(self.kit)["errors"])

    def test_starter_kit_is_valid(self) -> None:
        result = validate(self.kit)

        self.assertEqual(result["status"], "valid", result["errors"])
        self.assertEqual(result["caseCount"], 1)
        self.assertEqual(result["fixtureCount"], 1)

    def test_numeric_risk_requires_rationale_and_consistent_score(self) -> None:
        campaign = self.read("campaign.json")
        campaign["cases"][0]["risk"]["score"] = 125
        campaign["cases"][0]["risk"]["rationale"] = ""
        self.write("campaign.json", campaign)

        errors = self.error_text()

        self.assertIn("risk.score must equal 18", errors)
        self.assertIn("risk.rationale must be a non-empty string", errors)

    def test_qualitative_priority_does_not_require_numeric_risk(self) -> None:
        campaign = self.read("campaign.json")
        del campaign["cases"][0]["risk"]
        self.write("campaign.json", campaign)

        self.assertEqual(validate(self.kit)["status"], "valid")

    def test_generated_path_cannot_escape_kit(self) -> None:
        manifest = self.read("fixtures-manifest.json")
        manifest["generatedDirectory"] = "../shared"
        self.write("fixtures-manifest.json", manifest)

        self.assertIn(
            "generatedDirectory must be a normalized relative path",
            self.error_text(),
        )

    def test_relative_path_alias_is_rejected(self) -> None:
        evidence = self.read("evidence.json")
        evidence["records"][0]["artifacts"] = ["evidence//response.log"]
        self.write("evidence.json", evidence)

        self.assertIn("must be a normalized relative path", self.error_text())

    def test_generated_directory_symlink_is_rejected(self) -> None:
        external = Path(self.temporary.name) / "external"
        shutil.copytree(self.kit / "generated", external)
        shutil.rmtree(self.kit / "generated")
        (self.kit / "generated").symlink_to(external, target_is_directory=True)

        self.assertIn("generated directory must not be a symlink", self.error_text())

    def test_fixture_symlink_is_rejected(self) -> None:
        external = Path(self.temporary.name) / "external.txt"
        external.write_text("VEGA-27-CANARY\n", encoding="utf-8")
        fixture = self.kit / "generated" / "synthetic-report.txt"
        fixture.unlink()
        fixture.symlink_to(external)

        self.assertIn("generated entry must not be a symlink", self.error_text())

    def test_unsafe_generated_root_is_not_enumerated(self) -> None:
        external = Path(self.temporary.name) / "external"
        external.mkdir()
        shutil.rmtree(self.kit / "generated")
        (self.kit / "generated").symlink_to(external, target_is_directory=True)

        with mock.patch.object(Path, "rglob", side_effect=AssertionError("must not walk")):
            errors = self.error_text()

        self.assertIn("generated directory must not be a symlink", errors)

    def test_campaign_cannot_reference_unknown_fixture(self) -> None:
        campaign = self.read("campaign.json")
        campaign["cases"][0]["fixtures"] = ["MISSING"]
        self.write("campaign.json", campaign)

        self.assertIn("campaign references unknown fixtures", self.error_text())

    def test_stateful_case_requires_recovery_procedure(self) -> None:
        campaign = self.read("campaign.json")
        case = campaign["cases"][0]
        case["executionRisk"] = "reversible_mutation"
        case["recovery"] = {"required": True}
        self.write("campaign.json", campaign)

        errors = self.error_text()

        self.assertIn("recovery.procedure must be a non-empty string", errors)
        self.assertIn("recovery.verification must be a non-empty string", errors)

    def test_stateful_case_cannot_disable_recovery(self) -> None:
        campaign = self.read("campaign.json")
        case = campaign["cases"][0]
        case["executionRisk"] = "external_side_effect"
        case["recovery"] = {"required": False}
        self.write("campaign.json", campaign)

        self.assertIn(
            "recovery.required must be true for stateful cases", self.error_text()
        )

    def test_stateful_evidence_must_record_recovery_outcome(self) -> None:
        campaign = self.read("campaign.json")
        case = campaign["cases"][0]
        case["executionRisk"] = "reversible_mutation"
        case["recovery"] = {
            "required": True,
            "procedure": "restore the synthetic resource",
            "verification": "baseline checksum restored",
        }
        self.write("campaign.json", campaign)
        evidence = self.read("evidence.json")
        evidence["records"][0]["result"] = "pass"
        evidence["records"][0]["recoveryStatus"] = "not_required"
        self.write("evidence.json", evidence)

        self.assertIn(
            "recoveryStatus must record recovery outcome", self.error_text()
        )

    def test_evidence_must_cover_every_campaign_case(self) -> None:
        campaign = self.read("campaign.json")
        second = dict(campaign["cases"][0])
        second["id"] = "EC-EXAMPLE-002"
        second["risk"] = dict(second["risk"])
        campaign["cases"].append(second)
        self.write("campaign.json", campaign)

        self.assertIn("evidence is missing campaign cases", self.error_text())

    def test_passed_preflight_cannot_hide_failed_check(self) -> None:
        preflight = self.read("preflight.json")
        preflight["status"] = "passed"
        preflight["blockers"] = []
        preflight["checks"][0]["status"] = "failed"
        self.write("preflight.json", preflight)

        self.assertIn("passed preflight cannot contain failed checks", self.error_text())

    def test_blocker_requires_condition_and_reason(self) -> None:
        preflight = self.read("preflight.json")
        preflight["blockers"] = [{}]
        self.write("preflight.json", preflight)

        errors = self.error_text()

        self.assertIn("preflight.blockers[0].condition must be", errors)
        self.assertIn("preflight.blockers[0].reason must be", errors)

    def test_starter_preflight_is_blocked_by_default(self) -> None:
        preflight = self.read("preflight.json")

        self.assertEqual(preflight["status"], "blocked")
        self.assertTrue(preflight["blockers"])
        self.assertFalse(validate(self.kit)["executionAuthorized"])

    def test_executed_evidence_is_bound_to_campaign_oracle(self) -> None:
        evidence = self.read("evidence.json")
        record = evidence["records"][0]
        record["result"] = "pass"
        record["startedAt"] = "2026-08-26T10:30:00Z"
        record["oracleResult"] = {"passed": True, "details": ["canary matched"]}
        record["oracleDigest"] = "0" * 64
        self.write("evidence.json", evidence)
        preflight = self.read("preflight.json")
        preflight["status"] = "passed"
        preflight["checks"][0]["status"] = "passed"
        preflight["blockers"] = []
        self.write("preflight.json", preflight)

        self.assertIn("oracleDigest must match", self.error_text())

    def test_blocked_preflight_rejects_executed_evidence(self) -> None:
        campaign = self.read("campaign.json")
        digest = validator.oracle_digest(campaign["cases"][0]["oracle"])
        evidence = self.read("evidence.json")
        evidence["records"][0].update(
            {
                "result": "pass",
                "startedAt": "2026-08-26T10:30:00Z",
                "oracleDigest": digest,
                "oracleResult": {"passed": True, "details": ["claimed pass"]},
            }
        )
        self.write("evidence.json", evidence)

        self.assertIn("cannot be executed while preflight is not passed", self.error_text())

    def test_executed_evidence_requires_timezone_aware_start(self) -> None:
        evidence = self.read("evidence.json")
        record = evidence["records"][0]
        record["result"] = "fail"
        record["startedAt"] = "2026-08-26T10:30:00"
        record["oracleResult"] = {"passed": False, "details": ["canary absent"]}
        record["oracleDigest"] = "0" * 64
        self.write("evidence.json", evidence)

        self.assertIn("startedAt must be an RFC 3339 timestamp", self.error_text())

    def test_cli_prints_oracle_digests(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SKILL_ROOT / "scripts" / "validate_kit.py"),
                str(self.kit),
                "--oracle-digests",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        output = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, output["errors"])
        self.assertRegex(output["oracleDigests"]["EC-EXAMPLE-001"], r"^[0-9a-f]{64}$")

    def test_control_file_symlink_is_rejected(self) -> None:
        campaign = self.kit / "campaign.json"
        external = Path(self.temporary.name) / "campaign.json"
        shutil.copy2(campaign, external)
        campaign.unlink()
        campaign.symlink_to(external)

        self.assertIn("must be a regular non-symlink file", self.error_text())

    def test_artifact_symlink_and_secret_content_are_rejected(self) -> None:
        evidence_dir = self.kit / "evidence"
        evidence_dir.mkdir()
        external = Path(self.temporary.name) / "external.log"
        external.write_text("safe", encoding="utf-8")
        (evidence_dir / "linked.log").symlink_to(external)
        (evidence_dir / "secret.log").write_text(
            "Authorization: Bearer abcdefghijklmnopqrstuvwxyz", encoding="utf-8"
        )
        evidence = self.read("evidence.json")
        evidence["records"][0]["artifacts"] = [
            "evidence/linked.log",
            "evidence/secret.log",
        ]
        self.write("evidence.json", evidence)

        errors = self.error_text()

        self.assertIn("must reference a contained regular file", errors)
        self.assertIn("evidence contains secret-shaped content", errors)

    def test_duplicate_artifact_reference_is_rejected_without_second_read(self) -> None:
        evidence_dir = self.kit / "evidence"
        evidence_dir.mkdir()
        artifact = evidence_dir / "response.log"
        artifact.write_text("sanitized", encoding="utf-8")
        evidence = self.read("evidence.json")
        evidence["records"][0]["artifacts"] = [
            "evidence/response.log",
            "evidence/response.log",
        ]
        self.write("evidence.json", evidence)

        self.assertIn("duplicates an artifact reference", self.error_text())

    def test_artifact_reference_and_total_byte_limits_are_enforced(self) -> None:
        evidence_dir = self.kit / "evidence"
        evidence_dir.mkdir()
        (evidence_dir / "response.log").write_text("sanitized", encoding="utf-8")
        evidence = self.read("evidence.json")
        evidence["records"][0]["artifacts"] = ["evidence/response.log"]
        self.write("evidence.json", evidence)

        with mock.patch.object(validator, "MAX_ARTIFACT_REFERENCES", 0):
            count_errors = self.error_text()
        with mock.patch.object(validator, "MAX_TOTAL_ARTIFACT_BYTES", 1):
            byte_errors = self.error_text()

        self.assertIn("evidence exceeds 0 artifact references", count_errors)
        self.assertIn("evidence artifacts exceed 1 total bytes", byte_errors)

    def test_malformed_duplicate_reference_does_not_crash(self) -> None:
        manifest = self.read("fixtures-manifest.json")
        manifest["fixtures"][0]["duplicateOf"] = []
        self.write("fixtures-manifest.json", manifest)

        self.assertIn("duplicateOf must be a string", self.error_text())

    def test_malformed_collection_values_do_not_crash(self) -> None:
        campaign = self.read("campaign.json")
        campaign["cases"][0]["priority"] = []
        campaign["cases"][0]["executionRisk"] = {}
        self.write("campaign.json", campaign)
        preflight = self.read("preflight.json")
        preflight["status"] = []
        self.write("preflight.json", preflight)
        evidence = self.read("evidence.json")
        evidence["records"][0]["result"] = {}
        evidence["records"][0]["recoveryStatus"] = []
        self.write("evidence.json", evidence)

        errors = self.error_text()

        self.assertIn("priority must be one of", errors)
        self.assertIn("executionRisk must be one of", errors)
        self.assertIn("preflight.status must be", errors)
        self.assertIn("result must be one of", errors)
        self.assertIn("recoveryStatus must be one of", errors)

    def test_control_json_size_depth_and_node_limits_are_enforced(self) -> None:
        with mock.patch.object(validator, "MAX_JSON_BYTES", 1):
            size_errors = self.error_text()
        with mock.patch.object(validator, "MAX_JSON_DEPTH", 1):
            depth_errors = self.error_text()
        with mock.patch.object(validator, "MAX_JSON_NODES", 1):
            node_errors = self.error_text()

        self.assertIn("exceeds 1 bytes", size_errors)
        self.assertIn("JSON nesting exceeds 1", depth_errors)
        self.assertIn("JSON structure exceeds 1 nodes", node_errors)

    def test_nonstandard_json_numbers_are_rejected(self) -> None:
        campaign = self.read("campaign.json")
        campaign["cases"][0]["oracle"]["invalidNumber"] = float("nan")
        self.write("campaign.json", campaign)

        self.assertIn("invalid JSON constant NaN", self.error_text())

    def test_duplicate_json_keys_are_rejected(self) -> None:
        campaign_path = self.kit / "campaign.json"
        campaign_path.write_text(
            '{"schemaVersion":1,"schemaVersion":1,"campaignId":"x","cases":[]}',
            encoding="utf-8",
        )

        self.assertIn("duplicate JSON key 'schemaVersion'", self.error_text())

    def test_fixture_checksum_provenance_and_treatment_are_required(self) -> None:
        manifest = self.read("fixtures-manifest.json")
        fixture = manifest["fixtures"][0]
        del fixture["sha256"]
        del fixture["provenance"]
        del fixture["expectedTreatment"]
        self.write("fixtures-manifest.json", manifest)

        errors = self.error_text()

        self.assertIn("sha256 must be 64 lowercase hex", errors)
        self.assertIn("provenance must be an object", errors)
        self.assertIn("expectedTreatment must be one of", errors)

    def test_text_fixture_is_screened_for_secret_shapes(self) -> None:
        fixture_path = self.kit / "generated" / "synthetic-report.txt"
        fixture_path.write_text(
            "VEGA-27-CANARY\nBearer abcdefghijklmnopqrstuvwxyz", encoding="utf-8"
        )
        manifest = self.read("fixtures-manifest.json")
        manifest["fixtures"][0]["sha256"] = hashlib.sha256(
            fixture_path.read_bytes()
        ).hexdigest()
        self.write("fixtures-manifest.json", manifest)

        self.assertIn("fixture contains secret-shaped content", self.error_text())

    def test_generated_total_byte_limit_stops_fixture_reads(self) -> None:
        fixture = self.kit / "generated" / "synthetic-report.txt"
        fixture.write_text("VEGA-27-CANARY\nextra", encoding="utf-8")

        with mock.patch.object(validator, "MAX_GENERATED_BYTES", 4), mock.patch.object(
            Path, "read_bytes", side_effect=AssertionError("fixture must not be read")
        ):
            errors = self.error_text()

        self.assertIn("generated directory exceeds 4 total bytes", errors)

    def test_generated_file_count_limit_is_enforced(self) -> None:
        with mock.patch.object(validator, "MAX_GENERATED_FILES", 0):
            errors = self.error_text()

        self.assertIn("generated directory exceeds 0 files", errors)

    def test_generated_entry_count_limit_is_enforced_before_fixture_reads(self) -> None:
        (self.kit / "generated" / "empty-directory").mkdir()

        with mock.patch.object(validator, "MAX_GENERATED_ENTRIES", 1), mock.patch.object(
            Path, "read_bytes", side_effect=AssertionError("fixture must not be read")
        ):
            errors = self.error_text()

        self.assertIn("generated directory exceeds 1 entries", errors)

    def test_canary_count_and_length_are_bounded(self) -> None:
        manifest = self.read("fixtures-manifest.json")
        fixture = manifest["fixtures"][0]
        fixture["canaries"] = ["x", "y"]
        self.write("fixtures-manifest.json", manifest)

        with mock.patch.object(validator, "MAX_CANARIES_PER_FIXTURE", 1), mock.patch.object(
            validator, "MAX_CANARY_CHARS", 0
        ):
            errors = self.error_text()

        self.assertIn("canaries exceeds 1 entries", errors)
        self.assertIn("canaries[0] exceeds 0 characters", errors)

    def test_canary_encoding_is_required_and_malformed_canaries_do_not_crash(self) -> None:
        manifest = self.read("fixtures-manifest.json")
        fixture = manifest["fixtures"][0]
        del fixture["canaryEncoding"]
        fixture["canaries"] = 7
        self.write("fixtures-manifest.json", manifest)

        errors = self.error_text()

        self.assertIn("canaries must be a non-empty list", errors)
        self.assertIn("canaryEncoding must be 'utf-8'", errors)

    def test_sensitive_evidence_key_is_rejected(self) -> None:
        evidence = self.read("evidence.json")
        evidence["records"][0]["observed"]["api_key"] = "redacted"
        self.write("evidence.json", evidence)

        self.assertIn("evidence contains sensitive key", self.error_text())

    def test_secret_shaped_evidence_value_is_rejected(self) -> None:
        evidence = self.read("evidence.json")
        evidence["records"][0]["observed"]["response"] = (
            "sk-proj-abcdefghijklmnopqrstuv"
        )
        self.write("evidence.json", evidence)

        self.assertIn("evidence contains secret-shaped content", self.error_text())

    def test_schema_files_are_valid_json_schema_documents(self) -> None:
        schemas = sorted((self.kit / "schemas").glob("*.schema.json"))

        self.assertEqual(len(schemas), 4)
        for schema in schemas:
            value = json.loads(schema.read_text(encoding="utf-8"))
            self.assertEqual(
                value["$schema"], "https://json-schema.org/draft/2020-12/schema"
            )
            self.assertEqual(value["type"], "object")

    def test_starter_documents_satisfy_their_json_schemas(self) -> None:
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema is not installed; zero-dependency validator remains covered")

        for name in ("campaign", "fixtures-manifest", "preflight", "evidence"):
            schema = self.read(f"schemas/{name}.schema.json")
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.validate(self.read(f"{name}.json"), schema)

    def test_behavioral_evaluation_pack_contract_is_valid(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(
                    REPO_ROOT
                    / "skills"
                    / "krt-skill-arbiter"
                    / "scripts"
                    / "check_corpus.py"
                ),
                str(SKILL_ROOT / "references" / "evals" / "cases.json"),
                str(SKILL_ROOT / "references" / "evals" / "expectations.json"),
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["case_count"], 12)


if __name__ == "__main__":
    unittest.main()
