# Safety

- The user's request authorizes only its stated scope. Local implementation
  permission does not cover Jira changes, pushes, PRs, reviewer requests,
  merges, production actions, or destructive cleanup; get explicit approval
  for those, or an active autonomy ledger naming the exact mutation.
- Workers never stage, commit, switch branches, create or remove worktrees,
  push, open PRs, touch Jira, or merge. The primary agent owns consolidation and
  `krt-release-marshal` owns shipping.
- Give concurrent mutable workers disjoint ownership and separate worktrees.
  Serialize overlapping auth, data, migration, public-contract, central-model,
  generated, dependency, or lockfile work.
- Inspect the actual diff before trusting any worker report. When a root check
  disagrees with a worker's claim, the root result wins.
- Preserve unrelated user changes. Resolve exact paths before deleting a
  worktree; keep failed or disputed workspaces; never touch unregistered ones.
- Resolve Jira from an explicit provider, provider URL, or exactly one ready
  integration; never silently pick Cloud or Server/Data Center.
- Never put secrets, tokens, credential files, or environment dumps in worker
  prompts, logs, run records, or handoffs.
