#!/usr/bin/env python3
"""Atomically promote sanitized staged evidence into versionable summaries."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from check_evidence import check_evidence, scoped_path
from publication_safety import scan_publication


SUMMARIES_DIR = Path("docs/harnesses/summaries")


def failed(errors: list[str], paths: list[str]) -> dict[str, Any]:
    return {
        "allowed": False,
        "errors": errors,
        "warnings": [],
        "summary": {},
        "paths": paths,
    }


def write_atomic(destination: Path, content: bytes, overwrite: bool) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if overwrite:
            os.replace(temporary, destination)
        else:
            os.link(temporary, destination)
            temporary.unlink()
    finally:
        temporary.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", help="repo-relative Markdown under docs/harnesses/staging")
    parser.add_argument("--sidecar", required=True, help="repo-relative JSON under docs/harnesses/provenance")
    parser.add_argument("--destination", help="repo-relative destination under docs/harnesses/summaries")
    parser.add_argument("--overwrite", action="store_true", help="explicitly replace an existing summary")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    root = args.root.resolve()
    checked, source, _, content = check_evidence(root, args.summary, args.sidecar)
    if not checked["allowed"] or source is None or content is None:
        print(json.dumps(checked, sort_keys=True, indent=2))
        return 1

    destination_arg = args.destination or (SUMMARIES_DIR / source.name).as_posix()
    destination, scope_error = scoped_path(root, destination_arg, SUMMARIES_DIR, "destination")
    if scope_error or destination is None:
        result = failed(
            [scope_error or f"destination-must-be-under:{SUMMARIES_DIR.as_posix()}"],
            [args.summary, args.sidecar, destination_arg],
        )
        print(json.dumps(result, sort_keys=True, indent=2))
        return 1
    if destination.suffix.lower() != ".md":
        result = failed(["destination-must-be-markdown"], [args.summary, args.sidecar, destination_arg])
        print(json.dumps(result, sort_keys=True, indent=2))
        return 1
    if destination.is_symlink():
        result = failed(["destination-must-not-be-symlink"], [args.summary, args.sidecar, destination_arg])
        print(json.dumps(result, sort_keys=True, indent=2))
        return 1
    try:
        write_atomic(destination, content, args.overwrite)
    except FileExistsError:
        result = failed(
            [f"destination-exists:{destination.relative_to(root).as_posix()}"],
            [args.summary, args.sidecar, destination_arg],
        )
        print(json.dumps(result, sort_keys=True, indent=2))
        return 1
    except OSError as exc:
        result = failed([f"promotion-failed:{exc}"], [args.summary, args.sidecar, destination_arg])
        print(json.dumps(result, sort_keys=True, indent=2))
        return 1

    promoted = destination.read_bytes()
    rescan = scan_publication(promoted.decode("utf-8"))
    if promoted != content or rescan["blocking"]:
        destination.unlink(missing_ok=True)
        errors = ["destination-rescan-failed"]
        errors.extend(f"publication-safety:{code}" for code in rescan["blocking"])
        result = failed(sorted(set(errors)), [args.summary, args.sidecar, destination_arg])
        print(json.dumps(result, sort_keys=True, indent=2))
        return 1

    result = {
        "allowed": True,
        "errors": [],
        "warnings": checked["warnings"],
        "summary": {
            **checked["summary"],
            "destination": destination.relative_to(root).as_posix(),
            "destination_rescan": "passed",
        },
        "paths": [args.summary, args.sidecar, destination.relative_to(root).as_posix()],
    }
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
