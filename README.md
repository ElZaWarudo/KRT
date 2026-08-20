# KRT

KRT means **Knights of the Round Table**: portable agent skills for keeping a codebase in formation without asking one overcaffeinated linux squire to remember every ritual by heart.

KRT gives agent runtimes 27 reusable skills for requirements, harnesses, roadmaps, delivery orchestration, release hygiene, CI, deployment, security, evaluation, docs, and repo health. The bit is medieval. The contract is not.

## Choose A Skill

Start with the job in front of you. The groups below cover every KRT skill without making the front page wear the full catalog as plate armor.

### Shape The Work

| When you have... | Start with... |
|---|---|
| PDF or DOCX source material that agents need as versionable evidence | `krt-document-forge` |
| A professional Word document to create, edit, render, or validate | `krt-word-illuminator` |
| A fuzzy brief, prompt, or feature idea | `krt-requirements-weaver` |
| A repo you do not trust yourself to touch yet | `krt-harness-wise` |
| Existing context that needs a roadmap or readiness report | `krt-roadmap-cartographer` |
| Validated requirements that need a delivery plan | `krt-delivery-navigator` |

### Coordinate Delivery

| When you have... | Start with... |
|---|---|
| A larger initiative that needs artifact-first orchestration | `krt-compound-master` |
| Ready work packages or a backlog that needs bounded agent waves | `krt-swarm-seneschal` |
| Compound Master state that has become too noisy | `krt-state-archivist` |

### Improve The Product Experience

| When you have... | Start with... |
|---|---|
| An application that needs an end-to-end product polish audit | `krt-product-polish-council` |
| Frontend work that must stay functional, accessible, and responsive | `krt-frontend-ux-guardian` |
| An interface that needs an adversarial visual critique | `krt-interface-inquisitor` |
| An interface that needs distinctive design or implementation | `krt-interface-warden` |
| A working interface that still feels dead, abrupt, or sluggish | `krt-interaction-polisher` |
| Text that sounds generic or AI-written | `krt-bicentennial-writer` |

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
| A failing CI run | `krt-ci-questor` |
| Deployment manifests, rollout, or rollback risk | `krt-deploy-summoner` |
| Stale, missing, or noisy docs | `krt-docs-chronicler` |
| Suspicious repo health | `krt-repo-medic` |
| A skill portfolio that needs deterministic corpus, metadata, or safety checks | `krt-skill-arbiter` |

Full descriptions, aliases, and dependencies: [`docs/skills.md`](docs/skills.md). Prompt examples: [`docs/examples.md`](docs/examples.md).

## Common Flows

| Flow | Skills |
|---|---|
| Document intake | `krt-document-forge` -> `krt-harness-wise` |
| Document production | `krt-word-illuminator` |
| Discovery | `krt-requirements-weaver` -> `krt-roadmap-cartographer` -> `krt-delivery-navigator` |
| Execution | `krt-harness-wise` -> `krt-compound-master` -> `krt-release-marshal` |
| Swarm execution | `krt-swarm-seneschal` -> `krt-compound-master` -> `krt-release-marshal` |
| Product polish | `krt-product-polish-council` -> targeted `krt-frontend-ux-guardian`, `krt-interface-inquisitor`, or `krt-interaction-polisher` follow-up |
| Operations | `krt-review-herald`, `krt-ci-questor`, `krt-deploy-summoner`, `krt-docs-chronicler`, `krt-repo-medic`, `krt-security-sentinel` |
| Skill portfolio quality | `krt-repo-medic` -> `krt-skill-arbiter` |

`krt-compound-master` treats a **work package** as the PR/Jira unit while preserving the plan's implementation units inside it. One PR may carry the package; the bookkeeping should still know which pieces marched where.

### Seneschal Execution Lanes

Seneschal does not summon the whole court for every loose horseshoe. Small
independent work stays with the root agent when dispatch would cost more than
the change; dispatched implementation uses one of three stable lanes:

| Lane | Use it for... | Worker profile |
|---|---|---|
| `fast` | Decision-closed work with a confirmed edit path | Spark with `xhigh` reasoning |
| `standard` | Normal bounded implementation | Luna with `high` reasoning |
| `deep` | Architecture, auth, data, concurrency, public contracts, or other demanding work | Luna with `xhigh` reasoning |

Spark reasoning stays at `xhigh`; the lane changes the worker, not Spark's
thinking budget. Optional Planner, Reviewer, Fixer, Integrator, and Documenter
roles join only when their admission trigger is present. Leaf workers run
focused checks; Seneschal runs aggregate verification once per wave.

Canonical policy: [`execution-lanes.md`](skills/krt-swarm-seneschal/references/execution-lanes.md).

## Install

Install one skill globally:

```bash
npx -y skills add ElZaWarudo/krt --skill krt-<skill-name> -g
```

Install everything:

```bash
npx -y skills add ElZaWarudo/krt --all -g
```

### Install Seneschal Worker Profiles

The skill package carries Spark, Luna `high`, and Luna `xhigh` profiles, while
Codex discovers custom agents only from `.codex/agents/` in a project or
`agents/` under the active Codex home. After installing
`krt-swarm-seneschal`, preview the personal-agent copy:

```bash
rtk python3 <installed-seneschal-skill-dir>/scripts/install_worker_profiles.py --scope user
```

Then apply the reviewed copy:

```bash
rtk python3 <installed-seneschal-skill-dir>/scripts/install_worker_profiles.py --scope user --install
```

Existing differing profiles are preserved as conflicts unless `--replace` is
explicitly supplied. With that flag, the installer also retires recognized
legacy aliases such as `luna-worker.toml`; customized aliases remain guarded as
conflicts. Projects can instead commit overrides under `.codex/agents/`.

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

Install the product polish suite:

```bash
npx -y skills add ElZaWarudo/krt \
  --skill krt-product-polish-council \
  --skill krt-frontend-ux-guardian \
  --skill krt-interface-inquisitor \
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
