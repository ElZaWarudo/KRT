# Gates And Reconciliation

Use this reference after dispatching workers, when reviewing outputs, and before release handoff.

## Gate Ladder

For each unit:

0. **Compound inner gate when nested**
   - Load the child's canonical state path and active artifacts.
   - Confirm the observed queue snapshot matches the canonical state revision.
   - Require the relevant artifact, implementation, verification, review,
     security, and CI-prevention gates for the requested transition.
   - Do not substitute Seneschal review for a missing Compound gate.

1. **Scope gate**
   - Worker stayed inside included scope.
   - Excluded work remains untouched.
   - Any necessary scope expansion is recorded. Manual flow requires approval; autonomous flow marks broad expansion `split-required` unless the ledger allows it.
   - `changed_files` comes from the root-observed diff and passes
     `evaluate_worker_run.py` against the hashed contract. A scope violation
   preserves the code but invalidates the terminal evidence.
   - Root confirms the current index tree still equals the sealed baseline,
     then exports a baseline-bound patch manifest. An index mutation, unowned
     path, stale dependency hash, or patch hash mismatch fails this gate.

2. **Verification gate**
   - Each leaf ran only its assigned focused checks, or a material verification gap is recorded.
   - Seneschal/root ran aggregate or CI-equivalent commands once for the final
     wave fingerprint, or reused passing evidence for that exact fingerprint.
   - The fingerprint includes intended base, ordered changed paths and content
     digests, and ordered aggregate commands. Changed or stale fingerprints and
     failed prior evidence must run again.
   - `scripts/verification_evidence.py decide` returned `reuse`, or aggregate
     verification ran and its result was recorded in the canonical evidence
     registry. Manual fingerprint comparison is not gate evidence.
   - Changed contracts have consumer-aware checks.
   - Generated artifacts or docs were inspected when relevant.
   - Every readiness-bearing command has root-observed or runtime-audited exact
     argv, exit code, and output. Leaf prose and self-reported `passed`
     values are not gate evidence. Root executes focused checks that aggregate
     verification does not cover when no native command audit exists.

3. **Review gate**
   - `execution-lanes.md` was used to decide whether a Reviewer trigger exists.
   - When triggered, independent review ran and maps to the unit contract.
   - When not triggered, the wave records the mechanical/docs-only reason; it
     does not create an empty Reviewer stage.
   - Findings at or above threshold were fixed or explicitly deferred.
   - Every contract-required Reviewer certificate names a different actor, the
     exact contract hash, and the reviewed diff digest. Implementer prose cannot
     satisfy this gate.
   - When `review-coordination.md` is triggered, the compiled review plan covers
     every changed path through exactly one primary surface, every admitted
     reviewer terminal passes `validate_review_terminal.py`, and all queued
     capacity-limited assignments finish before coverage is complete.
   - Findings come from the root-owned digest-guarded registry. A required
     targeted validation wave evaluates canonical IDs through
     `evaluate_finding_validation.py`; validators do not mutate the registry.
   - No at-or-above-threshold confirmed or revised finding remains unresolved.
     Fixed findings bind focused evidence to the new root-observed diff digest;
     deferred findings remain explicit in release handoff.

4. **Security/production gate**
   - Security-sensitive units ran the security specialist or an explicit fallback.
   - High-risk direct deep units ran Security Watch during execution and the
     Security Sentinel Gate after the work-review loop; otherwise they must use
     the Compound Master security pipeline.
   - Production-sensitive units preserve compatibility unless manual approval or autonomy ledger policy explicitly allows a breaking change.
   - A required Security Sentinel certificate follows the same actor/hash/diff
     rules as Reviewer certification.

5. **State gate**
   - Queue status, branch/base facts, blockers, verification evidence, and downstream-fix notes are current.
   - Nested Compound state remains canonical; queue fields contain only a fresh observed projection.
   - Jira issue/subtask state, when relevant, is reconciled through the selected Jira provider skill.
   - Non-fatal blockers are recorded in `docs/swarm/blockers.yaml`.

6. **Release handoff gate**
   - `krt-release-marshal` receives the completed unit context.
   - The swarm seneschal does not commit, push, open PRs, mutate Jira, request reviewers, or merge unless routed through the release skill and a manual approval or autonomy ledger permits it.
   - Jira handoff context must name `jira_provider` as `cloud`, `server-datacenter`, or `none`. There is no default provider.

## Staged Topology Gates

For a topology compiled through `staged-decomposition.md`:

- Foundation must reach `release-ready` with focused contract evidence and all
  trigger-required review/security certificates before any dependent dispatch.
- Record the exact immutable foundation baseline: source base revision,
  root-observed diff digest, patch manifest hash, baseline tree, and workspace
  reference. Every dependent base and contract must bind to it and begin
  observation from a newly sealed worktree baseline.
- Reconcile each dependent independently. Unlock later children from their exact
  `depends_on` edges without waiting for unrelated siblings.
- A foundation baseline change invalidates stale dependent contracts and bases;
  do not reconcile their output against the new topology.
