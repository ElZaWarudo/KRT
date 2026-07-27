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


def ready(
    endpoint: str,
    project_key: str = "KRT",
    base_path: str = "",
) -> dict:
    return {
        "ok": True,
        "identity": {
            "origin": endpoint,
            "base_path": base_path,
            "project_key": project_key,
        },
    }


class JiraProviderResolutionTest(unittest.TestCase):
    def test_explicit_provider_wins_when_it_matches_url(self) -> None:
        result = MODULE.resolve_provider(
            explicit="cloud",
            jira_url="https://acme.atlassian.net/browse/KRT-42",
            readiness={"cloud": {"ok": False}, "server-datacenter": {"ok": True}},
        )
        self.assertEqual(result["provider"], "cloud")
        self.assertEqual(result["source"], "explicit")
        self.assertFalse(result["ok"])
        self.assertFalse(result["ready"])
        self.assertIn(
            "jira-provider-not-ready:cloud",
            result["block_reasons"],
        )

    def test_atlassian_url_selects_cloud(self) -> None:
        result = MODULE.resolve_provider(
            explicit=None,
            jira_url="https://acme.atlassian.net/browse/KRT-42",
            readiness={
                "cloud": ready("https://acme.atlassian.net"),
                "server-datacenter": {"ok": False},
            },
        )
        self.assertEqual(result["provider"], "cloud")
        self.assertEqual(result["source"], "url")
        self.assertTrue(result["ok"])
        self.assertTrue(result["ready"])
        self.assertEqual(result["block_reasons"], [])

    def test_non_atlassian_url_selects_server_datacenter(self) -> None:
        result = MODULE.resolve_provider(
            explicit=None,
            jira_url="https://jira.internal.example/browse/KRT-42",
            readiness={
                "cloud": {"ok": False},
                "server-datacenter": ready("https://jira.internal.example"),
            },
        )
        self.assertEqual(result["provider"], "server-datacenter")
        self.assertEqual(result["source"], "url")
        self.assertTrue(result["ok"])
        self.assertTrue(result["ready"])
        self.assertEqual(result["block_reasons"], [])

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


    def test_url_host_must_match_ready_credentials(self) -> None:
        result = MODULE.resolve_provider(
            explicit=None,
            jira_url="https://acme.atlassian.net/browse/KRT-42",
            readiness={
                "cloud": ready("https://other.atlassian.net"),
                "server-datacenter": {"ok": False},
            },
        )

        self.assertFalse(result["ok"])
        self.assertIn(
            "jira-provider-conflict:url-vs-readiness-endpoint",
            result["block_reasons"],
        )

    def test_url_project_must_match_ready_credentials(self) -> None:
        result = MODULE.resolve_provider(
            explicit=None,
            jira_url="https://acme.atlassian.net/browse/OTHER-42",
            readiness={
                "cloud": ready("https://acme.atlassian.net"),
                "server-datacenter": {"ok": False},
            },
        )

        self.assertFalse(result["ok"])
        self.assertIn(
            "jira-provider-conflict:url-vs-readiness-project",
            result["block_reasons"],
        )

    def test_url_requires_verifiable_readiness_identity(self) -> None:
        result = MODULE.resolve_provider(
            explicit=None,
            jira_url="https://acme.atlassian.net/browse/KRT-42",
            readiness={
                "cloud": {"ok": True},
                "server-datacenter": {"ok": False},
            },
        )

        self.assertFalse(result["ok"])
        self.assertIn(
            "jira-provider-identity-unverified:cloud",
            result["block_reasons"],
        )

    def test_server_endpoint_includes_port_and_base_path(self) -> None:
        jira_url = "https://jira.internal.example:8443/jira/browse/KRT-42"
        cases = (
            ready(
                "https://jira.internal.example:9443",
                base_path="/jira",
            ),
            ready(
                "https://jira.internal.example:8443",
                base_path="/other",
            ),
        )
        for readiness in cases:
            with self.subTest(readiness=readiness):
                result = MODULE.resolve_provider(
                    explicit=None,
                    jira_url=jira_url,
                    readiness={
                        "cloud": {"ok": False},
                        "server-datacenter": readiness,
                    },
                )
                self.assertFalse(result["ok"])
                self.assertIn(
                    "jira-provider-conflict:url-vs-readiness-endpoint",
                    result["block_reasons"],
                )


if __name__ == "__main__":
    unittest.main()
