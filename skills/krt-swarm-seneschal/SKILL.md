---
name: krt-swarm-seneschal
description: Meta-orchestrator turning rough initiatives, documented KRT work packages, backlog items, Jira queues, and roadmap backlogs into approved documentation packets, nested krt-compound-master flows, isolated Codex worker waves, decision brokering, reconciliation, and release handoffs. Use when the user asks for swarm-style workflow, multiple Compound Master workers, documentary planning before execution, dispatcher, parallel subagent orchestration, Jira-backed team flow, overnight/no-confirmation autonomous delivery, backlog-to-PR execution, Codex worker waves, or a layer above krt-compound-master.
---

# KRT Swarm Seneschal

Coordinate swarm-style delivery flow:

```text
rough brief -> initiative contract -> composition gate -> nested Compound flows -> reconciliation -> release handoff
```

This skill is a meta-orchestrator. It must not reproduce or bypass
`krt-compound-master` gates or replace `krt-release-marshal`. It may invoke
multiple isolated Compound Master flows, observe their canonical artifacts and
states, broker their user decisions, and reconcile their release-ready outputs.
When subagents are unavailable, produce exact prompts and wave plans.

## Operating Posture

- Treat approved documentation as a formal dependency of Jira mutation, worker dispatch, code mutation, and release handoff.
- Treat `krt-compound-master` as the complete per-flow artifact and quality pipeline for deep work that needs it. Route execution-ready fast and standard units directly; do not pay the nested pipeline cost by default.
- Treat each active Compound flow as an isolated run with a stable run ID and canonical state path. Never let active runs share one mutable `compound-master-state.md`.
- Treat Compound artifacts as authoritative. Store only paths and observed snapshots in swarm state.
- Treat `krt-release-marshal` as the only owner of commits, PR creation, Jira mutation during release, reviewer requests, and merge-related flow.
- Resolve Jira provider from an explicit `jira-provider`, a Jira URL, or exactly one ready provider through `krt-release-marshal/scripts/resolve_jira_provider.py`. Never default silently. Keep adapters separate: `cloud` selects `krt-jira-cloud-scribe`; `server-datacenter` selects `krt-jira-scribe`.
- Treat human approval as a startup policy problem, not a per-action interruption. In manual flow, ask before mutating. In autonomous flow, require an active autonomy mandate/ledger that allows the exact mutation class.
- Even in autonomous flow, do not bypass the documentary planning gate unless the user explicitly authorizes the exact downstream mutation or an existing gate state is already approved.
- Prefer small, independently reviewable units over broad backlog sweeps.
- When a broad unit is coupled through a small shared API, load
  `references/staged-decomposition.md`: serialize the smallest testable
  foundation, then fan out dependency-ready children with disjoint ownership
  before a final integration and aggregate-verification stage.
- Apply the break-even gate and execution lanes in `references/execution-lanes.md`: keep trivial single units in the root thread, preserve Spark at `xhigh`, use Luna `high` normally, and reserve Luna `xhigh` for demanding work.
- Classify assurance independently from execution difficulty. Low assurance uses
  tests plus one implementer self-review; medium uses one focused reviewer;
  high uses a relevant specialist plus independent validation; critical uses
  coordinated review, reconciliation, and explicit approval. File count,
  surface count, or behavior change alone never earns a larger review chain.
- Cap active mutable implementation work at the smallest safe wave; default to 2 concurrent Implementer workers until repo evidence supports more. Planner, Reviewer, Fixer, Integrator, and Documenter workers use separate role caps.
- Never let production outrun verification: a wave is not complete until worker output, any trigger-required review, verification evidence, and state reconciliation are captured.
- Never accept a worker's prose as its execution contract or certification.
  Materialize a hashed `worker-contract.json`, observe the real diff at root,
  and pass the contract plus evidence through the fail-closed evaluator.
- Require every implementation worker to run the contract-bound
  `validate_worker_terminal.py` command immediately before returning the exact
  `worker-terminal.schema.json` object. Do not accept prose, YAML, renamed
  fields, omitted empty arrays, or `phase` values other than `closeout`.
