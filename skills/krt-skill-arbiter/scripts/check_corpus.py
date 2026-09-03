#!/usr/bin/env python3
"""Validate the static KRT skill evaluation corpus without executing it."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    "routing",
    "negative-trigger",
    "fallback",
    "permissions",
    "restart",
    "outcome",
}
ROUTING_CATEGORIES = {"routing", "negative-trigger"}
MIN_CASES_PER_CATEGORY = 2


def load_object(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{path}: top level must be an object")
    return value


def corpus_digest(cases_path: Path, expectations_path: Path) -> str:
    digest = hashlib.sha256()
    for label, path in (
        (b"cases", cases_path),
        (b"expectations", expectations_path),
    ):
        digest.update(label)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def nonempty_strings(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def validate(
    cases_path: Path, expectations_path: Path, skills_root: Path
) -> dict:
    corpus = load_object(cases_path)
    expected = load_object(expectations_path)
    errors: list[str] = []

    if (
        type(corpus.get("schema_version")) is not int
        or corpus.get("schema_version") != 1
        or type(expected.get("schema_version")) is not int
        or expected.get("schema_version") != 1
    ):
        errors.append("schema_version must be 1 in both files")
    if corpus.get("corpus_version") != expected.get("corpus_version"):
        errors.append("corpus_version must match between files")

    cases = corpus.get("cases")
    expectations = expected.get("expectations")
    if not isinstance(cases, list):
        errors.append("cases must be a list")
        cases = []
    if not isinstance(expectations, list):
        errors.append("expectations must be a list")
        expectations = []

    case_ids: list[str] = []
    counts: Counter[str] = Counter()
    for index, case in enumerate(cases):
        label = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label} must be an object")
            continue
        case_id = case.get("id")
        category = case.get("category")
        mode = case.get("evaluation_mode")
        prompt = case.get("prompt")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{label}.id must be a non-empty string")
            continue
        case_ids.append(case_id)
        if category not in CATEGORIES:
            errors.append(f"{case_id}: unknown category {category!r}")
            continue
        counts[category] += 1
        expected_mode = "routing" if category in ROUTING_CATEGORIES else "capability"
        if mode != expected_mode:
            errors.append(f"{case_id}: evaluation_mode must be {expected_mode}")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{case_id}: prompt must be a non-empty string")
        target = case.get("target_skill")
        if mode == "routing":
            if "target_skill" in case:
                errors.append(f"{case_id}: routing cases must not expose target_skill")
            if isinstance(prompt, str) and "krt-" in prompt.lower():
                errors.append(f"{case_id}: routing prompts must not reveal a skill ID")
        else:
            if not isinstance(target, str) or not target.startswith("krt-"):
                errors.append(f"{case_id}: capability cases require target_skill")
            else:
                if not (skills_root / target / "SKILL.md").is_file():
                    errors.append(
                        f"{case_id}: target_skill does not exist: {target}"
                    )
                if isinstance(prompt, str) and target not in prompt:
                    errors.append(
                        f"{case_id}: capability prompt must reveal target_skill"
                    )

    if len(case_ids) != len(set(case_ids)):
        errors.append("case IDs must be unique")
    underrepresented = sorted(
        name for name in CATEGORIES if counts[name] < MIN_CASES_PER_CATEGORY
    )
    if underrepresented:
        errors.append(
            "corpus must contain at least two cases per category; missing coverage: "
            + ", ".join(underrepresented)
        )

    expectation_ids: list[str] = []
    by_case = {case.get("id"): case for case in cases if isinstance(case, dict)}
    for index, item in enumerate(expectations):
        label = f"expectations[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        case_id = item.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{label}.id must be a non-empty string")
            continue
        expectation_ids.append(case_id)
        if not isinstance(item.get("expected_behavior"), str):
            errors.append(f"{case_id}: expected_behavior must be a string")
        if not nonempty_strings(item.get("pass_criteria")):
            errors.append(f"{case_id}: pass_criteria must contain strings")
        if not nonempty_strings(item.get("fail_if")):
            errors.append(f"{case_id}: fail_if must contain strings")
        case = by_case.get(case_id)
        if case and case.get("evaluation_mode") == "routing":
            route = item.get("expected_skill")
            category = case.get("category")
            if category == "routing" and (
                not isinstance(route, str) or not route.startswith("krt-")
            ):
                errors.append(
                    f"{case_id}: routing expected_skill must be a KRT ID"
                )
            elif category == "negative-trigger" and route is not None:
                errors.append(
                    f"{case_id}: negative-trigger expected_skill must be null"
                )
            if (
                isinstance(route, str)
                and route.startswith("krt-")
                and not (skills_root / route / "SKILL.md").is_file()
            ):
                errors.append(
                    f"{case_id}: expected_skill does not exist: {route}"
                )

    if len(expectation_ids) != len(set(expectation_ids)):
        errors.append("expectation IDs must be unique")
    if set(case_ids) != set(expectation_ids):
        errors.append("case and expectation IDs must match exactly")
    if errors:
        raise ValueError("\n".join(errors))

    return {
        "status": "valid",
        "corpus_version": corpus["corpus_version"],
        "corpus_digest": corpus_digest(cases_path, expectations_path),
        "case_count": len(cases),
        "categories": dict(sorted(counts.items())),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "cases",
        nargs="?",
        type=Path,
        default=ROOT / "references" / "cases.json",
    )
    parser.add_argument(
        "expectations",
        nargs="?",
        type=Path,
        default=ROOT / "references" / "expectations.json",
    )
    parser.add_argument("--skills-root", type=Path, default=ROOT.parent)
    args = parser.parse_args(argv[1:])
    try:
        result = validate(args.cases, args.expectations, args.skills_root)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
