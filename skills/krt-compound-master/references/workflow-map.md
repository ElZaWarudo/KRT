# Workflow Map

Load for artifact generation and high-level resume decisions. Load phase-specific execution references only when the workflow reaches execution.

## Step 0 - Preflight

Load `role-and-runtime.md`. Resolve roles, runtime/delegation availability, repo status, integration base, working tree, production posture, and Jira posture. Do not print tokens.

In `mode:resume`, compact or selectively load state before broad ingestion when state would crowd context.

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

## Step 2 - Roadmap Review

Review the roadmap with `document_review`. Fix blockers without inventing behavior. Ask only when findings change scope, behavior, dependency order, or PR strategy.

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

Invoke `plan` for each reviewed `planning_input_path`. Verify stable U-IDs, dependencies, repo-relative paths, test scenarios, and verification criteria. Review plans until no blocking findings remain.

## Step 5 - Derive Work Packages

Load `artifact-templates.md`. Create delivery packages under `docs/work-packages/RDM-###-<roadmap-item-slug>/` with focused review units.

Each package must:

- Align included/excluded/split/deferred origin plan units.
- Define review units as the normal PR/Jira handoff units.
- Justify any review unit that mixes runtime logic with large generated artifacts or orchestration docs.
- Pass `<compound-master-skill-dir>/scripts/check_work_package.py`.
- Pass `document_review`.

If `mode:artifacts`, stop after artifact closeout with exact next invocation, including `review-unit:<RU#>` when known.

## Step 6 - Execution Wave Planning

Load `execution-flow.md`, then `execution-delegation.md`. Resolve autonomy/delegation and classify packages and review units as independent, dependent, overlapping, high-risk, and production-sensitive.

Execute serially unless `parallel:true`, `autonomy:high`, `worktree-policy:auto|required`, dependencies, isolation, and non-overlapping scopes make parallel execution safe. For serial execution, switch branches in the current checkout; reserve worktrees/checkouts for policy-allowed parallel mutation or explicit isolation needs.

## Step 7 - Execute Review Unit

Load `execution-delegation.md`. Invoke `work` in implementation-only/no-shipping mode for the selected review unit. Start Security Watch for high-risk review units. Inspect worker output, update state, run/attempt verification, and continue to review.

## Step 8 - Code Review And Fix Loop

Load `review-security-ci.md`. Invoke `code_review`, prefer autofix when safe, retry with report-only/inline only if runtime refuses agent launch. Loop findings at or above threshold through work and review. Stop after three blocked rounds.

## Step 9 - Security Sentinel Gate

Load `review-security-ci.md`. Run security review for high-risk review units, feeding Security Watch notes into the gate. Blockers loop back through work and code review before release handoff.

## Step 10 - CI Break-Prevention And Escalation

Load `impact-verification.md` and `review-security-ci.md`. Record contract-drift scan, consumer tests, surface-aware verification, and CI-only gaps. Do not poll CI in a loop.

## Step 11 - Release Marshal Handoff

Load `release-handoff.md`. Handoff the completed review unit to `krt-release-marshal`; do not duplicate its procedures.

When an active autonomous ledger exists, include the ledger path, allowed mutation classes, latest audit hash, executor mode, and requested autonomous mutation classes in the handoff. Handoff does not bypass Release Marshal validators.

## Step 12 - Continue Waves Or Finish

Refresh state, dependencies, and integration base after each PR handoff. If a parent PR is pending, fetch and inspect the integration base before continuing from the parent review-unit branch. Record stack/dependency context in state, not PR body.

For autonomous stacked PR delivery, run a merge checkpoint after each PR handoff or resume: scan contract-scoped PRs, order parent before child, hand merge candidates to Release Marshal one at a time, refresh downstream base/check/review/Jira state after each parent merge, and transition Jira to `Hecho` only after the linked PR is proven merged.

## State Archive Hygiene

Invoke `state_archivist` after major gates when state grows noisy: roadmap review, artifact set review, implementation/review/security gates, before long closeouts, after PR handoff, and before resume loads large state.
