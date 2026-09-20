#!/usr/bin/env python3
"""Integration regressions for evidence-bound reconciliation using a real Git repo."""

from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml

from deterministic_artifacts import canonical_sha256, file_sha256, write_atomic
from finding_registry import ingest_findings, new_registry
import test_swarm_state_transition as state_fixtures
from transition_swarm_state import state_digest, transition_state
from verification_evidence import compute_fingerprint, record_evidence


class ReconcileUnitTest(unittest.TestCase):
    @contextmanager
    def fixture(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            root = directory / "repo"
            root.mkdir()
            queue, blockers = state_fixtures.SwarmStateTransitionTest().fixtures(directory)
            state_fixtures.SwarmStateTransitionTest().approve(root, queue, blockers)
            (root / ".gitignore").write_text("receipt.json\n", encoding="utf-8")
            (root / "code.txt").write_text("before", encoding="utf-8")

            def git(*args):
                return subprocess.run(
                    ["git", "-C", str(root), *args], check=True, capture_output=True, text=True,
                ).stdout.strip()

            git("init", "-q")
            git("config", "user.name", "Test")
            git("config", "user.email", "test@example.invalid")
            git("add", ".")
            git("commit", "-qm", "baseline")
            base = git("rev-parse", "HEAD")
            (root / "code.txt").write_text("candidate", encoding="utf-8")
            git("add", ".")
            git("commit", "-qm", "candidate")
            revision = git("rev-parse", "HEAD")
            fingerprint = compute_fingerprint(
                repo_root=root, base_revision=base, changed_paths=["code.txt"], commands=["python -m unittest"],
            )
            candidate = canonical_sha256({"candidate_revision": revision, "fingerprint": fingerprint["fingerprint"]})
            contract = "sha256:" + "d" * 64

            def save(name, value):
                path = directory / name
                write_atomic(path, value)
                return {"path": str(path), "digest": file_sha256(path)}

            log = directory / "test.log"
            log.write_text("tests passed\nexit_code: 0\n", encoding="utf-8")
            record = record_evidence(
                registry_path=directory / "verification-registry.json", fingerprint=fingerprint,
                result="passed", evidence=[str(log)], captured_at="2026-09-05T08:00:00Z",
            )
            registry = new_registry(registry_id="unit-1", contract_hash=contract, diff_digest=candidate)
            registry_ref = save("findings.json", registry)
            certificates = [{
                "role": role, "actor_id": role + "-actor", "status": "passed",
                "contract_hash": contract, "diff_digest": candidate, "findings": [],
            } for role in ("reviewer", "security-sentinel")]
            bundle = {
                "schema_version": 1, "unit_id": "unit-1", "candidate_revision": revision,
                "fingerprint": save("fingerprint.json", fingerprint),
                "verification": save("verification.json", record),
                "verification_logs": [{"path": str(log), "digest": file_sha256(log)}],
                "certificates": [save(f"certificate-{index}.json", cert) for index, cert in enumerate(certificates)],
                "findings_registry": registry_ref,
            }
            state = yaml.safe_load(queue.read_text(encoding="utf-8"))
            state["units"]["dependency"] = {"status": "release-ready", "blocked_by": []}
            state["units"]["unit-1"].update({
                "status": "review-gated", "blocked_by": [], "depends_on": ["dependency"],
                "reconciliation_policy": {
                    "candidate_revision": revision, "candidate_digest": candidate,
                    "contract_hash": contract, "worker_id": "implementer",
                    "required_certifications": ["reviewer", "security-sentinel"],
                    "findings_registry": registry_ref,
                },
            })
            blockers.write_text(yaml.safe_dump({"schema_version": 1, "blockers": []}), encoding="utf-8")
            transition = {"schema_version": 1, "operation": "reconcile-unit", "unit_id": "unit-1", "from": "review-gated", "to": "release-ready"}

            def apply(*, queue_digest=None, blocker_digest=None):
                queue.write_text(yaml.safe_dump(state), encoding="utf-8")
                transition["evidence"] = save("bundle.json", bundle)
                before = queue.read_bytes(), blockers.read_bytes()
                try:
                    return transition_state(
                        queue_path=queue, blockers_path=blockers, repo_root=root, transition=transition,
                        expected_queue_digest=queue_digest or state_digest(queue),
                        expected_blockers_digest=blocker_digest or state_digest(blockers),
                    )
                except Exception:
                    self.assertEqual((queue.read_bytes(), blockers.read_bytes()), before)
                    raise

            yield locals()

    def test_success_persists_bound_evidence_and_leaves_blockers_unchanged(self):
        with self.fixture() as f:
            before = f["blockers"].read_bytes()
            f["apply"]()
            unit = yaml.safe_load(f["queue"].read_text())["units"]["unit-1"]
            self.assertEqual(unit["status"], "release-ready")
            self.assertEqual(unit["reconciliation"]["candidate_digest"], f["candidate"])
            self.assertEqual(unit["reconciliation"]["verification_record_digest"], f["record"]["record_digest"])
            self.assertEqual(len(unit["reconciliation"]["accepted_artifacts"]), 7)
            self.assertIn("documentation_approval", unit["reconciliation"])
            self.assertEqual(f["blockers"].read_bytes(), before)

    def test_rejections_leave_both_state_files_byte_identical(self):
        cases = ["content", "extra-path", "revision", "verification", "missing-review", "missing-security",
                 "certificate-diff", "certificate-actor", "findings", "registry-findings", "registry", "blocker", "dependency",
                 "queue-digest", "blocker-digest", "approval", "approval-coverage", "journal", "artifact-tamper", "release-target"]
        for case in cases:
            with self.subTest(case=case), self.fixture() as f:
                bundle, state = f["bundle"], f["state"]
                unit = state["units"]["unit-1"]
                kwargs = {}
                if case == "content":
                    (f["root"] / "code.txt").write_text("stale")
                elif case == "extra-path":
                    (f["root"] / "uncovered.txt").write_text("uncovered")
                elif case == "revision":
                    f["git"]("commit", "--allow-empty", "-qm", "new revision")
                elif case == "verification":
                    record = f["record"]
                    record["result"] = "failed"
                    record["record_digest"] = canonical_sha256({k: v for k, v in record.items() if k != "record_digest"})
                    bundle["verification"] = f["save"]("verification.json", record)
                elif case.startswith("missing-"):
                    bundle["certificates"].pop(0 if case == "missing-review" else 1)
                elif case in {"certificate-diff", "certificate-actor", "findings"}:
                    certificate = f["certificates"][0]
                    if case == "certificate-diff":
                        certificate["diff_digest"] = "sha256:" + "e" * 64
                    elif case == "certificate-actor":
                        certificate["actor_id"] = "implementer"
                    else:
                        certificate["findings"] = [{"severity": "p2"}]
                    bundle["certificates"][0] = f["save"]("certificate-0.json", certificate)
                elif case == "registry-findings":
                    registry = ingest_findings(f["registry"], {
                        "contract_hash": f["contract"], "diff_digest": f["candidate"],
                        "review_plan_hash": "sha256:" + "f" * 64,
                        "surface_id": "code", "reporter_id": "reviewer",
                        "findings": [{"severity": "p1", "principle": "correctness", "rule_id": "bug",
                                      "observation": "Bug", "impact": "Incorrect result",
                                      "recommendation": "Fix result", "evidence": ["code.txt"]}],
                    }, expected_digest=f["registry"]["registry_digest"])
                    reference = f["save"]("findings.json", registry)
                    bundle["findings_registry"] = reference
                    unit["reconciliation_policy"]["findings_registry"] = reference
                elif case == "registry":
                    # A different empty registry cannot replace the root-pinned one.
                    other = new_registry(registry_id="other", contract_hash=f["contract"], diff_digest=f["candidate"])
                    bundle["findings_registry"] = f["save"]("other-findings.json", other)
                elif case == "blocker":
                    unit["blocked_by"] = ["BLK-1"]
                    f["blockers"].write_text(yaml.safe_dump({"schema_version": 1, "blockers": [{"id": "BLK-1", "status": "open", "affected_units": ["unit-1"]}]}))
                elif case == "dependency":
                    state["units"]["dependency"]["status"] = "review-gated"
                elif case in {"queue-digest", "blocker-digest"}:
                    kwargs["queue_digest" if case == "queue-digest" else "blocker_digest"] = "sha256:stale"
                elif case == "approval":
                    (f["root"] / "plan.md").write_text("approval stale")
                elif case == "approval-coverage":
                    state["documentation_gate"]["approval_artifacts"].append("unapproved.md")
                elif case == "journal":
                    (f["directory"] / ".seneschal-state-transaction.json").write_text("{}")
                elif case == "artifact-tamper":
                    Path(bundle["verification"]["path"]).write_text("{}")
                elif case == "release-target":
                    f["transition"]["to"] = "handed-off"
                with self.assertRaises(ValueError):
                    f["apply"](**kwargs)

    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell example requires pwsh")
    def test_documented_powershell_example_executes_real_cli(self):
        with self.fixture() as f:
            scripts = Path(__file__).resolve().parent
            documentation = (scripts.parent / "references" / "queue-state-schema.md").read_text(encoding="utf-8")
            example = documentation.split("```powershell\n", 1)[1].split("```", 1)[0]
            f["queue"].write_text(yaml.safe_dump(f["state"]), encoding="utf-8")
            f["save"]("bundle.json", f["bundle"])
            paths = {
                "skillScripts": scripts, "repoRoot": f["root"], "queuePath": f["queue"],
                "blockersPath": f["blockers"], "bundlePath": f["directory"] / "bundle.json",
                "transitionPath": f["directory"] / "transition.json",
            }
            lines = []
            for line in example.splitlines():
                variable = line.split(" =", 1)[0].removeprefix("$")
                if variable in paths:
                    line = f"${variable} = '" + str(paths[variable]).replace("'", "''") + "'"
                if line.startswith("python "):
                    line = "& '" + sys.executable.replace("'", "''") + "' " + line[len("python "):]
                lines.append(line)
            result = subprocess.run(
                [shutil.which("pwsh"), "-NoProfile", "-Command", "\n".join(lines)],
                capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["queue_digest"], state_digest(f["queue"]))
            self.assertEqual(yaml.safe_load(f["queue"].read_text())["units"]["unit-1"]["status"], "release-ready")


if __name__ == "__main__":
    unittest.main()
