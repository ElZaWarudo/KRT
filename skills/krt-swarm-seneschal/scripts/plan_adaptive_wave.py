#!/usr/bin/env python3
"""Plan a bounded wave from green history, review capacity, and real overlap."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from allocate_worker_slots import ROLE_PRIORITY, allocate_slots
from deterministic_artifacts import canonical_sha256


HIGH_RISK_SURFACES = {
    "auth",
    "data",
    "migration",
    "public-contract",
    "dependency-manifest",
    "generated",
    "release-infrastructure",
    "security-production",
}


def _non_negative_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{field} must be a list of non-empty strings")
    return value


def consecutive_green_waves(history: list[dict[str, Any]]) -> int:
    count = 0
    for wave in reversed(history):
        if (
            wave.get("result") != "green"
            or wave.get("scope_violations") != 0
            or wave.get("merge_conflicts") != 0
            or wave.get("review_lagging") is not False
        ):
            break
        count += 1
    return count


def implementation_cap(
    *, history: list[dict[str, Any]], green_streak: int,
    scale_authorization: dict[str, Any], review_capacity: int,
) -> tuple[int, list[str]]:
    reasons: list[str] = []
    cap = 2
    if history and history[-1].get("result") in {"failed", "partial"}:
        cap = 1
        reasons.append("last-wave-not-green")
    elif history and history[-1].get("review_lagging") is True:
        cap = 1
        reasons.append("review-capacity-lagging")
    elif scale_authorization["authorized"] and green_streak >= 4:
        cap = 4
        reasons.append("four-consecutive-green-waves")
    elif scale_authorization["authorized"] and green_streak >= 2:
        cap = 3
        reasons.append("two-consecutive-green-waves")
    else:
        reasons.append("scale-not-authorized" if green_streak >= 2 else "default-cap")
    if review_capacity < cap:
        reasons.append("review-capacity-cap")
    cap = min(cap, review_capacity, scale_authorization["max_implementers"])
    if cap < 1:
        reasons.append("no-review-capacity")
    return cap, reasons


def validate_scale_authorization(value: Any) -> dict[str, Any]:
    expected = {"authorization_id", "authorized", "authorized_by", "max_implementers", "authorization_digest"}
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("scale_authorization has missing or unknown fields")
    if not isinstance(value.get("authorized"), bool):
        raise ValueError("scale_authorization.authorized must be boolean")
    if not isinstance(value.get("authorization_id"), str) or not value["authorization_id"].strip():
        raise ValueError("scale_authorization.authorization_id must be non-empty")
    if not isinstance(value.get("authorized_by"), str) or not value["authorized_by"].strip():
        raise ValueError("scale_authorization.authorized_by must be non-empty")
    maximum = _non_negative_int(value.get("max_implementers"), "scale_authorization.max_implementers")
    payload = {key: value[key] for key in expected - {"authorization_digest"}}
    expected_digest = canonical_sha256(payload)
    if value.get("authorization_digest") != expected_digest:
        raise ValueError("scale_authorization digest is invalid")
    if value["authorized"] and maximum < 2:
        raise ValueError("authorized scaling must allow at least two implementers")
    return value


def requests_overlap(left: dict[str, Any], right: dict[str, Any]) -> bool:
    if set(left["owned_paths"]) & set(right["owned_paths"]):
        return True
    shared_risk = set(left["risk_surfaces"]) & set(right["risk_surfaces"])
    if shared_risk & HIGH_RISK_SURFACES:
        return True
    if left["id"] in right["unresolved_dependencies"]:
        return True
    if right["id"] in left["unresolved_dependencies"]:
        return True
    return False


def normalize_request(raw: Any) -> dict[str, Any]:
    expected = {
        "id",
        "role",
        "priority",
        "owned_paths",
        "risk_surfaces",
        "unresolved_dependencies",
        "blocked",
    }
    if not isinstance(raw, dict) or set(raw) != expected:
        raise ValueError("each adaptive request has missing or unknown fields")
    request_id = raw.get("id")
    role = raw.get("role")
    if not isinstance(request_id, str) or not request_id:
        raise ValueError("request id must be a non-empty string")
    if role not in ROLE_PRIORITY:
        raise ValueError("request role is unsupported")
    if not isinstance(raw.get("blocked"), bool):
        raise ValueError("request blocked must be boolean")
    return {
        "id": request_id,
        "role": role,
        "priority": _non_negative_int(raw.get("priority"), "priority"),
        "owned_paths": _string_list(raw.get("owned_paths"), "owned_paths"),
        "risk_surfaces": _string_list(raw.get("risk_surfaces"), "risk_surfaces"),
        "unresolved_dependencies": _string_list(
            raw.get("unresolved_dependencies"), "unresolved_dependencies"
        ),
        "blocked": raw["blocked"],
    }


def plan_adaptive_wave(
    plan: dict[str, Any], *, expected_scale_authorization_digest: str
) -> dict[str, Any]:
    expected = {
        "schema_version",
        "total_slots",
        "reserve_slots",
        "role_caps",
        "scale_authorization",
        "review_capacity",
        "wave_history",
        "requests",
    }
    if not isinstance(plan, dict) or set(plan) != expected:
        raise ValueError("adaptive plan has missing or unknown fields")
    if plan.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    total_slots = _non_negative_int(plan.get("total_slots"), "total_slots")
    reserve_slots = _non_negative_int(plan.get("reserve_slots"), "reserve_slots")
    review_capacity = _non_negative_int(plan.get("review_capacity"), "review_capacity")
    scale_authorization = validate_scale_authorization(plan.get("scale_authorization"))
    if scale_authorization["authorization_digest"] != expected_scale_authorization_digest:
        raise ValueError("scale_authorization does not match trusted handoff digest")
    history = plan.get("wave_history")
    if not isinstance(history, list) or not all(isinstance(wave, dict) for wave in history):
        raise ValueError("wave_history must be a list of objects")
    raw_requests = plan.get("requests")
    if not isinstance(raw_requests, list):
        raise ValueError("requests must be a list")
    requests = [normalize_request(request) for request in raw_requests]
    ids = [request["id"] for request in requests]
    if len(ids) != len(set(ids)):
        raise ValueError("request ids must be unique")

    green_streak = consecutive_green_waves(history)
    cap, cap_reasons = implementation_cap(
        history=history,
        green_streak=green_streak,
        scale_authorization=scale_authorization,
        review_capacity=review_capacity,
    )
    rejected: list[dict[str, Any]] = []
    selected_implementers: list[dict[str, Any]] = []
    supporting: list[dict[str, Any]] = []
    for request in sorted(
        requests,
        key=lambda item: (item["priority"], ROLE_PRIORITY[item["role"]], item["id"]),
    ):
        if request["blocked"] or request["unresolved_dependencies"]:
            rejected.append({"id": request["id"], "role": request["role"], "reason": "blocked-or-dependency"})
        elif request["role"] != "implementer":
            supporting.append(request)
        elif len(selected_implementers) >= cap:
            rejected.append({"id": request["id"], "role": request["role"], "reason": "adaptive-cap"})
        elif any(requests_overlap(request, selected) for selected in selected_implementers):
            rejected.append({"id": request["id"], "role": request["role"], "reason": "surface-overlap"})
        else:
            selected_implementers.append(request)

    role_caps = plan.get("role_caps")
    if not isinstance(role_caps, dict):
        raise ValueError("role_caps must be an object")
    effective_caps = dict(role_caps)
    effective_caps["implementer"] = cap
    allocation_requests = [
        {"id": request["id"], "role": request["role"], "priority": request["priority"]}
        for request in [*selected_implementers, *supporting]
    ]
    allocation = allocate_slots(
        {
            "schema_version": 1,
            "total_slots": total_slots,
            "reserve_slots": reserve_slots,
            "role_caps": effective_caps,
            "requests": allocation_requests,
        }
    )
    rejected.extend(allocation["rejected"])
    return {
        "schema_version": 1,
        "green_wave_streak": green_streak,
        "implementer_cap": cap,
        "cap_reasons": cap_reasons,
        "allocation": {**allocation, "rejected": rejected},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--expected-scale-authorization-digest", required=True)
    args = parser.parse_args()
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
        result = plan_adaptive_wave(
            document,
            expected_scale_authorization_digest=args.expected_scale_authorization_digest,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
