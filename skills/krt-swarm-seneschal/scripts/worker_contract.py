#!/usr/bin/env python3
"""Validate and hash executable Seneschal worker contracts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import shlex
from typing import Any


SCHEMA_VERSION = 1
TERMINAL_VALIDATOR = str(
    Path(__file__).with_name("validate_worker_terminal.py").resolve()
)


def terminal_validation_argv(contract_path: str, terminal_path: str) -> list[str]:
    return [
        "rtk", "python3", TERMINAL_VALIDATOR,
        "--contract", contract_path, "--input", terminal_path,
    ]


def terminal_validation_command(contract_path: str, terminal_path: str) -> str:
    return shlex.join(terminal_validation_argv(contract_path, terminal_path))


def is_terminal_validation_argv(argv: list[str]) -> bool:
    return (
        len(argv) == 7
        and argv[:3] == ["rtk", "python3", TERMINAL_VALIDATOR]
        and argv[3] == "--contract"
        and bool(argv[4])
        and argv[5] == "--input"
        and bool(argv[6])
    )


def _lane_profiles() -> dict[str, str]:
    manifest_path = Path(__file__).resolve().parents[1] / "assets" / "codex-workers" / "manifest.yaml"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    stages = manifest.get("lane_stages")
    if not isinstance(stages, dict) or set(stages) != {"fast", "standard", "deep"}:
        raise RuntimeError("worker manifest lane_stages is invalid")
    workers = manifest.get("workers")
    if not isinstance(workers, dict):
        raise RuntimeError("worker manifest workers is invalid")
    result: dict[str, str] = {}
    for lane, worker_ids in stages.items():
        if (
            not isinstance(worker_ids, list)
            or not worker_ids
            or not all(isinstance(worker_id, str) and worker_id in workers for worker_id in worker_ids)
        ):
            raise RuntimeError(f"worker manifest stage is invalid: {lane}")
        result[lane] = worker_ids[-1]
    return result


LANE_PROFILE = _lane_profiles()
CERTIFICATIONS = {"reviewer", "security-sentinel"}
COMMAND_TRUST = {"self-reported": 0, "runtime-audited": 1}
PACKAGE_MANIFESTS = {
    "bundle": "Gemfile",
    "cargo": "Cargo.toml",
    "npm": "package.json",
    "npx": "package.json",
    "pnpm": "package.json",
    "yarn": "package.json",
}
TOP_LEVEL_FIELDS = {
    "schema_version",
    "contract_id",
    "unit_id",
    "lane",
    "profile",
    "objective",
    "owned_files",
    "required_context",
    "closed_decisions",
    "forbidden_changes",
    "acceptance_criteria",
    "commands",
    "execution_budget",
    "supervision",
    "terminal_protocol",
    "terminal_schema",
    "required_certifications",
    "evidence_policy",
    "contract_hash",
}


def canonical_payload(contract: dict[str, Any]) -> bytes:
    unsigned = {key: value for key, value in contract.items() if key != "contract_hash"}
    return json.dumps(
        unsigned, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def contract_hash(contract: dict[str, Any]) -> str:
    return f"sha256:{hashlib.sha256(canonical_payload(contract)).hexdigest()}"


def _non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    result = [_non_empty_string(item, field) for item in value]
    if len(result) != len(set(result)):
        raise ValueError(f"{field} must not contain duplicates")
    return result


def _path_list(value: Any, field: str) -> list[str]:
    paths = _string_list(value, field)
    for path in paths:
        candidate = PurePosixPath(path)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"{field} must contain repo-relative paths")
    return paths


def _exact_fields(value: Any, expected: set[str], field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    missing = expected - set(value)
    extra = set(value) - expected
    if missing or extra:
        raise ValueError(
            f"{field} fields invalid; missing={sorted(missing)}, extra={sorted(extra)}"
        )
    return value


def _non_negative_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"{field} must be a non-negative integer")
    return value


def _command_argv(command: str) -> list[str]:
    try:
        argv = shlex.split(command)
    except ValueError as exc:
        raise ValueError(f"command is not valid shell syntax: {command}") from exc
    if len(argv) < 2 or argv[0] != "rtk":
        raise ValueError(f"contract commands must start with rtk: {command}")
    if any(token in {"&&", "||", ";", "|", "cd"} for token in argv):
        raise ValueError(
            f"contract commands must not change cwd or chain commands: {command}"
        )
    return argv


def _package_context(argv: list[str], repo_root: Path) -> tuple[Path, str] | None:
    tool = argv[1]
    manifest = PACKAGE_MANIFESTS.get(tool)
    if manifest is None:
        return None
    context = repo_root
    options = {
        "npm": ("--prefix",),
        "npx": ("--prefix",),
        "pnpm": ("--dir", "-C"),
        "yarn": ("--cwd",),
    }.get(tool, ())
    for option in options:
        if option in argv:
            index = argv.index(option)
            if index + 1 >= len(argv):
                raise ValueError(f"{option} requires a path")
            context = repo_root / argv[index + 1]
            break
    if tool == "cargo" and "--manifest-path" in argv:
        index = argv.index("--manifest-path")
        if index + 1 >= len(argv):
            raise ValueError("--manifest-path requires a path")
        manifest_path = repo_root / argv[index + 1]
        return manifest_path.parent, manifest_path.name
    return context, manifest


def _path_tokens(argv: list[str]) -> list[str]:
    result: list[str] = []
    for token in argv[2:]:
        candidate = (
            token.split("=", 1)[1]
            if token.startswith("--") and "=" in token
            else token
        )
        if candidate.startswith("-") or "://" in candidate:
            continue
        if "/" in candidate or candidate.startswith("."):
            result.append(candidate)
    return result


def preflight_contract_commands(
    contract: dict[str, Any], *, repo_root: Path
) -> dict[str, Any]:
    """Validate command cwd assumptions without executing contract commands."""
    validate_contract(contract)
    root = repo_root.resolve()
    if not root.is_dir():
        raise ValueError("repo_root must be an existing directory")
    commands = contract["commands"]
    command_groups = {
        "exact": commands["exact"],
        "focused": commands["verification"]["focused"],
        "natural": commands["verification"]["natural"],
    }
    checked = 0
    for group, values in command_groups.items():
        for command in values:
            argv = _command_argv(command)
            package_context = _package_context(argv, root)
            if package_context is not None:
                context, manifest = package_context
                if not (context / manifest).is_file():
                    raise ValueError(
                        f"{group} command has no {manifest} in its resolved cwd "
                        f"{context}: {command}"
                    )
            if group in {"focused", "natural"}:
                for token in _path_tokens(argv):
                    candidate = Path(token)
                    resolved = (
                        candidate if candidate.is_absolute() else root / candidate
                    )
                    if not resolved.exists():
                        raise ValueError(
                            f"{group} command path does not exist from repo_root: "
                            f"{token} ({command})"
                        )
            checked += 1
    for prefix in commands["read_only_prefixes"]:
        argv = _command_argv(prefix)
        for token in _path_tokens(argv):
            candidate = Path(token)
            resolved = candidate if candidate.is_absolute() else root / candidate
            if not resolved.exists():
                raise ValueError(
                    "read-only command path does not exist from repo_root: "
                    f"{token} ({prefix})"
                )
        checked += 1
    return {"commands_checked": checked, "repo_root": str(root)}


def validate_contract(
    contract: dict[str, Any], *, require_hash: bool = True
) -> dict[str, Any]:
    expected_fields = TOP_LEVEL_FIELDS if require_hash else TOP_LEVEL_FIELDS - {"contract_hash"}
    _exact_fields(contract, expected_fields, "contract")
    if contract.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    for field in ("contract_id", "unit_id", "objective"):
        _non_empty_string(contract.get(field), field)
    lane = contract.get("lane")
    if lane not in LANE_PROFILE:
        raise ValueError("lane must be fast, standard, or deep")
    if contract.get("profile") != LANE_PROFILE[lane]:
        raise ValueError(f"lane {lane} requires profile {LANE_PROFILE[lane]}")
    _path_list(contract.get("owned_files"), "owned_files")
    _path_list(contract.get("required_context"), "required_context")
    _string_list(contract.get("closed_decisions"), "closed_decisions")
    _string_list(contract.get("forbidden_changes"), "forbidden_changes")

    criteria = contract.get("acceptance_criteria")
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("acceptance_criteria must be a non-empty list")
    criterion_ids: list[str] = []
    for index, criterion in enumerate(criteria):
        _exact_fields(criterion, {"id", "description"}, f"acceptance_criteria[{index}]")
        criterion_ids.append(_non_empty_string(criterion.get("id"), "criterion id"))
        _non_empty_string(criterion.get("description"), "criterion description")
    if len(criterion_ids) != len(set(criterion_ids)):
        raise ValueError("acceptance criterion ids must be unique")

    commands = _exact_fields(
        contract.get("commands"), {"exact", "read_only_prefixes", "verification"}, "commands"
    )
    exact = _string_list(commands.get("exact"), "commands.exact")
    read_only_prefixes = _string_list(
        commands.get("read_only_prefixes"), "commands.read_only_prefixes"
    )
    if any(len(prefix.split()) < 2 or prefix in {"rtk proxy", "rtk summary"} for prefix in read_only_prefixes):
        raise ValueError("read_only_prefixes must name a narrow read-only command")
    verification = _exact_fields(
        commands.get("verification"),
        {"focused", "natural", "max_retries_per_command"},
        "commands.verification",
    )
    focused = _string_list(verification.get("focused"), "verification.focused")
    natural = _string_list(verification.get("natural"), "verification.natural")
    if len(focused + natural + exact) != len(set(focused + natural + exact)):
        raise ValueError("exact and verification commands must be globally unique")
    _non_negative_int(
        verification.get("max_retries_per_command"), "max_retries_per_command"
    )

    budget = _exact_fields(
        contract.get("execution_budget"),
        {
            "discovery_passes",
            "implementation_rounds",
            "fix_rounds",
            "review_rounds",
            "extra_verification",
        },
        "execution_budget",
    )
    if budget.get("extra_verification") != "forbidden":
        raise ValueError("execution_budget.extra_verification must be forbidden")
    for field, value in budget.items():
        if field == "extra_verification":
            continue
        _non_negative_int(value, f"execution_budget.{field}")

    supervision = _exact_fields(
        contract.get("supervision"), {"mode", "transition_after_ms"}, "supervision"
    )
    expected_mode = "discovery-checkpoint" if lane == "deep" else "terminal-only"
    if supervision.get("mode") != expected_mode:
        raise ValueError(f"lane {lane} requires supervision mode {expected_mode}")
    _non_negative_int(supervision.get("transition_after_ms"), "transition_after_ms")
    terminal = _exact_fields(
        contract.get("terminal_protocol"),
        {"return_when", "grace_actions"},
        "terminal_protocol",
    )
    _string_list(terminal.get("return_when"), "terminal_protocol.return_when")
    if terminal.get("grace_actions") != 0:
        raise ValueError("terminal_protocol.grace_actions must be 0")
    if contract.get("terminal_schema") != "worker-terminal-v1":
        raise ValueError("terminal_schema must be worker-terminal-v1")

    certifications = _string_list(
        contract.get("required_certifications"), "required_certifications"
    )
    if any(role not in CERTIFICATIONS for role in certifications):
        raise ValueError("required_certifications contains an unsupported role")
    policy = _exact_fields(
        contract.get("evidence_policy"),
        {"minimum_command_trust", "changed_files_source"},
        "evidence_policy",
    )
    if policy.get("minimum_command_trust") not in COMMAND_TRUST:
        raise ValueError("minimum_command_trust is invalid")
    if policy.get("changed_files_source") != "root-diff":
        raise ValueError("changed_files_source must be root-diff")
    if require_hash:
        expected_hash = contract_hash(contract)
        if contract.get("contract_hash") != expected_hash:
            raise ValueError("contract_hash does not match canonical contract content")
    return contract


def materialize_contract(draft: dict[str, Any]) -> dict[str, Any]:
    validate_contract(draft, require_hash=False)
    result = dict(draft)
    result["contract_hash"] = contract_hash(result)
    validate_contract(result)
    return result
