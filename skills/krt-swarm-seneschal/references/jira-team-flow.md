# Jira Team Flow

Use this reference for `jira-team-flow` and `jira-seed-and-drain`.

## Purpose

Run the swarm like a normal delivery team with Jira Cloud as backlog source:

```text
approved documentation -> Jira Cloud seed/read -> persistent queue map -> safe waves -> worker reconciliation -> release marshal handoff
```

Seneschal coordinates. It does not directly own Jira mutations, commits, pushes, PRs, reviewer requests, merge flow, or issue transitions. In autonomous flow it passes the autonomy ledger to owning skills instead of asking during the run.

## Required Skill Boundaries

- Jira Cloud issue lookup, create/update proposals, comments, links, and transitions belong to `krt-jira-cloud-scribe`.
- Commits, PRs, Jira PR backlinks, release transitions, and merge flow belong to `krt-release-marshal`.
- Quality pipeline, review units, and high-risk work package execution belong to `krt-compound-master`.
- Seneschal owns documentation gate checks, queue normalization, wave selection, worker dispatch prompts, blocker ledger updates, reconciliation, and release-ready handoff packets.

Use `krt-jira-scribe` only when the user explicitly says the Jira target is Server/Data Center.

## Persistent Files

Default local files in the consumer repository:

- `docs/swarm/queue-state.yaml`: documentation gate, queue units, Jira key mapping, dependency graph, wave history, release handoff facts.
- `docs/swarm/blockers.yaml`: non-fatal high-risk blockers discovered by workers or readiness checks.

Create files when the mode needs them and they do not exist. Do not treat contents as live Jira authority; re-read Jira Cloud through `krt-jira-cloud-scribe` before release decisions or seed proposals.

## Documentation Gate

Before Jira seed/drain:

- Load `references/documentary-planning.md`.
- Read `documentation_gate` from `docs/swarm/queue-state.yaml` when present.
- If no gate exists and the source is a rough brief, roadmap, new initiative, Jira program, or swarm startup, switch to `document-plan`.
- If `documentation_gate.status != approved`, stop with the documentation review packet.
- Proceed to Jira seed/drain only when the gate is approved or the user explicitly authorizes the exact Jira mutation in the current request.

## Flow

1. **Preflight**
- Load `krt-jira-cloud-scribe` because Jira Cloud is the default Jira posture.
- Verify whether Jira Cloud env/config is available only when live Jira reads or mutations are needed.
- Read local queue state and blocker ledger if present.
- Inspect git state and isolation options.
- Check `documentation_gate.status` before seed, drain, dispatch, or release handoff.

2. **Optional seed**
- If the user supplied a roadmap or backlog file to seed, load `references/jira-seeding.md`.
- Build Jira seed plan and local issue map only after documentation is approved.
- In manual flow, ask confirmation before any Jira create/update.
- In autonomous flow, use active autonomy ledger covered Jira mutation classes; record uncovered needs and continue approved independent work.

3. **Drain active work**
- Read active Jira Cloud issues/subtasks using `krt-jira-cloud-scribe`.
- Convert each eligible Jira issue into a queue unit with source key, title, scope, acceptance criteria, dependencies, surfaces, verification, and status.
- Merge live Jira facts into `docs/swarm/queue-state.yaml` without losing local documentation gate, verification, blocker, or handoff history.
- Use Planner workers to decompose Jira epics or parent issues too broad for one implementer.

4. **Readiness filtering**
- Exclude units when documentation gate is not approved.
- Exclude units with open blockers in `docs/swarm/blockers.yaml`.
- Exclude units that depend on open blockers.
- Exclude units with unclear acceptance criteria, missing branch/base strategy, unresolved product/auth/data decisions, or risky surface overlap.
- Prefer units already mapped to `krt-compound-master` review units.

5. **Wave selection**
- Apply `references/parallel-dispatch-policy.md`.
- Default to 2 workers when isolation exists.
- Produce a wave plan listing unit IDs, Jira keys, worker prompts, isolation targets, verification gates, overlap analysis, and stop conditions.

6. **Dispatch**
- Assign one Jira subtask or standalone Jira issue per worker.
- Use implementation-only/no-shipping worker contracts.
- Workers must not commit, push, open PRs, mutate Jira, request reviewers, merge, or transition Jira.

7. **Reconcile**
- Inspect actual diffs and changed files, not only worker reports.
- Run relevant tests and review gates.
- Record blockers in blocker ledger.
- Use Reviewer workers for code-quality gates, Fixer workers for bounded failures, and Integrator workers for cross-worker merge/order conflicts.
- Mark each unit `release-ready`, `needs-fix`, `blocked`, `deferred`, or `split-required`.

8. **Handoff**
- Prepare release-ready packets for `krt-release-marshal`.
- Include Jira key, PR grouping suggestion, verification evidence, release notes, affected surfaces, and suggested Jira transition.
- Do not execute Jira transitions or PR operations from Seneschal. In autonomous flow, pass the ledger path so `krt-release-marshal` can run its autonomous executor/validators where available.

## Readiness Rules For Jira Units

A Jira-sourced unit is ready only when:

- Documentation gate is approved.
- Jira key is unambiguous and active.
- Scope maps to one executable work unit.
- Dependencies are resolved and available on the intended base.
- No open blocker affects the unit.
- Touched surfaces are known well enough for overlap checks.
- Acceptance criteria are testable.
- Verification commands or justified gaps are present.
- Isolation target is known.

If readiness cannot be established, leave the unit planned or mark it blocked/deferred with a blocker ledger entry. In autonomous flow after approval, do not ask; keep draining other ready units.

## Non-Interruption Rule

Do not interrupt the whole goal when a question can be captured as a blocker and deferred. In autonomous flow, do not ask during the run after the documentation gate is approved. Stop when:

- Documentation gate is not approved and the requested action would seed Jira, dispatch workers, mutate code, or release handoff.
- No ready independent work remains.
- A missing decision affects architecture, auth, data, public contracts, central technical foundations, or production behavior broadly.
- The autonomy ledger explicitly denies continuing the decision class.
- Continuing would create high-risk compliance, security, accounting, payroll, or DIAN exposure.
