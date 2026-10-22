# Safety Model

`krt-review-herald` edits code in response to review and can write to GitHub.

- Posting replies, resolving or unresolving threads, requesting reviewers,
  dismissing reviews, commenting and pushing all notify people. Do them only
  after the user approves the exact actions, or within an enclosing release
  workflow that named them.
- Publish thread actions through `scripts/apply_review_threads.py`; run it
  without `--execute` first.
- Never resolve a thread whose concern is not actually addressed on the PR,
  and never resolve an open question or a decision that belongs to the user.
- Ask before fixes that change public API or serialized output, persistence,
  auth or tenancy, dependencies, release behavior or product scope.
