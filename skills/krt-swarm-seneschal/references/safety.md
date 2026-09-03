# Safety

Read this reference before any Seneschal operation that can mutate code,
repository state, orchestration state, Jira, branches, pull requests, or release
state.

## Authority

- Treat the user's request as authority only for its stated scope. Local
  implementation authority does not automatically authorize Jira changes,
  pushes, pull requests, reviewer requests, merges, production actions, or
  destructive cleanup.
- In manual flow, obtain explicit approval immediately before an external,
  irreversible, notification-causing, or production-impacting action.
- In autonomous flow, require a current validated autonomy ledger that names the
  exact mutation class. Record uncovered decisions as blockers; do not infer
  permission from a general no-confirmation request.
- Never expose secrets, tokens, credential files, environment dumps, or URLs
  containing credentials in prompts, logs, state, timing, or handoff artifacts.

## Planning And Provider Gates

- Require an approved documentation packet before Jira seeding or worker
  dispatch from a rough initiative, roadmap, program, or unrefined backlog.
- Action-specific authorization does not waive a documentation gate that
  applies to rough source work.
- An explicit, execution-ready unit with settled acceptance criteria does not
  require a newly manufactured initiative packet. Existing repository and user
  authorization rules still apply. If persisted, record its unit-scoped
  exemption with the trusted user-event digest; never infer that exemption.
- Resolve Jira from an explicit provider, a provider-specific URL, or exactly
  one ready integration. Never silently choose Cloud or Server/Data Center.
- Use the selected Jira provider skill for Jira reads and mutations. Seneschal
  stores mappings and observations; it is not live Jira authority.
- `krt-release-marshal` owns commits, pushes, PR creation, release-time Jira
  mutation, reviewer requests, and merge flow.

## Isolation And Change Safety

- Inspect repository status before work and preserve unrelated user changes.
- Give concurrent mutable workers disjoint ownership and isolated workspaces.
  Serialize overlapping auth, data, migration, public-contract, central-model,
  generated, dependency, or lockfile work.
- Workers never stage, commit, apply patches, switch branches, create or remove
  worktrees, push, open PRs, mutate Jira, request reviewers, or merge.
- Resolve and verify exact targets before destructive, recursive, cleanup, or
  worktree operations. Prefer recoverable cleanup.
- The root orchestrator owns consolidation and must inspect the actual diff;
  worker prose is never authoritative evidence of changed files or readiness.

## Verification And State

- Match protocol depth to assurance. High, critical, deep, and autonomous work
  uses executable contracts and fail-closed reconciliation. Do not impose that
  machinery on an eligible lightweight unit.
- Capture or rerun required checks at root when worker evidence is not
  independently observable. A conflicting root result wins.
- Critical work requires explicit approval or an exact autonomy-ledger grant
  after its coordinated review and evidence reconciliation pass.
- Create persistent queue and blocker state only when an operation needs it.
  Apply guarded lifecycle changes through `scripts/transition_swarm_state.py`;
  do not hand-edit approval, documentation-exemption, or release-ready facts.
- Treat queue projections, Compound snapshots, timing records, and cached Jira
  fields as observations. Refresh their live authority before consequential
  decisions.
