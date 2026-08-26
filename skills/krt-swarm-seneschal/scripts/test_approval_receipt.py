#!/usr/bin/env python3
"""Tests for content-bound documentation approval receipts."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from materialize_approval_receipt import materialize_receipt, validate_receipt

APPROVAL_EVENT_DIGEST = "sha256:" + "a" * 64

class ApprovalReceiptTest(unittest.TestCase):
    def test_receipt_is_bound_to_every_approved_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "plan.md").write_text("approved", encoding="utf-8")
            receipt = materialize_receipt(
                repo_root=root,
                source_artifacts=["plan.md"],
                approved_by="user",
                approved_at="2026-08-25T08:00:00Z",
                approval_event_digest=APPROVAL_EVENT_DIGEST,
            )
            self.assertIs(validate_receipt(root, receipt), receipt)
            (root / "plan.md").write_text("changed later", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "artifact digest mismatch"):
                validate_receipt(root, receipt)

    def test_missing_and_escaping_artifacts_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for artifact in ["missing.md", "../outside.md"]:
                with self.subTest(artifact=artifact):
                    with self.assertRaises(ValueError):
                        materialize_receipt(
                            repo_root=root,
                            source_artifacts=[artifact],
                            approved_by="user",
                            approved_at="2026-08-25T08:00:00Z",
                            approval_event_digest=APPROVAL_EVENT_DIGEST,
                        )

    def test_receipt_requires_a_real_root_observed_event_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "plan.md").write_text("approved", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "trusted lowercase SHA-256"):
                materialize_receipt(
                    repo_root=root, source_artifacts=["plan.md"], approved_by="user",
                    approved_at="2026-08-25T08:00:00Z", approval_event_digest="sha256:guess",
                )


if __name__ == "__main__":
    unittest.main()
