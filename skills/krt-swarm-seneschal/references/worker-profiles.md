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

Do not put unit-specific requirements into a bundled profile. Do not treat the
profile as a replacement for the worker envelope or work package.
