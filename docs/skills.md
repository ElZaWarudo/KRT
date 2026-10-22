# KRT Skills

Formal skill IDs use lowercase hyphenated `krt-*` names. Some runtimes may expose friendlier `$krt:*` aliases, because apparently even a command name can wear court clothes.

## Catalog

| Alias | Formal skill ID | Purpose |
|---|---|---|
| `$krt:requirements-weaver` | `krt-requirements-weaver` | Turn a rough brief into a draft requirements packet with testable acceptance criteria and ranked open questions. |
| `$krt:harness-wise` | `krt-harness-wise` | Create or review a compact coding harness under `docs/harnesses/`, and promote staged evidence safely. |
| `$krt:document-forge` | `krt-document-forge` | Convert PDF and DOCX sources into versionable Markdown evidence, treating converted text as untrusted. |
| `$krt:word-illuminator` | `krt-word-illuminator` | Create, edit, validate, and privacy-scrub professional Word DOCX documents without editing the source in place. |
| `$krt:delivery-navigator` | `krt-delivery-navigator` | Turn requirements or project docs into a delivery plan, phased roadmap, or readiness report. |
| `$krt:compound-master` | `krt-compound-master` | Take a bounded work package from context to a release-ready handoff with one compact state record and risk-based review. |
| `$krt:swarm-seneschal` | `krt-swarm-seneschal` | Coordinate several ready units across workers, reconcile them into one candidate, and hand off release. |
| `$krt:muse-artificer` | `krt-muse-artificer` | Run Muse Code headlessly on one ready, settled implementation unit. |
| `$krt:release-marshal` | `krt-release-marshal` | Ship work for review: commits, rebase, Jira, push, PR, reviewers, Jira follow-up, and gated merges. |
| `$krt:review-herald` | `krt-review-herald` | Triage PR review feedback, apply approved fixes, and draft or publish approved replies. |
| `$krt:security-sentinel` | `krt-security-sentinel` | Review security-sensitive changes and diagnose systems and agentic workflows for risk. |
| `$krt:deploy-summoner` | `krt-deploy-summoner` | Review and diagnose Docker, Compose, Helm, and Kubernetes deployments, proposing rather than applying mutations. |
| `$krt:gitflow-knight` | `krt-gitflow-knight` | Semantic feature branches and approved atomic commits, with no AI attribution. |
| `$krt:rebase-smith` | `krt-rebase-smith` | Rebase a branch onto its real base, including `--onto`, with exact push approval. |
| `$krt:jira-scribe` | `krt-jira-scribe` | Manage Jira Server/Data Center issues, subtasks, sprints, and transitions in Spanish. |
| `$krt:jira-cloud-scribe` | `krt-jira-cloud-scribe` | Manage Jira Cloud issues, subtasks, sprints, and transitions in Spanish. |
| `$krt:skill-arbiter` | `krt-skill-arbiter` | Evaluate skills behaviorally with `evals/run_skill_eval.py` and check portfolio metadata and safety wiring. |
| `$krt:product-polish-council` | `krt-product-polish-council` | Audit an application's polish with twelve lenses and a cognitive-load lens, and produce an evidence-based backlog. |
| `$krt:interface-warden` | `krt-interface-warden` | Design, redesign, or critique interfaces with the Editorial Product UI doctrine. |
| `$krt:interaction-polisher` | `krt-interaction-polisher` | Refine feedback, motion, latency, focus continuity, and state transitions. |
| `$krt:before-after-herald` | `krt-before-after-herald` | Build a single-file HTML before/after report for a visual change. |
| `$krt:bicentennial-writer` | `krt-bicentennial-writer` | Draft and revise text so it sounds natural and specific, without inventing facts. |

Skills can bring their own references, templates, scripts, assets, or agent definitions. Keep the main `SKILL.md` readable; put the heavy armor nearby.

## Dependencies

Companions are optional unless marked required. A missing optional skill never blocks the work; the caller does that part inline.

| Skill | Companions | Why |
|---|---|---|
| `krt-document-forge` | `krt-harness-wise` downstream | Converts sources into evidence without owning the harness. |
| `krt-delivery-navigator` | `krt-requirements-weaver` output when available | Plans from validated requirements without redoing discovery. |
| `krt-compound-master` | Required: `krt-release-marshal`. Optional: `krt-security-sentinel`, a `krt-swarm-seneschal` parent | Delivers one unit; release and high-risk security review go to their owners. |
| `krt-swarm-seneschal` | `krt-compound-master` for child runs, `krt-muse-artificer`, `krt-release-marshal`, the selected Jira skill | Coordinates units; shipping stays with Release Marshal. |
| `krt-muse-artificer` | Muse Code CLI | Runs one unit; the caller keeps review, verification, and release. |
| `krt-release-marshal` | `krt-gitflow-knight`, `krt-rebase-smith`, `krt-jira-scribe` or `krt-jira-cloud-scribe` | Clean commits, clean history, Jira, and PR handoff. Owns the autonomy ledger validator. |
| `krt-jira-scribe` | `.krt/env/jira-scribe.env` | Jira Server/Data Center work through `scripts/jira_api.py`. |
| `krt-jira-cloud-scribe` | `.krt/env/jira-cloud-scribe.env` | Jira Cloud work via REST API v3 through `scripts/jira_api.py`. |
| `krt-product-polish-council` | `krt-interface-warden`, `krt-interaction-polisher` for accepted fixes | The audit stands alone; specialists deepen visual or interaction fixes. |
| `krt-skill-arbiter` | `evals/` harness in this repo | Runs no-skill / old / new comparisons and structural portfolio checks. |

For Jira Server/Data Center flows, configure the active checkout's `.krt/env/jira-scribe.env` and verify readiness with `check_jira_env.py` without printing `JIRA_API_TOKEN`, because secrets are not confetti.

For Jira Cloud flows, configure `.krt/env/jira-cloud-scribe.env` and verify readiness with the Cloud skill's `check_jira_env.py` without printing `JIRA_CLOUD_API_TOKEN`.
