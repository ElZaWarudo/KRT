#!/usr/bin/env python3
"""Validate KRT skill identity, metadata, and critical safety wiring."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def frontmatter_value(frontmatter: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", frontmatter)
    return match.group(1).strip("'\"") if match else None


def yaml_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s+{re.escape(key)}:\s*(.+?)\s*$", text)
    return match.group(1).strip("'\"") if match else None


def validate(repo_root: Path) -> dict:
    skills_root = repo_root / "skills"
    safety_index = repo_root / "docs" / "safety.md"
    if not skills_root.is_dir():
        raise ValueError(f"missing skills directory: {skills_root}")
    safety_text = (
        safety_index.read_text(encoding="utf-8") if safety_index.is_file() else ""
    )

    skills = sorted(
        path for path in skills_root.iterdir() if path.is_dir() and path.name.startswith("krt-")
    )
    errors: list[str] = []
    safety_critical: list[str] = []
    for skill in skills:
        skill_id = skill.name
        skill_md = skill / "SKILL.md"
        metadata = skill / "agents" / "openai.yaml"
        if not skill_md.is_file():
            errors.append(f"{skill_id}: missing SKILL.md")
            continue
        body = skill_md.read_text(encoding="utf-8")
        match = FRONTMATTER.search(body)
        if not match:
            errors.append(f"{skill_id}: missing YAML frontmatter")
        else:
            name = frontmatter_value(match.group(1), "name")
            description = frontmatter_value(match.group(1), "description")
            if name != skill_id:
                errors.append(
                    f"{skill_id}: frontmatter name must match folder (found {name!r})"
                )
            if not description:
                errors.append(f"{skill_id}: frontmatter description is required")

        if not metadata.is_file():
            errors.append(f"{skill_id}: missing agents/openai.yaml")
        else:
            yaml = metadata.read_text(encoding="utf-8")
            display_name = yaml_value(yaml, "display_name")
            default_prompt = yaml_value(yaml, "default_prompt")
            if display_name != skill_id:
                errors.append(
                    f"{skill_id}: display_name must equal canonical ID"
                )
            expected_prompt_prefix = f"Use {skill_id}"
            if not default_prompt or not default_prompt.startswith(
                expected_prompt_prefix
            ):
                errors.append(
                    f"{skill_id}: default_prompt must start with "
                    f"{expected_prompt_prefix!r}"
                )

        safety = skill / "references" / "safety.md"
        declares_safety = "references/safety.md" in body
        if safety.is_file():
            safety_critical.append(skill_id)
            if not declares_safety:
                errors.append(
                    f"{skill_id}: critical safety reference is not loaded by SKILL.md"
                )
            expected_path = f"skills/{skill_id}/references/safety.md"
            expected_row = f"| `{skill_id}` |"
            if expected_row not in safety_text or expected_path not in safety_text:
                errors.append(
                    f"{skill_id}: missing or invalid row in docs/safety.md"
                )
        elif declares_safety:
            errors.append(f"{skill_id}: loads missing references/safety.md")

    if errors:
        raise ValueError("\n".join(errors))
    return {
        "status": "valid",
        "skill_count": len(skills),
        "safety_critical_count": len(safety_critical),
        "safety_critical_skills": safety_critical,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv[1:])
    try:
        output = validate(args.repo_root.resolve())
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
