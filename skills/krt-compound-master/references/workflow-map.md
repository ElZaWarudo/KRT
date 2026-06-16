# Workflow Map

Load for artifact generation and high-level resume decisions. Load phase-specific execution references only when the workflow reaches execution.

## Step 0 - Preflight

Load `role-and-runtime.md`. Resolve roles, runtime/delegation availability, repo status, integration base, working tree, production posture, and Jira posture. Do not print tokens.

In `mode:resume`, compact or selectively load state before broad ingestion when state would crowd context.

Before planning new work or resuming old work, reconcile live artifacts. If `docs/orchestration/compound-master-state.md`, the active work package, or linked roadmap/plan artifacts disagree with the current branch/base, dependency state, blocker set, review status, next invocation, or PR/Jira reality, repair those files first and record the correction.

Worktree posture:

- Default to `worktree-policy:avoid`.
- Record the policy in state before execution.
- Do not treat `parallel:true` as permission to create worktrees. If parallel mutation requires worktrees while policy is `avoid`, run the review units serially or ask for an explicit policy change.

Autonomous posture:

- If `autonomous-ledger:<path>` is present, load `autonomous-mode.md` and `autonomy-ledger-schema.md`.
- Run the ledger validator before any autonomous external mutation planning.
- Resolve the Release Marshal mutation executor and required class validators before autonomous shipping starts.
- If the ledger, executor, validator, live-state input, audit path, or enforcement boundary is unavailable, record `autonomous-validation-only` or `autonomous-blocked` and continue only according to `autonomous-flow-matrix.md`.

Jira posture:

- Resolve `jira-policy` before asking workflow questions; default to `optional`.
- For `optional`, treat Jira as important traceability but non-blocking. Detect existing issue keys/URLs and required env var presence, prepare semantic Spanish handoff text, and continue if Jira is unavailable.
- For `required`, block before shipping if Jira role, context, or configuration needed for safe mutation is missing.
- For `skip`, record intentional omission and avoid Jira lookup/mutation.

Production posture:

- Accept explicit argument first.
- Otherwise infer only from strong evidence: production deploy docs, live config, incidents/runbooks, release history, real user/data language, or explicit prototype/sandbox language.
- If evidence is mixed or weak, set `production:unknown` and ask before risky persistence, API, auth, tenant, deployment, deletion, migration, or workflow changes.
- Record posture, evidence, confidence, and consequences in state and downstream artifacts.

## Step 1 - Roadmap Generator Gate

Invoke `roadmap_generator`. It must return exactly one:

```text
artifact_kind: roadmap | readiness-report
artifact_path: docs/...
```

If readiness report, update state and stop with a context-blocked closeout. If roadmap, update state and continue.

After each roadmap/readiness result, refresh state plus any touched orchestration artifact before continuing or stopping. Do not accumulate stale statuses for later cleanup.

## Step 2 - Roadmap Review

Review the roadmap with `document_review`. Fix blockers without inventing behavior. Ask only when findings change scope, behavior, dependency order, or PR strategy. Stop after three blocked review rounds and escalate with the blocker and next question.

## Step 3 - Brainstorm Per Roadmap Item

For each roadmap item in dependency order, invoke `brainstorm` for that item only. Keep it interactive unless the current invocation explicitly requested non-interactive discovery.

The brainstorm gate finishes with:

```text
brainstorm_path: docs/brainstorms/...
planning_input_path: docs/brainstorms/...
requirements_decisions: captured | assumption-backed
open_decisions: none | [...]
```

Review `planning_input_path` before planning. If brainstorm was skipped, record the override and assumptions.

## Step 4 - Plan Per Reviewed Requirements Artifact

Invoke `plan` for each reviewed `planning_input_path`. Verify stable U-IDs, dependencies, repo-relative paths, test scenarios, and verification criteria. Review plans until no blocking findings remain or three blocked review rounds elapse, then escalate with the blocker and next question.

## Step 5 - Derive Work Packages

Load `artifact-templates.md`. Create delivery packages under `docs/work-packages/RDM-###-<roadmap-item-slug>/` with focused review units.

Each package must:

- Align included/excluded/split/deferred origin plan units.
- Define review units as the normal PR/Jira handoff units.
- Justify any review unit that mixes runtime logic with large generated artifacts or orchestration docs.
- Pass `<compound-master-skill-dir>/scripts/check_work_package.py`.
- Pass `document_review`.

If `mode:artifacts`, stop after artifact closeout with exact next invocation, including `review-unit:<RU#>` when known.

## Step 5b - Reviewability Gate

Before locking review-unit/PR boundaries, diagnose the proposed decomposition from the reviewer's seat. This gate optimizes for a usable human review, not for maximal atomicity or one-to-one Jira fit. Atomicity and Jira shape are inputs, not goals.

For the proposed sequence, confirm:

