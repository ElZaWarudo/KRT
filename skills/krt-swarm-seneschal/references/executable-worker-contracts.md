# Executable Worker Contracts

Load this reference before dispatch and reconciliation. The executable artifact
is the authority for one worker invocation; prose envelopes are only a human
rendering of it.

## Materialization

Create a JSON draft matching `worker-contract.schema.json`, then materialize it:

```bash
rtk python3 <seneschal-skill-dir>/scripts/materialize_worker_contract.py \
  --input <draft.json> \
  --repo-root <worktree-root> \
  --output docs/orchestration/runs/<run-id>/<unit-id>-worker-contract.json
```

The script validates exact fields, lane/profile mapping, repo-relative unique
paths, unique acceptance IDs, exact command sets, budgets, certification roles,
and evidence policy. It writes a canonical `sha256:` hash over every field
except `contract_hash`. Any later mutation invalidates the artifact.

Materialization also performs a non-mutating command-context preflight from the
declared worktree root. It rejects shell chaining or `cd`, verification paths
that do not resolve there, and package commands whose resolved directory lacks
the required manifest. Use native root-relative paths or an explicit supported
package context such as `npm --prefix`, `pnpm --dir`, `yarn --cwd`, or Cargo's
`--manifest-path`. Dispatch is blocked when this preflight fails.

Render the only dispatch envelope from that artifact:

```bash
rtk python3 <seneschal-skill-dir>/scripts/render_worker_envelope.py \
  --contract <worker-contract.json> \
  --terminal-path /tmp/<run-id>-<unit-id>-terminal.json \
  --output <worker-envelope.json>
```

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

This preflight proves command context, not command success. It never executes
the contract commands and does not promote later self-reported outcomes to
runtime-audited evidence.

## Observation And Evaluation

Root creates the observation. The worker must not choose these facts:

- `changed_files` and `changed_files_source: root-diff`;
- root/runtime timestamps;
- isolation and checkpoint facts;
- independent Reviewer and Security Sentinel certificates.

Capture changed files and their content digest from Git and the root filesystem:

```bash
rtk python3 <seneschal-skill-dir>/scripts/capture_worker_observation.py \
  --repo-root <worktree> --base-revision <full-revision> \
  --input <partial-observation-outside-worktree.json> \
  --output <root-observation-outside-worktree.json>
```

The worker may supply terminal fields, acceptance evidence, and self-reported
command evidence. When native command events exist, root replaces the latter
with `trust: runtime-audited`.

## Pre-return Terminal Validation

Before dispatch, give every implementation worker the canonical
`worker-terminal.schema.json` shape and this validator command, with a unique
temporary output path:

```bash
rtk python3 <seneschal-skill-dir>/scripts/validate_worker_terminal.py \
  --contract <worker-contract.json> \
  --input /tmp/<run-id>-<unit-id>-terminal.json
```

The worker drafts only the terminal object in that temporary file, runs the
validator after its required implementation and verification work, fixes only
reported shape or consistency errors, and returns the exact validated object.
It must not translate the object into headings, prose, YAML, or a different
envelope. Validation is the final local command before return and does not
authorize more implementation or verification. Include the validator command
prefix in `commands.read_only_prefixes`; it reads the contract and temporary
candidate without mutating the repo. The final command-evidence entry before
return must be a passing validator invocation, so root fails closed when it is
missing or followed by more work. A worker may correct protocol-only errors and
rerun it; the last invocation must pass.

This pre-return check covers worker-owned facts: exact fields, `phase:
closeout`, empty `remaining_actions`, `terminal_ready: true`, acceptance
evidence, verification accounting, and `unowned_failures`. Root still builds
and evaluates the authoritative observation because the worker cannot certify
the real diff, timestamps, scope, command trust, or independent review and
security evidence.

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

Every certificate `diff_digest` must equal the root observation's digest.
Non-empty but mismatched digests are contract violations. The terminal
validator evidence is parsed as exact argv with only `--contract` and `--input`;
mentioning the validator filename in an unrelated command never satisfies it.

The actor must differ from the implementer. Use `security-sentinel` for the
security certificate. A certificate for another contract or diff is invalid.
Root aggregate verification remains a wave gate and is not folded into a leaf
worker's self-report.
