#!/usr/bin/env python3
"""Append immutable audit events for autonomous mutations."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


GENESIS = "GENESIS"


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def event_hash(event: dict[str, Any]) -> str:
    payload = {key: value for key, value in event.items() if key != "event_hash"}
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def latest_hash(audit_dir: Path) -> str:
    head = audit_dir / "HEAD"
    if head.exists():
        value = head.read_text(encoding="utf-8").strip()
        if value:
            return value
    return GENESIS


def verify_head(audit_dir: Path) -> list[str]:
    current = latest_hash(audit_dir)
    events_dir = audit_dir / "events"
    if current == GENESIS:
        return [] if not events_dir.exists() or not any(events_dir.glob("*.json")) else ["audit-head-genesis-with-events"]
    if not events_dir.exists():
        return ["audit-head-without-events"]
    for event_path in events_dir.glob("*.json"):
        try:
            event = json.loads(event_path.read_text(encoding="utf-8"))
        except Exception as exc:
            return [f"audit-event-unreadable:{event_path.name}:{exc}"]
        if event.get("event_hash") == current:
            if event_hash(event) != current:
                return [f"audit-event-hash-mismatch:{event_path.name}"]
            return []
    return ["audit-head-event-missing"]


def append_event(audit_dir: Path, event: dict[str, Any]) -> dict[str, Any]:
    audit_dir.mkdir(parents=True, exist_ok=True)
    events_dir = audit_dir / "events"
    events_dir.mkdir(exist_ok=True)
    chain_errors = verify_head(audit_dir)
    if chain_errors:
        raise RuntimeError(";".join(chain_errors))

    enriched = dict(event)
    enriched.setdefault("timestamp", dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"))
    enriched["previous_event_hash"] = latest_hash(audit_dir)
    enriched["event_hash"] = event_hash(enriched)

    stage = str(enriched.get("stage", "event")).replace("/", "-")
    filename = f"{enriched['timestamp'].replace(':', '').replace('.', '')}-{stage}-{enriched['event_hash'][:12]}.json"
    target = events_dir / filename

    fd, tmp_name = tempfile.mkstemp(prefix=".audit-", suffix=".json", dir=str(events_dir))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            json.dump(enriched, tmp, sort_keys=True, indent=2)
            tmp.write("\n")
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, target)
        head_tmp = audit_dir / ".HEAD.tmp"
        head_tmp.write_text(f"{enriched['event_hash']}\n", encoding="utf-8")
        os.replace(head_tmp, audit_dir / "HEAD")
    finally:
        tmp_path = Path(tmp_name)
        if tmp_path.exists():
            tmp_path.unlink()

    return {"event_path": str(target), "event_hash": enriched["event_hash"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit_dir")
    parser.add_argument("--event-file", required=True)
    args = parser.parse_args()

    event = json.loads(Path(args.event_file).read_text(encoding="utf-8"))
    result = append_event(Path(args.audit_dir), event)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
