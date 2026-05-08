# KRT Repository Rules

These rules apply to work in this repository.

## Commands

- Prefix shell commands with `rtk` when possible.
- In command chains, prefix each segment: `rtk git status && rtk git diff`.
- Use raw commands only when debugging wrapper behavior or when `rtk` would hide required detail.

## Skill Naming

- Formal skill IDs must use lowercase hyphenated `krt-*` names.
- Skill folders must match the formal ID exactly: `skills/krt-example-name/`.
- Frontmatter `name` must match the folder name exactly.
- Runtime aliases may use `$krt:*`, but repo files should prefer canonical `krt-*` IDs.

## Autocomplete Metadata

- For any new or modified skill, `agents/openai.yaml` must expose the canonical ID in `display_name`.
- Use:

```yaml
interface:
  display_name: "krt-example-name"
```

- Do not use title-case names such as `"Example Name"` for `display_name`; autocomplete surfaces that field and should show the exact skill ID.
- Keep `default_prompt` using the same canonical ID: `Use krt-example-name ...`.

## Skill Structure

- Keep `SKILL.md` focused on core workflow and guardrails.
- Put reusable detail in `references/`.
- Do not add README, installation guides, changelogs, or other extra docs inside individual skill folders unless a runtime explicitly requires them.
- Prefer stable synthesized reference files over link-only literature lists. External sources may appear as a compact source basis, but the operational guidance should live in the repo.

## Compound Master Integration

- Compound Master coordinates other skills; it should not duplicate their full procedures.
- Optional specialist skills should not block the pipeline when missing. Resolve an equivalent skill if available; otherwise perform an inline fallback and record the degraded path.
- High-risk work packages should use Security Watch during execution and the Security Sentinel Gate after the work-review loop.
- CI is not polled in a loop by Compound Master. Prevent predictable CI failures before handoff; if CI breaks later, escalate to the CI investigation flow.

## Git Hygiene

- Do not commit directly to protected branches unless the user explicitly asks for `main` work.
- Prefer atomic commits by skill or concern.
- Do not add LLM attribution or co-author trailers.
- Do not revert unrelated user changes.

## Validation

- Validate new or changed skills with:

```bash
rtk python3 /home/teb/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/<skill-name>
```

- Run `rtk git diff --check` before committing documentation or skill changes.
- Sync edited skills to `/home/teb/.agents/skills/` when the user expects them to be immediately available:

```bash
rtk rsync -a skills/ /home/teb/.agents/skills/
```
