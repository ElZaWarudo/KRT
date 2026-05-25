# Development

Edit skills in `skills/<name>/`. Keep reusable detail in `references/`, scripts in `scripts/`, runtime adapter metadata in `agents/`, and heavier reusable assets in `assets/`.

## Validate

Validate one changed skill:

```bash
rtk python3 /home/teb/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/<skill-name>
```

Validate all KRT skills:

```bash
rtk bash -lc 'for d in skills/krt-*; do rtk python3 /home/teb/.codex/skills/.system/skill-creator/scripts/quick_validate.py "$d" || exit 1; done'
```

Before committing docs or skill changes:

```bash
rtk git diff --check
```

Sync edited skills into the local runtime:

```bash
rtk rsync -a skills/ /home/teb/.agents/skills/
```

## Layout

```text
skills/
  krt-<skill-name>/
    SKILL.md
    agents/
    references/
    scripts/
    assets/
```

Not every skill needs every directory. Add only what the skill actually uses; empty armor is still weight.

## Metadata

- Formal skill IDs must use lowercase hyphenated `krt-*` names.
- Skill folders must match the formal ID exactly.
- `SKILL.md` frontmatter `name` must match the folder name.
- `agents/openai.yaml` should expose the canonical ID as `interface.display_name`.
- Keep `default_prompt` aligned with the canonical ID.

Runtime aliases such as `$krt:*` are allowed in user-facing examples, but repo files should prefer canonical `krt-*` IDs.
