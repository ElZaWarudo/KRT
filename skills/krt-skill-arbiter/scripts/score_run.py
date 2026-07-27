#!/usr/bin/env python3
"""Aggregate supervisor-captured statuses without judging model output."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"pass", "fail", "inconclusive"}


def load_object(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top level must be an object")
    return value


def score(results_path: Path, cases_path: Path) -> dict:
    submitted = load_object(results_path)
    corpus = load_object(cases_path)
    cases = corpus.get("cases")
    results = submitted.get("results")
    if not isinstance(cases, list):
        raise ValueError("corpus cases must be a list")
    if not isinstance(results, list):
        raise ValueError("results must be a list")

    known = {
        case["id"]: case["category"]
        for case in cases
        if isinstance(case, dict)
        and isinstance(case.get("id"), str)
        and isinstance(case.get("category"), str)
    }
    seen: set[str] = set()
    counts: Counter[str] = Counter({status: 0 for status in STATUSES})
    categories: dict[str, Counter[str]] = defaultdict(Counter)
    errors: list[str] = []

    for index, item in enumerate(results):
        if not isinstance(item, dict):
            errors.append(f"results[{index}] must be an object")
            continue
        case_id = item.get("case_id")
        status = item.get("status")
        if case_id not in known:
            errors.append(f"results[{index}]: unknown case_id {case_id!r}")
            continue
        if case_id in seen:
            errors.append(f"results[{index}]: duplicate case_id {case_id}")
            continue
        seen.add(case_id)
        if status not in STATUSES:
            errors.append(
                f"{case_id}: status must be pass, fail, or inconclusive"
            )
            continue
        counts[status] += 1
        categories[known[case_id]][status] += 1

    if errors:
        raise ValueError("\n".join(errors))

    conclusive = counts["pass"] + counts["fail"]
    total = len(known)
    return {
        "run_id": submitted.get("run_id"),
        "corpus_version": corpus.get("corpus_version"),
        "corpus_size": total,
        "submitted": len(seen),
        "corpus_coverage": round(len(seen) / total, 6) if total else 0.0,
        "counts": {
            "fail": counts["fail"],
            "inconclusive": counts["inconclusive"],
            "pass": counts["pass"],
        },
        "conclusive_pass_rate": (
            round(counts["pass"] / conclusive, 6) if conclusive else None
        ),
        "by_category": {
            category: {
                "fail": values["fail"],
                "inconclusive": values["inconclusive"],
                "pass": values["pass"],
            }
            for category, values in sorted(categories.items())
        },
        "unsubmitted_case_ids": sorted(set(known) - seen),
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: score_run.py <results.json> [cases.json]", file=sys.stderr)
        return 2
    results = Path(argv[1])
    cases = (
        Path(argv[2]) if len(argv) > 2 else ROOT / "references" / "cases.json"
    )
    try:
        output = score(results, cases)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
