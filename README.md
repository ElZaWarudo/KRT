# KRT

KRT means **Knights of the Round Table**: portable agent skills for keeping a codebase in formation without asking one overcaffeinated linux squire to remember every ritual by heart.

KRT gives agent runtimes 22 reusable skills for requirements, harnesses, roadmaps, delivery orchestration, release hygiene, deployment, security, and skill evaluation. Each skill keeps only what a current model would get wrong without it, and every one has a behavioral eval under [`evals/`](evals/). The bit is medieval. The contract is not.

Repository documentation and skill instructions use English. Localized Jira values, multilingual routing triggers, parser fixtures, and language-specific writing examples remain in their source language when translation would change behavior.

## Choose A Skill

Start with the job in front of you. The groups below cover every KRT skill without making the front page wear the full catalog as plate armor.

### Shape The Work

| When you have... | Start with... |
|---|---|
| PDF or DOCX source material that agents need as versionable evidence | `krt-document-forge` |
| A professional Word document to create, edit, render, or validate | `krt-word-illuminator` |
| A fuzzy brief, prompt, or feature idea | `krt-requirements-weaver` |
| A repo you do not trust yourself to touch yet | `krt-harness-wise` |
| Validated requirements or project docs that need a delivery plan, roadmap, or readiness report | `krt-delivery-navigator` |

### Coordinate Delivery

| When you have... | Start with... |
|---|---|
| A bounded work package to take from context to a release-ready PR | `krt-compound-master` |
| Several ready units that benefit from parallel or sequential workers | `krt-swarm-seneschal` |
| A ready, settled implementation unit to hand to Muse Code | `krt-muse-artificer` |

### Improve The Product Experience

| When you have... | Start with... |
|---|---|
| An application that needs an end-to-end polish audit, or a flow that feels mentally taxing | `krt-product-polish-council` |
| An interface that needs distinctive design, a redesign, or a visual critique | `krt-interface-warden` |
| A working interface that still feels dead, abrupt, or sluggish | `krt-interaction-polisher` |
| A visual change that needs before/after screenshot evidence | `krt-before-after-herald` |
| English or Spanish text that sounds generic or AI-written | `krt-bicentennial-writer` |

### Ship And Collaborate

| When you have... | Start with... |
|---|---|
| Pending changes that need branch hygiene and atomic commits | `krt-gitflow-knight` |
| A child branch that must be rebased cleanly onto its real base | `krt-rebase-smith` |
| A finished change that needs clean shipping | `krt-release-marshal` |
| PR review feedback | `krt-review-herald` |
| Jira Server or Data Center issue management | `krt-jira-scribe` |
| Jira Cloud issue management | `krt-jira-cloud-scribe` |

### Operate And Maintain

| When you have... | Start with... |
|---|---|
| Security-sensitive work or a repository-wide security review | `krt-security-sentinel` |
| Deployment manifests, rollout, or rollback risk | `krt-deploy-summoner` |
| A new or changed skill that needs a behavioral eval, or portfolio metadata and safety checks | `krt-skill-arbiter` |

Full descriptions, aliases, and dependencies: [`docs/skills.md`](docs/skills.md). Prompt examples: [`docs/examples.md`](docs/examples.md).

## Common Flows

| Flow | Skills |
|---|---|
| Document intake | `krt-document-forge` -> `krt-harness-wise` |
| Document production | `krt-word-illuminator` |
| Discovery | `krt-requirements-weaver` -> `krt-delivery-navigator` |
| Execution | `krt-harness-wise` -> `krt-compound-master` -> `krt-release-marshal` |
| Swarm execution | `krt-swarm-seneschal` -> `krt-compound-master` -> `krt-release-marshal` |
| Product polish | `krt-product-polish-council` (with its cognitive-load lens) -> `krt-interface-warden` / `krt-interaction-polisher` for fixes |
| Skill quality | `krt-skill-arbiter` with `evals/run_skill_eval.py` |

`krt-compound-master` keeps one compact state record per run and sizes PRs for human review: at most two or three open stacked PRs, Jira at review-unit granularity.

### Seneschal Workers

Seneschal keeps a clear single task with the root agent. When several ready units benefit from separate workers, it routes them by risk:

| Unit | Worker |
|---|---|
| Fast or settled standard work | Muse Code via `krt-muse-artificer` (model `muse-spark-1.3-contributor`), when installed |
| Standard work | GPT-6 Luna (`luna_worker`) |
| Deep, ambiguous, or high-risk work | `luna_xhigh_discovery_worker` read-only first, then `luna_xhigh_worker` |

Seneschal still inspects each diff, merges the units into one candidate, runs the full suite there, and hands release to `krt-release-marshal`. Muse must be installed in the environment that runs the worker (WSL in the current setup).

## Install

Install one skill globally:

```bash
npx -y skills add ElZaWarudo/krt --skill krt-<skill-name> -g
```

For Muse-backed Seneschal units, install both `krt-swarm-seneschal` and
`krt-muse-artificer` in the runtime that launches Muse.

Install everything:

```bash
npx -y skills add ElZaWarudo/krt --all -g
```

### Install Seneschal Worker Profiles

Codex discovers custom agents only from `.codex/agents/` in a project or
`agents/` under the active Codex home. Copy the profiles from the installed
skill's `assets/codex-workers/` into one of those, after reviewing any existing
profile with the same name. This repo already carries them in `.codex/agents/`.

Install the Compound Master pipeline:

```bash
npx -y skills add ElZaWarudo/krt \
  --skill krt-requirements-weaver \
  --skill krt-delivery-navigator \
  --skill krt-compound-master \
  --skill krt-release-marshal \
  --skill krt-gitflow-knight \
  --skill krt-rebase-smith \
  --skill krt-jira-scribe \
  -g
```

Install the product polish suite:

```bash
npx -y skills add ElZaWarudo/krt \
  --skill krt-product-polish-council \
  --skill krt-interface-warden \
  --skill krt-interaction-polisher \
  --skill krt-bicentennial-writer \
  -g
```

Install the release flow:

```bash
npx -y skills add ElZaWarudo/krt \
  --skill krt-release-marshal \
  --skill krt-gitflow-knight \
  --skill krt-rebase-smith \
  --skill krt-jira-scribe \
  -g
```

Update installed skills:

```bash
npx skills update
```

If `npx` gets dramatic:

```bash
npm exec --yes --package skills -- skills update
```

## Safety

KRT is deliberately fussy about mutation:

- read first, mutate second
- keep every action inside the active skill's job
- ask before remote, destructive, notification-causing, production-impacting, or credential-sensitive work
- never print or copy secrets, tokens, kubeconfigs, full env dumps, or masked CI values
- keep merge approval separate from release-plan approval

Per-skill safety notes live in [`docs/safety.md`](docs/safety.md). They are short on purpose; if a safety note needs a throne room, it has already failed.

## Develop

Edit skills in `skills/<name>/`. Keep reusable detail in `references/` or `assets/` so `SKILL.md` stays readable.

Measure a changed skill against `main` and against no skill (see [`evals/README.md`](evals/README.md)):

```bash
python3 evals/run_skill_eval.py evals/<skill-name> \
  --variant none=none --variant old=main --variant new=worktree --reps 2
```

Validate a changed skill:

```bash
rtk python3 /home/teb/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/<skill-name>
```

Before committing docs or skill changes:

```bash
rtk git diff --check
```

Sync edited skills into the local runtime:

```bash
rtk rsync -a skills/ /home/teb/.agents/skills/
```

Contributor details: [`docs/development.md`](docs/development.md).
