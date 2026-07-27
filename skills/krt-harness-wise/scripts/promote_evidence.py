#!/usr/bin/env python3
"""Atomically promote sanitized staged evidence into versionable summaries."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import stat
import sys
from pathlib import Path
from typing import Any

from check_evidence import check_evidence, scoped_path
from publication_safety import scan_publication


SUMMARIES_DIR = Path("docs/harnesses/summaries")


class PromotionValidationError(ValueError):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("\n".join(errors))
        self.errors = errors


def failed(errors: list[str], paths: list[str]) -> dict[str, Any]:
    return {
        "allowed": False,
        "errors": errors,
        "warnings": [],
        "summary": {},
        "paths": paths,
    }


def open_parent(root: Path, destination: Path) -> int:
    relative_parent = destination.parent.relative_to(root)
    flags = os.O_RDONLY | os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(root, flags)
    try:
        for part in relative_parent.parts:
            try:
                os.mkdir(part, mode=0o755, dir_fd=descriptor)
            except FileExistsError:
                pass
            child = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def write_atomic(
    root: Path,
    destination: Path,
    content: bytes,
    overwrite: bool,
) -> dict[str, list[str]]:
    parent = open_parent(root, destination)
    temporary = f".{destination.name}.{secrets.token_hex(8)}.tmp"
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    created = False
    try:
        descriptor = os.open(
            temporary,
            flags,
            0o600,
            dir_fd=parent,
        )
        created = True
        with os.fdopen(descriptor, "w+b") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            handle.seek(0)
            promoted = handle.read()

        try:
            decoded = promoted.decode("utf-8")
        except UnicodeDecodeError as error:
            raise PromotionValidationError(["destination-not-utf8"]) from error
        rescan = scan_publication(decoded)
        validation_errors: list[str] = []
        if promoted != content:
            validation_errors.append("destination-content-mismatch")
        validation_errors.extend(
            f"publication-safety:{code}" for code in rescan["blocking"]
        )
        if validation_errors:
            raise PromotionValidationError(validation_errors)

        try:
            existing = os.stat(
                destination.name,
                dir_fd=parent,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            existing = None
        if existing is not None and stat.S_ISLNK(existing.st_mode):
            raise PromotionValidationError(["destination-must-not-be-symlink"])

        if overwrite:
            os.replace(
                temporary,
                destination.name,
                src_dir_fd=parent,
                dst_dir_fd=parent,
            )
            created = False
        else:
            os.link(
                temporary,
                destination.name,
                src_dir_fd=parent,
                dst_dir_fd=parent,
                follow_symlinks=False,
            )
            os.unlink(temporary, dir_fd=parent)
            created = False
        os.fsync(parent)
        return rescan
    finally:
        if created:
            try:
                os.unlink(temporary, dir_fd=parent)
            except FileNotFoundError:
                pass
        os.close(parent)


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
    try:
        rescan = write_atomic(root, destination, content, args.overwrite)
    except PromotionValidationError as exc:
        errors = ["destination-rescan-failed", *exc.errors]
        result = failed(
            sorted(set(errors)),
            [args.summary, args.sidecar, destination_arg],
        )
        print(json.dumps(result, sort_keys=True, indent=2))
        return 1
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