- Treat every worker claim that a check passed as provisional until root has
  machine-captured the exact command, exit code, and output through a
  runtime audit or a root-owned execution. A prose success claim never advances
  a verification gate.
- Give every dispatched role a finite action and elapsed-time budget. Interrupt
  a worker that exhausts its budget, repeats settled exploration, or continues
  after its return condition; complete a smaller remaining validation at root
  when dispatch overhead has exceeded the work.
- If the user explicitly asks for no human confirmation, convert the instruction into a ledger-bound autonomous run: execute allowed actions after required gates pass, record uncovered decisions as blockers, continue independent work, and leave a morning-ready status packet instead of stopping to ask.

## Reference Router

Load only what the current task needs:

| Need | Load |
|---|---|
| Explain design swarm model | `references/swarm-protocol.md` |
| Start, observe, resume, or reconcile nested Compound Master flows | `references/compound-master-nesting.md` |
| Produce, review, revise, approve documentation packet | `references/documentary-planning.md` |
| Build queue, choose ready work, plan waves | `references/queue-and-dispatch.md` |
| Split coupled work into serial foundation, parallel dependents, and integration | `references/staged-decomposition.md` |
| Create, seed, observe, consolidate, and clean role-specific worktrees | `references/worktree-collaboration.md` |
| Classify execution lanes and assurance tiers, admit roles, assign verification ownership | `references/execution-lanes.md` |
| Launch or prepare subagent prompts | `references/subagent-contracts.md` |
| Materialize and validate executable worker contracts | `references/executable-worker-contracts.md` |
| Resolve a named Codex worker profile | `references/worker-profiles.md` |
| Monitor Luna checkpoint, closeout, and timing | `references/lightweight-supervision.md` |
| Recover Reviewer/Fixer returns or classify failed checks | `references/role-recoverability.md` |
| Reconcile outputs, review gates, hand off release work | `references/gates-and-reconciliation.md` |
| Partition review surfaces, register findings, target validators | `references/review-coordination.md` |
| Run Jira backlog source and drain ready waves | `references/jira-team-flow.md` |
| Seed Jira from roadmap or work-package backlog | `references/jira-seeding.md` |
| Decide parallelism surface isolation | `references/parallel-dispatch-policy.md` |
| Compute/reuse evidence, adapt concurrency, render compact status | `references/automated-wave-control.md` |
| Maintain persistent documentation gate, queue, Jira issue mapping | `references/queue-state-schema.md` |
| Record, review, resolve non-fatal blockers | `references/blocker-ledger.md` |
| Run without interactive confirmations | `references/autonomous-team-flow.md` |

## Modes

Supported modes:

- `design-only`: explain or design the swarm delivery model without mutating code, Jira, PRs, or queue state.
- `document-plan`: create only the starting documentation packet and mark the documentation gate `in_review`.
- `document-review`: present the current documentation packet for human review without Jira, worker, or code mutation.
- `document-revise`: adjust documentation packet artifacts from user feedback and mark the documentation gate `changes_requested` or `in_review` as appropriate.
- `document-approve`: mark the documentation packet approved after explicit user approval.
- `wave-plan`: normalize approved backlog into queue units and propose the next safe wave.
- `dispatch`: launch or prepare implementation-only workers for an approved wave.
- `reconcile`: inspect worker outputs, real diffs, verification, blockers, and review gates.
- `resume`: reload persistent queue state, documentation gate, live repo state, and active worker facts before continuing.
- `jira-team-flow`: use the resolved Jira provider as backlog source and drain ready waves after documentation approval.
- `jira-seed-and-drain`: seed Jira through the resolved provider and drain ready work only when documentation is approved or the user explicitly authorizes this exact bypass.
- `overnight-team-flow` or `autonomous-team-flow`: run Jira team flow with an autonomy mandate, still respecting the documentary planning gate.
- `blocker-review`: read blocker ledger and list open blockers grouped by type, Jira key, wave, and suggested owner.
- `blocker-resolve`: apply user-supplied decisions to the blocker ledger and mark affected units as candidates for readiness checks.
- `wave-status`: derive a compact read-only panel from queue state, blockers,
  gates, evidence, and the latest allocation.

