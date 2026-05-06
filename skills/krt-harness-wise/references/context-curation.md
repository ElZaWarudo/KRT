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

## Project Intelligence

When broader project understanding would materially improve the handoff, include compact, task-relevant project intelligence. Keep it tied to the current task:

- **Task-relevant project map** - The entry points, layers, modules, commands, or tests the next agent should understand for this task.
- **Module map** - A focused relationship summary for a specific subsystem, not a whole-repo inventory.
- **Convention summary** - Observed naming, structure, testing, error-handling, dependency, or review patterns the next agent should follow.
- **Document map** - Which docs are current, stale, task-relevant, or useful only as historical background.
- **Persistent project artifact proposal** - A suggestion to create `docs/project-map.md`, `docs/conventions.md`, or another project knowledge document in a follow-up planning or work step when repeated future work would benefit.
- **Saved harness artifact proposal** - A suggested markdown coding harness path for a distinct task, work package, or agent handoff when persistence would reduce handoff loss or repeated discovery.
- **Saved harness artifact** - A markdown coding harness requested or confirmed by the user for a distinct task, work package, or agent handoff.

Do not generate persistent project artifacts by default. If the user asks for a saved map or conventions document, make the proposed path explicit and hand off actual file writing to a planning or work flow.

If persistence would help but the user did not ask for a file, propose a saved harness path using `harness-artifacts.md` and continue with the response-only harness. If the user explicitly asks for or confirms a saved harness file, write the harness artifact. Keep it grounded in inspected evidence and label unverified technical facts. Do not treat this as permission to write application code or general project documentation.

## Anti-Bloat Rules

- Do not ask the next agent to read directories without naming why.
- Do not include entire docs because they are nearby; classify them first.
- Do not add a whole-repo project map when a task-relevant map is enough.
- Do not include convention summaries that are generic or unverified; tie each convention to observed files, tests, or docs.
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

Separate inspected evidence from deferred verification. Do not present uninspected files, docs, generated harnesses, or inferred behavior as facts; label them as assumptions or verification targets.
