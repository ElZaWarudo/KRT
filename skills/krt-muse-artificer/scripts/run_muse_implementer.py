#!/usr/bin/env python3
"""Run Muse Code headlessly on one bounded implementation assignment.

The caller owns the worktree, review, verification, and release. This runner
only checks the boundary (paths, CLI flags, budgets), invokes `muse exec`, and
validates the terminal report Muse must write.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

MODEL = "muse-spark-1.3-contributor"
REQUIRED_FLAGS = (
    "--json", "--prompt-file", "--workspace", "--model",
    "--max-model-steps", "--approval-mode", "--user-input-auto-resolve",
    "--disable-web-tools", "--no-foreign-personal-context", "--trust-workspace",
)
STATUSES = {"done", "blocked", "needs_review"}
TERMINAL_SCHEMA = {
    "type": "object",
    "required": ["status", "summary", "changed_files", "checks", "blockers"],
    "properties": {
        "status": {"enum": sorted(STATUSES)},
        "summary": {"type": "string"},
        "changed_files": {"type": "array", "items": {"type": "string"}},
        "checks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["command", "result"],
                "properties": {
                    "command": {"type": "string"},
                    "result": {"enum": ["passed", "failed", "skipped"]},
                    "note": {"type": "string"},
                },
            },
        },
        "blockers": {"type": "array", "items": {"type": "string"}},
    },
}

PROMPT_HEADER = """You are a bounded implementation worker. The assignment below is authoritative.
Edit only the paths it allows. Do not stage, commit, switch branches, create
worktrees, push, or make any external change. Run only the checks it names.
Stop with status "blocked" when the work needs a decision or edits outside
your paths. Your report is a claim; the caller inspects the diff and reruns
checks before accepting anything.

When finished, write exactly one JSON object to {terminal_path} matching this
schema, and nothing else to that file:
{schema}

Assignment:
"""


def _inside(parent: Path, child: Path) -> bool:
    return child == parent or parent in child.parents


def validate_terminal(data: object) -> list[str]:
    """Return a list of problems with a terminal report; empty means valid."""
    if not isinstance(data, dict):
        return ["terminal must be a JSON object"]
    errors = [f"missing field: {k}" for k in TERMINAL_SCHEMA["required"] if k not in data]
    if errors:
        return errors
    if data["status"] not in STATUSES:
        errors.append(f"status must be one of {sorted(STATUSES)}")
    if not isinstance(data["summary"], str):
        errors.append("summary must be a string")
    for key in ("changed_files", "blockers"):
        if not isinstance(data[key], list) or not all(isinstance(x, str) for x in data[key]):
            errors.append(f"{key} must be a list of strings")
    checks = data["checks"]
    if not isinstance(checks, list):
        errors.append("checks must be a list")
    else:
        for i, check in enumerate(checks):
            if not isinstance(check, dict) or not isinstance(check.get("command"), str) \
                    or check.get("result") not in {"passed", "failed", "skipped"}:
                errors.append(f"checks[{i}] needs a command and a passed/failed/skipped result")
    if data["status"] == "blocked" and not data["blockers"]:
        errors.append("blocked status requires at least one blocker")
    return errors


def run_muse(
    *, assignment_path: Path, workspace: Path, terminal_path: Path, log_path: Path,
    max_model_steps: int = 50, timeout_seconds: int = 1800, muse_binary: str = "muse",
) -> dict[str, object]:
    assignment_path = assignment_path.resolve(strict=True)
    workspace = workspace.resolve(strict=True)
    terminal_path = terminal_path.resolve()
    log_path = log_path.resolve()
    if not workspace.is_dir() or not (workspace / ".git").exists():
        raise ValueError("workspace must be an existing Git worktree")
    for name, path in (("assignment", assignment_path), ("terminal_path", terminal_path),
                       ("log_path", log_path)):
        if _inside(workspace, path):
            raise ValueError(f"{name} must be outside the worker worktree")
    if terminal_path == log_path:
        raise ValueError("terminal_path and log_path must differ")
    if terminal_path.exists() or log_path.exists():
        raise ValueError("terminal_path and log_path must be fresh paths")
    if max_model_steps < 1 or timeout_seconds < 1:
        raise ValueError("max_model_steps and timeout_seconds must be positive")
    assignment = assignment_path.read_text(encoding="utf-8").strip()
    if not assignment:
        raise ValueError("assignment is empty")

    binary = shutil.which(muse_binary)
    if binary is None:
        raise ValueError(f"Muse executable unavailable: {muse_binary}")
    help_result = subprocess.run([binary, "exec", "--help"], capture_output=True, text=True, check=False)
    if help_result.returncode != 0 or any(flag not in help_result.stdout for flag in REQUIRED_FLAGS):
        raise ValueError("Muse CLI does not expose the required headless flags")

    prompt = PROMPT_HEADER.format(
        terminal_path=terminal_path, schema=json.dumps(TERMINAL_SCHEMA, indent=2)
    ) + assignment + "\n"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    terminal_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="muse-artificer-") as temporary:
        prompt_path = Path(temporary) / "prompt.md"
        prompt_path.write_text(prompt, encoding="utf-8")
        argv = [
            binary, "exec", "--json", "--prompt-file", str(prompt_path),
            "--workspace", str(workspace), "--model", MODEL,
            "--max-model-steps", str(max_model_steps),
            "--approval-mode", "never", "--user-input-auto-resolve",
            "--disable-web-tools", "--no-foreign-personal-context", "--trust-workspace",
        ]
        # The log can contain prompt and tool content, so keep it private.
        log_descriptor = os.open(log_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(log_descriptor, "w", encoding="utf-8") as log:
            try:
                result = subprocess.run(
                    argv, cwd=workspace, stdout=log, stderr=subprocess.PIPE,
                    text=True, timeout=timeout_seconds, check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError("Muse exceeded the elapsed budget") from exc
    if result.returncode != 0:
        raise RuntimeError(f"Muse exited {result.returncode}; inspect the private run log")
    if not terminal_path.is_file():
        raise RuntimeError("Muse returned without the required terminal artifact")
    try:
        terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Muse terminal artifact is not JSON: {exc}") from exc
    problems = validate_terminal(terminal)
    if problems:
        raise RuntimeError("Muse terminal artifact is invalid: " + "; ".join(problems))
    return {
        "model": MODEL,
        "status": terminal["status"],
        "terminal_path": str(terminal_path),
        "jsonl_log_path": str(log_path),
        "command_trust": "self-reported",
        "readiness": "requires-caller-diff-inspection-and-verification",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assignment", type=Path, required=True, help="assignment text file outside the worktree")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--terminal-path", type=Path, required=True)
    parser.add_argument("--log-path", type=Path, required=True)
    parser.add_argument("--max-model-steps", type=int, default=50)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--muse-binary", default="muse")
    args = parser.parse_args()
    try:
        result = run_muse(
            assignment_path=args.assignment, workspace=args.workspace,
            terminal_path=args.terminal_path, log_path=args.log_path,
            max_model_steps=args.max_model_steps, timeout_seconds=args.timeout_seconds,
            muse_binary=args.muse_binary,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
