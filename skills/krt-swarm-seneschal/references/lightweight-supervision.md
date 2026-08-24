# Lightweight Luna Supervision

Load this reference when dispatching or reconciling Luna workers. The objective
is to shorten tail latency without creating an event stream or adding tool calls
for every worker action.

## Supervision Modes

| Profile | Mode | Additional worker message |
|---|---|---|
| `luna` | `terminal-only` | none before the final return |
| `luna_xhigh` | `discovery-checkpoint` | exactly one non-blocking checkpoint |

Spark has no live supervision. Detailed read/action tracing is diagnostic-only
and must not run in ordinary waves.

## Discovery Checkpoint

After its single discovery pass, `luna_xhigh` sends the parent:

```yaml
event: discovery_complete
edit_path_found: true | false
planned_files: []
```

The message is non-blocking. When `edit_path_found: true`, the worker begins
implementation immediately; it does not wait for an acknowledgement. When
false, it reconciles state and returns `needs_review` without a second pass.

The worker emits no per-read, per-edit, or per-command events. Every Luna
returns its terminal fields, structured verification accounting, and
`verification_commands_run` in the existing final return contract.

## Root Observation

Root records worker start and return timestamps, timestamps the checkpoint when
received, and observes the first owned filesystem change in the worker's
isolation target. It builds a JSON observation for
`scripts/evaluate_luna_run.py`:

```json
{
  "schema_version": 1,
  "profile": "luna_xhigh",
  "started_at_ms": 1000,
  "owned_files": ["src/service.py"],
  "checkpoint_count": 1,
  "checkpoint": {
    "discovery_complete_at_ms": 5000,
    "edit_path_found": true,
    "planned_files": ["src/service.py"]
  },
  "first_change_at_ms": 7000,
  "phase_duration_ms": {
    "discovery": 4000,
    "implementation": 8000
  },
  "verification_manifest": {
    "focused": ["pytest tests/test_service.py"],
    "natural": ["pytest tests/"]
  },
  "last_required_command_finished_at_ms": 30000,
  "returned_at_ms": 31000,
  "interventions_sent": [],
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

Use the root/runtime timestamp for received messages rather than trusting a
worker clock. `checkpoint_count` is the number of checkpoint messages root
actually received. `owned_files` comes from the compiled contract. Root appends
an action to `interventions_sent` only after it successfully sends that message.
Keep the observation in runtime scratch; the authoritative durable output
remains the timing record.

For `luna_xhigh`, a terminal result is valid only after exactly one checkpoint.
When `edit_path_found` is true, `planned_files` must be non-empty and every path
must appear in `owned_files`. When it is false, `planned_files` must be empty.

## Evaluation And Intervention

Evaluate the observation with:

```bash
rtk python3 <seneschal-skill-dir>/scripts/evaluate_luna_run.py \
  --input <observation.json> \
  --now-ms <root-clock-ms>
```

The evaluator returns one action:

- `continue`: take no action.
- `transition_to_implementation`: send exactly `Discovery is complete;
  implement now.` once. The default fires 15 seconds after a successful
  checkpoint when no owned change is visible.
- `return_needs_review`: tell the worker to reconcile and return; do not grant
  another discovery pass.
- `return_now`: terminal fields are complete but the worker has not returned;
  tell it to return without another action.
- `complete`: accept the terminal return for normal reconciliation.
- `contract_violation`: preserve the result and reconcile it as a bounded
  failure; do not silently trust its completion status.

Never poll faster than the orchestrator's existing worker wait cadence. The
supervisor must not add a dedicated busy loop. Count an intervention only when
the parent actually sends the recommended transition or return message. The
evaluator never increments the count for a recommendation and never recommends
an action already present in `interventions_sent`.

The terminal result accounts for every focused and natural command exactly
once as attempted or skipped. Attempted entries carry an attempt count and
outcome; skipped entries carry a concrete reason. `verification_commands_run`
contains one exact command string per actual invocation. The evaluator rejects
missing commands, excess retries, a mismatched `last_required_command`, an
xhigh return without its checkpoint, and contradictory root timestamps.

## Timing Consolidation

Persist calculated metrics through the existing recorder:

```bash
rtk python3 <seneschal-skill-dir>/scripts/record_run_timing.py \
  <normal timing arguments> \
  --supervision-result <evaluation.json>
```

The evaluator supplies time to first change, discovery/implementation ratio,
commands outside the verification manifest, last-command-to-return latency,
and actual acknowledged root interventions. The recorder validates the full
evaluation envelope: only `complete` with terminal `done` or
`done_with_baseline_gaps` may persist as `completed`; a valid terminal
`needs_review` or `blocked` persists as `blocked`; `contract_violation`
persists as `failed`; intermediate actions remain `running`. Repeated context
reads remain unset in normal runs; collect them only in an explicitly sampled
diagnostic run with native runtime event evidence.

This supervision is cooperative. It validates that the worker return is
self-consistent, but without native runtime hooks it cannot prove that a listed
command actually ran or observe every worker tool action. Do not present this
telemetry as an audit trail.

## Overhead Guard

Compare supervised and unsupervised samples before expanding the checkpoint to
another lane. Keep it only when median overhead is below `max(3%, 2 seconds)`,
closeout latency improves by at least 20%, and p90 total duration improves by at
least 10% without a correctness or verification regression.
