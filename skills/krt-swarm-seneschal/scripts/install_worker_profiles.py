#!/usr/bin/env python3
"""Install bundled Seneschal profiles into a Codex custom-agent directory."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from check_worker_profiles import (
    default_codex_home,
    inside,
    load_manifest,
    validate_profile,
)


def install_profiles(
    *,
    skill_dir: Path,
    repo_root: Path,
    codex_home: Path,
    scope: str,
    requested_workers: list[str] | None = None,
    install: bool = False,
    replace: bool = False,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    repo_root = repo_root.resolve()
    codex_home = codex_home.resolve()
    manifest, errors = load_manifest(skill_dir)
    result: dict[str, Any] = {
        "allowed": False,
        "applied": False,
        "errors": list(errors),
        "profiles": {},
        "summary": {"scope": scope, "mode": "install" if install else "dry-run"},
    }
    if manifest is None or errors:
        return result

    workers = manifest["workers"]
    selected_ids = requested_workers or sorted(workers)
    pending: list[tuple[Path, Path]] = []

    for worker_id in selected_ids:
        worker = workers.get(worker_id)
        if not isinstance(worker, dict):
            result["errors"].append(f"worker-not-registered:{worker_id}")
            continue
        source = (skill_dir / worker["profile"]).resolve()
        target_root = repo_root if scope == "project" else codex_home
        target_key = "project_override" if scope == "project" else "user_install"
        target = (target_root / worker[target_key]).resolve()
        if not inside(source, skill_dir) or not inside(target, target_root):
            result["errors"].append(f"worker-install-path-escape:{worker_id}")
            continue
        _, profile_errors = validate_profile(source, worker["expected_name"])
        if profile_errors:
            result["errors"].extend(
                f"{worker_id}:{error}" for error in profile_errors
            )
            continue

        if target.exists():
            try:
                identical = source.read_bytes() == target.read_bytes()
            except OSError as exc:
                result["errors"].append(
                    f"worker-target-unreadable:{worker_id}:{exc}"
                )
                continue
            if identical:
                status = "current"
            elif replace:
                status = "replace"
                pending.append((source, target))
            else:
                status = "conflict"
                result["errors"].append(
                    f"worker-target-conflict:{worker_id}:use-project-override-or-explicit-replace"
                )
        else:
            status = "create"
            pending.append((source, target))

        result["profiles"][worker_id] = {
            "source": str(source),
            "target": str(target),
            "status": status,
        }

    if result["errors"]:
        return result

    if install:
        for source, target in pending:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        result["applied"] = True

    result["allowed"] = True
    result["summary"]["pending_changes"] = len(pending)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install bundled Seneschal workers as Codex custom agents."
    )
    parser.add_argument(
        "--skill-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--codex-home", type=Path, default=default_codex_home())
    parser.add_argument("--scope", choices=("project", "user"), default="user")
    parser.add_argument("--worker", action="append", dest="workers")
    parser.add_argument("--install", action="store_true")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace a differing existing profile; never implied by --install.",
    )
    args = parser.parse_args()

    result = install_profiles(
        skill_dir=args.skill_dir,
        repo_root=args.repo_root,
        codex_home=args.codex_home,
        scope=args.scope,
        requested_workers=args.workers,
        install=args.install,
        replace=args.replace,
    )
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