## Workflow

1. **Preflight**
- Resolve the user's requested mode: design-only, document-plan, document-review, document-revise, document-approve, wave-plan, dispatch, reconcile, resume, jira-team-flow, jira-seed-and-drain, overnight-team-flow, autonomous-team-flow, blocker-review, blocker-resolve, or wave-status.
- Inspect repo state and active orchestration artifacts before mutating anything.
- Identify source work: `docs/work-packages/`, GitHub Issues, Linear, backlog file, Jira queue, or user-provided tasks.
- Read persistent state from `docs/swarm/queue-state.yaml` and `docs/swarm/blockers.yaml` when they exist. Create them only when the requested mode needs local state.
- When a queue unit uses Compound Master, load `references/compound-master-nesting.md`, resolve its run ID and canonical state path, and refresh its observed snapshot before selecting or resuming it.
- When Jira is involved, resolve `jira_provider` before reading or mutating Jira state. If both providers are ready or neither is identifiable, treat the provider as ambiguous/unresolved instead of guessing.
- For Jira team flow, load `references/jira-team-flow.md`, `references/queue-state-schema.md`, `references/blocker-ledger.md`, and `references/parallel-dispatch-policy.md`.
- For autonomous or no-confirmation flow, load `references/autonomous-team-flow.md` and resolve an autonomy ledger before external or irreversible mutations.
- When a unit selects a named Codex profile, load `references/worker-profiles.md` and run its static profile preflight before dispatch. If only the bundled package profile exists, block dispatch and preview the explicit project or personal installation step; do not install into the user's Codex home without authorization.
- Before wave selection or dispatch, load `references/execution-lanes.md`, apply
  its break-even gate, classify every implementation unit's lane and assurance
  tier, and record both triggers. Missing classification blocks dispatch; it
  does not default to a review council.
- Load `references/worktree-collaboration.md`. Resolve a run-specific worktree
  parent and require one purpose-built worktree per worker invocation; serial
  execution does not permit workspace reuse.
- In `wave-status`, load canonical local state and render the derived panel; do
  not require documentation approval or continue into mutation workflows.

2. **Documentary Planning Gate**
- Load `references/documentary-planning.md`.
- If the user is starting a new initiative, roadmap, Jira program, swarm, overnight run, or implementation request from a rough brief, enter `document-plan` first.
- Produce the documentation packet before Jira mutation, queue execution state, worker dispatch, code mutation, or release handoff.
- For a new initiative, produce or reuse one reviewed requirements-only initiative contract before deriving child Compound flows. Treat it as shared inherited context, not a replacement for focused item discovery.
- Treat this gate as a composition gate: verify the shared contract, roadmap, child invocation envelopes, existing artifact gates, dependencies, and execution topology without repeating Compound Master's document reviews or requiring not-yet-generated child artifacts.
- Persist the gate in `docs/swarm/queue-state.yaml`:

```yaml
documentation_gate:
  status: draft | in_review | approved | changes_requested
  approved_by: null
  approved_at: null
  initiative_contract: docs/plans/<initiative>/initiative-requirements.md
  source_artifacts:
    - docs/plans/<initiative>/initiative-requirements.md
    - docs/product/roadmap.md
    - docs/jira/seed-plan.md
    - docs/swarm/swarm-startup.md
    - docs/swarm/queue-state.yaml
    - docs/swarm/blockers.yaml
  approval_artifacts:
    - docs/plans/<initiative>/initiative-requirements.md
    - docs/product/roadmap.md
    - docs/jira/seed-plan.md
    - docs/swarm/swarm-startup.md
  approval_receipt: null
  approved_packet_digest: null
  approval_receipt_digest: null
```

