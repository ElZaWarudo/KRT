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
  --registry docs/orchestration/verification-evidence.json \
  --fingerprint <fingerprint.json> \
  --max-age-seconds <project-policy-seconds>
```

- `reuse` is valid only for the exact passing fingerprint within the declared
  age policy.
- `run` with `evidence-missing`, `prior-evidence-failed`, or `evidence-stale`
  requires aggregate verification.
- A modified fingerprint document is invalid; do not fall back to worker prose.

After running, record the result and durable evidence references:

```bash
rtk python3 <seneschal-skill-dir>/scripts/verification_evidence.py record \
  --registry docs/orchestration/verification-evidence.json \
  --fingerprint <fingerprint.json> \
  --result <passed|failed> \
  --evidence <path-or-reference>
```

The registry replaces the same fingerprint record rather than appending
duplicate executions. It stores no command output or source content.

## Adaptive Wave Plan

Build an adaptive input from runtime capacity, approval/ledger authority,
review capacity, prior wave results, blockers, unresolved dependencies, owned
paths, and risk surfaces. Then run:

```bash
rtk python3 <seneschal-skill-dir>/scripts/plan_adaptive_wave.py \
  --input <adaptive-plan.json>
```

The planner:

- defaults to two Implementers;
- permits three after two consecutive clean green waves and four after four,
  only when `scale_authorized` is true;
- drops to one after a failed/partial wave or review lag;
- caps implementation by actual review capacity;
- rejects blocked/dependent requests, overlapping owned paths, and overlapping
  auth/data/migration/public-contract/dependency/generated/release/security
  surfaces;
- passes the surviving requests to the global slot allocator, preserving its
  reserve and functional role caps.

The returned allocation is the dispatch authority for that wave. Do not add a
worker manually after the adaptive plan.

## Compact Status

Render a read-only panel from queue state, blocker ledger, evidence registry,
and the latest allocation:

```bash
rtk python3 <seneschal-skill-dir>/scripts/render_swarm_status.py \
  --queue docs/swarm/queue-state.yaml \
  --blockers docs/swarm/blockers.yaml \
  --evidence docs/orchestration/verification-evidence.json \
  --allocation <adaptive-allocation.json>
```

Use `--format json` for automation. The panel derives unit counts, current wave,
gates, blockers, slots, and evidence. Never persist its output as another state
file. YAML input requires PyYAML; JSON input remains dependency-free.
