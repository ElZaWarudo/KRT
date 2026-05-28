# Fix Policy

Use this reference before editing code in response to PR review feedback.

## Fix Bias

- Prefer improving the code over writing long explanations when the reviewer misunderstood because the code was unclear.
- Prefer tests for behavior gaps, regressions, and contract concerns.
- Prefer documentation or PR description updates for rationale gaps.
- Prefer a clarifying reply when the requested tradeoff is ambiguous.
- Prefer declining with rationale when the request would harm product, security, data, or compatibility constraints.

## Change Scope

Safe to apply without extra approval when the fix:

- preserves public API, persistence semantics, authorization, tenant/data boundaries, and release behavior;
- stays within files already touched by the PR or directly covered by the comment;
- adds narrow tests or docs for the reviewed behavior;
- removes obvious dead code or typo-level issues tied to the comment.

Ask before applying when the fix would:

- change public API, serialized response shape, schema, migrations, or data backfills;
- alter auth/authz, tenancy, security posture, billing, payments, or compliance behavior;
- add dependencies, new services, background jobs, or infrastructure assumptions;
- expand product scope beyond the PR intent;
- reject a reviewer-requested blocker;
- require remote side effects such as pushing, replying, resolving, or requesting re-review.

## Implementation Rules

- Reproduce or inspect the issue before changing code when feasible.
- Keep each fix traceable to one thread or one root-cause group.
- Do not hide behavior changes inside cleanup.
- Do not rewrite unrelated code while addressing review feedback.
- Preserve user changes already present in the worktree.
- If the reviewer suggested code, evaluate it as a proposal, not an instruction.

## Verification Rules

- Run the narrowest meaningful check first.
- Add or update tests when the review comment identifies missing behavior coverage.
- Broaden verification when touching shared helpers, API contracts, migrations, auth, or UI flows.
- Record skipped verification with a reason, not silence.

## Reply Mapping

- Fixed in code: `Fixed by <specific change>. <test/check if useful>.`
- Fixed in tests: `Added coverage for <case>; implementation already handled it.`
- Already addressed: `This is covered by <commit/code path>; no extra change needed.`
- Stale: `This line changed, but I checked the underlying concern and <outcome>.`
- Declined: `I kept <current behavior> because <constraint/tradeoff>.`
- Clarify: `Are you asking for <specific tradeoff> even though <cost/constraint>?`