- Integration begins only after every dependent is release-ready. Aggregate
  verification binds the final combined diff and retains every review/security
  gate that the original monolithic unit would have required.

## Reconciliation Checklist

Load `worktree-collaboration.md`. Reconciliation happens through the one
authoritative consolidation worktree; leaf worktrees are evidence sources, not
merge destinations.

For each worker result:

- Fetch or inspect the actual changed files.
- Verify the workspace plan hash, source revision, baseline tree, ordered
  dependency/candidate patch hashes, and role-specific worktree mode.
- Evaluate the root observation with `scripts/evaluate_worker_run.py`; accept
  only `complete` as leaf certification evidence. Route
  `awaiting_certification`, `needs_fix`, and `contract_violation` literally.
- Compare changes to the unit contract.
- Identify shared files touched by multiple workers.
- Detect public contract, auth, data, dependency, config, or generated-artifact changes.
- Record verification commands and outcomes.
- Compare each leaf claim with machine-captured evidence. Preserve
  contradictions explicitly, trust the observed exit code, and route a claimed
  pass with a nonzero observed exit to `needs-fix`.
- When coordinated review ran, record the review-plan hash, findings-registry
  path and digest, exact-duplicate count, validator verdicts, and unresolved
  canonical finding IDs.
- Compare the recorded execution lane/profile to `execution-lanes.md` and reject
  silent reasoning-effort or worker substitutions.
- Record focused unit evidence separately from aggregate wave evidence and
  reuse only when the automated evidence decision returns `reuse`.
- Record timing phases, context bytes, review/fix rounds, evidence trust, scope
  violations, repeated verification, review findings, and acceptance latency with
  `scripts/record_run_timing.py`.
- Record blockers and whether they affect sibling units.
- Record elapsed-budget exhaustion and root interventions. Interrupt bounded
  workers when the return condition is already met, exploration repeats, or the
  deadline expires; do not reward delay with a broader assignment.
- Normalize nested `decision_request` entries, deduplicate them, and route them through the decision broker in `blocker-ledger.md`.
- Decide: `release-ready`, `needs-fix`, `blocked`, `deferred`, or `split-required`.
- Update `docs/swarm/queue-state.yaml` and `docs/swarm/blockers.yaml` when statuses or blockers change.

## Conflict Handling

If two workers changed the same surface:

1. Stop new dispatch for dependent units.
2. Identify which unit owns the surface.
3. Stop patch application in the consolidation worktree; never retry with
   fuzzy or three-way application.
4. Choose one of:
   - rebuild the dependent workspace from the newly accepted parent manifest
   - collapse into one reviewable PR if that improves reviewability
   - split one worker's change into a follow-up unit
4. Record the decision in queue state.

Do not resolve conflicts by creating one large unreviewable PR.

## Blocker Reconciliation

Use `blocker-ledger.md` when a worker reports a blocker.

- If the blocker affects only one unit, record it, mark that unit `blocked` or `deferred`, and continue with unrelated ready units.
- If the blocker affects a dependency, public contract, auth, data, or central technical foundation, stop dependent dispatch and continue only with independent work.
- If the blocker affects security, real DIAN compliance, productive accounting, productive payroll, or legal production exposure, record it as high risk and require resolution before production release.
- In manual flow, ask only when no ready independent work remains or the blocker can make the wave implement the wrong foundation.
- In autonomous flow, do not ask; record the blocker, stop dependent work, and continue unrelated units until no safe work remains.

## Release Handoff Packet

For each release-ready unit, prepare:

```text
Work package or source: <path/link>
Review unit or queue ID: <id>
Compound run ID: <run-id or none>
Canonical Compound state: <state-path or none>
Jira key: <key or none>
Current branch: <branch>
Intended base: <branch>
PR grouping: standalone | grouped | stacked
Covered units: <ids>
Jira policy: required | optional | skip
jira_provider: cloud | server-datacenter | none
Suggested PR title: <semantic title>
Suggested PR body bullets:
- <user-facing change>
Release notes:
- <user-facing release note>
Suggested commit grouping:
- <type(scope): summary> -- <surfaces> -- <reason>
Verification results for readiness:
- <command/result>
Impact/CI risk:
- <summary or not required>
Downstream-fix notes:
- <none or PR/finding mapping>
Suggested Jira transition:
- <transition name or none>
```

Pass this to `krt-release-marshal`. Do not include internal queue mechanics in public PR copy unless repo convention requires it.

Include the resolved `jira_provider` and matching skill in every handoff. Do not silently switch providers. Suggested Jira transitions are context only; Release Marshal and the selected Jira provider skill own confirmed or ledger-covered execution.

## Closeout Shape

Factory closeout should say:

```text
Factory status: <mode/status>
Wave: <name>
Completed:
- <unit>
Blocked:
- <unit>: <reason>
Blockers recorded:
- <blocker id>: <type>/<owner>/<status>
Release-ready:
- <unit>
Handed off:
- <unit>: <PR/Jira if available>
Updated state:
- <files>
Next invocation:
Use krt-swarm-seneschal ...
```
