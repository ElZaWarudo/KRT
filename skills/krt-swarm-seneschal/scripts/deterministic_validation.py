#!/usr/bin/env python3
"""Shared strict validation primitives for deterministic Seneschal artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def string_list(
    value: Any,
    field: str,
    *,
    allow_empty: bool = True,
    unique: bool = False,
) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{field} must be a list of non-empty strings")
    if not allow_empty and not value:
        raise ValueError(f"{field} must not be empty")
    if unique and len(value) != len(set(value)):
        raise ValueError(f"{field} must not contain duplicates")
    return list(value)


def exact_object(value: Any, fields: set[str], name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{name} has missing or unknown fields")
    return value


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value