- Each PR can be understood, verified, and merged on its own, without holding a deep mental stack of sibling PRs.
- The open stacked-PR chain stays within the cap: target <=2, hard max 3 open unmerged PRs (see Step 12 governance).
- Each split earns its keep through independent value, verification, or risk for the reviewer. "Atomic is tidier" and "one PR per Jira subtask" are not sufficient reasons; prefer the coarsest independently-mergeable capability slice that still verifies on its own.
- Feedback stays traceable: a later unit that fixes a surface an earlier still-open PR flagged is recorded as a downstream-fix note, not silently buried.
- The plan avoids both failure modes at once: a deep stack of micro-PRs, and a deferred mega-consolidation PR that swallows an abandoned stack.

Record the chosen granularity, the reviewer-experience rationale, and the open-stack plan in the work package and state. If the only justification for a split is atomicity or Jira shape, coarsen to the independently-mergeable capability slice. If reviewability cannot be met within the cap, restructure the packages before execution.

## Step 6 - Execution Wave Planning

Load `execution-flow.md`, then `execution-delegation.md`. Resolve autonomy/delegation and classify packages and review units as independent, dependent, overlapping, high-risk, and production-sensitive.

Execute serially unless `parallel:true`, `autonomy:high`, `worktree-policy:auto|required`, dependencies, isolation, and non-overlapping scopes make parallel execution safe. For serial execution, switch branches in the current checkout; reserve worktrees/checkouts for policy-allowed parallel mutation or explicit isolation needs.

## Step 7 - Execute Review Unit

Load `execution-delegation.md`. Invoke `work` in implementation-only/no-shipping mode for the selected review unit. Start Security Watch for high-risk review units. Inspect worker output, update state, run/attempt verification, and continue to review.
Update `compound-master-state.md` and the active work-package artifact in the same turn as the worker result. Sync implementation status, blockers, changed files/tests, branch/base facts, and the next review action before launching review.

## Step 8 - Code Review And Fix Loop

Load `review-security-ci.md`. Invoke `code_review`, prefer autofix when safe, retry with report-only/inline only if runtime refuses agent launch. Loop findings at or above threshold through work and review. Stop after three blocked rounds.
When review findings or fixes change readiness, package scope, verification state, or release inputs, update the state and work-package files before the next review loop or handoff.

## Step 9 - Security Sentinel Gate

Load `review-security-ci.md`. Run security review for high-risk review units, feeding Security Watch notes into the gate. Blockers loop back through work and code review before release handoff.

## Step 10 - CI Break-Prevention And Escalation

Load `impact-verification.md` and `review-security-ci.md`. Record contract-drift scan, consumer tests, surface-aware verification, and CI-only gaps. Do not poll CI in a loop.

## Step 11 - Release Marshal Handoff

Load `release-handoff.md`. Handoff the completed review unit to `krt-release-marshal`; do not duplicate its procedures.

When an active autonomous ledger exists, include the ledger path, allowed mutation classes, latest audit hash, executor mode, and requested autonomous mutation classes in the handoff. Handoff does not bypass Release Marshal validators.

## Step 12 - Continue Waves Or Finish

Refresh state, dependencies, and integration base after each PR handoff. If a parent PR is pending, fetch and inspect the integration base before continuing from the parent review-unit branch. Record stack/dependency context in state, not PR body.

Open-stack governance: keep at most 2-3 open unmerged PRs in one stacked chain (target <=2). When the chain reaches the cap, do not extend it. Either wait for the parent PR to merge into the integration base and re-base the next unit on the refreshed base, or collapse the pending chain onto the integration base and continue from there. Never accumulate a deep chain of unmerged stacked PRs, and never resolve an over-deep chain by abandoning it for one mega-consolidation PR.

Collapsing merges PRs, not Jira: when a grouped or collapsed PR covers several review units, keep one Jira subtask per review unit under a shared parent and backlink them all from that PR. Jira stays at review-unit granularity for traceability even though the PR is the coarser reviewable slice.

Downstream-fix trace: maintain a per-open-PR register of at/above-threshold review findings in state. When a later review unit changes a surface that an earlier still-open PR's reviewer flagged, record `addresses finding from PR #X` in state and carry it into that PR's review/release notes so the earlier review is not lost.

For autonomous stacked PR delivery, run a merge checkpoint after each PR handoff or resume: scan contract-scoped PRs, order parent before child, hand merge candidates to Release Marshal one at a time, refresh downstream base/check/review/Jira state after each parent merge, and transition Jira to `Hecho` only after the linked PR is proven merged.

Autonomous `Hecho` requires, per issue, a Jira remote link matching the merged PR plus an exact done transition. For a grouped PR covering several review-unit subtasks under a shared parent, remote-link the merged grouped PR to the parent and to every covered subtask, then complete the parent and let the subtasks inherit: the executor transitions the parent to `Hecho` and fans `Hecho` out to each covered subtask, with every transition still validated individually (matching remote link + merged PR + exact done transition). Leave any issue whose remote link or done transition is missing or ambiguous for manual completion, record the gap, and do not force it. Manual/guarded backlink and `En Revisión` transition already fan out to every covered subtask.

## State And Artifact Hygiene

Keep the live state concise, but keep it current first. Invoke `state_archivist` after major gates when state grows noisy: roadmap review, artifact set review, implementation/review/security gates, before long closeouts, after PR handoff, and before resume loads large state.
