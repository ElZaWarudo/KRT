#!/usr/bin/env python3
"""Tests for deterministic Jira provider resolution."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("resolve_jira_provider", ROOT / "resolve_jira_provider.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class JiraProviderResolutionTest(unittest.TestCase):
    def test_explicit_provider_wins_when_it_matches_url(self) -> None:
        result = MODULE.resolve_provider(
            explicit="cloud",
            jira_url="https://acme.atlassian.net/browse/KRT-42",
            readiness={"cloud": {"ok": False}, "server-datacenter": {"ok": True}},
        )
        self.assertEqual(result["provider"], "cloud")
        self.assertEqual(result["source"], "explicit")

    def test_atlassian_url_selects_cloud(self) -> None:
        result = MODULE.resolve_provider(
            explicit=None,
            jira_url="https://acme.atlassian.net/browse/KRT-42",
            readiness={"cloud": {"ok": True}, "server-datacenter": {"ok": False}},
        )
        self.assertEqual(result["provider"], "cloud")
        self.assertEqual(result["source"], "url")

    def test_non_atlassian_url_selects_server_datacenter(self) -> None:
        result = MODULE.resolve_provider(
            explicit=None,
            jira_url="https://jira.internal.example/browse/KRT-42",
            readiness={"cloud": {"ok": False}, "server-datacenter": {"ok": True}},
        )
        self.assertEqual(result["provider"], "server-datacenter")
        self.assertEqual(result["source"], "url")

    def test_unique_ready_provider_is_selected(self) -> None:
        result = MODULE.resolve_provider(
            explicit=None,
            jira_url=None,
            readiness={"cloud": {"ok": True}, "server-datacenter": {"ok": False}},
        )
        self.assertEqual(result["provider"], "cloud")
        self.assertEqual(result["source"], "readiness")

    def test_both_ready_is_ambiguous_instead_of_defaulting(self) -> None:
        result = MODULE.resolve_provider(
            explicit=None,
            jira_url=None,
            readiness={"cloud": {"ok": True}, "server-datacenter": {"ok": True}},
        )
        self.assertIsNone(result["provider"])
        self.assertIn("jira-provider-ambiguous", result["block_reasons"])

    def test_neither_ready_is_unresolved_instead_of_defaulting(self) -> None:
        result = MODULE.resolve_provider(
            explicit=None,
            jira_url=None,
            readiness={"cloud": {"ok": False}, "server-datacenter": {"ok": False}},
        )
        self.assertIsNone(result["provider"])
        self.assertIn("jira-provider-unresolved", result["block_reasons"])

    def test_conflicting_explicit_provider_and_url_blocks(self) -> None:
        result = MODULE.resolve_provider(
            explicit="server-datacenter",
            jira_url="https://acme.atlassian.net/browse/KRT-42",
            readiness={"cloud": {"ok": True}, "server-datacenter": {"ok": True}},
        )
        self.assertIsNone(result["provider"])
        self.assertIn("jira-provider-conflict:explicit-vs-url", result["block_reasons"])


if __name__ == "__main__":
    unittest.main()
