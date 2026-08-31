# Worktree Collaboration

Load this reference before planning, dispatching, reviewing, fixing, validating,
documenting, or consolidating worker output. Every worker invocation receives a
purpose-built Git worktree. A role is isolated even when it is read-only and
even when the same agent performs another role later.

## Role Matrix

| Role | Worktree mode | Starting snapshot | Permitted result |
|---|---|---|---|
| Planner / discovery | detached read-only | recorded source or dependency baseline | artifacts or terminal discovery only |
| Implementer | mutable, path-scoped | dependency baseline | owned working-tree patch |
| Reviewer | detached read-only | exact candidate tree | certificate and findings |
| Security reviewer | separate detached read-only | exact candidate tree | security certificate and findings |
| Targeted / CI validator | disposable verification | exact candidate or consolidated tree | machine-captured evidence |
| Fixer | mutable, path-scoped | confirmed-finding candidate | finding-to-change patch |
| Documenter | mutable, path-scoped | consolidated code baseline | owned documentation patch |
| Integrator | mutable authoritative consolidation | source plus accepted dependency patches | reconciled checkout and integration patch |
| Compound Master | isolated mutable or read-only by assigned phase | assigned unit baseline | bounded artifacts or patch |

The orchestrator owns every worktree, Git index, baseline, patch manifest, and
cleanup action. Workers may read Git state but must not stage, commit, switch or
create branches, push, rebase, merge, apply patches, create worktrees, or remove
worktrees. Release Marshal remains the only final commit/push/PR owner.

## Compile Workspace Assignments

Materialize one invocation entry for every role call, including recertification
or a second fixer pass; reuse of a previous path is forbidden. Compile it with:

```bash
rtk python3 <seneschal-skill-dir>/scripts/plan_worker_workspaces.py \
  --input <workspace-plan.json> > <compiled-workspaces.json>
```

The compiler validates the role/mode mapping, unique invocation IDs and paths,
candidate/dependency references, read-only ownership, path safety, and exactly
one authoritative Integrator workspace. Preserve its hash in wave state. A
Reviewer and Security reviewer for the same candidate still receive different
detached worktrees.

## Create And Seal A Baseline

Resolve and record the full source revision before creating any worktree. Root
creates the emitted path and branch/detached state. For a dependent or candidate
snapshot:

1. Start from the recorded source revision.
2. Apply accepted dependency patches in declared topological order with
   `git apply --index`.
3. Reject an unexpected patch hash, missing dependency, apply failure, fuzzy or
   three-way recovery, conflict, or changed path outside the dependency
   manifest.
4. Run `git write-tree` and record the resulting `baseline_tree`.
5. Leave the index untouched. The staged index is the immutable baseline and
   the working tree initially matches it.

This index baseline is intentional orchestration state, not a release commit.
Do not create hidden commits to move changes between workers. Do not calculate
a child delta by subtracting inherited files from a revision-wide diff.

The worker contract binds the source revision, baseline tree, ordered dependency
patch hashes, workspace ID, role, unit, and owned paths. Dispatch is forbidden
until the emitted worktree exists, its index tree matches `baseline_tree`, and
its path is unique to that invocation.

## Observe And Export Mutable Work

Root observes mutable output against the sealed index:

```bash
rtk python3 <seneschal-skill-dir>/scripts/capture_worker_observation.py \
  --repo-root <worker-worktree> \
  --base-revision <full-source-revision> \
  --baseline-tree <sealed-tree> \
  --input <partial-observation-outside-worktree.json> \
  --output <root-observation-outside-worktree.json>
```

The observer includes untracked files and fails closed when `git write-tree`
no longer equals the expected baseline, proving that the worker did not mutate
the index. Root then exports the delta and manifest:

```bash
rtk python3 <seneschal-skill-dir>/scripts/export_worker_patch.py \
  --repo-root <worker-worktree> \
  --metadata <root-owned-patch-metadata.json> \
  --patch-output <artifact-dir>/<invocation>.patch \
  --manifest-output <artifact-dir>/<invocation>-patch.json
```

The manifest binds workspace, worker, role, unit, source revision, baseline
tree/digest, ordered dependency patch hashes, owned paths, changed-file content
digests, contract hash, diff digest, patch hash, and manifest hash. Export fails
on an index mutation or unowned path. Store patches and manifests outside the
worker worktree.

## Review And Validation Snapshots

Build a read-only candidate snapshot from the source revision plus the exact
ordered dependency and candidate patches. Seal it with `git write-tree` and bind
the review assignment and certificate to that candidate tree, contract hash,
and diff digest. Run Reviewer and Security in separate worktrees so neither can
alter or contaminate the other's evidence. Enforce the runtime read-only
sandbox in addition to the Git contract.

Targeted and CI validators receive disposable worktrees built by the same
method. Root captures exact argv, exit code, and output. Destroying a validator
workspace after evidence capture does not invalidate its tree-bound evidence.

A Fixer never edits an Implementer worktree. Root creates a new mutable
worktree from the confirmed candidate snapshot, seals that index, narrows owned
paths to one defect cluster, and exports a new patch. Recertification receives
another fresh read-only candidate snapshot containing the accepted fix patch.

## Consolidation

Exactly one Integrator worktree is authoritative for consolidation. Root—not
the Integrator worker—applies accepted patches with `git apply --index` in
topological order. Stop on a missing manifest, hash mismatch, stale baseline,
overlap without an explicit owner, or apply conflict. Never silently choose a
winner or use a three-way merge.

After every accepted patch, verify the resulting index tree and record the
applied manifest hash. If integration code or documentation remains, reset the
working tree to match the new sealed index, dispatch the named mutable owner,
observe/export its delta, and apply that patch through the same gate. Aggregate
verification and final review run only on a fresh snapshot of the fully
reconciled consolidation tree.

Release Marshal receives the consolidated checkout plus ordered patch
manifests and verification/review evidence. Leaf branches and worktrees are
never independently released.

## Lifecycle And Failure Rules

Queue state records `workspace_id`, path, branch/detached mode, role, source
revision, baseline source, baseline tree, dependency and candidate manifest
hashes, status, patch manifest, and cleanup status for every invocation.

- Never dispatch until the required baseline gate passes.
- Invalidate undispatched and active descendants when an accepted ancestor
  patch changes; rebuild them from the new ordered manifests.
- Preserve a contract-violating or conflicted worktree and its root evidence for
  diagnosis; do not consolidate it.
- Remove successful disposable review/validation worktrees after their
  artifacts are durable. Remove mutable worktrees only after consolidation and
  release handoff evidence make them reproducible.
- Root verifies a path belongs to the run-specific worktree parent before
  cleanup. Never recursively delete a guessed, broad, or unresolved path.
- `git worktree prune` is housekeeping after explicit removals, not the cleanup
  mechanism itself.

When worktree creation, baseline sealing, or safe consolidation is unavailable,
stop the affected dependency chain. Serial execution does not waive isolated
workspace or evidence requirements.
