#!/usr/bin/env python3
"""Validate Spanish semantic Jira text for autonomous mutations."""

from __future__ import annotations

import argparse
import json
import re


FORBIDDEN_PATTERNS = {
    "roadmap-id": re.compile(r"\bRDM-\d+\b", re.I),
    "review-unit-id": re.compile(r"\bRU\d+\b", re.I),
    "date-sequence": re.compile(r"\b20\d{2}[-/]\d{2}[-/]\d{2}\b"),
    "commit-prefix": re.compile(r"^(feat|fix|docs|chore|refactor|test)(\(.+\))?:", re.I),
    "pr-chatter": re.compile(r"\b(PR|pull request|merge|rebase|reviewer|checks?)\b", re.I),
}


SPANISH_HINTS = {
    "el",
    "la",
    "los",
    "las",
    "para",
    "con",
    "sin",
    "que",
    "de",
    "del",
    "una",
    "un",
    "usuario",
    "flujo",
    "tarea",
    "validar",
    "crear",
}


def validate_text(text: str) -> list[str]:
    reasons: list[str] = []
    stripped = text.strip()
    if len(stripped) < 12:
        reasons.append("text-too-short")
    if stripped == stripped.upper() and len(stripped) > 20:
        reasons.append("text-all-caps")
    words = {word.lower() for word in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", stripped)}
    if len(words & SPANISH_HINTS) < 2:
        reasons.append("spanish-semantic-text-missing")
    for name, pattern in FORBIDDEN_PATTERNS.items():
        if pattern.search(stripped):
            reasons.append(f"forbidden-pattern:{name}")
    return reasons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", required=True)
    args = parser.parse_args()
    reasons = validate_text(args.text)
    result = {
        "allowed": not reasons,
        "mutation_class": "jira_text",
        "target": {},
        "payload_hash": None,
        "block_reasons": reasons,
        "warnings": [],
        "live_state_summary": {"length": len(args.text)},
        "audit_required": False,
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
