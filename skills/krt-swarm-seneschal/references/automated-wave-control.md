# Automated Wave Control

Load this reference when computing aggregate verification, selecting adaptive
concurrency, or rendering current factory status. These tools derive decisions
from canonical inputs; they do not create a second orchestration authority.

## Verification Fingerprint And Evidence

Compute the fingerprint from the intended base revision, sorted real changed
paths and their content digests, and ordered aggregate commands:

```bash
rtk python3 <seneschal-skill-dir>/scripts/verification_evidence.py compute \
  --repo-root <repo-root> \
  --base-revision <full-revision> \
  --path <changed-path> \
  --verification-command <exact-command> \
  --output docs/orchestration/runs/<run-id>/<wave-id>-fingerprint.json
```

Before running aggregate verification, decide reuse against the canonical
registry:

```bash
rtk python3 <seneschal-skill-dir>/scripts/verification_evidence.py decide \
  --repo-root <repo-root> \
  --registry <root-owned-registry-outside-worktree> \
  --fingerprint <fingerprint.json> \
  --expected-fingerprint <trusted-wave-handoff-sha256> \
  --expected-record-digest <trusted-registry-head-or-none> \
  --max-age-seconds <project-policy-seconds>
```

- `reuse` is valid only for the exact passing fingerprint within the declared
  age policy.
- `run` with `evidence-missing`, `prior-evidence-failed`, or `evidence-stale`
  requires aggregate verification.
- A modified fingerprint document is invalid; do not fall back to worker prose.

Execute the fingerprinted commands and record observed results:

```bash
rtk python3 <seneschal-skill-dir>/scripts/verification_evidence.py run \
  --repo-root <repo-root> \
  --registry <root-owned-registry-outside-worktree> \
  --fingerprint <fingerprint.json> \
  --expected-fingerprint <trusted-wave-handoff-sha256> \
  --timeout-seconds <per-command-limit> \
  --evidence-dir <root-owned-path-outside-the-worktree>
```

The runner uses parsed argv without a shell, derives pass/fail from exit codes,
captures one log per command, and rejects any unlisted worktree change. Its
evidence directory must sit outside the worktree so runner-owned logs cannot
contaminate the diff. There is no caller-supplied result. The
registry replaces the same fingerprint record rather than appending duplicates.

After a fix or recertification cycle, recompute the fingerprint first. Reuse an
unchanged passing fingerprint; do not rerun aggregate verification merely
because another review certificate arrived. A changed diff or aggregate command
set produces a new fingerprint and must pass the normal decision path.

## Throughput Objective

Optimize the factory for root-observed time to accepted, release-ready work—not
for the shortest individual worker return. Track implementation duration
separately from end-to-end acceptance latency, fix/recertification cycles, and
aggregate executions. Weak discovery or invalid commands caught after dispatch
are factory defects even when the worker itself returned quickly.

Use stricter discovery and command preflight before increasing concurrency or
reducing reasoning effort. Two avoided review cycles usually matter more than a
small reduction in worker runtime. Treat worker-reported phase durations as
indicative. Compare or tune throughput from root/runtime timestamps and audited
command events when available, and keep self-reported samples labeled rather
than presenting them as rigorous benchmarks.

## Adaptive Wave Plan

Build an adaptive input from runtime capacity, approval/ledger authority,
review capacity, prior wave results, blockers, unresolved dependencies, owned
paths, risk surfaces, and each implementation request's assurance tier. Then
run:

```bash
rtk python3 <seneschal-skill-dir>/scripts/plan_adaptive_wave.py \
  --input <adaptive-plan.json> \
  --expected-scale-authorization-digest <trusted-handoff-sha256>
```

The expected authorization digest is an out-of-band trusted handoff from the
root-observed user approval or validated autonomy ledger. Never derive it from
the adaptive plan being checked.

Adaptive-plan schema version 2 requires `assurance_tier` on every request.
Older queue units remain readable, but classify them before producing a new
adaptive plan rather than inferring assurance from their implementation lane.

The planner:

- defaults to two Implementers;
- permits three after two consecutive clean green waves and four after four,
  only when a digest-valid `scale_authorization` artifact permits it;
- drops to one after a failed/partial wave;
- charges review capacity by assurance demand (`low: 0`, `medium: 1`,
  `high: 2`, `critical: 3`) instead of charging every Implementer equally;
- lets low-assurance work continue when specialist review capacity is occupied;
- rejects blocked/dependent requests, overlapping owned paths, and overlapping
  auth/data/migration/public-contract/dependency/generated/release/security
  surfaces;
- passes the surviving requests to the global slot allocator, preserving its
  reserve and functional role caps.

For a compiled staged topology, invoke the adaptive planner once per emitted
wave, not once for the unsplit parent. Before foundation reconciliation,
dependent IDs remain in `unresolved_dependencies`. After root records the exact
release-ready foundation baseline, remove only satisfied edges and submit the
newly ready children. A consumed stable foundation contract belongs in worker
context; do not repeat its `public-contract` mutation risk on children that
cannot edit it.

The returned allocation is the dispatch authority for that wave. Do not add a
worker manually after the adaptive plan.

Adaptive allocation owns capacity, not post-implementation review
partitioning. Only `high` and `critical` units enter `review-coordination.md`
and `plan_review_wave.py`; do not infer review depth from available slots,
reviewer count, file count, or code-surface count.

## Compact Status

Render a read-only panel from queue state, blocker ledger, evidence registry,
and the latest allocation:

```bash
rtk python3 <seneschal-skill-dir>/scripts/render_swarm_status.py \
  --queue docs/swarm/queue-state.yaml \
  --blockers docs/swarm/blockers.yaml \
  --evidence <root-owned-registry-outside-worktree> \
  --allocation <adaptive-allocation.json>
```

Use `--format json` for automation. The panel derives unit counts, current wave,
gates, blockers, slots, and evidence. Never persist its output as another state
file. YAML input requires PyYAML; JSON input remains dependency-free.
