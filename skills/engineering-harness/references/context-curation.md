# Context Curation

Curate context before reading deeply. The goal is to give the next agent enough signal without turning the harness into a repo dump.

## Scan Order

1. Read instruction files that govern the target area, such as `AGENTS.md`.
2. List top-level structure and likely entry points.
3. Search for task terms, symbols, routes, commands, models, and tests.
4. Inspect file names, exports, headings, public interfaces, and nearby tests.
5. Open full files only when they are directly relevant to the task.

## Context Buckets

- **Read First** - Required to understand or implement the task safely.
- **Summarize** - Relevant but too broad or long to include raw; summarize from the task angle.
- **Inspect If Needed** - Useful only if implementation reveals a dependency.
- **Ignore For Now** - Out of scope for this task; include the reason.

When existing project documents are present and plausibly related, actively look for summarization opportunities. Do not emphasize summarization over code, tests, risks, or skills, but do not leave the `Summarize` bucket empty just because the documents are not worth reading in full.

## Anti-Bloat Rules

- Do not ask the next agent to read directories without naming why.
- Do not include entire docs because they are nearby; classify them first.
- For relevant long, broad, or partially stale docs, prefer a task-specific summary over raw inclusion or silent omission.
- Prefer symbols, interfaces, tests, and examples over unrelated implementation bodies.
- If there are many similar files, pick representative examples and say why.
- If a file is large, inspect headings, exports, or search hits before reading all of it.

## Sparse Repo Behavior

When the repo has little or no source code:

- Produce a useful low-confidence harness anyway.
- State which conclusions are unknown.
- Recommend the first files or conventions to establish.
- Avoid inventing architecture that has not been observed.

## Output Guidance

Every context item should answer: "Why does the next agent need this for this task?"
