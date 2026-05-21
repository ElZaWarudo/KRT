# Role And Runtime

Load during preflight, argument parsing, and runtime/delegation setup.

## Role Resolution

Resolve these logical roles:

| Role | Canonical portable skill | Required when |
|---|---|---|
| `roadmap_generator` | `krt-roadmap-cartographer` | artifact generation |
| `brainstorm` | `ce-brainstorm` | artifact generation |
| `plan` | `ce-plan` | artifact generation |
| `document_review` | `document-review` | artifact generation |
| `state_archivist` | `krt-state-archivist` | optional state compaction |
| `work` | `ce-work` | execution |
| `code_review` | `ce-review` | execution |
| `security_review` | `krt-security-sentinel` | high-risk review units |
| `project_pr` | `krt-release-marshal` | shipping |
| `ci_investigator` | `krt-ci-questor` | optional CI escalation |
| `gitflow_commit` | `krt-gitflow-knight` | shipping component |
| `clean_rebase` | `krt-rebase-smith` | shipping component |
| `jira_workflow` | `krt-jira-scribe` | shipping with required Jira, or preferred Jira when available |

Resolution order:

1. Exact canonical portable skill name.
2. Documented runtime alias exposed by the host.
3. If unresolved and required for the current phase, stop with the role, canonical skill, aliases checked, and blocked phase.

Missing optional roles do not block:

- Missing `state_archivist`: preserve long state and record skipped compaction.
- Missing `security_review`: resolve another security-review skill or do direct evidence-based review.
- Missing `ci_investigator`: do direct evidence-first triage if CI breaks.

Missing required shipping roles block before shipping. Missing Jira blocks only when `jira-policy:required`; with the default optional policy, record the missing role/config/context and continue the no-Jira handoff path.

## Runtime Adapter

The portable core is role-based. Subagents are optional runtime adapters.

- Use delegated agents only when the host supports them and the work can be isolated safely.
- Prefer normal branch switching in the current checkout over creating worktrees. Use isolated worktrees/checkouts only when parallel mutating workers, overlapping scopes, or explicit isolation requirements make a single checkout unsafe.
- Keep the lead as supervisor; subagents do not coordinate with each other.
- Do not add free-form swarm behavior. Use bounded delegation and reviewer fan-out only when useful and recorded.
- Distinguish direct KRT-owned agent launch from invoking another resolved skill. Do not downgrade `document_review`, `work`, or `code_review` just because that skill may internally launch agents.

Resolve delegation at the start of execution (`mode:execute`, execution resume, or post-artifact `mode:full`):

- `delegation:inline` or "sin subagentes": no KRT-owned subagents.
- `delegation:ask`, `autonomy:manual`, `parallel:true` without `autonomy:high`, or "con subagentes": ask before mutating subagents.
- `delegation:auto`: use `autonomy:guarded` unless explicit.
- `autonomy:guarded`: read-only agents and one scoped worker may run when ownership is clear and no blocking decision remains.
- `autonomy:high`: parallel mutating workers only with `parallel:true`, isolated worktrees/checkouts, non-overlapping scopes, dependencies, and fallback branch strategy. If work is serial, prefer branch changes in the current checkout.

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
- `parallel:false|true`: default `false`; `true` requires safe dependencies and isolation.
- `delegation:auto|ask|inline`: default `auto`.
- `autonomy:manual|guarded|high`: default `guarded`.
- `review-threshold:P0-P2|P0-P1|P0`: default `P0-P2`.
- `subagent-model:<value>`: runtime-specific advisory only.

Jira policy semantics:

- `optional`: Jira-preferred and non-blocking. During preflight, detect existing Jira keys/URLs, `krt-jira-scribe` availability, and required env var presence without printing secrets. During package and release handoff, include Spanish Jira summary/description and create/reuse guidance. If Jira context, role, or configuration is absent, record the degraded path and continue without asking whether Jira matters.
- `required`: Jira traceability is part of the delivery contract. Missing Jira role, context needed for safe mutation, or required configuration blocks before shipping.
- `skip`: Do not do Jira lookup, creation, backlinking, or transition; record that Jira was intentionally skipped.

## Paths And State

Create as needed:

```text
docs/orchestration/
docs/orchestration/archive/compound-master-state/
docs/roadmaps/
docs/work-packages/RDM-###-<roadmap-item-slug>/
docs/review-findings/
docs/brainstorms/
docs/plans/
```

Maintain `docs/orchestration/compound-master-state.md` as a compact live resume entrypoint. Archive long historical detail under `docs/orchestration/archive/compound-master-state/` and link it from the live state.
