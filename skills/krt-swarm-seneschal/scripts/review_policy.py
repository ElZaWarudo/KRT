#!/usr/bin/env python3
"""Shared assurance-tier policy for Seneschal review planning."""

from __future__ import annotations

from typing import Any


ASSURANCE_TIERS = ("low", "medium", "high", "critical")
COORDINATED_REVIEW_TIERS = {"high", "critical"}
REVIEW_DEMAND = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}


def normalize_assurance_tier(value: Any, field: str = "assurance_tier") -> str:
    if value not in ASSURANCE_TIERS:
        choices = ", ".join(ASSURANCE_TIERS)
        raise ValueError(f"{field} must be one of: {choices}")
    return value


def review_demand(value: Any) -> int:
    return REVIEW_DEMAND[normalize_assurance_tier(value)]

