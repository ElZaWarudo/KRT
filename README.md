# KRT

KRT means **Knights of the Round Table**: portable agent skills for keeping a codebase in formation without asking one overcaffeinated linux squire to remember every ritual by heart.

KRT gives agent runtimes reusable workflows for requirements, harnesses, roadmaps, delivery orchestration, release hygiene, CI, deployment, security, docs, and repo health. The bit is medieval. The contract is not.

## Choose A Skill

| When you have... | Start with... |
|---|---|
| A fuzzy brief, prompt, or feature idea | `krt-requirements-weaver` |
| A repo you do not trust yourself to touch yet | `krt-harness-wise` |
| Existing context that needs a roadmap or readiness report | `krt-roadmap-cartographer` |
| Validated requirements that need a delivery plan | `krt-delivery-navigator` |
| A larger initiative that needs orchestration | `krt-compound-master` |
| Noisy Compound Master state | `krt-state-archivist` |
| A finished change that needs clean shipping | `krt-release-marshal` |
| PR review feedback | `krt-review-herald` |
| Jira Cloud issue management | `krt-jira-cloud-scribe` |
| Security-sensitive work | `krt-security-sentinel` |
| A failing CI run | `krt-ci-questor` |
| Deployment manifests, rollout, or rollback risk | `krt-deploy-summoner` |
| Stale, missing, or noisy docs | `krt-docs-chronicler` |
| Suspicious repo health | `krt-repo-medic` |
| A working interface that still feels dead, abrupt, or sluggish | `krt-interaction-polisher` |
| Text that sounds generic or AI-written | `krt-bicentennial-writer` |

Full catalog: [`docs/skills.md`](docs/skills.md). Prompt examples: [`docs/examples.md`](docs/examples.md).

## Common Flows

| Flow | Skills |
|---|---|
| Discovery | `krt-requirements-weaver` -> `krt-roadmap-cartographer` -> `krt-delivery-navigator` |
| Execution | `krt-harness-wise` -> `krt-compound-master` -> `krt-release-marshal` |
| Operations | `krt-review-herald`, `krt-ci-questor`, `krt-deploy-summoner`, `krt-docs-chronicler`, `krt-repo-medic`, `krt-security-sentinel` |

`krt-compound-master` treats a **work package** as the PR/Jira unit while preserving the plan's implementation units inside it. One PR may carry the package; the bookkeeping should still know which pieces marched where.

## Install

Install one skill globally:

```bash
npx -y skills add ElZaWarudo/krt --skill krt-<skill-name> -g
```

Install everything:

```bash
npx -y skills add ElZaWarudo/krt --all -g
```

Install the Compound Master pipeline:

```bash
npx -y skills add ElZaWarudo/krt \
  --skill krt-requirements-weaver \
  --skill krt-roadmap-cartographer \
  --skill krt-delivery-navigator \
  --skill krt-compound-master \
  --skill krt-state-archivist \
  --skill krt-release-marshal \
  --skill krt-gitflow-knight \
  --skill krt-rebase-smith \
  --skill krt-jira-scribe \
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
