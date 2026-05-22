# Create Harness

Load when no existing harness should be diagnosed first.

## Inputs

Use these sources in order:

1. User task or explicit harness target.
2. Agent initialization context from `agent-initialization-context.md`.
3. Project documentation that directly shapes the task.
4. Narrow task-relevant repository evidence.

Do not scan the entire source tree by default. If the task needs implementation detail, point the next agent to the bounded files or symbols to inspect instead of embedding broad code context in the harness.

## Write Behavior

Harness files are versionable by default. Use:

```text
docs/harnesses/<task-slug>.md
```

Write the harness without another confirmation when:

- The task objective is clear.
- No likely existing harness should be patched first.
- The path is obvious and versionable.
- Confidence is medium or high.

Ask one question when the task, scope, or file target is ambiguous. Use local-only output only when the user explicitly requests a temporary or untracked harness.

## Required Content

Use the structure in `harness-schema.md`. Keep the harness compact and operational:

- Objective and task boundary.
- Source-of-truth ranking.
- Agent initialization summary.
- Context plan with read/summarize/inspect/ignore buckets.
- Guardrails and non-goals.
- Risks and deferred verification.
- Validation expectations.
- Agent-ready instructions.

## Creation Discipline

- Include initialization constraints even when they are only "none found".
- Mark unverified technical claims as deferred verification.
- Do not include implementation code, exact shell choreography, or broad repo maps.
- Do not recommend `krt-harness-wise` inside the harness.
- If a later planning/work skill is appropriate, mention it as a next step outside the harness or in agent-ready instructions only when task-relevant.

## Final Checks

After writing, run `check_harness.py` when available and report any warnings/errors. Errors should be fixed before marking the harness `ready`.
