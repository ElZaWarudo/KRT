#!/usr/bin/env python3
"""Allocate a bounded Seneschal wave across functional worker roles."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import sys
from pathlib import Path
from typing import Any


ROLE_PRIORITY = {
    "integrator": 0,
    "security": 1,
    "reviewer": 2,
    "ci-platform": 3,
    "implementer": 4,
    "fixer": 5,
    "planner": 6,
    "documenter": 7,
}
DEFAULT_CAPS = {
    "implementer": 2,
    "reviewer": 2,
    "security": 1,
    "ci-platform": 1,
    "integrator": 1,
    "fixer": 1,
    "planner": 1,
    "documenter": 1,
}


def _non_negative_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def allocate_slots(plan: dict[str, Any]) -> dict[str, Any]:
    expected = {"schema_version", "total_slots", "reserve_slots", "role_caps", "requests"}
    if not isinstance(plan, dict) or set(plan) != expected:
        raise ValueError("slot plan has missing or unknown fields")
    if plan.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    total_slots = _non_negative_int(plan.get("total_slots"), "total_slots")
    reserve_slots = _non_negative_int(plan.get("reserve_slots"), "reserve_slots")
    if total_slots < 1 or reserve_slots >= total_slots:
        raise ValueError("reserve_slots must leave at least one usable slot")
    raw_caps = plan.get("role_caps")
    if not isinstance(raw_caps, dict) or any(role not in ROLE_PRIORITY for role in raw_caps):
        raise ValueError("role_caps contains an unsupported role")
    caps = dict(DEFAULT_CAPS)
    for role, cap in raw_caps.items():
        caps[role] = _non_negative_int(cap, f"role_caps.{role}")
    requests = plan.get("requests")
    if not isinstance(requests, list):
        raise ValueError("requests must be a list")
    normalized: list[dict[str, Any]] = []
    request_ids: list[str] = []
    for request in requests:
        if not isinstance(request, dict) or set(request) != {"id", "role", "priority"}:
            raise ValueError("each request requires exactly id, role, and priority")
        request_id = request.get("id")
        role = request.get("role")
        priority = _non_negative_int(request.get("priority"), "request.priority")
        if not isinstance(request_id, str) or not request_id:
            raise ValueError("request.id must be a non-empty string")
        if role not in ROLE_PRIORITY:
            raise ValueError("request.role is unsupported")
        request_ids.append(request_id)
        normalized.append({"id": request_id, "role": role, "priority": priority})
    if len(request_ids) != len(set(request_ids)):
        raise ValueError("request ids must be unique")

    usable_slots = total_slots - reserve_slots
    admitted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for request in sorted(
        normalized,
        key=lambda item: (item["priority"], ROLE_PRIORITY[item["role"]], item["id"]),
    ):
        if counts[request["role"]] >= caps[request["role"]]:
            rejected.append({**request, "reason": "role-cap"})
        elif len(admitted) >= usable_slots:
            rejected.append({**request, "reason": "capacity-reserved"})
        else:
            admitted.append(request)
            counts[request["role"]] += 1
    return {
        "schema_version": 1,
        "total_slots": total_slots,
        "reserve_slots": reserve_slots,
        "usable_slots": usable_slots,
        "role_caps": caps,
        "admitted": admitted,
        "rejected": rejected,
        "active_by_role": dict(sorted(counts.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        plan = json.loads(args.input.read_text(encoding="utf-8"))
        result = allocate_slots(plan)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
