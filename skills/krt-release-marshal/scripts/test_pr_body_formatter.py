#!/usr/bin/env python3
"""Tests for PR body formatting and validation."""

from __future__ import annotations

import subprocess
import sys
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run(script: str, input_text: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / script), *args],
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


class PrBodyFormatterTest(unittest.TestCase):
    def test_formats_noisy_summary_body(self) -> None:
        noisy = textwrap.dedent(
            """
            Summary

                add a RAG Drive reconciliation service for full folder comparison
                classify discovered files as new, unchanged, changed, or stale
                extend the source-document store contract with sync-status lookup
                cover idempotent reconciliation and stale marking with unit tests

            Verification

                npm run unit-tests -- --grep "RAG Drive reconciliation service"
                npm run unit-tests -- --grep "RAG ingestion service"
                npm run build
                npm run check-lint
                npm run unit-tests

            Stacked on PR #30 / feat/rag-drive-folder-sync.
            """
        )

        completed = run("format_pr_body.py", noisy)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            completed.stdout,
            textwrap.dedent(
                """\
                - add a RAG Drive reconciliation service for full folder comparison
                - classify discovered files as new, unchanged, changed, or stale
                - extend the source-document store contract with sync-status lookup
                - cover idempotent reconciliation and stale marking with unit tests
                """
            ),
        )

    def test_preserves_jira_url_as_last_line(self) -> None:
        clean = textwrap.dedent(
            """
            - add a local Text Embeddings Inference provider for RAG embeddings
            - wire Docker Compose to run Qwen/Qwen3-Embedding-0.6B with bounded CPU warmup

            https://jira.example.com/browse/KRT-42
            """
        )

        completed = run("format_pr_body.py", clean)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(completed.stdout.endswith("\n\nhttps://jira.example.com/browse/KRT-42\n"))

    def test_formatted_body_passes_validator(self) -> None:
        formatted = run("format_pr_body.py", "Summary\n\n    add a deterministic PR body formatter\n")
        self.assertEqual(formatted.returncode, 0, formatted.stderr)

        validated = run("check_pr_body.py", formatted.stdout)

        self.assertEqual(validated.returncode, 0, validated.stderr)

    def test_rejects_verification_only_body(self) -> None:
        completed = run("format_pr_body.py", "Verification\n\nnpm run unit-tests\n")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("no change lines found", completed.stderr)


if __name__ == "__main__":
    unittest.main()
