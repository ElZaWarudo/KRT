# Lightweight Luna Supervision

Load this reference when dispatching or reconciling Luna workers. The objective
is to make deep-lane discovery a technical write barrier without introducing a
per-action event stream.

## Supervision Modes

| Profile | Mode | Checkpoint behavior |
|---|---|---|
| `luna` | `terminal-only` | no checkpoint |
| `luna_xhigh_discovery` | `read-only-discovery` | exactly one terminal checkpoint |
| `luna_xhigh` | `manifested-implementation` | no live checkpoint; edits only the accepted manifest |

Spark has no live supervision. Detailed read/action tracing is diagnostic-only
and must not run in ordinary waves.

## Two-Stage Deep Lane

Deep execution is two fresh worker invocations:

```text
luna_xhigh_discovery (read-only)
  -> validated discovery_complete
  -> luna_xhigh (workspace-write, narrowed manifest)
```

The discovery profile has runtime-enforced `sandbox_mode = "read-only"`. It
performs one discovery pass and returns exactly one terminal payload:

```yaml
event: discovery_complete
edit_path_found: true | false
planned_files: []
evidence_digest: brief concrete evidence
```

It sends no intermediate parent message. A valid terminal return makes the
checkpoint exactly-once for that invocation. When `edit_path_found` is true,
`planned_files` is non-empty and is a subset of the unit's `owned_files`. When
false, `planned_files` is empty. The checkpoint schema is closed: unknown fields,
including `contract_hash`, are invalid. Root binds the discovery invocation to
the contract hash at the observation level.

Discovery must narrow a multi-file ownership manifest rather than return it
unchanged. For every planned file, `evidence_digest` contains a line beginning
`edit <repo-relative-path> |` with at least one of `symbol=`, `pattern=`, or
`callers=`, plus `why=` explaining why that file must change. Use
`dependency <path> |` for
read-only evidence and `contingency <path> |` for a possible later scope
extension. Prefer an additive path around CRITICAL existing hubs; when one is
unavoidable, name the exact impacted symbols and explain why the additive path
is insufficient.

Root validates the checkpoint and immediately dispatches a fresh
`luna_xhigh` implementation worker. The implementation contract carries the
accepted checkpoint and narrows editable ownership to `planned_files`; it does
not repeat discovery. The dispatch itself is the editing capability. There is
no acknowledgement handshake and no permission change inside a live worker.

If discovery finds no safe edit path, root reconciles the unit as
`needs_review` and does not launch the implementation stage.

## Scope Changes

The implementation worker must not edit outside `planned_files`. If another
file becomes necessary, it stops and returns:

```yaml
status: needs_review
scope_extension:
  additional_files: []
  reason: concrete reason the manifest is insufficient
```

It does not edit the additional files and does not emit another checkpoint.
Root may create a new reviewed contract later; this version intentionally adds
no live scope-approval protocol.

## Root Observation

Materialize the executable contract first as described in
`executable-worker-contracts.md`. Root binds both deep invocations to the same
`contract_hash` in the observation; neither the exact checkpoint nor the exact
implementation terminal grows an extra hash field.

Root timestamps worker returns and the implementation dispatch, then inspects
the real diff. It builds a JSON observation for
`scripts/evaluate_luna_run.py`:

