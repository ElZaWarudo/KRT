#!/usr/bin/env python3
"""Summarize Seneschal timing records by worker profile and evidence trust."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from statistics import median
import sys
from typing import Any


COUNT_FIELDS = (
    "fix_rounds",
    "out_of_manifest_commands",
    "repeated_verification_commands",
    "review_findings_p0",
    "review_findings_p1",
    "review_findings_p2",
    "scope_violations",
)
MEDIAN_FIELDS = (
    "acceptance_latency_ms",
    "discovery_implementation_ratio",
    "time_to_first_change_ms",
    "total_duration_ms",
)


def summarize(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("schema_version") != 1 or not isinstance(document.get("records"), list):
        raise ValueError("timing document must use schema_version 1 and records[]")
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in document["records"]:
        if not isinstance(record, dict):
            raise ValueError("timing records must be objects")
        profile = record.get("worker_profile")
        trust = record.get("evidence_trust", "unknown")
        if not isinstance(profile, str) or not profile or not isinstance(trust, str):
            raise ValueError("timing record profile and evidence trust are required")
        groups[(profile, trust)].append(record)

    summaries: list[dict[str, Any]] = []
    for (profile, trust), records in sorted(groups.items()):
        status_counts = Counter(record.get("status", "unknown") for record in records)
        summary: dict[str, Any] = {
            "worker_profile": profile,
            "evidence_trust": trust,
            "samples": len(records),
            "status_counts": dict(sorted(status_counts.items())),
        }
        for field in COUNT_FIELDS:
            values = [record.get(field, 0) for record in records]
            if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in values):
                raise ValueError(f"{field} must contain non-negative integers")
            summary[f"total_{field}"] = sum(values)
        for field in MEDIAN_FIELDS:
            values = [record.get(field) for record in records if record.get(field) is not None]
            if any(
                isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0
                for value in values
            ):
                raise ValueError(f"{field} must contain non-negative numbers")
            summary[f"median_{field}"] = median(values) if values else None
        summaries.append(summary)
    return {"schema_version": 1, "groups": summaries}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
        result = summarize(document)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
