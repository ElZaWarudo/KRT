# Executable Worker Contracts

Load this reference before dispatch and reconciliation. The executable artifact
is the authority for one worker invocation; prose envelopes are only a human
rendering of it.

## Materialization

Create a JSON draft matching `worker-contract.schema.json`, then materialize it:

```bash
rtk python3 <seneschal-skill-dir>/scripts/materialize_worker_contract.py \
  --input <draft.json> \
  --output docs/orchestration/runs/<run-id>/<unit-id>-worker-contract.json
```

The script validates exact fields, lane/profile mapping, repo-relative unique
paths, unique acceptance IDs, exact command sets, budgets, certification roles,
and evidence policy. It writes a canonical `sha256:` hash over every field
except `contract_hash`. Any later mutation invalidates the artifact.

The contract distinguishes:

- `commands.exact`: non-verification commands that must occur exactly once;
- `commands.read_only_prefixes`: explicitly permitted read-only exploration;
- `commands.verification`: focused and natural checks with a retry ceiling.

Do not use a broad shell prefix. Prefer `rtk read`, `rtk grep`, or an equally
narrow read-only command. Editing tools remain controlled by `owned_files` and
the real root-observed diff.

Set `minimum_command_trust` to `runtime-audited` only when the runtime supplies
an independent command event source. Otherwise use `self-reported` and retain
that trust label through timing and handoff; never describe self-reported
command evidence as runtime-enforced.

## Observation And Evaluation

Root creates the observation. The worker must not choose these facts:

- `changed_files` and `changed_files_source: root-diff`;
- root/runtime timestamps;
- isolation and checkpoint facts;
- independent Reviewer and Security Sentinel certificates.

The worker may supply terminal fields, acceptance evidence, and self-reported
command evidence. When native command events exist, root replaces the latter
with `trust: runtime-audited`.

Evaluate every implementation lane:

```bash
rtk python3 <seneschal-skill-dir>/scripts/evaluate_worker_run.py \
  --contract <worker-contract.json> \
  --input <root-observation.json> \
  --now-ms <root-clock-ms>
```

Actions are strict:

- `complete`: terminal, evidence, scope, commands, criteria, and required
  certifications are valid;
- `awaiting_certification`: implementation evidence is valid but an independent
  Reviewer or Security Sentinel certificate is still missing;
- `needs_fix`: a required independent certificate failed;
- `contract_violation`: preserve the code, mark timing failed, and do not count
  the terminal or its tests as readiness evidence.

The compatibility-only `evaluate_luna_run.py` remains available for existing
deep-checkpoint callers. New dispatch and reconciliation use
`evaluate_worker_run.py`.

## Independent Certificates

Each required certificate contains exactly:

```json
{
  "role": "reviewer",
  "actor_id": "reviewer-worker-id",
  "status": "passed",
  "contract_hash": "sha256:...",
  "diff_digest": "sha256:...",
  "findings": [{"severity": "p1"}]
}
```

The actor must differ from the implementer. Use `security-sentinel` for the
security certificate. A certificate for another contract or diff is invalid.
Root aggregate verification remains a wave gate and is not folded into a leaf
worker's self-report.
