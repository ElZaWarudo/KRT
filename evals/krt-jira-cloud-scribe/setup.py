#!/usr/bin/env python3
"""Jira Cloud fixture: reuses the Jira-scribe builder with a Basic-auth v3 fake Jira."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "jira_fixture", Path(__file__).resolve().parents[1] / "krt-jira-scribe" / "setup.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)

if __name__ == "__main__":
    fixture.build(sys.argv[1], Path(sys.argv[2]), cloud=True)
