#!/usr/bin/env python3
"""Tests for the deterministic Fixer terminal."""

from __future__ import annotations

import unittest

from validate_fixer_terminal import validate_fixer_terminal


class FixerTerminalTest(unittest.TestCase):
    def assignment(self) -> dict[str, object]:
        return {
            "contract_hash": "sha256:contract",
            "registry_digest": "sha256:registry",
            "finding_ids": ["F-ONE", "F-TWO"],
            "owned_paths": ["src/service.py", "tests/test_service.py"],
            "verification_commands": ["rtk pytest tests/test_service.py"],
        }

    def terminal(self) -> dict[str, object]:
        return {
            "contract_hash": "sha256:contract",
            "registry_digest": "sha256:registry",
            "fixer_id": "fixer-one",
            "finding_changes": [
                {
                    "finding_id": "F-ONE",
                    "changed_paths": ["src/service.py"],
                    "verification_commands": ["rtk pytest tests/test_service.py"],
                },
                {
                    "finding_id": "F-TWO",
                    "changed_paths": ["tests/test_service.py"],
                    "verification_commands": ["rtk pytest tests/test_service.py"],
                },
            ],
            "blockers": [],
            "stop_reason": "mapping-complete",
        }

    def test_accepts_complete_closed_mapping(self) -> None:
        result = validate_fixer_terminal(self.assignment(), self.terminal())

        self.assertTrue(result["valid"])
        self.assertEqual(result["finding_count"], 2)

    def test_rejects_narrative_or_missing_mapping(self) -> None:
        narrative = {"status": "done", "summary": "Fixed both findings."}
        incomplete = self.terminal()
        incomplete["finding_changes"] = incomplete["finding_changes"][:1]

        for terminal in (narrative, incomplete):
            with self.subTest(terminal=terminal):
                with self.assertRaises(ValueError):
                    validate_fixer_terminal(self.assignment(), terminal)

    def test_rejects_unowned_paths_and_unassigned_commands(self) -> None:
        for field, value in (
            ("changed_paths", ["src/other.py"]),
            ("verification_commands", ["rtk pytest tests/"]),
        ):
            terminal = self.terminal()
            terminal["finding_changes"][0][field] = value
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    validate_fixer_terminal(self.assignment(), terminal)

    def test_blocked_terminal_may_return_a_partial_mapping(self) -> None:
        terminal = self.terminal()
        terminal["finding_changes"] = terminal["finding_changes"][:1]
        terminal["blockers"] = ["The remaining fix needs an external decision."]
        terminal["stop_reason"] = "blocked"

        result = validate_fixer_terminal(self.assignment(), terminal)

        self.assertEqual(result["stop_reason"], "blocked")


if __name__ == "__main__":
    unittest.main()
