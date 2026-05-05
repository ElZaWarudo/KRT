---
name: krt:harness-wise
description: Build or review a compact, architecture-aware coding harness before implementation. Use when a user asks to prepare a coding agent before work, map task-relevant project structure, summarize repository conventions, curate context, reduce token waste, select relevant skills, review an existing harness, audit skill coverage, trim documentation context, or avoid premature coding on feature, bugfix, refactor, migration, integration, testing, documentation, security, or architecture work.
---

# Harness Wise

Build the harness before coding. A harness is a compact operational brief that tells a coding agent what the task is, what context matters, which project patterns and skills apply, what risks exist, what not to do, and how to proceed safely.

This skill prepares or reviews that harness. It does not implement application changes.

## Core Rule

Do not code while using this skill. If the user asks for implementation, first produce the harness or review the existing harness, then hand off to the appropriate planning or work flow.

Do not claim or imply that this skill is included in the model's startup context, system prompt, default behavior, or always-on environment. Treat it as an explicitly invoked workflow only.

Do not add this skill itself to any generated or reviewed harness. The harness may recommend other task-relevant skills, but it must not instruct the next agent to use `$krt:harness-wise`, mention that this skill generated the harness, or embed this skill as part of the handoff.

## Workflow

1. Interpret the user's task and classify the task type.
2. Select the mode: quick, deep, bugfix, feature, refactor, skill-audit, harness-review, or docs-trim.
3. Scan the repository lightly before reading large files.
4. Curate source files, tests, documentation, and ignored context.
5. Extract observable project patterns and architecture guardrails.
6. Surface task-relevant project intelligence when it materially improves the handoff: module maps, conventions, document maps, or reusable context gaps.
7. Recommend relevant skills and identify missing skills.
8. Estimate impact and risks.
9. Ask one blocking question only when product or scope ambiguity would make the harness misleading.
10. Emit the Coding Harness or Existing Harness Review.

## Execution Rules

- Treat current code and tests as stronger sources of truth than old docs or comments.
- Prefer structure, names, exports, public interfaces, nearby tests, and short targeted reads before opening large files.
- If a technical fact is not verified, label it as an assumption or deferred verification item.
- If product behavior, scope, or success criteria are unclear, ask one focused question before producing the final harness.
- If the user provides an existing harness, switch to `harness-review` and evaluate it before generating a replacement.
- Include project maps, convention summaries, or persistent artifact proposals only when they reduce risk or make repeated handoffs materially easier.
- Do not write files such as `docs/project-map.md`, `docs/conventions.md`, or saved harness documents while using this skill. If the user explicitly asks for persistent artifacts, propose the paths and hand off to planning or work execution.

## Final Output

For new harnesses, load `references/harness-template.md` and fill only task-relevant sections. The final output should be compact enough to guide the next agent without becoming a second repository dump.

For classification-heavy work, load `references/task-classification.md`, `references/modes.md`, and `references/impact-estimation.md` before deciding scan depth.

For documentation-heavy, uncertain, or project-intelligence work, load `references/context-curation.md`, `references/document-classification.md`, and `references/confidence-rubric.md` before finalizing context recommendations.

For skill-heavy work, load `references/skill-selection.md` and separate available, missing, review-only, and unverified recommendations.

For existing harnesses, load `references/harness-review.md` and return review findings before suggesting a patch or regeneration.

## References

Load only the references needed for the selected mode:

- `references/harness-template.md` - final Coding Harness output structure.
- `references/task-classification.md` - task type and scope classification.
- `references/modes.md` - mode selection and mode-specific behavior.
- `references/impact-estimation.md` - impact matrix and risk surfaces.
- `references/context-curation.md` - context budget and source selection rules.
- `references/document-classification.md` - documentation labels and freshness checks.
- `references/confidence-rubric.md` - confidence labels and source-of-truth ranking.
- `references/skill-selection.md` - skill recommendation and gap analysis.
- `references/harness-review.md` - review mode for an existing harness.
- `references/validation-scenarios.md` - forward-test prompts and expected qualities.

## Output Discipline

Keep the output task-specific. Omit irrelevant sections in quick mode, but do not omit source-of-truth ranking, confidence on material conclusions, blocking questions, or validation guidance when they affect safe execution.
