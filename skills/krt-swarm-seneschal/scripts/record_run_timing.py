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
    "implementation",
    "verification",
    "review",
    "reconciliation",
)
SKILL_ROOT = Path(__file__).resolve().parents[1]
TERMINAL_STATUSES = {"completed", "blocked", "failed"}


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
        worker_id = manifest["lanes"][lane]
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
    supplied_counts = tuple(
        value
        for value in (context_bytes, review_rounds, fix_rounds)
        if value is not None
    )
    if any(value < 0 for value in supplied_counts):
        raise ValueError("byte and round counts must be non-negative")
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
        record = {
            "captured_at": captured_at or utc_now(),
            "context_bytes": retained("context_bytes", context_bytes, 0),
            "fix_rounds": retained("fix_rounds", fix_rounds, 0),
            "lane": lane,
            "model_class": model_class,
            "phase_duration_ms": merged_phases,
            "reasoning_effort": reasoning_effort,
            "review_rounds": retained("review_rounds", review_rounds, 0),
            "run_id": run_id,
            "status": status,
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
    parser.add_argument(
        "--status",
        choices=("planned", "running", "completed", "blocked", "failed"),
        required=True,
    )
    parser.add_argument("--captured-at")
    args = parser.parse_args()
    try:
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