- Mark documentation `in_review` when the packet is ready and stop with a review packet.
- In `document-review`, present the packet and review focus; do not mutate Jira, queue execution state, workers, or code.
- In `document-revise`, update only the documentation packet and gate status based on feedback.
- In `document-approve`, require explicit user approval, materialize a content-bound receipt with `scripts/materialize_approval_receipt.py`, then apply it with `scripts/transition_swarm_state.py`. Never set approval fields by hand.
- If `documentation_gate.status != approved`, do not seed Jira, dispatch workers, mutate code, or hand off release work unless the user explicitly authorizes that exact action in the current request.

3. **Normalize Work**
- Convert candidate work into executable units with scope, acceptance criteria,
  dependencies, touched surfaces, verification commands, intended base,
  assurance tier, and concrete assurance triggers.
- Use Planner workers only when broad or ambiguous work still needs decomposition, acceptance criteria, dependency mapping, or decision closure. Never insert a Planner before an execution-ready work package.
- Prefer existing `krt-compound-master` review units. If only high-level backlog items exist, route discovery/planning through existing requirements, roadmap, and compound-master skills rather than inventing hidden scope.
- When several roadmap items need full artifact and quality pipelines, create one nested Compound run per independent item. Give each run the initiative contract, target item, artifact namespace, stable state path, and brokered interaction mode.
- Reject units that are too broad, lack acceptance criteria, share a risky surface with another active unit, or need unresolved product/auth/data decisions.
- Before leaving a broad coupled unit monolithic, load
  `references/staged-decomposition.md` and test whether a small explicit
  foundation unlocks at least two disjoint downstream units. If the compiler
  accepts the topology, mark the parent `split-required` and normalize the
  emitted children; if it rejects, record the failed guardrail and serialize.
- For Jira queues, maintain the resolved `jira_provider` with the persistent mapping from Jira issue key to work package, review unit, queue unit, current status, dependencies, and handoff facts.

4. **Seed Jira When Requested**
- Confirm `documentation_gate.status == approved` before any Jira seed or drain. If not approved, stop with the documentation review packet unless the user explicitly authorized Jira seeding in the current request.
- Load `references/jira-seeding.md`.
- Convert roadmap into proposed Jira hierarchy: product epic, parent issues by wave/domain, subtasks per work package or executable unit.
- Mark units that depend on expert decisions as blocked/deferred in local queue state and include intended Jira status/labels in the seed plan.
- In manual flow, do not create, update, comment on, link, or transition Jira issues unless the user confirms the exact mutation plan.
- In autonomous flow, execute only mutation classes covered by the autonomy ledger through the selected Jira provider skill; record uncovered mutation needs as blockers and keep draining independent approved work.

5. **Plan A Wave**
- Confirm `documentation_gate.status == approved` before selecting executable work.
- Load `references/queue-and-dispatch.md`.
- Load `references/execution-lanes.md`. Keep a single low-assurance unit in the
  root thread unless isolation, concurrency, or duration gives a named benefit;
  otherwise assign both `fast`, `standard`, or `deep` and `low`, `medium`,
  `high`, or `critical` before selecting its worker.
- For Jira team flow, read active Jira issues through the selected Jira provider skill, convert them into queue units, and reconcile them with the local Jira issue map.
- Read `docs/swarm/blockers.yaml` before selection. Do not select units with open blockers or units depending on open blockers.
- Select only dependency-ready, non-overlapping units.
- For staged topology, select foundation alone first. After its focused and
  triggered gates pass, derive downstream isolation from the exact immutable
  foundation baseline and let the adaptive allocator fan out only ready,
  disjoint children. Reconverge all children before integration.
- Apply concurrency algorithm in `references/parallel-dispatch-policy.md`: default to 2 mutable Implementer workers, role-specific caps for non-implementation workers, increase implementation concurrency only after green wave history, and never parallelize overlapping auth, migrations, public contracts, central models, or lockfiles.
- Load `references/automated-wave-control.md` and run
  `scripts/plan_adaptive_wave.py` from canonical history, blockers,
  dependencies, owned paths, risk surfaces, assurance tiers, review capacity, and scale
  authority. Its allocation already invokes the slot allocator and replaces
  manual concurrency selection; do not run allocation a second time.
