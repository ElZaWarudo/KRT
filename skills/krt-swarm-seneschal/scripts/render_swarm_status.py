#!/usr/bin/env python3
"""Render a compact read-only view of Seneschal waves, blockers, gates, and slots."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
from typing import Any


COMPLETE_STATUSES = {"release-ready", "handed-off", "merged"}
ACTIVE_STATUSES = {"running", "review-gated", "needs-fix"}


def load_structured(path: Path | None, *, default: dict[str, Any]) -> dict[str, Any]:
    if path is None:
        return default
    raw = path.read_text(encoding="utf-8")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ValueError("YAML input requires PyYAML; JSON is dependency-free") from exc
        value = yaml.safe_load(raw)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def build_snapshot(
    *,
    queue: dict[str, Any],
    blockers: dict[str, Any],
    evidence: dict[str, Any],
    allocation: dict[str, Any],
) -> dict[str, Any]:
    units = queue.get("units", {})
    if not isinstance(units, dict):
        raise ValueError("queue units must be an object")
    history = queue.get("wave_history", [])
    if not isinstance(history, list):
        raise ValueError("wave_history must be a list")
    wave = history[-1] if history and isinstance(history[-1], dict) else {}
    selected_units = wave.get("selected_units")
    if isinstance(selected_units, list) and selected_units:
        if len(selected_units) != len(set(selected_units)) or any(
            not isinstance(unit_id, str) or unit_id not in units
            for unit_id in selected_units
        ):
            raise ValueError("current wave selected_units is inconsistent with queue units")
        visible_units = {
            unit_id: units[unit_id]
            for unit_id in selected_units
            if unit_id in units
        }
    else:
        visible_units = units
    statuses = Counter(
        unit.get("status", "unknown")
        for unit in visible_units.values()
        if isinstance(unit, dict)
    )
    raw_blockers = blockers.get("blockers", [])
    if not isinstance(raw_blockers, list):
        raise ValueError("blockers must be a list")
    open_blockers = [
        blocker
        for blocker in raw_blockers
        if isinstance(blocker, dict) and blocker.get("status") == "open"
    ]
    high_risk_blockers = sum(blocker.get("risk") == "high" for blocker in open_blockers)

    aggregate = wave.get("aggregate_verification", {})
    if not isinstance(aggregate, dict):
        aggregate = {}
    gates = wave.get("gates", {})
    if not isinstance(gates, dict):
        gates = {}
    gate_snapshot = {
        "documentation": queue.get("documentation_gate", {}).get("status", "unknown")
        if isinstance(queue.get("documentation_gate"), dict)
        else "unknown",
        "scope": gates.get("scope", "unknown"),
        "verification": gates.get("verification", aggregate.get("result", "not-run")),
        "review": gates.get(
            "review",
            "pending" if statuses["review-gated"] or statuses["needs-fix"] else "unknown",
        ),
        "security": gates.get("security", "not-required"),
        "state": gates.get("state", "unknown"),
    }

    allocation_view = allocation.get("allocation", allocation)
    if not isinstance(allocation_view, dict):
        allocation_view = {}
    admitted = allocation_view.get("admitted", [])
    usable_slots = allocation_view.get("usable_slots")
    reserve_slots = allocation_view.get("reserve_slots")
    if not isinstance(admitted, list):
        admitted = []
    records = evidence.get("records", [])
    if not isinstance(records, list):
        raise ValueError("evidence records must be a list")
    passing_evidence = sum(
        isinstance(record, dict) and record.get("result") == "passed" for record in records
    )
    completed = sum(count for status, count in statuses.items() if status in COMPLETE_STATUSES)
    active = sum(count for status, count in statuses.items() if status in ACTIVE_STATUSES)
    fingerprint = aggregate.get("fingerprint")
    return {
        "schema_version": 1,
        "wave": {
            "id": wave.get("id", "none"),
            "result": wave.get("result", "unknown"),
            "units": len(visible_units),
            "completed": completed,
            "active": active,
            "blocked": statuses["blocked"],
            "awaiting_review": statuses["review-gated"],
        },
        "gates": gate_snapshot,
        "blockers": {"open": len(open_blockers), "high_risk": high_risk_blockers},
        "slots": {
            "active": len(admitted),
            "usable": usable_slots,
            "reserved": reserve_slots,
        },
        "evidence": {
            "passing_records": passing_evidence,
            "fingerprint": fingerprint,
        },
        "status_counts": dict(sorted(statuses.items())),
    }


def render_text(snapshot: dict[str, Any]) -> str:
    wave = snapshot["wave"]
    blockers = snapshot["blockers"]
    slots = snapshot["slots"]
    gates = snapshot["gates"]
    fingerprint = snapshot["evidence"]["fingerprint"]
    short_fingerprint = fingerprint[:19] + "…" if isinstance(fingerprint, str) else "none"
    return "\n".join(
        [
            (
                f"Wave {wave['id']} · {wave['completed']}/{wave['units']} complete · "
                f"{wave['active']} active · {wave['blocked']} blocked · "
                f"{wave['awaiting_review']} awaiting review"
            ),
            (
                "Gates · "
                + " · ".join(f"{name}={value}" for name, value in gates.items())
            ),
            f"Blockers · {blockers['open']} open · {blockers['high_risk']} high risk",
            (
                f"Slots · {slots['active']}/{slots['usable'] if slots['usable'] is not None else '?'} "
                f"active · {slots['reserved'] if slots['reserved'] is not None else '?'} reserved"
            ),
            (
                f"Evidence · {snapshot['evidence']['passing_records']} passing records · "
                f"fingerprint {short_fingerprint}"
            ),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--blockers", type=Path)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--allocation", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    try:
        snapshot = build_snapshot(
            queue=load_structured(args.queue, default={}),
            blockers=load_structured(args.blockers, default={"blockers": []}),
            evidence=load_structured(args.evidence, default={"records": []}),
            allocation=load_structured(args.allocation, default={}),
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    if args.format == "json":
        json.dump(snapshot, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_text(snapshot) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
