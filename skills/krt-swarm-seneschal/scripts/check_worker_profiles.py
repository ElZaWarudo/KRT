#!/usr/bin/env python3
"""Resolve and validate Codex custom-agent profiles used by Seneschal."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tomllib
from pathlib import Path
from typing import Any


REQUIRED_PROFILE_FIELDS = {
    "name": str,
    "description": str,
    "developer_instructions": str,
}
OPTIONAL_PROFILE_FIELDS = {
    "model": str,
    "model_reasoning_effort": str,
    "sandbox_mode": str,
}
REQUIRED_WORKER_FIELDS = {
    "profile",
    "project_override",
    "user_install",
    "required_runtime",
    "expected_name",
    "expected_model",
    "expected_reasoning_effort",
    "model_class",
}


def default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured) if configured else Path.home() / ".codex"


def inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def load_manifest(skill_dir: Path) -> tuple[dict[str, Any] | None, list[str]]:
    manifest_path = skill_dir / "assets" / "codex-workers" / "manifest.yaml"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [f"worker-manifest-missing:{manifest_path}"]
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"worker-manifest-invalid:{exc}"]

    errors: list[str] = []
    if manifest.get("schema_version") != 1:
        errors.append("worker-manifest-schema-version-must-be-1")
    if not isinstance(manifest.get("workers"), dict) or not manifest["workers"]:
        errors.append("worker-manifest-workers-must-be-a-non-empty-object")
    lanes = manifest.get("lanes")
    if not isinstance(lanes, dict) or set(lanes) != {"fast", "standard", "deep"}:
        errors.append("worker-manifest-lanes-must-map-fast-standard-deep")
    elif any(
        not isinstance(worker_id, str) or not worker_id
        for worker_id in lanes.values()
    ):
        errors.append("worker-manifest-lane-worker-invalid")
    return manifest, errors


def validate_profile(
    profile_path: Path,
    expected_name: str,
    expected_model: str | None = None,
    expected_reasoning_effort: str | None = None,
) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        with profile_path.open("rb") as stream:
            profile = tomllib.load(stream)
    except FileNotFoundError:
        return None, [f"worker-profile-missing:{profile_path}"]
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return None, [f"worker-profile-invalid:{profile_path}:{exc}"]

    errors: list[str] = []
    for field, expected_type in REQUIRED_PROFILE_FIELDS.items():
        value = profile.get(field)
        if not isinstance(value, expected_type) or not value.strip():
            errors.append(f"worker-profile-field-invalid:{field}")
    for field, expected_type in OPTIONAL_PROFILE_FIELDS.items():
        value = profile.get(field)
        if value is not None and (
            not isinstance(value, expected_type) or not value.strip()
        ):
            errors.append(f"worker-profile-field-invalid:{field}")
    if profile.get("name") != expected_name:
        errors.append(
            "worker-profile-name-mismatch:"
            f"expected={expected_name}:actual={profile.get('name')}"
        )
    if expected_model is not None and profile.get("model") != expected_model:
        errors.append(
            "worker-profile-model-mismatch:"
            f"expected={expected_model}:actual={profile.get('model')}"
        )
    if (
        expected_reasoning_effort is not None
        and profile.get("model_reasoning_effort") != expected_reasoning_effort
    ):
        errors.append(
            "worker-profile-reasoning-effort-mismatch:"
            f"expected={expected_reasoning_effort}:"
            f"actual={profile.get('model_reasoning_effort')}"
        )
    return profile, errors


def check_profiles(
    *,
    skill_dir: Path,
    repo_root: Path,
    codex_home: Path | None = None,
    requested_workers: list[str] | None = None,
    runtime: str = "codex",
    model_class: str | None = None,
    lane: str | None = None,
    allow_bundled: bool = False,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    repo_root = repo_root.resolve()
    codex_home = (codex_home or default_codex_home()).resolve()
    manifest, errors = load_manifest(skill_dir)
    result: dict[str, Any] = {
        "allowed": False,
        "errors": list(errors),
        "workers": {},
        "summary": {
            "repo_root": str(repo_root),
            "codex_home": str(codex_home),
            "skill_dir": str(skill_dir),
            "runtime": runtime,
            "model_availability": "not-checked-by-static-preflight",
        },
    }
    if manifest is None or errors:
        return result

    workers = manifest["workers"]
    if lane is not None:
        expected_worker = manifest["lanes"].get(lane)
        if expected_worker is None:
            result["errors"].append(f"worker-lane-unknown:{lane}")
            return result
        if requested_workers and requested_workers != [expected_worker]:
            result["errors"].append(
                f"worker-lane-mismatch:{lane}:expected={expected_worker}:"
                f"actual={','.join(requested_workers)}"
            )
            return result
        selected_ids = [expected_worker]
    else:
        selected_ids = requested_workers or sorted(workers)
    if model_class is not None and len(selected_ids) != 1:
        result["errors"].append("model-class-check-requires-exactly-one-worker")
        return result

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
        if worker["required_runtime"] != runtime:
            result["errors"].append(
                f"worker-runtime-mismatch:{worker_id}:"
                f"required={worker['required_runtime']}:actual={runtime}"
            )
            continue
        if model_class is not None and worker["model_class"] != model_class:
            result["errors"].append(
                f"worker-model-class-mismatch:{worker_id}:"
                f"expected={model_class}:actual={worker['model_class']}"
            )
            continue

        project_path = (repo_root / worker["project_override"]).resolve()
        user_path = (codex_home / worker["user_install"]).resolve()
        bundled_path = (skill_dir / worker["profile"]).resolve()
        if not inside(project_path, repo_root):
            result["errors"].append(f"worker-project-path-escape:{worker_id}")
            continue
        if not inside(user_path, codex_home):
            result["errors"].append(f"worker-user-path-escape:{worker_id}")
            continue
        if not inside(bundled_path, skill_dir):
            result["errors"].append(f"worker-bundled-path-escape:{worker_id}")
            continue

        if project_path.exists():
            profile_path = project_path
            source = "project-agent"
            runtime_discoverable = True
        elif user_path.exists():
            profile_path = user_path
            source = "user-agent"
            runtime_discoverable = True
        elif allow_bundled:
            profile_path = bundled_path
            source = "bundled-package"
            runtime_discoverable = False
        else:
            bundled_profile, bundled_errors = validate_profile(
                bundled_path,
                worker["expected_name"],
                worker["expected_model"],
                worker["expected_reasoning_effort"],
            )
            if bundled_errors:
                result["errors"].extend(
                    f"{worker_id}:{error}" for error in bundled_errors
                )
            elif bundled_profile is not None:
                result["errors"].append(
                    f"worker-profile-not-installed:{worker_id}:"
                    "run-install_worker_profiles.py"
                )
            continue

        profile, profile_errors = validate_profile(
            profile_path,
            worker["expected_name"],
            worker["expected_model"],
            worker["expected_reasoning_effort"],
        )
        if profile_errors:
            result["errors"].extend(
                f"{worker_id}:{error}" for error in profile_errors
            )
            continue

        result["workers"][worker_id] = {
            "source": source,
            "path": str(profile_path),
            "profile_name": profile["name"],
            "model": profile.get("model"),
            "model_reasoning_effort": profile.get("model_reasoning_effort"),
            "model_class": worker["model_class"],
            "required_runtime": worker["required_runtime"],
            "runtime_discoverable": runtime_discoverable,
            "model_availability": "not-checked-by-static-preflight",
        }

    result["allowed"] = (
        not result["errors"] and len(result["workers"]) == len(selected_ids)
    )
    result["summary"]["requested"] = selected_ids
    result["summary"]["resolved"] = sorted(result["workers"])
    result["summary"]["lane"] = lane
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve project or personal Codex custom-agent profiles."
    )
    parser.add_argument(
        "--skill-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--codex-home", type=Path, default=default_codex_home())
    parser.add_argument("--worker", action="append", dest="workers")
    parser.add_argument("--runtime", default="codex")
    parser.add_argument("--model-class")
    parser.add_argument("--lane")
    parser.add_argument(
        "--allow-bundled",
        action="store_true",
        help="Validate package assets even though Codex does not discover them there.",
    )
    args = parser.parse_args()

    result = check_profiles(
        skill_dir=args.skill_dir,
        repo_root=args.repo_root,
        codex_home=args.codex_home,
        requested_workers=args.workers,
        runtime=args.runtime,
        model_class=args.model_class,
        lane=args.lane,
        allow_bundled=args.allow_bundled,
    )
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