- Keep the wave within open-stack reviewability limits already enforced by `krt-compound-master`.
- Admit Planner, Reviewer, Fixer, Integrator, Documenter, and Compound Master roles only through their explicit triggers in `references/execution-lanes.md`.
- Assign focused verification to each leaf and one aggregate verification owner/fingerprint to the wave.
- Compile every admitted role invocation with
  `scripts/plan_worker_workspaces.py`. Require unique workspace paths, exactly
  one consolidation workspace, and explicit dependency/candidate inputs.
- Produce a short wave plan with unit IDs, lanes, profiles, assurance tiers,
  review modes and demand, role triggers, worker prompts, isolation target,
  verification ownership, risks, and stop conditions.

6. **Dispatch Workers**
- Confirm `documentation_gate.status == approved` before dispatch.
- Load `references/subagent-contracts.md`.
- Load `references/worktree-collaboration.md`. Root creates each emitted
  worktree, applies dependency/candidate patches with `git apply --index`, and
  records `git write-tree` as the sealed baseline before dispatch. Workers
  never stage, commit, apply patches, switch branches, or manage worktrees.
- Load `references/executable-worker-contracts.md`. Materialize one immutable
  `docs/orchestration/runs/<run-id>/<unit-id>-worker-contract.json` with
  `scripts/materialize_worker_contract.py` before every implementation dispatch.
  Pass the actual worktree root and dispatch only after schema plus non-mutating
  command-context preflight validation. Bind its `contract_hash` at the
  root observation level through discovery, implementation, review, security,
  timing, and reconciliation. The discovery checkpoint itself has no hash or
  other extra fields.
- Render the dispatch prompt only with `scripts/render_worker_envelope.py`; do
  not hand-compose a second protocol beside the executable contract.
- Add the pre-return terminal validator prefix to
  `commands.read_only_prefixes` and its unique invocation to the worker
  envelope. The passing invocation must be the final observed command. A
  worker returns the exact JSON object that passed it; root-owned observation
  fields are attached only during reconciliation.
- Load `references/execution-lanes.md` and enforce the lane/profile mapping: `fast` uses `spark` at `xhigh`, `standard` uses `luna` at `high`, and `deep` uses read-only `luna_xhigh_discovery` followed by `luna_xhigh`, both at `xhigh`. Never lower Spark reasoning.
- Classify staged children independently. A dependent that consumes a settled
  foundation contract as read-only context does not inherit the foundation's
  deep lane; any worker that needs to edit foundation paths must stop and force
  a new foundation baseline instead of expanding its ownership.
- For a named Codex profile, require a successful `check_worker_profiles.py` result. Record whether resolution selected a project or personal custom agent; a bundled-only profile does not authorize dispatch. Never substitute a different profile when resolution or invocation fails.
- If runtime exposes subagents, launch each worker only with the relevant unit contract and artifact paths.
- If subagents are unavailable, write exact prompts the user can run in the
  already prepared, invocation-specific worktrees.
- Use only the role-specific workers admitted by the wave plan. Do not expand the standard role chain speculatively.
- Give Fixers one concrete defect cluster per invocation, exact owned paths,
  exact focused checks, and an explicit prohibition on additional review.
  Require the canonical finding-to-change mapping and reject a prose substitute.
- For every Reviewer or Fixer, load `references/role-recoverability.md` and
  render its concrete invocation with `scripts/render_role_envelope.py`. Do not
  add an acknowledgement exchange. Enable a recovery path only for a
  trigger-qualified coordinated high/critical review.
