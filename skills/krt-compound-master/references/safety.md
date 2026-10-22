# Safety

Compound Master coordinates delivery; it never turns orchestration into shipping
authority.

- Local implementation permission does not cover pushes, PRs, reviewer
  requests, Jira changes, merges, deploys, or deletion. Those go through
  `krt-release-marshal` with explicit user approval, or through an active
  autonomy ledger validated for the exact mutation.
- Internal review, Security Sentinel output, and CI-prevention evidence are
  readiness signals, not merge authorization.
- Workers and nested runs never commit, push, open PRs, or touch Jira.
- Do not invent product behavior, authorization or data rules, production
  posture, or Jira structure; raise them as decisions.
- Preserve unrelated user changes. Resolve exact targets before any
  destructive or cleanup operation.
- Never copy secrets, tokens, or environment dumps into state, prompts, PR text,
  or handoffs.
