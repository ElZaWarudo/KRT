#!/usr/bin/env python3
"""Aggregate supervisor-captured statuses without judging model output."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from check_corpus import corpus_digest, load_object


ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"pass", "fail", "inconclusive"}


def score(
    results_path: Path,
    cases_path: Path,
    expectations_path: Path,
) -> dict:
    submitted = load_object(results_path)
    corpus = load_object(cases_path)
    expectations = load_object(expectations_path)
    cases = corpus.get("cases")
    results = submitted.get("results")
    if not isinstance(cases, list):
        raise ValueError("corpus cases must be a list")
    if not isinstance(results, list):
        raise ValueError("results must be a list")

    expected_version = corpus.get("corpus_version")
    expected_digest = corpus_digest(cases_path, expectations_path)
    identity_errors: list[str] = []
    if type(submitted.get("schema_version")) is not int:
        identity_errors.append("results schema_version must be integer 1")
    elif submitted.get("schema_version") != 1:
        identity_errors.append("results schema_version must be 1")
    if expectations.get("corpus_version") != expected_version:
        identity_errors.append("corpus_version must match expectations")
    if submitted.get("corpus_version") != expected_version:
        identity_errors.append("results corpus_version does not match corpus")
    if submitted.get("corpus_digest") != expected_digest:
        identity_errors.append("results corpus_digest does not match corpus")
    if identity_errors:
        raise ValueError("\n".join(identity_errors))

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
        "schema_version": 1,
        "run_id": submitted.get("run_id"),
        "corpus_version": expected_version,
        "corpus_digest": expected_digest,
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
        print(
            "usage: score_run.py <results.json> [cases.json] [expectations.json]",
            file=sys.stderr,
        )
        return 2
    results = Path(argv[1])
    cases = (
        Path(argv[2]) if len(argv) > 2 else ROOT / "references" / "cases.json"
    )
    expectations = (
        Path(argv[3])
        if len(argv) > 3
        else ROOT / "references" / "expectations.json"
    )
    try:
        output = score(results, cases, expectations)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
