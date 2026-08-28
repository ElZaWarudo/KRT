# Worker Profiles

Load this reference before installing or dispatching a named Codex worker such
as Spark or Luna.

## Distribution And Discovery

Generic profiles ship with the skill under `assets/codex-workers/`. Codex does
not discover custom agents inside a skill asset directory. It discovers:

- project agents under `.codex/agents/`; and
- personal agents under the active Codex home `agents/` directory, normally
  `~/.codex/agents/`.

Every custom-agent TOML defines `name`, `description`, and
`developer_instructions`. Optional model, reasoning, sandbox, MCP, and skill
settings override or inherit according to the Codex runtime.

Resolution order is strict:

1. Use the project agent when it exists.
2. Otherwise use the personal agent installed from the skill.
3. Block dispatch when neither runtime-discoverable profile exists.

The registered execution profiles are:

- `spark`: small, completely decision-closed work; Spark remains `xhigh`.
- `luna`: normal bounded work; Luna uses `high`.
- `luna_xhigh_discovery`: read-only first stage for every deep unit; Luna uses
  `xhigh` and returns the terminal discovery checkpoint.
- `luna_xhigh`: demanding work admitted by `execution-lanes.md`; Luna uses
  `xhigh` and implements only after an accepted checkpoint.

Do not mutate reasoning effort dynamically. Select the registered profile whose
stable effort matches the classified lane.

## Luna Defaults

Every Luna dispatch inherits these operational defaults through its compiled
contract:

```yaml
execution_budget:
  discovery_passes: 1
  implementation_rounds: 1
  fix_rounds: 2
  review_rounds: 1
  extra_verification: forbidden
  max_elapsed_ms: <role-sized positive deadline>
terminal_protocol:
  grace_actions: 0
commands:
  verification:
    max_retries_per_command: 1
evidence_policy:
  changed_files_source: root-diff
```

Wave verification keeps the existing `aggregate_owner: root` invariant; that
wave-level field is intentionally outside the leaf contract.

`luna` and the two deep stages share the same bounded-round discipline. Luna
may request one
extension by returning `needs_review` with a concrete new finding, the exact
additional round requested, and expected payoff; it may not spend the extension
before approval.

Supervision differs by profile: `luna` uses terminal-only supervision.
`luna_xhigh_discovery` runs under a runtime-enforced read-only sandbox and
returns exactly one terminal checkpoint with `edit_path_found`, `planned_files`,
and `evidence_digest`; extra fields are invalid. Root rejects unchanged broad
ownership or planned paths without file-specific justification, validates the
result against compiled `owned_files`, then automatically launches a fresh
`luna_xhigh` implementation worker with ownership narrowed to `planned_files`.
Neither stage emits per-action telemetry.

The implementation stage sends no checkpoint and does not repeat discovery. If
another file is required, it returns `needs_review` with a structured scope
extension request without editing that file. Root inspects the actual diff and
rejects changes outside the accepted manifest.

After the last manifest command and state reconciliation, Luna returns with no
grace action. It does not reread references, repeat a passing check, run root's
aggregate suite, or investigate an unowned failure.

Root evaluates the deep-stage checkpoint and terminal return through
`scripts/evaluate_luna_run.py` as described in
`lightweight-supervision.md`. Repeated-read tracing is permitted only in an
explicit diagnostic sample, never as a normal profile default.

All implementation profiles, including Spark, also receive a materialized
`worker-contract.json` and are reconciled through
`scripts/evaluate_worker_run.py`. The worker echoes the hash and supplies
criterion and command evidence; root independently supplies the actual diff and
certificates. `evaluate_luna_run.py` is retained only for the deep-stage
checkpoint transition.

An invalid project or personal profile is an error. Never ignore it, use the
bundled package file directly, or substitute another worker or model class.

The manifest is YAML 1.2 expressed in its JSON-compatible subset so the
deterministic scripts need no third-party parser.

## Installation

After installing or updating the skill, preview personal-agent installation:

```bash
python3 <seneschal-skill-dir>/scripts/install_worker_profiles.py \
  --scope user
```

Apply it only when authorized:

```bash
python3 <seneschal-skill-dir>/scripts/install_worker_profiles.py \
  --scope user \
  --install
```

Use `--scope project --repo-root <repo-root> --install` when the profiles should
belong only to one trusted project. Existing differing profiles are preserved
and reported as conflicts. `--replace` is always explicit.

## Dispatch Preflight

Resolve `<seneschal-skill-dir>` to the installed directory containing this
skill's `SKILL.md`. Before dispatch, run:

```bash
python3 <seneschal-skill-dir>/scripts/check_worker_profiles.py \
  --repo-root <repo-root> \
  --lane <fast|standard|deep>
```

The checker validates discovery location, manifest, TOML syntax, required
custom-agent fields, every profile in the lane stage sequence, profile identity,
exact model, reasoning effort, sandbox mode, and model-class match.
Record the selected source, path, and reasoning effort in dispatch evidence.

`--allow-bundled` exists only to validate the skill package before installing
it. A bundled-only result is not runtime-discoverable and must never authorize
dispatch.

Static preflight cannot prove that the active account exposes the configured
model. When the runtime offers model discovery, verify it before dispatch.
Otherwise treat an unavailable-model invocation error as a blocker and do not
substitute another profile silently.

## Profile And Contract Boundary

The worker profile defines stable runtime behavior: model, sandbox, reasoning
effort, and durable role constraints. The unit contract defines the exact
objective, write scope, decisions, acceptance criteria, verification, and stop
conditions for one dispatch.

The unit contract is a schema-validated JSON artifact, not only prompt text.
Materialize it with `scripts/materialize_worker_contract.py` and carry its hash
unchanged through every worker and certificate.

For Luna, the unit contract is compiled from
`krt-compound-master/references/fast-contract.md` and is its only operational
instruction package besides repository `AGENTS.md` and explicitly listed
context. The profile does not authorize loading the broader skill trees.

Do not put unit-specific requirements into a bundled profile. Do not treat the
profile as a replacement for the worker envelope or work package.
