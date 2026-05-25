# Context Budget

Load when deciding what evidence belongs in a harness.

## Priority Order

1. Project/agent initialization rules.
2. Requirements, plans, ADRs, specs, or task-relevant docs.
3. Narrow source/test evidence needed to avoid misleading the next agent.
4. Historical docs only when they explain why current guidance changed.

## Buckets

- `Read First`: must read before planning or coding.
- `Summarize`: useful context but too broad to paste or read fully.
- `Inspect If Needed`: conditional implementation evidence.
- `Ignore For Now`: nearby but out of scope.

For `krt-document-forge` evidence, classify sanitized summaries as `Read First` and generated sources as `Inspect If Needed`. Do not promote raw/sources evidence to `Read First` unless no summary exists and the harness will remain local-only or be sanitized before versioning.

Every item must answer why it matters for this task.

## Anti-Bloat Rules

- Prefer doc headings, indexes, and targeted search before full reads.
- Avoid whole-repo maps.
- Avoid generic convention summaries unless grounded in inspected evidence.
- Keep task-relevant docs summarized; do not dump long documents into the harness.
- Do not include raw client/commercial evidence, source document hashes, exact budgets, personal contact details, or named RACI/escalation paths in versionable harnesses.
- If a fact is not verified, mark it as deferred verification rather than hiding uncertainty.
