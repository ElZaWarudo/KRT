# Skill Selection

Recommend skills that materially improve the next step. Do not list skills for decoration.

## Inventory Rules

- Use the visible skill inventory when the environment exposes it.
- If a skill is visible by name and description, it can be recommended without loading its body.
- Load a skill body only when the harness needs workflow details from that skill.
- If inventory is not visible, mark recommendations as unverified.
- Distinguish available skills from missing or desirable skills.

## Recommendation Categories

- **required** - The next step should use this skill to avoid missing core workflow or domain rules.
- **optional** - Useful if the task grows, but not needed for the first safe pass.
- **review-only** - Best used after implementation or after a document/harness draft exists.
- **missing** - No visible skill covers an important expertise gap.
- **unverified** - The skill may exist, but availability was not confirmed in the current context.

## Selection Heuristics

Recommend skills for:

- Frontend UI or design work.
- Skill creation or skill updates.
- Planning, brainstorming, or implementation workflows.
- Security, auth, data migrations, external APIs, payments, or compliance.
- Code review, document review, architecture review, performance review, or testing review.
- Repository research when local patterns are not obvious.
- Browser or visual verification when UI behavior matters.

Avoid recommending skills when:

- The task is small and the skill would add ceremony without reducing risk.
- The skill name is only loosely related.
- The recommendation duplicates the current skill's job.
- The recommendation is `$engineering-harness` itself. This skill prepares or reviews the harness; it must not be included as a recommended skill inside that harness.

## Output Format

Use this format in the harness:

```markdown
## Skills

**Recommended**
- `$skill-name` - required - [why it matters and when to use it]
- `$skill-name` - review-only - [what it should review later]

**Missing Or Desirable**
- `[skill-name-idea]` - missing - [gap it would cover]

**Unverified**
- `$possible-skill` - unverified - [why availability needs checking]
```

## Gap Analysis

Call out a missing skill when the task needs a repeatable workflow or specialized review that is not covered by visible skills. Good missing-skill proposals are specific:

- `database-migration-safety`
- `backward-compatibility-review`
- `prompt-rubric-versioning`
- `domain-boundary-detection`

Avoid vague proposals like `better-coding` or `general-review`.

## Confidence

Add a confidence label to skill recommendations when availability, relevance, or timing is uncertain.
