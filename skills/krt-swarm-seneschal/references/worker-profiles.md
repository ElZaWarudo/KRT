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
- `luna_xhigh`: demanding work admitted by `execution-lanes.md`; Luna uses
  `xhigh`.

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
terminal_protocol:
  grace_actions: 0
verification:
  aggregate_owner: root
  max_retries_per_command: 1
  stop_on_unowned_failure: true
```

`luna` and `luna_xhigh` share the same duration and closeout limits. Their only
difference is reasoning depth and admission trigger. Luna may request one
extension by returning `needs_review` with a concrete new finding, the exact
additional round requested, and expected payoff; it may not spend the extension
before approval.

Supervision differs by profile: `luna` uses terminal-only supervision and adds
no live message; `luna_xhigh` sends one non-blocking discovery checkpoint with
`edit_path_found` and `planned_files`. Neither emits per-action telemetry.
Root records the xhigh checkpoint count, validates planned files against the
compiled `owned_files`, and records only successfully sent interventions.

After the xhigh checkpoint, Seneschal may send exactly one transition
instruction, `Discovery is complete; implement now.`, only when an edit path
was reported but no owned change appears within the configured threshold. A
worker that reports no safe edit path returns `needs_review` or `blocked`
without another discovery pass.

After the last manifest command and state reconciliation, Luna returns with no
grace action. It does not reread references, repeat a passing check, run root's
aggregate suite, or investigate an unowned failure.

Root evaluates the xhigh checkpoint and terminal return through
`scripts/evaluate_luna_run.py` as described in
`lightweight-supervision.md`. Repeated-read tracing is permitted only in an
explicit diagnostic sample, never as a normal profile default.

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
custom-agent fields, lane-to-profile mapping, profile identity, exact model,
reasoning effort, and model-class match.
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

For Luna, the unit contract is compiled from
`krt-compound-master/references/fast-contract.md` and is its only operational
instruction package besides repository `AGENTS.md` and explicitly listed
context. The profile does not authorize loading the broader skill trees.

Do not put unit-specific requirements into a bundled profile. Do not treat the
profile as a replacement for the worker envelope or work package.
