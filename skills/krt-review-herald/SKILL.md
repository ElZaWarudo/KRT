---
name: krt-review-herald
description: Triage pull request review feedback, plan response work, apply approved fixes when requested, and draft clear reviewer replies. Use when a user asks to address PR comments, summarize review feedback, resolve GitHub review threads, prepare reply text, decide which comments are blocking, or turn review feedback into commits and responses. Runtime aliases may expose this as krt:review-herald.
---

# Review Herald

Review Herald carries PR feedback from noise to resolution: gather every thread, classify intent, decide what needs code versus explanation, apply or plan fixes, and draft concise replies that help reviewers re-review quickly.

It does not push, create PRs, request reviewers, or transition Jira unless another release skill explicitly owns that step.

## Load References

- Load `references/response-rubric.md` before classifying comments or drafting replies.
- Load `references/source-literature.md` when explaining the communication model or when the user asks what the workflow is based on.

## Workflow

### Step 1 - Gather Feedback

Collect review context from the source the user provides:

- PR URL/number via `gh` when available;
- pasted review comments;
- local review finding docs;
- current diff and branch when needed to assess validity.

Prefer structured sources such as review threads, requested changes, check failures, and file paths. If GitHub access is unavailable, work from pasted comments and say what could not be verified.

### Step 2 - Classify Threads

For each comment/thread, classify:

- **Blocking fix:** correctness, security, data, contract, test, build, or requested-change blocker.
- **Valid improvement:** should be fixed if low/medium cost and aligned with scope.
- **Clarification needed:** reviewer intent is unclear; ask or draft a clarifying reply.
- **Discuss/decline:** valid concern but current approach is justified by tradeoffs.
- **Nit/advisory:** optional cleanup; batch only if cheap.
- **Already addressed:** code or later comment resolves it.

Do not treat every comment as a task. Preserve reviewer intent and project standards.

### Step 3 - Build A Response Plan

Return or execute a plan depending on the user's request:

- If the user asks for analysis only, produce a response plan.
- If the user asks to resolve comments, implement safe fixes, run targeted verification when practical, and draft replies.
- If a comment would change product scope, public API, migration behavior, auth, data semantics, or release risk, ask before changing it.

Group fixes into coherent commits or leave them unstaged for `krt-gitflow-knight`, according to the user's requested workflow.

### Step 4 - Draft Replies

Use this reply shape:

```text
<what changed or decision made>. <where to look, if useful>. <verification or follow-up, if relevant>.
```

Examples:

- `Fixed by preserving the tenant filter in the query builder and added coverage for the empty-result case.`
- `Good catch. I kept the public response shape unchanged and moved the new metadata behind the internal serializer.`
- `I think the current approach is safer because it preserves rollback behavior; are you asking for the stricter validation even if it rejects legacy records?`

Keep replies short. Do not argue. When disagreeing, explain tradeoffs and ask whether the reviewer is optimizing for a different constraint.

### Step 5 - Closeout

Return:

```text
Review status: ready for re-review | fixes pending | blocked

Threads:
- [status] [file/thread] summary
  Action: fixed/replied/needs user/declined with rationale
  Reply: <draft reply when useful>

Verification:
- <commands/results or skipped reason>

Next action:
- <exact next step>
```

## Guardrails

- Do not respond in anger or defensiveness. Convert rough feedback into the constructive technical question underneath.
- Prefer changing code over explaining confusing code when a reviewer did not understand it.
- Do not resolve a thread as addressed unless code, tests, docs, or a clear reply actually address it.
- Do not bury unresolved blockers under a general "done" comment.
- Do not notify reviewers, push commits, or mutate remote PR state without explicit approval or an enclosing release workflow.