- Use a nested Compound Master Worker when a deep unit needs its brainstorm, plan, work-package, review, security, or CI-prevention pipeline. Route an execution-ready deep package through the direct two-stage Luna path when those artifacts and gates are already settled.
- Require nested Compound workers to use `interaction:brokered`: they formulate structured decision requests but never ask the user directly.
- Each worker must operate in implementation-only/no-shipping mode unless the task is explicitly artifact-only.
- Assign exactly one Jira subtask or standalone Jira issue per worker when Jira is the backlog source.
- Forbid workers from staging, committing, applying patches, changing branches,
  managing worktrees, pushing, opening PRs, mutating Jira, requesting
  reviewers, merging, or transitioning issues.
- Require structured blocker reporting in the worker return contract.
- Start or update compact timing telemetry with `scripts/record_run_timing.py`; never store prompts, source text, logs, or secrets in timing records.
- Load `references/lightweight-supervision.md` for Luna. Require no checkpoint
  from `luna`. For deep work, launch `luna_xhigh_discovery` read-only, validate
  its single exact terminal checkpoint, reject unchanged multi-file ownership
  manifests or planned files without file-specific evidence, and automatically
  launch `luna_xhigh` with ownership narrowed to the accepted manifest. Keep
  detailed action tracing diagnostic-only.

7. **Review Reconcile**
- Load `references/gates-and-reconciliation.md`.
- Read each worker result, changed-file summary, verification output, blockers, and branch/base facts.
- Inspect real diff filesystem state before trusting worker reports.
- Build the observation with `scripts/capture_worker_observation.py` against
  the sealed `baseline_tree`, so inherited dependency changes are excluded and
  any worker index mutation fails closed. Export accepted mutable deltas with
  `scripts/export_worker_patch.py`; its manifest binds ownership, baseline,
  dependencies, content digests, contract, and patch hash. Attach available
  command evidence, then run `scripts/evaluate_worker_run.py` for Spark, Luna, and Luna
  xhigh. A `contract_violation` never counts as verification or readiness;
  preserve the code for inspection. `awaiting_certification` cannot advance
  until every contract-required independent certificate is attached.
- Treat absent pre-return validator command evidence as a contract violation;
  do not repair or infer a malformed worker terminal on the worker's behalf.
- Run required review and verification gates before marking any unit release-ready.
- Only for `high` or `critical` assurance, load
  `references/review-coordination.md`. Distinct high-risk boundaries—not file
  count, surface count, or available personas—admit coordinated reviewers.
  Compile the root-owned
  review plan with `plan_review_wave.py`, validate every reviewer terminal,
  ingest findings through the digest-guarded registry, and run only the
  targeted validation wave authorized by the compiled plan. Do not let workers
  mutate the shared registry or hand-compose canonical finding IDs.
- Validate every Reviewer, Security Sentinel, Targeted Validator, and Fixer
  return against its role-specific closed shape before accepting it. A missing
  principle, finding ID, mapping, evidence field, or required empty collection
  is a protocol failure to correct in that worker session, not a root inference.
- Persist each accepted Reviewer or Fixer terminal immediately with
  `scripts/persist_role_terminal.py` before registry ingestion or another
  dispatch. On interruption, treat a validated recovery artifact as
  non-certifying redispatch context and prefer a fresh worker unless runtime
  continuity is proven.
- Load `references/automated-wave-control.md`. Compute the aggregate fingerprint
  with `scripts/verification_evidence.py`, decide reuse against the evidence
  registry, and run aggregate verification only when the decision is `run`.
  Execute and record every aggregate result through the script's `run`
  subcommand, which derives pass/fail from exit codes. Never accept a claimed
  result or decide reuse by inspection.
- If a leaf check is not covered by aggregate verification and lacks
  runtime-audited command evidence, execute it through the root-owned evidence
  runner before readiness. Record the observed exit code even when it
  contradicts the worker's report.
- When a failed check is described as baseline, environmental, or unowned,
  load `references/role-recoverability.md` and classify root-captured evidence
  with `scripts/classify_verification_result.py`. Missing worktree dependencies
  are environmental evidence, never a baseline failure.
