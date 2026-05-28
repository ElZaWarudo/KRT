# Thread Lifecycle

Use this reference to turn PR review threads into an auditable resolution queue.

## Lifecycle

1. **Collect**: Capture reviewer, thread URL or ID, file path, line, original comment, current resolved state, review state, and any suggested change.
2. **Normalize**: Merge duplicate comments that point to the same root cause. Keep separate replies for separate threads.
3. **Validate**: Check whether the comment still applies to the current diff and whether the premise is technically true.
4. **Decide**: Choose exactly one action: fix, reply, clarify, decline, mark already addressed, mark stale, or block on user input.
5. **Implement**: Make the smallest scoped change that satisfies valid feedback.
6. **Verify**: Run targeted tests or checks that match the changed surface.
7. **Draft**: Prepare one concise reply per thread.
8. **Close**: Report local status and list remote actions that still need approval.

## Decision Record Shape

Use this shape internally and in closeout summaries:

```text
Thread: <id/url/path:line>
Reviewer: <name if known>
Classification: blocking_fix | valid_improvement | nit_batch | clarify | decline_with_rationale | already_addressed | stale_or_invalid
Decision: fix | reply | clarify | decline | already-addressed | stale | blocked
Rationale: <one sentence>
Files: <changed paths or none>
Verification: <command/result or skipped reason>
Reply: <draft reply or none>
Remote: <needs reply | needs resolve | no remote action | needs user approval>
```

## Stale And Resolved Threads

- Treat GitHub's resolved state as useful context, not proof that the underlying issue is fixed.
- If a thread is already resolved, verify whether a later commit or reply addressed it before ignoring it.
- If a comment points to removed or rewritten lines, classify it as stale only after checking whether the concern survives elsewhere.
- If a stale comment reveals a real underlying issue, fix the underlying issue and reply with that framing.

## Grouping

- Group by root cause, not by reviewer or file order.
- Keep blocking fixes ahead of nits.
- Batch cheap nits only when they do not obscure the main correction.
- Avoid broad refactors unless the reviewer concern cannot be solved locally.

## Closeout Status

- `ready for re-review`: no known blockers remain, fixes are verified or verification gaps are explicit.
- `fixes pending`: valid feedback remains but is not yet implemented.
- `blocked`: user decision, missing credentials, unclear reviewer intent, or risky scope change prevents completion.
