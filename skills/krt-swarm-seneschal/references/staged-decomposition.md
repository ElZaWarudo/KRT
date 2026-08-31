# Staged Decomposition

Load this reference when one broad implementation unit contains a small shared
API or architectural seam plus multiple downstream surfaces. The objective is
to serialize only the dependency-defining slice, then fan out work whose
post-foundation ownership is disjoint.

Do not keep a unit monolithic merely because every child cannot start in the
first wave. Prefer this topology when the shared contract can be explicit and
tested:

```text
foundation -> parallel dependents -> chained dependents -> integration
```

## Admission Test

Attempt staged decomposition when all are true:

- discovery identifies a non-empty set of shared API or seam-defining paths;
- those paths can belong to one smallest viable foundation unit with focused
  contract tests and any trigger-required review or security gate;
- at least two downstream implementation surfaces have materially disjoint
  write ownership after the foundation stabilizes;
- downstream workers consume foundation paths as read-only context instead of
  editing them;
- every generated artifact and shared integration path has one named owner;
- dependency order can be represented with queue `depends_on` edges; and
- the reconciled checkout can run one root-owned aggregate verification set.

Serialization remains correct when the shared API cannot be settled and tested,
downstream workers must edit the same central implementation files, generated
ownership is ambiguous, isolation cannot materialize and observe an immutable
foundation baseline, or the
final verification surface cannot be reconciled safely.

## Compile The Topology

Root or a triggered Planner performs one read-only decomposition pass before
materializing implementation contracts. Identify the parent unit's complete
owned-path set, shared API paths, the foundation, dependent units, integration
ownership, exact focused commands, and aggregate commands. Compile it with:

```json
{
  "schema_version": 1,
  "parent_unit_id": "broad-unit",
  "parent_owned_paths": [
    "src/contract.py",
    "src/runtime.py",
    "src/client.py",
    "src/glue.py"
  ],
  "shared_api_paths": ["src/contract.py"],
  "foundation": {
    "id": "foundation",
    "title": "Settle shared contract",
    "owned_paths": ["src/contract.py"],
    "depends_on": [],
    "focused_commands": ["rtk pytest tests/test_contract.py"],
    "generated_paths": []
  },
  "dependents": [
    {
      "id": "runtime",
      "title": "Implement runtime",
      "owned_paths": ["src/runtime.py"],
      "depends_on": ["foundation"],
      "focused_commands": ["rtk pytest tests/test_runtime.py"],
      "generated_paths": []
    },
    {
      "id": "client",
      "title": "Integrate client",
      "owned_paths": ["src/client.py"],
      "depends_on": ["foundation"],
      "focused_commands": ["rtk pytest tests/test_client.py"],
      "generated_paths": []
    }
  ],
  "integration": {
    "id": "integration",
    "title": "Reconcile shared glue",
    "owned_paths": ["src/glue.py"],
    "depends_on": ["runtime", "client"],
    "focused_commands": ["rtk pytest tests/test_glue.py"],
    "generated_paths": []
  },
  "aggregate_commands": ["rtk pytest tests/"]
}
```

```bash
rtk python3 <seneschal-skill-dir>/scripts/plan_staged_decomposition.py \
  --input <staged-plan.json> \
  > <staged-topology.json>
```

The compiler fails closed unless:

- foundation owns every shared API path and has no staged dependency;
- at least two dependent units exist and every one transitively descends from
  foundation;
- staged ownership is a complete, non-overlapping partition of parent paths;
- generated paths belong to their single unit owner;
- every mutating unit has focused verification;
- integration depends on every dependent unit; and
- aggregate verification is non-empty and root-owned.

It emits a content hash, child units, and topological cohorts. Cohorts explain
potential concurrency; they are not batch barriers. Preserve the topology
artifact with the wave artifacts. Mark the original parent `split-required`
and create its child queue units using the emitted `depends_on` edges; do not
also dispatch the parent.

## Execute The Stages

1. Dispatch only foundation. Classify its lane from its own risk; a public
   contract or architecture decision normally makes it deep.
2. Reconcile foundation through scope, focused verification, and every triggered
   review/security gate. Dependents remain ineligible until foundation is
   `release-ready` and root records an immutable baseline containing the source
   base revision, root-observed foundation diff digest, and isolation reference.
3. Derive each newly eligible dependent isolation target from that exact
   baseline. The isolation mechanism may use a commit, patch snapshot, cloud
   snapshot, or equivalent only when root can observe it as the child's clean
   starting state. Put shared API paths in `required_context`, not `owned_files`.
4. Classify every child independently. A child that only consumes a settled
   public contract does not inherit foundation's deep lane or public-contract
   mutation risk. If it must change the contract, stop, create, and recertify a
   new foundation baseline instead of editing through the
   dependent.
5. Feed only dependency-ready children to `plan_adaptive_wave.py`. Dispatch
   disjoint children concurrently; unlock a later child as soon as its exact
   dependencies reconcile rather than waiting for unrelated siblings in the
   same topological cohort.
6. After all dependents reconcile, run the integration unit when it owns files.
   If it owns no files, root performs integration reconciliation directly. An
   admitted Integrator may coordinate ordering but does not replace a mutating
   implementation owner.
7. Compute aggregate evidence from the final reconciled checkout. Apply the
   same review, security, state, and release gates that a monolithic unit would
   have required.

## Ownership Rules

- Foundation owns only shared contract/seam files and the tests needed to prove
  that contract. It does not absorb downstream implementation for convenience.
- Downstream units may read but never edit foundation paths.
- A generated artifact and its generation command have exactly one child owner.
- Reserve cross-unit glue files for the integration unit; do not give them to
  foundation and every dependent.
- No worker contract spans two concurrently executable children.
- If a downstream discovery reveals a genuine foundation change, invalidate the
  affected topology, stop dependent dispatch, revise and recertify foundation,
  then recompile eligibility from the new revision.

## Queue And Evidence

Use existing queue fields rather than a second state model:

- `depends_on` carries the emitted dependency edges;
- `affects_dependents` names children invalidated by a foundation change;
- parent status is `split-required` and child statuses progress normally;
- wave history records the topology artifact/hash and exact foundation baseline;
- each child records narrow ownership and focused evidence; and
- the final wave owns the aggregate fingerprint and evidence registry.

An autonomous instruction to maximize productive parallelism authorizes this
decomposition analysis and the resulting dependency-ready waves only within the
existing documentation and autonomy gates. It does not permit speculative API
decisions or overlapping writes.

Materialize every stage through `worktree-collaboration.md`. Seal foundation
and dependency patches in each child's index, record `baseline_tree`, and
observe only working-tree changes against that index. If the runtime cannot
provide those isolated, root-observable baselines without violating commit or
release ownership, stop the affected dependency chain; do not improvise hidden
commits or subtract inherited diffs from evidence.