- Reconcile blockers using `references/blocker-ledger.md`: record non-fatal blockers, mark only affected units blocked/deferred, and continue independent ready units.
- Reconcile each nested Compound result against its canonical state and artifacts. Treat swarm snapshots as stale observations, not authority.
- Deduplicate decision requests, ask one decision at a time in manual interactive flow, persist the answer in the canonical shared or item artifact, and resume every affected child.
- When the wave plan admitted an Integrator, use it to inspect merge order, dependency edges, stacked PR choreography, and cross-worker conflicts before release handoff.
- For staged topology, reconcile each stage before unlocking its dependents.
  Invalidate undispatched or active dependents when the foundation baseline
  changes, and run final aggregate verification only on the checkout that
  contains the recertified foundation plus every reconciled child.
- Apply accepted patch manifests in dependency order only in the authoritative
  Integrator worktree. Build Reviewer, Security, Fixer, Documenter, and
  Validator snapshots as fresh role-specific worktrees; aggregate verification
  runs on a disposable snapshot of the fully consolidated tree.
- Decide each unit status: `release-ready`, `needs-fix`, `blocked`, `deferred`, or `split-required`.
- Apply supported documentation, pre-release unit, and blocker status changes
  through `scripts/transition_swarm_state.py` with observed input digests.
  Generic `unit-status` intentionally refuses release-ready, handed-off, and
  merged; those require authoritative reconciliation or release evidence and
  remain host-owned until their dedicated compiler validates it.
- Close timing telemetry with phase durations, context bytes, review/fix rounds,
  verification fingerprint, evidence trust, scope violations, repeated
  verification, review findings, acceptance latency, and final status.
  Judge factory throughput primarily by root-observed acceptance latency,
  recertification cycles, and aggregate executions. Keep worker speed separate
  and label self-reported timing as indicative.

8. **Release Handoff**
- Confirm `documentation_gate.status == approved` before release handoff.
- Hand release-ready units to `krt-release-marshal`; do not duplicate its commit, PR, Jira, reviewer, or merge procedure.
- Do not hand off a `critical` unit until its review plan reports
  `approval_required` and the explicit approval is recorded through the manual
  flow or an autonomy ledger entry that names the unit and critical risk.
- Carry Jira key, work package review unit, suggested PR grouping, verification evidence, release notes, downstream-fix notes, and suggested Jira transition.
- Suggested Jira transitions are handoff context only. Seneschal does not execute them directly.
- State the resolved `jira_provider` and provider skill in the handoff. Do not substitute the sibling provider.
- In manual or guarded flow, stop at release-plan approval.
- In autonomous flow, pass the canonical autonomy ledger JSON path, expected contract hash, latest audit event, `jira_provider`, and only ledger-scoped mutation candidates to `krt-release-marshal`; do not ask the user during the run.

## Stop Conditions

Stop or ask direction when:

- Documentation gate is not approved and the requested action would seed Jira, dispatch workers, mutate code, or hand off release work.
- Manual flow requires direction for mutations, risky ambiguity, failed gates, unsafe overlap, scope creep, or no ready work.
- Autonomous flow must not interrupt for questions. Instead, record decision needs in `docs/swarm/blockers.yaml`, mark affected units blocked/deferred, skip uncovered mutation classes, and continue independent approved work.
- Autonomous flow stops only on runtime impossibility: no runnable independent work remains, credentials/tools are absent for every remaining path, isolation cannot be achieved for any unit, or continuing would violate an explicit deny rule in the autonomy ledger.

## Closeout

End with:

- Current mode and documentation gate status.
- Units dispatched, blocked, release-ready, or handed off.
- Non-fatal blockers recorded, high-risk blockers, and whether independent work remains.
- Branch/worktree/thread references when available.
- Verification and review evidence.
- Findings registry path and digest when coordinated review ran.
- Lane/profile and assurance/review decisions, plus the timing artifact path.
- Queue/state files updated.
- Exact next invocation.

For `wave-status`, run `scripts/render_swarm_status.py` and return its derived
panel without mutating queue state or creating a dashboard artifact.
