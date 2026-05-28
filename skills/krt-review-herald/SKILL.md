---
name: krt-review-herald
description: Triage pull request review feedback, plan response work, apply approved fixes when requested, verify the result, and draft clear reviewer replies. Use when a user asks to address PR comments, summarize review feedback, resolve GitHub review threads, prepare reply text, decide which comments are blocking, apply fixes from review comments, or turn review feedback into commits and responses. Runtime aliases may expose this as krt:review-herald.
---

# Review Herald

Review Herald carries PR feedback from noise to resolution: gather every thread, classify intent, decide what needs code versus explanation, apply or plan fixes, verify the result, and draft concise replies that help reviewers re-review quickly.

It does not push, create PRs, request reviewers, or transition Jira unless another release skill explicitly owns that step.

## Load References

- Load `references/response-rubric.md` before classifying comments or drafting replies.
- Load `references/thread-lifecycle.md` when working through multiple threads, stale comments, or "fix everything" requests.
- Load `references/fix-policy.md` before editing code for review feedback.
- Load `references/commit-guidance.md` before proposing commit groups or commit titles for review feedback fixes.
- Load `references/github-operations.md` when reading from or writing to GitHub through `gh`, REST, GraphQL, or a connector/plugin fallback.
- Load `references/source-literature.md` when explaining the communication model or when the user asks what the workflow is based on.

## Workflow

### Step 1 - Gather Feedback

Collect review context from the source the user provides:

- PR URL/number via `gh` when available;
- pasted review comments;
- local review finding docs;
- current diff and branch when needed to assess validity.

Prefer `gh` for GitHub reads and writes before connector/plugin APIs. Prefer structured sources such as review threads, requested changes, unresolved status, check failures, and file paths. If GitHub access is unavailable, work from pasted comments and say what could not be verified.

### Step 2 - Classify Threads

For each comment/thread, classify:

- **Blocking fix:** correctness, security, data, contract, test, build, or requested-change blocker.
- **Valid improvement:** should be fixed if low/medium cost and aligned with scope.
- **Nit batch:** optional cleanup; batch only if cheap and local.
- **Clarification needed:** reviewer intent is unclear; ask or draft a clarifying reply.
- **Discuss/decline:** valid concern but current approach is justified by tradeoffs.
- **Already addressed:** code or later comment resolves it.
- **Stale or invalid:** comment no longer applies or rests on a false premise.

Do not treat every comment as a task. Preserve reviewer intent and project standards.

### Step 3 - Build A Response Plan

Return or execute a plan depending on the user's request:

- If the user asks for analysis only, produce a response plan.
- If the user asks to resolve comments, implement safe fixes, run targeted verification when practical, and draft replies.
- If a comment would change product scope, public API, migration behavior, auth, data semantics, or release risk, ask before changing it.

For each thread, preserve the decision record: classification, action, changed files, verification, reply draft, and whether remote action is still pending. Group fixes into coherent commits or leave them unstaged for `krt-gitflow-knight`, according to the user's requested workflow. Use review-aware commit titles when proposing those groups.

### Step 4 - Apply Fixes And Verify

Apply the smallest code, test, or documentation change that resolves the reviewer concern. When several comments point to one root cause, fix the root cause and link each thread to that same decision.

Run targeted verification before drafting final replies when practical. If verification is skipped, record the reason and residual risk.

If CI failures are part of the feedback and the cause is not obvious from the review thread, hand diagnosis to `krt-ci-questor` or produce an inline CI triage fallback.

### Step 5 - Draft Replies

Use this reply shape:

```text
<what changed or decision made>. <where to look, if useful>. <verification or follow-up, if relevant>.
```

Examples:

- `Fixed by preserving the tenant filter in the query builder and added coverage for the empty-result case.`
- `Good catch. I kept the public response shape unchanged and moved the new metadata behind the internal serializer.`
- `I think the current approach is safer because it preserves rollback behavior; are you asking for the stricter validation even if it rejects legacy records?`

Keep replies short. Do not argue. When disagreeing, explain tradeoffs and ask whether the reviewer is optimizing for a different constraint.

### Step 6 - Closeout

Return:

```text
Review status: ready for re-review | fixes pending | blocked

Threads:
- [status] [file/thread] summary
  Action: fixed/replied/needs user/declined/already addressed/stale
  Files: <paths changed or none>
  Reply: <draft reply when useful>

Verification:
- <commands/results or skipped reason>

Remote actions:
- <comments/replies/thread resolutions/re-review requests still requiring approval, or none>

Next action:
- <exact next step>
```

## Guardrails

- Do not respond in anger or defensiveness. Convert rough feedback into the constructive technical question underneath.
- Prefer changing code over explaining confusing code when a reviewer did not understand it.
- Do not resolve a thread as addressed unless code, tests, docs, or a clear reply actually address it.
- Do not bury unresolved blockers under a general "done" comment.
- Do not notify reviewers, push commits, or mutate remote PR state without explicit approval or an enclosing release workflow.
- Do not blindly accept review comments. Validate the premise against code, tests, product constraints, and project standards before changing behavior.
