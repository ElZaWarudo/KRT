#!/usr/bin/env python3
"""Helpers for loading checkout-local Jira env files safely."""

from __future__ import annotations

from pathlib import Path


REQUIRED_VARS = ("JIRA_HOST", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY")
OPTIONAL_VARS = ("JIRA_EMAIL", "JIRA_BOARD_ID")
SUPPORTED_VARS = REQUIRED_VARS + OPTIONAL_VARS

ENV_DIR = Path(".krt/env")
IGNORE_PATH = ENV_DIR / ".gitignore"
SECRET_PATH = ENV_DIR / "jira-scribe.env"
EXAMPLE_PATH = ENV_DIR / "jira-scribe.env.example"


def bool_map(env: dict[str, str], names: tuple[str, ...]) -> dict[str, bool]:
    return {name: bool(env.get(name)) for name in names}


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            raise ValueError(f"invalid-line:{lineno}")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key not in SUPPORTED_VARS:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key] = value
    return values


def load_env_from_secret(root: Path, *, base_env: dict[str, str] | None = None) -> tuple[dict[str, str], list[str]]:
    env = dict(base_env or {})
    secret = root / SECRET_PATH
    parsed = parse_env_file(secret)
    loaded: list[str] = []
    for name in SUPPORTED_VARS:
        value = parsed.get(name, "")
        if not value:
            continue
        env[name] = value
        loaded.append(name)
    return env, loaded
