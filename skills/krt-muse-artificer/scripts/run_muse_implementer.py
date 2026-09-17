#!/usr/bin/env python3
"""Run Muse against a Seneschal worker contract without owning reconciliation."""

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


def run_muse(
    *, seneschal_skill_dir: Path, contract_path: Path, workspace: Path, terminal_path: Path,
    log_path: Path, max_model_steps: int, muse_binary: str = "muse",
) -> dict[str, object]:
    seneschal_skill_dir = seneschal_skill_dir.resolve(strict=True)
    seneschal_scripts = seneschal_skill_dir / "scripts"
    if not (seneschal_skill_dir / "SKILL.md").is_file() or not seneschal_scripts.is_dir():
        raise ValueError("seneschal_skill_dir must contain the installed Seneschal skill")
    sys.path.insert(0, str(seneschal_scripts))
    from render_worker_envelope import render_envelope
    from worker_contract import validate_contract

    contract_path = contract_path.resolve(strict=True)
    workspace = workspace.resolve(strict=True)
    terminal_path = terminal_path.resolve()
    log_path = log_path.resolve()
    if not workspace.is_dir() or not (workspace / ".git").exists():
        raise ValueError("workspace must be an existing Git worktree")
    if workspace == contract_path or workspace in contract_path.parents:
        raise ValueError("contract_path must be outside the worker worktree")
    if workspace == terminal_path or workspace in terminal_path.parents:
        raise ValueError("terminal_path must be outside the worker worktree")
    if workspace == log_path or workspace in log_path.parents:
        raise ValueError("log_path must be outside the worker worktree")
    if terminal_path == log_path:
        raise ValueError("terminal_path and log_path must differ")
    if terminal_path.exists() or log_path.exists():
        raise ValueError("terminal_path and log_path must be fresh paths")
    if max_model_steps < 1:
        raise ValueError("max_model_steps must be positive")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    validate_contract(contract)
    if contract["profile"] != "muse_contributor":
        raise ValueError("contract profile must be muse_contributor")
    if contract["lane"] not in {"fast", "standard"}:
        raise ValueError("Muse contributor is only admitted for fast or standard units")
    binary = shutil.which(muse_binary)
    if binary is None:
        raise ValueError(f"Muse executable unavailable: {muse_binary}")
    help_result = subprocess.run(
        [binary, "exec", "--help"], capture_output=True, text=True, check=False,
    )
    if help_result.returncode != 0 or any(
        flag not in help_result.stdout for flag in REQUIRED_FLAGS
    ):
        raise ValueError("Muse CLI does not expose the required headless flags")
    envelope = render_envelope(
        contract, contract_path=str(contract_path), terminal_path=str(terminal_path)
    )
    terminal_schema = (
        seneschal_skill_dir / "references" / "worker-terminal.schema.json"
    ).read_text(encoding="utf-8")
    prompt = (
        "You are the bounded Implementer for this Seneschal unit. "
        "The contract is authoritative. Edit only owned files. Do not stage, commit, "
        "switch branches, create worktrees, push, or perform external mutations. "
        "Stop and return blocked when a decision or scope extension is required. "
        "Run only contract commands and focused checks. Your report is a claim; "
        "Seneschal independently inspects the diff and verifies readiness.\n\n"
        + envelope["prompt"]
        + "\nTerminal JSON schema:\n"
        + terminal_schema
    )
    timeout_seconds = max(1, (contract["execution_budget"]["max_elapsed_ms"] + 999) // 1000)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    terminal_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="seneschal-muse-") as temporary:
        prompt_path = Path(temporary) / "prompt.md"
        prompt_path.write_text(prompt, encoding="utf-8")
        argv = [
            binary, "exec", "--json", "--prompt-file", str(prompt_path),
            "--workspace", str(workspace), "--model", MODEL,
            "--max-model-steps", str(max_model_steps),
            "--approval-mode", "never", "--user-input-auto-resolve",
            "--disable-web-tools", "--no-foreign-personal-context",
            "--trust-workspace",
        ]
        log_descriptor = os.open(log_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(log_descriptor, "w", encoding="utf-8") as log:
            try:
                result = subprocess.run(
                    argv, cwd=workspace, stdout=log, stderr=subprocess.PIPE,
                    text=True, timeout=timeout_seconds, check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError("Muse exceeded the contract elapsed budget") from exc
    if result.returncode != 0:
        raise RuntimeError(f"Muse exited {result.returncode}; inspect the private run log")
    if not terminal_path.is_file():
        raise RuntimeError("Muse returned without the required terminal artifact")
    validator = subprocess.run(
        ["rtk", "python3", str(seneschal_scripts / "validate_worker_terminal.py"),
         "--contract", str(contract_path), "--input", str(terminal_path)],
        cwd=workspace, capture_output=True, text=True, check=False,
    )
    if validator.returncode != 0:
        raise RuntimeError(f"Muse terminal artifact is invalid: {validator.stderr.strip()}")
    return {
        "contract_hash": contract["contract_hash"],
        "profile": contract["profile"],
        "model": MODEL,
        "terminal_path": str(terminal_path),
        "jsonl_log_path": str(log_path),
        "command_trust": "self-reported",
        "readiness": "requires-root-observation-and-verification",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seneschal-skill-dir", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--terminal-path", type=Path, required=True)
    parser.add_argument("--log-path", type=Path, required=True)
    parser.add_argument("--max-model-steps", type=int, default=50)
    parser.add_argument("--muse-binary", default="muse")
    args = parser.parse_args()
    try:
        result = run_muse(
            seneschal_skill_dir=args.seneschal_skill_dir,
            contract_path=args.contract, workspace=args.workspace,
            terminal_path=args.terminal_path, log_path=args.log_path,
            max_model_steps=args.max_model_steps, muse_binary=args.muse_binary,
        )
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
