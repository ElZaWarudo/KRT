#!/usr/bin/env python3
"""Export a baseline-bound worker delta and content-addressed patch manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from capture_worker_observation import observe_diff
from deterministic_artifacts import canonical_sha256, write_atomic
from deterministic_validation import exact_object, load_object, non_empty_string, string_list


METADATA_FIELDS = {
    "workspace_id",
    "worker_id",
    "unit_id",
    "role",
    "base_revision",
    "baseline_tree",
    "dependency_patch_hashes",
    "owned_paths",
    "contract_hash",
}


def _run_patch(repo_root: Path, *args: str, accepted_codes: set[int]) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode not in accepted_codes:
        raise ValueError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def export_worker_patch(repo_root: Path, metadata: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    exact_object(metadata, METADATA_FIELDS, "patch metadata")
    owned_paths = sorted(string_list(metadata["owned_paths"], "owned_paths", unique=True))
    base_revision = non_empty_string(metadata["base_revision"], "base_revision")
    baseline_tree = non_empty_string(metadata["baseline_tree"], "baseline_tree")
    dependency_hashes = sorted(string_list(metadata["dependency_patch_hashes"], "dependency_patch_hashes", unique=True))
    observation = observe_diff(repo_root, base_revision, baseline_tree)
    unowned = sorted(set(observation["changed_files"]) - set(owned_paths))
    if unowned:
        raise ValueError(f"worker changed unowned paths: {unowned}")

    patch = _run_patch(
        repo_root,
        "diff",
        "--binary",
        "--full-index",
        "--no-ext-diff",
        "--",
        accepted_codes={0},
    )
    untracked = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "--others", "--exclude-standard", "-z"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.split(b"\0")
    for raw_path in sorted(path for path in untracked if path):
        relative = raw_path.decode("utf-8")
        patch += _run_patch(
            repo_root,
            "diff",
            "--no-index",
            "--binary",
            "--full-index",
            "--",
            "/dev/null",
            relative,
            accepted_codes={0, 1},
        )

    changed_entries = []
    for relative in observation["changed_files"]:
        path = repo_root / relative
        if path.is_file():
            digest = f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"
        else:
            digest = "deleted"
        changed_entries.append({"path": relative, "digest": digest})
    patch_hash = f"sha256:{hashlib.sha256(patch).hexdigest()}"
    manifest_payload = {
        "schema_version": 1,
        "workspace_id": non_empty_string(metadata["workspace_id"], "workspace_id"),
        "worker_id": non_empty_string(metadata["worker_id"], "worker_id"),
        "unit_id": non_empty_string(metadata["unit_id"], "unit_id"),
        "role": non_empty_string(metadata["role"], "role"),
        "base_revision": base_revision,
        "baseline_tree": baseline_tree,
        "baseline_digest": observation["baseline_digest"],
        "dependency_patch_hashes": dependency_hashes,
        "owned_paths": owned_paths,
        "changed_files": changed_entries,
        "contract_hash": non_empty_string(metadata["contract_hash"], "contract_hash"),
        "diff_digest": observation["diff_digest"],
        "patch_sha256": patch_hash,
    }
    return patch, {**manifest_payload, "manifest_hash": canonical_sha256(manifest_payload)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--patch-output", type=Path, required=True)
    parser.add_argument("--manifest-output", type=Path, required=True)
    args = parser.parse_args()
    try:
        repo_root = args.repo_root.resolve()
        patch, manifest = export_worker_patch(repo_root, load_object(args.metadata))
        for output in (args.patch_output.resolve(), args.manifest_output.resolve()):
            try:
                output.relative_to(repo_root)
            except ValueError:
                continue
            raise ValueError("patch and manifest outputs must be outside repo_root")
        args.patch_output.parent.mkdir(parents=True, exist_ok=True)
        args.patch_output.write_bytes(patch)
        write_atomic(args.manifest_output, manifest)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    json.dump(manifest, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
