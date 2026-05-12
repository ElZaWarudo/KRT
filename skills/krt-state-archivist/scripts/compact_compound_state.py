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


def extract_signals(lines: list[str], limit: int = 42) -> list[str]:
    patterns = [
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
    matches: list[str] = []
    for line in lines:
        stripped = line.strip()
        lowered = stripped.lower()
        if stripped.startswith("-") and any(pattern in lowered for pattern in patterns):
            matches.append(stripped)

    deduped: list[str] = []
    seen: set[str] = set()
    for item in matches:
        normalized = re.sub(r"\s+", " ", item.lower())
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(item)

    return deduped[-limit:]


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
    date_value = values.get("date") or dt.date.today().isoformat()
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
    blockers = section_body(first_section(sections, "Current Blockers"), limit=16)
    next_action = extract_next_action(first_section(sections, "Next Action"))
    branch_strategy = section_body(first_section(sections, "Branch Strategy"), limit=16)
    signals = extract_signals(all_lines)
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
    output.append(f"- Full archived state: `{repo_relative(archive_path)}`")
    output.append("- Agent review required: confirm active phase, blockers, branch/base, PR/Jira, and next action before resuming.")
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
        output.append("- Current blockers: not explicitly recorded; review the archive before resuming.")
    if branch_strategy:
        output.append("")
        output.append("Branch/base notes:")
        output.extend(branch_strategy)
    if next_action:
        output.append("")
        output.append("Next action:")
        output.extend(next_action)
    output.append("")

    output.append("## Active Signals To Review")
    if signals:
        output.extend(signals)
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
    output.append("- This compact state is a scaffold. The agent must curate it before using it as the only resume context.")
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

    signals = extract_signals(original_lines, limit=8)
    next_action = section_body(first_section(sections, "Next Action"), limit=4)
    if not args.allow_ambiguous and not signals and not next_action:
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
