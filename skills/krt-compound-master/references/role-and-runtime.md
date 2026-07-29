# Role And Runtime

Load during preflight, argument parsing, and runtime/delegation setup.

## Role Resolution

Resolve these logical roles:

| Role | Canonical portable skill | Required when |
|---|---|---|
| `roadmap_generator` | `krt-roadmap-cartographer` | artifact generation |
| `brainstorm` | `ce-brainstorm` | artifact generation |
| `plan` | `ce-plan` | artifact generation |
| `document_review` | `ce-doc-review` | artifact generation |
| `state_archivist` | `krt-state-archivist` | optional state compaction |
| `work` | `ce-work` | execution |
| `code_review` | `ce-code-review` | execution |
| `security_review` | `krt-security-sentinel` | high-risk review units |
| `project_pr` | `krt-release-marshal` | shipping |
| `mutation_executor` | `krt-release-marshal` | autonomous external mutation |
| `ci_investigator` | `krt-ci-questor` | optional CI escalation |
| `gitflow_commit` | `krt-gitflow-knight` | shipping component |
| `clean_rebase` | `krt-rebase-smith` | shipping component |
| `jira_cloud` | `krt-jira-cloud-scribe` | shipping when the resolved provider is Jira Cloud |
| `jira_server_datacenter` | `krt-jira-scribe` | shipping when the resolved provider is Jira Server/Data Center |

Resolution order:

1. Exact canonical portable skill name.
2. Documented runtime alias exposed by the host.
3. If unresolved and required for the current phase, stop with the role, canonical skill, aliases checked, and blocked phase.

Missing optional roles do not block:

- Missing `state_archivist`: preserve long state and record skipped compaction.
- Missing `security_review`: resolve another security-review skill or do direct evidence-based review.
- Missing `ci_investigator`: do direct evidence-first triage if CI breaks.

Missing required shipping roles block before shipping. Resolve Jira through Release Marshal's deterministic provider resolver; do not choose Cloud or Server/Data Center by default. Missing or ambiguous Jira blocks only when `jira-policy:required`; with the default optional policy, record the diagnosis and continue the no-Jira handoff path.

Autonomous external mutation also requires the `mutation_executor` role and the ledger validator from `krt-compound-master`. If either is missing, autonomous shipping degrades to validation-only/manual-required mode before any PR, branch, reviewer, Jira, or merge side effect.

Portable naming and runtime syntax:

- Treat canonical hyphenated skill names as portable; runtime aliases are optional conveniences.
- Treat `Skill("<role>", "...")` examples as pseudocode and translate them to the current runtime.
- Use repo-relative paths in generated artifacts.

## Runtime Adapter

The portable core is role-based. Subagents are optional runtime adapters.

- Use delegated agents only when the host supports them and the work can be isolated safely.
- Prefer normal branch switching in the current checkout over creating worktrees. With default `worktree-policy:avoid`, do not create isolated worktrees/checkouts; when the policy is `auto|required`, use them only when parallel mutating workers, overlapping scopes, or explicit isolation requirements make a single checkout unsafe.
- Keep the lead as supervisor; subagents do not coordinate with each other.
- Do not add free-form swarm behavior. Use bounded delegation and reviewer fan-out only when useful and recorded.
- Distinguish direct KRT-owned agent launch from invoking another resolved skill. Do not downgrade `document_review`, `work`, or `code_review` just because that skill may internally launch agents.

Resolve delegation at the start of execution (`mode:execute`, execution resume, or post-artifact `mode:full`):

- `delegation:inline` or "sin subagentes": no KRT-owned subagents.
- `delegation:ask`, `autonomy:manual`, `parallel:true` without `autonomy:high`, or "con subagentes": ask before mutating subagents.
- `delegation:auto`: use `autonomy:guarded` unless explicit.
- `autonomy:guarded`: read-only agents and one scoped worker may run when ownership is clear and no blocking decision remains.
- `worktree-policy:avoid`: default. Do not create worktrees/checkouts; run serially in the current checkout or ask before changing the policy.
- `worktree-policy:auto`: worktrees/checkouts are allowed only when explicit parallel mutating execution needs safe isolation.
- `worktree-policy:required`: the user or runtime explicitly requires isolated checkouts; stop if safe isolation cannot be created.
- `autonomy:high`: parallel mutating workers only with `parallel:true`, `worktree-policy:auto|required`, isolated worktrees/checkouts, non-overlapping scopes, dependencies, and fallback branch strategy. If work is serial, prefer branch changes in the current checkout.

