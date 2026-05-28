# Commit Guidance

Use this reference when turning PR review feedback into commit groups or commit titles.

## Ownership

- Let `krt-gitflow-knight` own branch hygiene, deterministic staging, and final commit creation.
- Use this reference only to shape Review Herald's proposed grouping and titles.
- Keep each commit traceable to one thread, one root-cause group, or one coherent review response.

## Title Shape

Use the repository's commit convention first. When none is stricter, use:

```text
type(scope): imperative summary
```

Recommended types:

- `fix`: Correct behavior or resolve a blocker from review.
- `test`: Add or adjust coverage requested by review.
- `docs`: Clarify docs, PR-facing rationale, or skill guidance.
- `refactor`: Clarify code without changing behavior in response to review.
- `chore`: Update non-runtime maintenance surfaces.

Recommended scopes:

- `review`: Product/code fixes caused by PR feedback when no domain scope is clearer.
- Domain scope such as `api`, `auth`, `billing`, or `ci` when it better names the affected surface.
- `review-herald` for changes to this skill.

## Examples

- `fix(review): preserve tenant filter in feedback fix`
- `test(review): cover stale PR comment handling`
- `refactor(api): clarify serializer fallback path`
- `docs(review-herald): clarify GitHub thread lifecycle`
- `feat(review-herald): resolve PR feedback with safe fixes`

## Avoid

- `fix review comments`
- `address feedback`
- `update after PR`
- `misc fixes`
- Reviewer names, thread IDs, package IDs, or date sequences unless the repo explicitly requires them.

## Grouping

- Combine several comments into one commit only when they share a root cause.
- Separate tests only when they are a coherent review unit and earlier commits remain understandable.
- Prefer a domain scope over `review` when the commit should remain meaningful after the PR discussion disappears.
- Mention the thread linkage in the closeout or reply, not in the commit title.
