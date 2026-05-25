#!/usr/bin/env python3
"""Create one approved commit with deterministic staging and env-leak guards."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ENV_GUARD = SCRIPT_DIR / "ensure_krt_env_ignore.py"
ALLOWED_TYPES = {"feat", "fix", "docs", "test", "chore", "refactor", "perf", "build", "ci"}
SECRET_ENV_PATHS = {".krt/env/jira-scribe.env"}
SECRET_ASSIGNMENT = re.compile(
    r"^\+\s*([A-Z][A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|CREDENTIAL|PRIVATE_KEY|API_KEY|ACCESS_KEY|AUTH_KEY)[A-Z0-9_]*)=(.+)$"
)
COMMIT_RE = re.compile(r"^([a-z]+)(\([a-z0-9-]+\))?: [^\s].{1,70}$")
FORBIDDEN_MESSAGE_PATTERNS = [
    re.compile(r"Co-authored-by:", re.IGNORECASE),
    re.compile(r"\b(?:codex|claude|chatgpt|llm)\b", re.IGNORECASE),
    re.compile(r"\bRDM-\d+\b"),
    re.compile(r"\bU\d+\b"),
]
PLACEHOLDER_VALUES = {"", '""', "''", "replace-with-token", "example", "changeme", "todo"}


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def emit(ok: bool, **payload: object) -> int:
    print(json.dumps({"ok": ok, **payload}, sort_keys=True))
    return 0 if ok else 1


def normalize_paths(paths: list[str]) -> list[str]:
    normalized = sorted(dict.fromkeys(path.strip().strip("/") for path in paths if path.strip()))
    return normalized


def validate_message(message: str) -> list[str]:
    reasons: list[str] = []
    if "\n" in message or "\r" in message:
        reasons.append("commit-message-must-be-one-line")
    match = COMMIT_RE.match(message)
    if not match:
        reasons.append("commit-message-format")
    elif match.group(1) not in ALLOWED_TYPES:
        reasons.append(f"commit-message-type:{match.group(1)}")
    if message.endswith("."):
        reasons.append("commit-message-trailing-period")
    for pattern in FORBIDDEN_MESSAGE_PATTERNS:
        if pattern.search(message):
            reasons.append(f"commit-message-forbidden-pattern:{pattern.pattern}")
    return reasons


def staged_paths(root: Path) -> list[str]:
    completed = git(root, "diff", "--cached", "--name-only")
    return sorted(path for path in completed.stdout.splitlines() if path)


def clear_index(root: Path) -> subprocess.CompletedProcess[str]:
    head = git(root, "rev-parse", "--verify", "HEAD")
    if head.returncode == 0:
        return git(root, "restore", "--staged", "--", ":/")
    return git(root, "rm", "--cached", "-r", "--ignore-unmatch", ".")


def scan_staged_diff(root: Path) -> list[str]:
    reasons: list[str] = []
    diff = git(root, "diff", "--cached", "--name-only").stdout.splitlines()
    for path in diff:
        if path in SECRET_ENV_PATHS:
            reasons.append(f"secret-env-path-staged:{path}")
        if path.startswith(".krt/env/") and path.endswith(".env"):
            reasons.append(f"secret-env-path-staged:{path}")
        if Path(path).name.startswith(".env") and not path.endswith(".example"):
            reasons.append(f"project-env-file-staged:{path}")

    patch = git(root, "diff", "--cached", "--unified=0").stdout.splitlines()
    for line in patch:
        if not line.startswith("+") or line.startswith("+++"):
            continue
        match = SECRET_ASSIGNMENT.match(line)
        if not match:
            continue
        name, value = match.groups()
        cleaned = value.strip().strip('"').strip("'")
        if cleaned.lower() not in PLACEHOLDER_VALUES:
            reasons.append(f"secret-like-env-assignment:{name}")
    return reasons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--message", required=True)
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument(
        "--reset-index-approved",
        action="store_true",
        help="Allow clearing existing staged changes before staging approved paths.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    paths = normalize_paths(args.path)
    if not paths:
        return emit(False, block_reasons=["no-paths-provided"])

    if not root.exists() or not root.is_dir():
        return emit(False, block_reasons=["root-not-directory"])

    worktree = git(root, "rev-parse", "--show-toplevel")
    if worktree.returncode != 0:
        return emit(False, block_reasons=["not-a-git-worktree"])

    reasons = validate_message(args.message)
    initial_staged_paths = staged_paths(root)
    if initial_staged_paths and not args.reset_index_approved:
        return emit(
            False,
            block_reasons=["index-not-clean"],
            staged_paths=initial_staged_paths,
        )
    if initial_staged_paths and args.reset_index_approved:
        reset = clear_index(root)
        if reset.returncode != 0:
            return emit(
                False,
                block_reasons=["index-reset-failed"],
                staged_paths=initial_staged_paths,
                stderr=reset.stderr,
            )

    guard = subprocess.run(
        [sys.executable, str(ENV_GUARD), "--root", str(root)],
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        guard_result = json.loads(guard.stdout)
    except json.JSONDecodeError:
        guard_result = {"ok": False, "block_reasons": ["env-guard-output-not-json"]}
    if guard.returncode != 0 or not guard_result.get("ok"):
        reasons.extend(str(reason) for reason in guard_result.get("block_reasons", ["env-guard-failed"]))

    for path in paths:
        if path in SECRET_ENV_PATHS or (path.startswith(".krt/env/") and path.endswith(".env")):
            reasons.append(f"secret-env-path-planned:{path}")
        if Path(path).name.startswith(".env") and not path.endswith(".example"):
            reasons.append(f"project-env-file-planned:{path}")

    if reasons:
        return emit(False, block_reasons=sorted(set(reasons)))

    add = git(root, "add", "--", *paths)
    if add.returncode != 0:
        return emit(False, block_reasons=["git-add-failed"], stderr=add.stderr)

    actual_paths = staged_paths(root)
    if actual_paths != paths:
        return emit(
            False,
            block_reasons=["staged-paths-mismatch"],
            expected_paths=paths,
            actual_paths=actual_paths,
        )

    leak_reasons = scan_staged_diff(root)
    if leak_reasons:
        return emit(False, block_reasons=sorted(set(leak_reasons)), staged_paths=actual_paths)

    commit = git(root, "commit", "-m", args.message)
    if commit.returncode != 0:
        return emit(False, block_reasons=["git-commit-failed"], stderr=commit.stderr)

    return emit(
        True,
        message=args.message,
        committed_paths=actual_paths,
        reset_index=bool(initial_staged_paths and args.reset_index_approved),
        previous_staged_count=len(initial_staged_paths),
        stdout=commit.stdout,
    )


if __name__ == "__main__":
    sys.exit(main())
