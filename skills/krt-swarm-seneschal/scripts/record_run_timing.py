#!/usr/bin/env python3
"""Create or update compact, dependency-free Seneschal timing records."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

if os.name == "nt":
    import msvcrt
else:
    import fcntl


PHASES = (
    "preflight",
    "context",
    "discovery",
    "implementation",
    "verification",
    "review",
    "reconciliation",
)
SKILL_ROOT = Path(__file__).resolve().parents[1]
TERMINAL_STATUSES = {"completed", "blocked", "failed"}
CLOSEOUT_METRIC_DEFAULTS = {
    "discovery_implementation_ratio": None,
    "last_required_command_to_return_ms": None,
    "out_of_manifest_commands": 0,
    "repeated_context_reads": None,
    "root_interventions": 0,
    "time_to_first_change_ms": None,
}
CLOSEOUT_COUNT_FIELDS = set(CLOSEOUT_METRIC_DEFAULTS) - {
    "discovery_implementation_ratio"
}
SUPERVISION_ACTIONS = {
    "continue",
    "dispatch_implementation",
    "return_now",
    "complete",
    "contract_violation",
}
WORKER_TERMINAL_STATUSES = {
    "done",
    "done_with_baseline_gaps",
    "needs_review",
    "blocked",
}
SUPERVISION_REQUIRED_METRICS = set(CLOSEOUT_METRIC_DEFAULTS) - {
    "repeated_context_reads"
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_phase(value: str) -> tuple[str, int]:
    try:
        name, raw_duration = value.split("=", 1)
        duration = int(raw_duration)
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError("phase must use NAME=MILLISECONDS") from exc
    if name not in PHASES:
        raise argparse.ArgumentTypeError(
            f"unknown phase {name!r}; expected one of {', '.join(PHASES)}"
        )
    if duration < 0:
        raise argparse.ArgumentTypeError("phase duration must be non-negative")
    return name, duration


def supervision_metrics_for_status(
    document: Any, timing_status: str
) -> dict[str, Any]:
    if not isinstance(document, dict) or not isinstance(document.get("metrics"), dict):
        raise ValueError("supervision result must contain metrics object")
    action = document.get("action")
    terminal_status = document.get("terminal_status")
    reasons = document.get("reasons")
    if action not in SUPERVISION_ACTIONS:
        raise ValueError("supervision result contains invalid action")
    if action == "complete" and terminal_status is None:
        raise ValueError("complete supervision result requires terminal_status")
    if terminal_status is not None and terminal_status not in WORKER_TERMINAL_STATUSES:
        raise ValueError("supervision result contains invalid terminal_status")
    if not isinstance(reasons, list) or not all(
        isinstance(reason, str) for reason in reasons
    ):
        raise ValueError("supervision result reasons must be a list of strings")

    if action == "complete":
        compatible_status = (
            "completed"
            if terminal_status in {"done", "done_with_baseline_gaps"}
            else "blocked"
        )
    elif action == "contract_violation":
        compatible_status = "failed"
    else:
        compatible_status = "running"
    if timing_status != compatible_status:
        raise ValueError(
            f"supervision action {action} is incompatible with timing status "
            f"{timing_status}; expected {compatible_status}"
        )
    if action == "contract_violation" and not reasons:
        raise ValueError("contract_violation supervision result requires reasons")
    if action != "contract_violation" and reasons:
        raise ValueError("non-violation supervision result cannot contain reasons")
    metrics = document["metrics"]
    unknown_metrics = set(metrics) - set(CLOSEOUT_METRIC_DEFAULTS)
    missing_metrics = SUPERVISION_REQUIRED_METRICS - set(metrics)
    if unknown_metrics or missing_metrics:
        raise ValueError(
            "supervision result metrics are incompatible with the evaluator "
            f"schema; missing={sorted(missing_metrics)}, "
            f"unknown={sorted(unknown_metrics)}"
        )
    return metrics


def load_document(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"schema_version": 1, "records": []}
    if document.get("schema_version") != 1 or not isinstance(
        document.get("records"), list
    ):
        raise ValueError("timing document must use schema_version 1 and records[]")
    return document


def load_worker_route(skill_dir: Path, lane: str) -> tuple[str, str, str]:
    manifest_path = skill_dir / "assets" / "codex-workers" / "manifest.yaml"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    try:
        worker_id = manifest["lane_stages"][lane][-1]
        worker = manifest["workers"][worker_id]
        return (
            worker_id,
            worker["model_class"],
            worker["expected_reasoning_effort"],
        )
    except (KeyError, TypeError) as exc:
        raise ValueError(f"worker manifest cannot resolve lane {lane}") from exc


def write_atomic(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(document, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@contextmanager
def document_lock(path: Path) -> Iterator[None]:
    lock_root = Path(tempfile.gettempdir()) / "krt-seneschal-timing-locks"
    lock_root.mkdir(parents=True, exist_ok=True)
    lock_name = hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest()
    with (lock_root / f"{lock_name}.lock").open("a+b") as stream:
        if os.name == "nt":
            stream.seek(0, os.SEEK_END)
            if stream.tell() == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)
        else:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == "nt":
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def record_timing(
    *,
    output: Path,
    run_id: str,
    wave_id: str,
    unit_id: str,
    lane: str,
    worker_profile: str,
    phases: dict[str, int],
    context_bytes: int | None,
    verification_fingerprint: str | None,
    review_rounds: int | None,
    fix_rounds: int | None,
    status: str,
    closeout_metrics: dict[str, int | float | None] | None = None,
    captured_at: str | None = None,
    skill_dir: Path = SKILL_ROOT,
) -> dict[str, Any]:
    expected_profile, model_class, reasoning_effort = load_worker_route(
        skill_dir, lane
    )
    if worker_profile != expected_profile:
        raise ValueError(
            f"lane {lane} requires worker {expected_profile}, received {worker_profile}"
        )
    supplied_closeout_metrics = dict(closeout_metrics or {})
    unknown_metrics = sorted(
        set(supplied_closeout_metrics) - set(CLOSEOUT_METRIC_DEFAULTS)
    )
    if unknown_metrics:
        raise ValueError(f"unknown closeout metrics: {unknown_metrics}")
    supplied_counts = tuple(
        value
        for value in (context_bytes, review_rounds, fix_rounds)
        if value is not None
    )
    if any(value < 0 for value in supplied_counts):
        raise ValueError("byte and round counts must be non-negative")
    for field in CLOSEOUT_COUNT_FIELDS:
        value = supplied_closeout_metrics.get(field)
        if value is not None and (
            isinstance(value, bool) or not isinstance(value, int) or value < 0
        ):
            raise ValueError(f"{field} must be a non-negative integer")
    supplied_ratio = supplied_closeout_metrics.get(
        "discovery_implementation_ratio"
    )
    if supplied_ratio is not None and (
        isinstance(supplied_ratio, bool)
        or not isinstance(supplied_ratio, (int, float))
        or supplied_ratio < 0
    ):
        raise ValueError("discovery/implementation ratio must be non-negative")
    unknown_phases = sorted(set(phases) - set(PHASES))
    if unknown_phases or any(value < 0 for value in phases.values()):
        raise ValueError(f"invalid phase durations: {unknown_phases or phases}")

    with document_lock(output):
        document = load_document(output)
        key = (run_id, wave_id, unit_id)
        existing_index = next(
            (
                index
                for index, item in enumerate(document["records"])
                if (item.get("run_id"), item.get("wave_id"), item.get("unit_id"))
                == key
            ),
            None,
        )
        existing = (
            document["records"][existing_index]
            if existing_index is not None
            else None
        )
        if (
            existing
            and existing.get("status") in TERMINAL_STATUSES
            and status != existing["status"]
        ):
            raise ValueError("terminal timing status cannot transition")

        def retained(field: str, supplied: Any, default: Any) -> Any:
            if supplied is not None:
                return supplied
            return existing.get(field, default) if existing else default

        merged_phases = (
            dict(existing.get("phase_duration_ms", {})) if existing else {}
        )
        merged_phases.update(phases)
        implementation_ms = merged_phases.get("implementation", 0)
        discovery_ms = merged_phases.get("discovery", 0)
        calculated_discovery_implementation_ratio = (
            round(discovery_ms / implementation_ms, 3)
            if implementation_ms
            else None
        )
        record = {
            "captured_at": captured_at or utc_now(),
            "context_bytes": retained("context_bytes", context_bytes, 0),
            "discovery_implementation_ratio": (
                calculated_discovery_implementation_ratio
                if calculated_discovery_implementation_ratio is not None
                else retained(
                    "discovery_implementation_ratio",
                    supplied_ratio,
                    None,
                )
            ),
            "fix_rounds": retained("fix_rounds", fix_rounds, 0),
            "lane": lane,
            "last_required_command_to_return_ms": retained(
                "last_required_command_to_return_ms",
                supplied_closeout_metrics.get(
                    "last_required_command_to_return_ms"
                ),
                None,
            ),
            "model_class": model_class,
            "out_of_manifest_commands": retained(
                "out_of_manifest_commands",
                supplied_closeout_metrics.get("out_of_manifest_commands"),
                0,
            ),
            "phase_duration_ms": merged_phases,
            "reasoning_effort": reasoning_effort,
            "review_rounds": retained("review_rounds", review_rounds, 0),
            "repeated_context_reads": retained(
                "repeated_context_reads",
                supplied_closeout_metrics.get("repeated_context_reads"),
                None,
            ),
            "root_interventions": retained(
                "root_interventions",
                supplied_closeout_metrics.get("root_interventions"),
                0,
            ),
            "run_id": run_id,
            "status": status,
            "time_to_first_change_ms": retained(
                "time_to_first_change_ms",
                supplied_closeout_metrics.get("time_to_first_change_ms"),
                None,
            ),
            "total_duration_ms": sum(merged_phases.values()),
            "unit_id": unit_id,
            "verification_fingerprint": retained(
                "verification_fingerprint", verification_fingerprint, None
            ),
            "wave_id": wave_id,
            "worker_profile": worker_profile,
        }
        if existing is None:
            document["records"].append(record)
            document["records"].sort(
                key=lambda item: (item["run_id"], item["wave_id"], item["unit_id"])
            )
        else:
            existing.clear()
            existing.update(record)
        write_atomic(output, document)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--wave-id", required=True)
    parser.add_argument("--unit-id", required=True)
    parser.add_argument("--lane", required=True)
    parser.add_argument("--worker-profile", required=True)
    parser.add_argument("--skill-dir", type=Path, default=SKILL_ROOT)
    parser.add_argument("--phase", action="append", type=parse_phase, default=[])
    parser.add_argument("--context-bytes", type=int)
    parser.add_argument("--verification-fingerprint")
    parser.add_argument("--review-rounds", type=int)
    parser.add_argument("--fix-rounds", type=int)
    parser.add_argument("--time-to-first-change-ms", type=int)
    parser.add_argument("--out-of-manifest-commands", type=int)
    parser.add_argument("--last-required-command-to-return-ms", type=int)
    parser.add_argument("--root-interventions", type=int)
    parser.add_argument("--repeated-context-reads", type=int)
    parser.add_argument("--discovery-implementation-ratio", type=float)
    parser.add_argument("--supervision-result", type=Path)
    parser.add_argument(
        "--status",
        choices=("planned", "running", "completed", "blocked", "failed"),
        required=True,
    )
    parser.add_argument("--captured-at")
    args = parser.parse_args()
    try:
        supervision_metrics: dict[str, Any] = {}
        if args.supervision_result:
            supervision_document = json.loads(
                args.supervision_result.read_text(encoding="utf-8")
            )
            supervision_metrics = supervision_metrics_for_status(
                supervision_document, args.status
            )

        direct_metrics = {
            "discovery_implementation_ratio": (
                args.discovery_implementation_ratio
            ),
            "last_required_command_to_return_ms": (
                args.last_required_command_to_return_ms
            ),
            "out_of_manifest_commands": args.out_of_manifest_commands,
            "repeated_context_reads": args.repeated_context_reads,
            "root_interventions": args.root_interventions,
            "time_to_first_change_ms": args.time_to_first_change_ms,
        }
        closeout_metrics: dict[str, Any] = {}
        for field, direct in direct_metrics.items():
            supervised = supervision_metrics.get(field)
            if direct is not None and supervised is not None:
                raise ValueError(
                    f"{field} supplied directly and by supervision result"
                )
            value = direct if direct is not None else supervised
            if value is not None:
                closeout_metrics[field] = value

        record = record_timing(
            output=args.output,
            run_id=args.run_id,
            wave_id=args.wave_id,
            unit_id=args.unit_id,
            lane=args.lane,
            worker_profile=args.worker_profile,
            phases=dict(args.phase),
            context_bytes=args.context_bytes,
            verification_fingerprint=args.verification_fingerprint,
            review_rounds=args.review_rounds,
            fix_rounds=args.fix_rounds,
            closeout_metrics=closeout_metrics,
            status=args.status,
            captured_at=args.captured_at,
            skill_dir=args.skill_dir,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    json.dump(record, fp=sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