```json
{
  "schema_version": 1,
  "profile": "luna_xhigh",
  "started_at_ms": 1000,
  "owned_files": ["src/service.py", "src/config.py"],
  "changed_files": ["src/service.py"],
  "checkpoint_count": 1,
  "checkpoint": {
    "discovery_complete_at_ms": 5000,
    "edit_path_found": true,
    "planned_files": ["src/service.py"],
    "evidence_digest": "edit src/service.py | symbol=Service.run; why=the established additive path requires this implementation change.\ndependency src/config.py | symbol=Config.load; inspected only, no change required."
  },
  "discovery_returned_at_ms": 5000,
  "implementation_started_at_ms": 6000,
  "first_change_at_ms": 7000,
  "phase_duration_ms": {
    "discovery": 4000,
    "implementation": 8000
  },
  "verification_manifest": {
    "focused": ["pytest tests/test_service.py"],
    "natural": ["pytest tests/"],
    "max_retries_per_command": 1
  },
  "last_required_command_finished_at_ms": 30000,
  "returned_at_ms": 31000,
  "interventions_sent": ["dispatch_implementation"],
  "final": {
    "status": "done",
    "phase": "closeout",
    "remaining_actions": [],
    "terminal_ready": true,
    "acceptance_criteria_resolved": true,
    "last_required_command": "pytest tests/",
    "verification": {
      "attempted": [
        {
          "command": "pytest tests/test_service.py",
          "attempts": 1,
          "outcome": "passed"
        },
        {
          "command": "pytest tests/",
          "attempts": 1,
          "outcome": "passed"
        }
      ],
      "skipped": []
    },
    "verification_commands_run": [
      "pytest tests/test_service.py",
      "pytest tests/"
    ],
    "unowned_failures": []
  }
}
```

Use root/runtime timestamps rather than worker clocks. `checkpoint_count` is
the number of terminal discovery payloads actually received. `changed_files`
comes from inspection of the real isolation target, never from the worker
report. Root records `dispatch_implementation` only after the second worker was
successfully launched.

The evaluator rejects an absent or duplicate checkpoint, unknown fields, missing
or non-file-specific evidence, unchanged multi-file ownership manifests,
planned files outside ownership, implementation before a valid checkpoint, a
first change before the implementation dispatch, and changed files outside the
accepted manifest.

## Evaluation

For compatibility, the Luna-only checkpoint evaluator remains available:

```bash
rtk python3 <seneschal-skill-dir>/scripts/evaluate_luna_run.py \
  --input <observation.json> \
  --now-ms <root-clock-ms>
```

The evaluator returns one action:

- `continue`: wait for the active stage.
- `dispatch_implementation`: launch `luna_xhigh` immediately with the
  narrowed contract and record the dispatch once.
- `return_now`: terminal fields are complete but the implementation worker has
  not returned, or its elapsed budget is exhausted; tell it to return without
  another action.
- `complete`: accept the terminal result for reconciliation. A discovery with
  no edit path completes as terminal `needs_review` without an implementation
  dispatch.
- `contract_violation`: preserve the result and reconcile it as a bounded
  failure; do not trust its completion status.

The terminal implementation result accounts for every focused and natural
command exactly once as attempted or skipped. The evaluator rejects missing
commands, excess retries, a mismatched `last_required_command`, and
contradictory timestamps.

Before readiness, run the cross-lane evaluator with the executable contract:

```bash
rtk python3 <seneschal-skill-dir>/scripts/evaluate_worker_run.py \
  --contract <worker-contract.json> \
  --input <root-observation.json> \
  --now-ms <root-clock-ms>
```

It adds contract-hash verification, root-observed file scope for every lane,
command evidence and trust, acceptance evidence per criterion, and independent
certificates. Its `complete` action supersedes the compatibility evaluator for
readiness decisions.

## Timing Consolidation

Persist calculated metrics through the existing recorder:

```bash
rtk python3 <seneschal-skill-dir>/scripts/record_run_timing.py \
  <normal timing arguments> \
  --supervision-result <evaluation.json>
```

The evaluator supplies time to first change, discovery/implementation ratio,
commands outside the verification manifest, last-command-to-return latency,
and actual root actions. Only `complete` with terminal `done` or
`done_with_baseline_gaps` persists as `completed`; terminal `needs_review` or
`blocked` persists as `blocked`; `contract_violation` persists as `failed`;
intermediate actions remain `running`.

This design technically prevents discovery-stage writes. Manifest enforcement
after dispatch is fail-closed reconciliation based on the real diff because the
current runtime cannot grant path-scoped write tokens. Command evidence remains
explicitly `self-reported` unless the runtime supplies independent events. Do
not present either observation as a native runtime audit log.

## Overhead Guard

Compare deep-lane samples before expanding the two-stage barrier elsewhere.
Keep it only when correctness improves without unacceptable p90 duration or
startup overhead. Do not add the second invocation to standard Luna unless
observed violations justify it.
