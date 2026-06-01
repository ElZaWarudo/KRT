#!/usr/bin/env python3
"""Check whether a PR diff looks like one focused review unit."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


DOC_PREFIXES = (
    "docs/brainstorms/",
    "docs/plans/",
    "docs/work-packages/",
    "docs/orchestration/compound-master-state.md",
)

GENERATED_MARKERS = (
    ".auto.",
    "generated",
    "bindings",
    "definitions.ts",
)


def run_numstat(base: str | None) -> list[tuple[int, int, str]]:
    cmd = ["git", "diff", "--numstat"]
    if base:
        cmd.append(base)
    output = subprocess.check_output(cmd, text=True)
    rows: list[tuple[int, int, str]] = []
    for line in output.splitlines():
        added, deleted, path = line.split("\t", 2)
        if added == "-" or deleted == "-":
            rows.append((0, 0, path))
        else:
            rows.append((int(added), int(deleted), path))
    return rows


def untracked_files() -> list[str]:
    output = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"],
        text=True,
    )
    return [line for line in output.splitlines() if line]


def count_lines(path: str) -> int:
    data = Path(path).read_bytes()
    if b"\0" in data:
        return 0
    if not data:
        return 0
    return data.count(b"\n") + (0 if data.endswith(b"\n") else 1)


def is_doc(path: str) -> bool:
    return path.startswith(DOC_PREFIXES)


def is_generated(path: str) -> bool:
    lowered = path.lower()
    return any(marker in lowered for marker in GENERATED_MARKERS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", help="git diff base, for example origin/develop...HEAD")
    parser.add_argument("--no-untracked", action="store_true", help="do not count untracked files")
    parser.add_argument("--fail-on-warning", action="store_true")
    parser.add_argument(
        "--fail-on-blocking",
        action="store_true",
        help="exit 1 when the diff requires explicit split/oversized approval",
    )
    args = parser.parse_args()

    rows = run_numstat(args.base)
    untracked: set[str] = set()
    if not args.no_untracked:
        untracked = set(untracked_files())
        for path in sorted(untracked):
            rows.append((count_lines(path), 0, path))

    doc = gen = human = 0
    doc_files: list[str] = []
    gen_files: list[str] = []

    for added, deleted, path in rows:
        total = added + deleted
        if is_doc(path):
            doc += total
            doc_files.append(path)
        elif is_generated(path):
            gen += total
            gen_files.append(path)
        else:
            human += total

    warnings: list[str] = []
    blocking: list[str] = []
    if human > 1000:
        blocking.append(f"human-authored diff is ~{human} lines; split or approve oversized PR")
    elif human > 900:
        warnings.append(f"human-authored diff is ~{human} lines; review-size warning")

    if doc and human:
        warnings.append(
            "orchestration/planning docs are mixed with functional files; confirm they are related and not obscuring review"
        )
    if gen and human and gen >= human * 0.5:
        blocking.append("generated/mechanical files dominate or substantially obscure functional review")

    print(f"human_lines={human}")
    print(f"generated_lines={gen}")
    print(f"orchestration_doc_lines={doc}")
    print(f"untracked_files_count={len(untracked)}")
    if doc_files:
        print("orchestration_doc_files:")
        for path in doc_files:
            print(f"- {path}")
    if gen_files:
        print("generated_files:")
        for path in gen_files:
            print(f"- {path}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for item in blocking:
        print(f"BLOCKING: {item}")

    if (warnings or blocking) and args.fail_on_warning:
        return 1
    if blocking and args.fail_on_blocking:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
