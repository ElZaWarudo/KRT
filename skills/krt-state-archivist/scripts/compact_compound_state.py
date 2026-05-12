#!/usr/bin/env python3
"""Compact Compound Master state while preserving a full archive snapshot."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


DEFAULT_ARCHIVE_DIR = Path("docs/orchestration/archive/compound-master-state")
DEFAULT_MAX_LINES = 160


@dataclass
class Section:
    heading: str
    level: int
    lines: list[str]
    start_line: int

    @property
    def line_count(self) -> int:
        return len(self.lines)


@dataclass
class StateSignals:
    latest_phase: int | None
    next_action: list[str]
    active_signals: list[str]
    signal_phases: list[int]
    curation_warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a compact Compound Master state file and archive the full original."
    )
    parser.add_argument("--state", default="docs/orchestration/compound-master-state.md")
    parser.add_argument("--archive-dir", default=str(DEFAULT_ARCHIVE_DIR))
    parser.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="compact even when already below max-lines")
    parser.add_argument(
        "--allow-ambiguous",
        action="store_true",
        help="write a scaffold even when no next-action signal is found",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"State file not found: {path}")


def split_frontmatter(text: str) -> tuple[list[str], list[str]]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return [], lines

    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return lines[: idx + 1], lines[idx + 1 :]

    return [], lines


def parse_frontmatter_values(frontmatter: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in frontmatter[1:-1]:
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def parse_sections(body_lines: list[str]) -> list[Section]:
    sections: list[Section] = []
    current = Section("Preamble", 0, [], 1)

    for idx, line in enumerate(body_lines, start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match and len(match.group(1)) <= 2:
            if current.lines:
                sections.append(current)
            current = Section(match.group(2).strip(), len(match.group(1)), [line], idx)
        else:
            current.lines.append(line)

    if current.lines:
        sections.append(current)
    return sections


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "compound-master-state"


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def first_section(sections: list[Section], *names: str) -> Section | None:
    lowered = {name.lower() for name in names}
    for section in sections:
        if section.heading.lower() in lowered:
            return section
    return None


def section_body(section: Section | None, limit: int | None = None) -> list[str]:
    if section is None:
        return []
    body = section.lines[1:] if section.lines and section.lines[0].startswith("#") else section.lines
    body = [line.rstrip() for line in body if line.strip()]
    if limit is not None:
        return body[:limit]
    return body


def phase_numbers(text: str) -> list[int]:
    return [int(match) for match in re.findall(r"\b(?:phase|fase)\s+(\d+)\b", text, flags=re.IGNORECASE)]


def latest_phase_number(lines: list[str]) -> int | None:
    phases: list[int] = []
    for line in lines:
        phases.extend(phase_numbers(line))
    return max(phases) if phases else None


def latest_phase_window(lines: list[str], latest_phase: int | None) -> list[str]:
    if latest_phase is None:
        return lines

    labels = (f"phase {latest_phase}", f"fase {latest_phase}")
    indices = [
        idx
        for idx, line in enumerate(lines)
        if any(label in line.lower() for label in labels)
    ]
    if not indices:
        return lines

    start = min(indices)
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if re.match(r"^##\s+", lines[idx]):
            end = idx
            break

    return lines[start:end]


def signal_patterns() -> list[str]:
    return [
        "next required gate",
        "next action",
        "recommended next",
        "current blocker",
        "no technical blockers",
        "active branch",
        "branch status",
        "base-branch",
        "stacking update",
        "implementation status",
        "review status",
        "security gate",
        "ci break-prevention",
        "release status",
        "jira status",
        "pr status",
        "open pr",
        "blocked",
        "blocker",
        "required decision",
    ]


def extract_latest_next_action(lines: list[str], sections: list[Section], latest_phase: int | None) -> list[str]:
    next_patterns = ["next required gate", "next action", "recommended next"]
    phase_label = f"phase {latest_phase}" if latest_phase is not None else None
    fase_label = f"fase {latest_phase}" if latest_phase is not None else None

    fallback: str | None = None
    for line in reversed(lines):
        stripped = line.strip()
        lowered = stripped.lower()
        if not stripped:
            continue
        if any(pattern in lowered for pattern in next_patterns):
            if fallback is None:
                fallback = stripped
            if phase_label is None or phase_label in lowered or fase_label in lowered:
                return [stripped]

    if fallback:
        return [fallback]

    return extract_next_action(first_section(sections, "Next Action"))


def extract_signals(lines: list[str], latest_phase: int | None = None, limit: int = 24) -> tuple[list[str], list[int]]:
    patterns = [
        *signal_patterns(),
    ]
    phase_label = f"phase {latest_phase}" if latest_phase is not None else None
    fase_label = f"fase {latest_phase}" if latest_phase is not None else None

    preferred: list[str] = []
    fallback: list[str] = []
    for line in reversed(lines):
        stripped = line.strip()
        lowered = stripped.lower()
        if not stripped.startswith("-") or not any(pattern in lowered for pattern in patterns):
            continue

        phases = phase_numbers(stripped)
        has_other_phase = latest_phase is not None and phases and latest_phase not in phases
        has_latest_phase = phase_label is not None and (phase_label in lowered or fase_label in lowered)
        if has_latest_phase or not has_other_phase:
            preferred.append(stripped)
        else:
            fallback.append(stripped)

    deduped: list[str] = []
    seen: set[str] = set()
    signal_phases: set[int] = set()
    for item in preferred:
        normalized = re.sub(r"\s+", " ", item.lower())
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(item)
            signal_phases.update(phase_numbers(item))
        if len(deduped) >= limit:
            break

    if not deduped:
        for item in fallback:
            normalized = re.sub(r"\s+", " ", item.lower())
            if normalized not in seen:
                seen.add(normalized)
                deduped.append(item)
                signal_phases.update(phase_numbers(item))
            if len(deduped) >= limit:
                break

    deduped.reverse()
    return deduped, sorted(signal_phases)


def extract_required_decisions(lines: list[str], limit: int = 20) -> list[str]:
    patterns = ["required user decision", "decision needed", "ask before", "blocking question"]
    results = []
    for line in lines:
        stripped = line.strip()
        lowered = stripped.lower()
        if stripped.startswith("-") and any(pattern in lowered for pattern in patterns):
            results.append(stripped)
    return results[-limit:]


def extract_next_action(section: Section | None, limit: int = 8) -> list[str]:
    body = section_body(section)
    if not body:
        return []

    stop_patterns = [
        " decision recorded ",
        " brainstorm artifact created",
        " plan artifact created",
        " work package created",
        " inline document review",
        " inline package review",
    ]
    selected: list[str] = []
    for line in body:
        lowered = f" {line.lower()}"
        if selected and any(pattern in lowered for pattern in stop_patterns):
            break
        selected.append(line)
        if len(selected) >= limit:
            break
    return selected


def analyze_state(lines: list[str], sections: list[Section]) -> StateSignals:
    latest_phase = latest_phase_number(lines)
    next_action = extract_latest_next_action(lines, sections, latest_phase)
    active_source = latest_phase_window(lines, latest_phase)
    active_signals, signal_phases = extract_signals(active_source, latest_phase=latest_phase)

    warnings: list[str] = []
    if latest_phase is not None:
        warnings.append(f"Latest phase detected structurally: Phase {latest_phase}. Agent must confirm this is the real active phase.")
        if active_source == lines:
            warnings.append("Curation required: no bounded latest-phase window was found; active signals may include historical noise.")

    contradictory_phases = [phase for phase in signal_phases if latest_phase is None or phase != latest_phase]
    if contradictory_phases:
        labels = ", ".join(f"Phase {phase}" for phase in contradictory_phases)
        warnings.append(f"Curation required: extracted active signals still mention historical phases ({labels}).")

    if not next_action:
        warnings.append("Curation required: no next action was extracted.")

    if len(active_signals) > 18:
        warnings.append("Curation required: many active signals were extracted; trim historical noise before resuming.")

    return StateSignals(
        latest_phase=latest_phase,
        next_action=next_action,
        active_signals=active_signals,
        signal_phases=signal_phases,
        curation_warnings=warnings,
    )


def update_frontmatter(frontmatter: list[str], archive_path: Path) -> list[str]:
    today = dt.date.today().isoformat()
    if not frontmatter:
        return [
            "---",
            "title: Compound Master State",
            "status: in_progress",
            f"date: {today}",
            "state_format: compact",
            f"last_compacted: {today}",
            f"archive_snapshot: {repo_relative(archive_path)}",
            "---",
        ]

    extra = {
        "state_format": "compact",
        "last_compacted": today,
        "archive_snapshot": repo_relative(archive_path),
    }
    existing_keys = {
        line.split(":", 1)[0].strip()
        for line in frontmatter[1:-1]
        if ":" in line and not line.startswith(" ")
    }
    output = frontmatter[:-1]
    for key, value in extra.items():
        line = f"{key}: {value}"
        if key not in existing_keys:
            output.append(line)
    output.append("---")
    return output


def choose_archive_path(state_path: Path, archive_dir: Path, values: dict[str, str]) -> Path:
    date_value = dt.date.today().isoformat()
    initiative = values.get("initiative") or values.get("title") or state_path.stem
    base = archive_dir / f"{date_value}-{slugify(initiative)}-full-state.md"
    if not base.exists():
        return base

    for index in range(2, 1000):
        candidate = archive_dir / f"{date_value}-{slugify(initiative)}-full-state-{index}.md"
        if not candidate.exists():
            return candidate

    raise SystemExit("Could not choose a unique archive path")


def build_compact_state(
    frontmatter: list[str],
    values: dict[str, str],
    sections: list[Section],
    all_lines: list[str],
    archive_path: Path,
) -> str:
    title = values.get("title") or "Compound Master State"
    source_docs = section_body(first_section(sections, "Source Documents"), limit=32)
    state_signals = analyze_state(all_lines, sections)
    historical_sections_are_suspect = state_signals.latest_phase is not None
    blockers = [] if historical_sections_are_suspect else section_body(first_section(sections, "Current Blockers"), limit=16)
    branch_strategy = [] if historical_sections_are_suspect else section_body(first_section(sections, "Branch Strategy"), limit=16)
    decisions = extract_required_decisions(all_lines)

    output: list[str] = []
    output.extend(update_frontmatter(frontmatter, archive_path))
    output.append("")
    output.append(f"# {title}")
    output.append("")
    output.append("## Resume Snapshot")
    output.append(f"- Initiative: {values.get('initiative', 'not recorded')}")
    output.append(f"- Status: {values.get('status', 'not recorded')}")
    output.append(f"- Mode: {values.get('mode', 'not recorded')}")
    if state_signals.latest_phase is not None:
        output.append(f"- Latest phase detected by scaffold: Phase {state_signals.latest_phase}")
    output.append(f"- Full archived state: `{repo_relative(archive_path)}`")
    output.append("- CURATION REQUIRED: confirm active phase, blockers, branch/base, PR/Jira, and next action before resuming.")
    if state_signals.curation_warnings:
        output.append("- Curation warnings:")
        output.extend(f"  - {warning}" for warning in state_signals.curation_warnings)
    output.append("")

    output.append("## Source Documents")
    if source_docs:
        output.extend(source_docs)
    else:
        output.append("- Not recorded in the original state.")
    output.append("")

    output.append("## Current Operating State")
    if blockers:
        output.append("Current blockers:")
        output.extend(blockers)
    else:
        output.append("- Current blockers: not extracted from the latest-phase window; agent must confirm from archive and current repo state.")
    if branch_strategy:
        output.append("")
        output.append("Branch/base notes:")
        output.extend(branch_strategy)
    else:
        output.append("- Branch/base: not extracted from the latest-phase window; agent must refresh the receiving branch before continuing.")
    if state_signals.next_action:
        output.append("")
        output.append("Next action:")
        output.extend(state_signals.next_action)
    output.append("")

    output.append("## Active Signals To Review")
    if state_signals.active_signals:
        output.extend(state_signals.active_signals)
    else:
        output.append("- No active signal extracted; review the archive before resuming.")
    output.append("")

    output.append("## Required Decisions")
    if decisions:
        output.extend(decisions)
    else:
        output.append("- No explicit required user decisions extracted.")
    output.append("")

    output.append("## Archived History")
    output.append(f"- Full pre-compaction state: `{repo_relative(archive_path)}`")
    output.append("- Archived top-level sections:")
    for section in sections:
        if section.heading == "Preamble" and section.line_count <= 1:
            continue
        output.append(f"  - {section.heading} ({section.line_count} lines)")
    output.append("")

    output.append("## Archivist Notes")
    output.append("- CURATION REQUIRED: this compact state is a scaffold, not a final semantic summary.")
    output.append("- Prefer the latest phase and latest next-gate evidence; remove historical signals before resuming.")
    output.append("- Keep canonical details in linked brainstorm, plan, work-package, PR, Jira, and archive artifacts.")

    return "\n".join(output).rstrip() + "\n"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temp_name = handle.name
    Path(temp_name).replace(path)


def main() -> int:
    args = parse_args()
    state_path = Path(args.state)
    archive_dir = Path(args.archive_dir)
    original = read_text(state_path)
    original_lines = original.splitlines()
    frontmatter, body_lines = split_frontmatter(original)
    values = parse_frontmatter_values(frontmatter)
    sections = parse_sections(body_lines)
    archive_path = choose_archive_path(state_path, archive_dir, values)

    line_count = len(original_lines)
    if line_count <= args.max_lines and not args.force:
        print(f"already-compact state={state_path} lines={line_count} max_lines={args.max_lines}")
        return 0

    state_signals = analyze_state(original_lines, sections)
    if not args.allow_ambiguous and not state_signals.active_signals and not state_signals.next_action:
        print(
            "blocked ambiguous-state: no next-action or active resume signal found; "
            "rerun with --allow-ambiguous only after agent review",
            file=sys.stderr,
        )
        return 2

    compact = build_compact_state(frontmatter, values, sections, original_lines, archive_path)
    compact_lines = len(compact.splitlines())

    print(f"state={state_path}")
    print(f"original_lines={line_count}")
    print(f"compact_lines={compact_lines}")
    print(f"archive={archive_path}")
    print(f"sections={len(sections)}")
    if state_signals.latest_phase is not None:
        print(f"latest_phase=Phase {state_signals.latest_phase}")
    if state_signals.curation_warnings:
        print("curation_required=true")
        for warning in state_signals.curation_warnings:
            print(f"warning={warning}")

    if args.dry_run:
        print("dry_run=true")
        return 0

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    archive_path.write_text(original, encoding="utf-8")
    atomic_write(state_path, compact)
    print("status=compacted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
