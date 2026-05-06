# Existing Harness Review

Use this mode when the user provides, references, or asks to improve an existing harness. Review the harness before generating a replacement.

## Inputs

An existing harness may arrive as:

- A file path.
- Pasted markdown.
- A prior assistant output.
- A request such as "review this harness", "improve the current harness", or "does this harness cover enough?"

If the referenced harness cannot be found, ask one targeted question for the correct path or pasted content.

## Review Contract

Compare the harness against these required areas:

- Objective and task interpretation.
- Task type, mode, and impact shape.
- Source-of-truth ranking.
- Context plan with read/summarize/inspect/ignore buckets.
- Bounded reading scope that avoids broad dumps unless justified by the task.
- Documentation classification and freshness.
- Project rules and architecture guardrails.
- Skill recommendations, missing skills, and unverified skills.
- Change impact estimate.
- Risks and mitigations.
- Blocking questions vs deferred technical verification.
- Separation between inspected evidence, inference, assumptions, and deferred checks.
- Execution plan and validation guidance.
- Validation boundaries, stop/ask conditions, and action guidance: summarize intended changes before sensitive action, but reserve human approval for destructive, external-system, or not-git-recoverable work.
- Agent-ready instructions.
- Confidence levels on material conclusions.

## Labels

- **Keep** - Correct and useful as written.
- **Revise** - Present but needs correction, sharpening, or better grounding.
- **Missing** - Required for this task but absent.
- **Overloaded** - Adds too much context, broad reading, or irrelevant material.
- **Risk** - Could lead the implementation agent toward unsafe, incompatible, or unverified work.
- **Stale/Verify** - Depends on old docs, assumptions, or contradictions that need checking.

## Output Format

```markdown
# Existing Harness Review

## Verdict
[Ready to use | Revise before coding | Regenerate recommended]

## Existing Harness Summary
[Compact operational summary of what the current harness tells the next agent to do, after accounting for findings.]

## Strong Sections
- [Keep] [section] - [why it works]

## Findings
| Severity | Label | Section | Issue | Recommendation |
|----------|-------|---------|-------|----------------|
| P1/P2/P3 | Missing/Revise/Overloaded/Risk/Stale/Verify | [section] | [specific problem] | [specific fix] |

## Recommended Patch
- [Minimal change that improves the harness]

## Regeneration Trigger
- [When the current harness is too weak and should be rebuilt from repo context]
```

## Severity

- **P1** - The harness is likely to mislead coding or miss a blocking scope/product issue.
- **P2** - The harness is usable but misses meaningful context, confidence, risk, skills, or validation.
- **P3** - Low-risk clarity, formatting, or compactness improvement.

## Regenerate Instead Of Patch

Recommend regeneration when:

- The objective is unclear or contradicts the user task.
- Context is mostly irrelevant or broad directory dumps.
- Source-of-truth ranking is absent and docs/code may conflict.
- It lacks enough sections that patching would be longer than rebuilding.
- It invents architecture or patterns not grounded in the repo.

## Review Discipline

Findings come before summary. Ground each finding in a harness section or missing section. Do not rewrite the harness silently unless the user asked for a patched version.
