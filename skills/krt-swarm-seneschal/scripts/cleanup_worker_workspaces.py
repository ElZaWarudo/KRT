#!/usr/bin/env python3
"""Reconcile and safely remove cleanup-ready Seneschal worktrees."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from deterministic_validation import exact_object, load_object, non_empty_string
from record_run_timing import document_lock


REGISTRY_FIELDS = {"schema_version", "entries"}
ENTRY_FIELDS = {
    "workspace_id",
    "run_id",
    "path",
    "branch",
    "lifecycle_status",
    "preserve_for_diagnosis",
    "durable_artifacts",
}
ARTIFACT_FIELDS = {"path", "sha256"}
CLEANUP_READY = "cleanup-ready"
BRANCH_PREFIX = "seneschal/"
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


def _git(repo_root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _resolved(path: Path) -> Path:
    return Path(os.path.normcase(str(path.resolve())))


def _is_within(path: Path, parent: Path) -> bool:
    try:
        _resolved(path).relative_to(_resolved(parent))
    except ValueError:
        return False
    return True


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _worktrees(repo_root: Path) -> dict[Path, dict[str, Any]]:
    records: dict[Path, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    for line in _git(repo_root, "worktree", "list", "--porcelain").stdout.splitlines():
        if line.startswith("worktree "):
            path = _resolved(Path(line.removeprefix("worktree ")))
            current = {"path": path, "branch": None, "detached": False}
            records[path] = current
        elif current is not None and line.startswith("branch refs/heads/"):
            current["branch"] = line.removeprefix("branch refs/heads/")
        elif current is not None and line == "detached":
            current["detached"] = True
    return records


def _seneschal_branches(repo_root: Path) -> set[str]:
    output = _git(
        repo_root,
        "for-each-ref",
        "--format=%(refname:short)",
        "refs/heads/seneschal/",
    ).stdout
    return {line for line in output.splitlines() if line}


def _validate_registry(registry: dict[str, Any], worktree_parent: Path) -> list[dict[str, Any]]:
    exact_object(registry, REGISTRY_FIELDS, "cleanup registry")
    if registry["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    entries = registry["entries"]
    if not isinstance(entries, list):
        raise ValueError("entries must be a list")

    normalized: list[dict[str, Any]] = []
    workspace_ids: set[str] = set()
    paths: set[Path] = set()
    for index, raw in enumerate(entries):
        item = exact_object(raw, ENTRY_FIELDS, f"entries[{index}]")
        workspace_id = non_empty_string(item["workspace_id"], f"entries[{index}].workspace_id")
        run_id = non_empty_string(item["run_id"], f"entries[{index}].run_id")
        raw_path = Path(non_empty_string(item["path"], f"entries[{index}].path"))
        if not raw_path.is_absolute():
            raise ValueError(f"entries[{index}].path must be absolute")
        path = _resolved(raw_path)
        expected_parent = _resolved(worktree_parent / run_id)
        if not _is_within(path, expected_parent) or path == expected_parent:
            raise ValueError(f"entries[{index}].path must be a child of the run-specific worktree parent")
        if workspace_id in workspace_ids or path in paths:
            raise ValueError("workspace ids and paths must be unique")
        workspace_ids.add(workspace_id)
        paths.add(path)

        branch = item["branch"]
        if branch is not None:
            branch = non_empty_string(branch, f"entries[{index}].branch")
            if not branch.startswith(f"{BRANCH_PREFIX}{run_id}/"):
                raise ValueError(f"entries[{index}].branch must belong to its run namespace")
        lifecycle_status = non_empty_string(item["lifecycle_status"], f"entries[{index}].lifecycle_status")
        if not isinstance(item["preserve_for_diagnosis"], bool):
            raise ValueError(f"entries[{index}].preserve_for_diagnosis must be boolean")
        artifacts = item["durable_artifacts"]
        if not isinstance(artifacts, list):
            raise ValueError(f"entries[{index}].durable_artifacts must be a list")
        normalized_artifacts = []
        for artifact_index, raw_artifact in enumerate(artifacts):
            artifact = exact_object(raw_artifact, ARTIFACT_FIELDS, f"entries[{index}].durable_artifacts[{artifact_index}]")
            raw_artifact_path = Path(non_empty_string(artifact["path"], "artifact.path"))
            if not raw_artifact_path.is_absolute():
                raise ValueError("artifact.path must be absolute")
            artifact_path = _resolved(raw_artifact_path)
            expected_hash = non_empty_string(artifact["sha256"], "artifact.sha256")
            if not SHA256_PATTERN.fullmatch(expected_hash):
                raise ValueError("artifact.sha256 must be a canonical SHA-256 digest")
            if _is_within(artifact_path, path):
                raise ValueError("durable artifacts must be stored outside the disposable worktree")
            normalized_artifacts.append({"path": artifact_path, "sha256": expected_hash})
        if lifecycle_status == CLEANUP_READY and not normalized_artifacts:
            raise ValueError("cleanup-ready entries require at least one durable artifact")
        normalized.append({
            **item,
            "workspace_id": workspace_id,
            "run_id": run_id,
            "path": path,
            "branch": branch,
            "lifecycle_status": lifecycle_status,
            "durable_artifacts": normalized_artifacts,
        })
    return normalized


def reconcile_cleanup(
    *,
    repo_root: Path,
    worktree_parent: Path,
    registry: dict[str, Any],
    apply: bool,
) -> dict[str, Any]:
    if not repo_root.is_absolute():
        raise ValueError("repo_root must be absolute")
    if not worktree_parent.is_absolute():
        raise ValueError("worktree_parent must be absolute")
    repo_root = _resolved(repo_root)
    worktree_parent = _resolved(worktree_parent)
    if not repo_root.is_dir():
        raise ValueError("repo_root must be an existing directory")
    entries = _validate_registry(registry, worktree_parent)
    observed_worktrees = _worktrees(repo_root)
    observed_branches = _seneschal_branches(repo_root)
    registered_paths = {entry["path"] for entry in entries}
    registered_branches = {entry["branch"] for entry in entries if entry["branch"]}
    report: dict[str, Any] = {
        "mode": "apply" if apply else "dry-run",
        "removed": [],
        "already_removed": [],
        "would_remove": [],
        "retained": [],
        "errors": [],
        "unregistered_worktrees": sorted(
            str(path)
            for path in observed_worktrees
            if _is_within(path, worktree_parent) and path not in registered_paths
        ),
        "unregistered_branches": sorted(observed_branches - registered_branches),
    }

    for entry in entries:
        workspace_id = entry["workspace_id"]
        path = entry["path"]
        observed = observed_worktrees.get(path)
        branch_present = bool(entry["branch"] and entry["branch"] in observed_branches)
        reasons = []
        if entry["lifecycle_status"] != CLEANUP_READY:
            reasons.append(f"status={entry['lifecycle_status']}")
        if entry["preserve_for_diagnosis"]:
            reasons.append("preserve-for-diagnosis")
        if observed is None and path.exists():
            reasons.append("unregistered-path-exists")
        elif observed is not None and entry["branch"] != observed["branch"]:
            reasons.append("observed-branch-mismatch")
        for artifact in entry["durable_artifacts"]:
            artifact_path = artifact["path"]
            if not artifact_path.is_file():
                reasons.append(f"missing-artifact:{artifact_path}")
            elif _sha256(artifact_path) != artifact["sha256"]:
                reasons.append(f"artifact-hash-mismatch:{artifact_path}")
        if reasons:
            report["retained"].append({"workspace_id": workspace_id, "reasons": reasons})
            continue
        if observed is None and not branch_present:
            report["already_removed"].append(workspace_id)
            continue
        if not apply:
            report["would_remove"].append(workspace_id)
            continue

        if observed is not None:
            removal = _git(repo_root, "worktree", "remove", "--force", str(path), check=False)
            if removal.returncode != 0:
                report["errors"].append({"workspace_id": workspace_id, "operation": "worktree-remove", "error": removal.stderr.strip()})
                continue
        branch = entry["branch"]
        if branch_present:
            deletion = _git(repo_root, "branch", "-d", "--", branch, check=False)
            if deletion.returncode != 0:
                report["errors"].append({"workspace_id": workspace_id, "operation": "branch-delete", "error": deletion.stderr.strip()})
                continue
        report["removed"].append(workspace_id)

    if apply:
        _git(repo_root, "worktree", "prune")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--worktree-parent", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="remove eligible worktrees; default is a dry run")
    args = parser.parse_args()
    try:
        registry = load_object(args.registry)
        if args.apply:
            with document_lock(args.worktree_parent.resolve() / ".seneschal-cleanup"):
                result = reconcile_cleanup(
                    repo_root=args.repo_root,
                    worktree_parent=args.worktree_parent,
                    registry=registry,
                    apply=True,
                )
        else:
            result = reconcile_cleanup(
                repo_root=args.repo_root,
                worktree_parent=args.worktree_parent,
                registry=registry,
                apply=False,
            )
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
