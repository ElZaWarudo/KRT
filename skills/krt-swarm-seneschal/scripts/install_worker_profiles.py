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
    REQUIRED_WORKER_FIELDS,
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
    pending_removals: list[Path] = []

    for worker_id in selected_ids:
        worker = workers.get(worker_id)
        if not isinstance(worker, dict):
            result["errors"].append(f"worker-not-registered:{worker_id}")
            continue
        missing = sorted(REQUIRED_WORKER_FIELDS - set(worker))
        if missing:
            result["errors"].append(
                f"worker-manifest-entry-missing:{worker_id}:{','.join(missing)}"
            )
            continue
        if any(
            not isinstance(worker[field], str) or not worker[field].strip()
            for field in REQUIRED_WORKER_FIELDS
        ):
            result["errors"].append(f"worker-manifest-entry-invalid:{worker_id}")
            continue
        source = (skill_dir / worker["profile"]).resolve()
        target_root = repo_root if scope == "project" else codex_home
        target_key = "project_override" if scope == "project" else "user_install"
        target = (target_root / worker[target_key]).resolve()
        if not inside(source, skill_dir) or not inside(target, target_root):
            result["errors"].append(f"worker-install-path-escape:{worker_id}")
            continue
        source_profile, profile_errors = validate_profile(
            source,
            worker["expected_name"],
            worker["expected_model"],
            worker["expected_reasoning_effort"],
        )
        if profile_errors:
            result["errors"].extend(
                f"{worker_id}:{error}" for error in profile_errors
            )
            continue

        legacy_targets: list[str] = []
        if scope == "user":
            legacy_installs = worker.get("legacy_user_installs", [])
            if not isinstance(legacy_installs, list) or any(
                not isinstance(path, str) or not path.strip()
                for path in legacy_installs
            ):
                result["errors"].append(
                    f"worker-legacy-installs-invalid:{worker_id}"
                )
                continue
            for relative_path in legacy_installs:
                legacy = (target_root / relative_path).resolve()
                if not inside(legacy, target_root) or legacy == target:
                    result["errors"].append(
                        f"worker-legacy-install-path-invalid:{worker_id}"
                    )
                    continue
                if not legacy.exists():
                    continue
                legacy_profile, legacy_errors = validate_profile(
                    legacy,
                    worker["expected_name"],
                    worker["expected_model"],
                )
                expected_legacy = dict(source_profile or {})
                actual_legacy = dict(legacy_profile or {})
                expected_legacy.pop("model_reasoning_effort", None)
                actual_legacy.pop("model_reasoning_effort", None)
                if legacy_errors or actual_legacy != expected_legacy:
                    result["errors"].append(
                        f"worker-legacy-profile-conflict:{worker_id}:{legacy}"
                    )
                elif replace:
                    pending_removals.append(legacy)
                    legacy_targets.append(str(legacy))
                else:
                    result["errors"].append(
                        f"worker-legacy-profile-conflict:{worker_id}:"
                        "use-explicit-replace"
                    )

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
            "legacy_removals": legacy_targets,
        }

    if result["errors"]:
        return result

    if install:
        for source, target in pending:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        for legacy in pending_removals:
            legacy.unlink()
        result["applied"] = True

    result["allowed"] = True
    result["summary"]["pending_changes"] = len(pending) + len(pending_removals)
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