Delegation budget:

- At most one mutating worker per review unit.
- At most three read-only reviewer subagents in review fan-out.
- If a subagent returns low confidence, do one targeted follow-up rather than launching generic agents.

Record delegation mode, roles used, read-only/mutating status, outcome, confidence, duration when useful, and whether delegation reduced or added loops.

## Arguments

- `mode:artifacts` default: artifact steps only.
- `mode:execute`: execute ready review units; if no `package:` is provided, choose the first unblocked package and first ready review unit from the earliest safe wave.
- `mode:full`: artifacts, execution gate, then execute the recommended review unit or safe wave.
- `mode:resume`: continue from the next incomplete state item.
- `package:<path>`: execute or resume only that work package.
- `review-unit:<RU#>`: execute or resume only that review unit.
- `production:unknown|live|preprod|prototype`: default `unknown` unless explicit context or strong repo evidence supports another value.
- `pr-granularity:auto|review-unit|work-package|roadmap-item|plan-unit`: default `auto`, but review-unit is the normal PR unit.
- `jira-policy:required|optional|skip`: default `optional`.
- `jira-provider:auto|cloud|server-datacenter|none`: default `auto`; resolve from explicit input, Jira URL, or exactly one ready provider, never from a silent provider default.
- `parallel:false|true`: default `false`; `true` requires safe dependencies and isolation.
- `delegation:auto|ask|inline`: default `auto`.
- `worktree-policy:avoid|auto|required`: default `avoid`; `parallel:true` does not override it.
- `autonomy:manual|guarded|high`: default `guarded`.
- `autonomous-ledger:<path>`: machine-readable authorization ledger for autonomous external mutation. `autonomy:high` without this ledger does not authorize external side effects.
- `review-threshold:P0-P2|P0-P1|P0`: default `P0-P2`.
- `subagent-model:<value>`: runtime-specific advisory only.
- `orchestrator:standalone|seneschal`: default `standalone`; load `nested-orchestration.md` for a Seneschal child.
- `run-id:<stable-id>`: required for `orchestrator:seneschal`; use it to isolate state and parent reconciliation.
- `state-path:<repo-relative-path>`: required for `orchestrator:seneschal`; it is the child's only live resume truth.
- `initiative-contract:<repo-relative-path>`: reviewed shared requirements-only contract inherited by the child.
- `interaction:direct|brokered`: default `direct`; require `brokered` for `orchestrator:seneschal`.

Jira policy semantics:

- `optional`: Jira-preferred and non-blocking. During preflight, preserve explicit provider/URL context and let Release Marshal resolve provider readiness without printing secrets. During package and release handoff, include `jira_provider`, Spanish Jira summary/description, and create/reuse guidance. If Jira context, role, provider, or configuration is absent or ambiguous, record the degraded path and continue without asking whether Jira matters.
- `required`: Jira traceability is part of the delivery contract. Missing Jira role, context needed for safe mutation, or required configuration blocks before shipping.
- `skip`: Do not do Jira lookup, creation, backlinking, or transition; record that Jira was intentionally skipped.

Autonomous ledger semantics:

- The Compound Master autonomy ledger JSON schema version 1 is the single authority for allowed mutation classes, target scope, expiry, issuer binding, and audit path.
- Markdown state may link to the ledger and summarize it, but scripts must validate the JSON directly before mutation.
- Active ledgers require issuer identity or an approval artifact reference/hash. Missing issuer binding blocks autonomous external mutation.
- Runtime permissions or credential routing must constrain mutation paths to the executor. If they cannot, the run may continue local work but external mutation remains manual-required.

## Paths And State

Create as needed:

```text
docs/orchestration/
docs/orchestration/compound-master/<run-id>/
docs/orchestration/autonomy-ledgers/
docs/orchestration/archive/compound-master-state/
docs/roadmaps/
docs/work-packages/RDM-###-<roadmap-item-slug>/
docs/review-findings/
docs/brainstorms/
docs/plans/
```

For standalone runs, maintain `docs/orchestration/compound-master-state.md` as a compact live resume entrypoint. For Seneschal-nested runs, require `docs/orchestration/compound-master/<run-id>/state.md` or another explicit collision-free repo-relative path. Never let active runs share a mutable state file. Archive long historical detail under `docs/orchestration/archive/compound-master-state/` and link it from the active run state.
