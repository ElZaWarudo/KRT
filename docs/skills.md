# KRT Skills

Formal skill IDs use lowercase hyphenated `krt-*` names. Some runtimes may expose friendlier `$krt:*` aliases, because apparently even a command name can wear court clothes.

## Catalog

| Alias | Formal skill ID | Purpose |
|---|---|---|
| `$krt:requirements-weaver` | `krt-requirements-weaver` | Clarify rough software requirements before planning or coding. |
| `$krt:harness-wise` | `krt-harness-wise` | Create versionable coding harnesses from project docs and agent initialization context, or diagnose and improve an existing harness. |
| `$krt:document-forge` | `krt-document-forge` | Convert PDF and DOCX source documents into versionable Markdown evidence for harness and planning workflows. |
| `$krt:word-illuminator` | `krt-word-illuminator` | Create, edit, render, compare, validate, and privacy-scrub professional Word DOCX documents. |
| `$krt:roadmap-cartographer` | `krt-roadmap-cartographer` | Generate exactly one roadmap or readiness report from existing project context. |
| `$krt:delivery-navigator` | `krt-delivery-navigator` | Turn validated requirements into a practical project delivery plan. |
| `$krt:compound-master` | `krt-compound-master` | Orchestrate larger delivery programs: context gate, roadmap, brainstorms, plans, reviews, work packages, execution, and release handoff. |
| `$krt:swarm-seneschal` | `krt-swarm-seneschal` | Coordinate safe waves of isolated Codex subagents above Compound Master. |
| `$krt:state-archivist` | `krt-state-archivist` | Keep Compound Master state compact by archiving long historical detail into linked files. |
| `$krt:release-marshal` | `krt-release-marshal` | Direct commits, rebase, Jira, push, PR creation, reviewer requests, and Jira review follow-up. |
| `$krt:review-herald` | `krt-review-herald` | Triage PR review feedback, plan fixes, draft reviewer replies, and apply approved thread replies or resolutions. |
| `$krt:security-sentinel` | `krt-security-sentinel` | Review security-sensitive slices and diagnose systems for cybersecurity risk. |
| `$krt:ci-questor` | `krt-ci-questor` | Investigate failing CI runs and produce concise cause reports. |
| `$krt:deploy-summoner` | `krt-deploy-summoner` | Prepare and diagnose Docker, Helm, and Kubernetes deployments. |
| `$krt:docs-chronicler` | `krt-docs-chronicler` | Keep durable docs, ADRs, changelogs, runbooks, and learnings current. |
| `$krt:gitflow-knight` | `krt-gitflow-knight` | Keep branch hygiene and atomic commits in formation. |
| `$krt:rebase-smith` | `krt-rebase-smith` | Re-forge branch history onto the correct base without dragging old steel into the PR. |
| `$krt:jira-scribe` | `krt-jira-scribe` | Manage Jira Server/Data Center issues, subtasks, sprints, and transitions in Spanish. |
| `$krt:jira-cloud-scribe` | `krt-jira-cloud-scribe` | Manage Jira Cloud issues, subtasks, sprints, and transitions in Spanish. |
| `$krt:repo-medic` | `krt-repo-medic` | Diagnose repository health, stale docs, broken workflows, and maintenance risks. |
| `$krt:skill-arbiter` | `krt-skill-arbiter` | Validate a KRT skill portfolio and score supervisor-captured routing, safety, restart, fallback, and outcome evaluations. |
| `$krt:product-polish-council` | `krt-product-polish-council` | Audit an application across twelve product-polish dimensions and produce an evidence-based, prioritized backlog. |
| `$krt:frontend-ux-guardian` | `krt-frontend-ux-guardian` | Guard frontend agents toward functional, accessible, responsive UX/UI and browser-verified workflows. |
| `$krt:interface-inquisitor` | `krt-interface-inquisitor` | Produce evidence-based adversarial visual critiques and implementation-ready change briefs. |
| `$krt:interface-warden` | `krt-interface-warden` | Design and implement distinctive working-surface interfaces within product constraints. |
| `$krt:interaction-polisher` | `krt-interaction-polisher` | Audit and refine feedback, motion, latency, continuity, and state transitions. |
| `$krt:bicentennial-writer` | `krt-bicentennial-writer` | Draft and revise text so it sounds natural, specific, and less formulaic. |

Skills can bring their own references, templates, scripts, assets, or agent definitions. Keep the main `SKILL.md` readable; put the heavy armor nearby.

## Dependencies

| Skill | Expected companions | Why |
|---|---|---|
| `krt-document-forge` | `krt-harness-wise` for downstream harness creation | Converts source documents into auditable Markdown evidence without taking ownership of the final harness. |
| `krt-delivery-navigator` | `krt-requirements-weaver` output when available | Turns validated requirements into delivery shape without re-litigating discovery. |
| `krt-compound-master` | Required: `krt-roadmap-cartographer`, `ce-brainstorm`, `ce-plan`, `document-review`, `ce-work`, `ce-review`, `krt-release-marshal`. Optional: `krt-state-archivist`, `krt-security-sentinel`, `krt-ci-questor` | Full artifact, execution, and release pipeline. Optional specialists are used when present and skipped with a recorded fallback when missing. |
| `krt-swarm-seneschal` | `krt-compound-master`, `krt-release-marshal`, `krt-jira-cloud-scribe`, and optional subagent/worktree/cloud runtime support | Meta-orchestrates ready work packages, backlog items, or Jira Cloud issue queues into bounded execution waves without changing Compound Master or owning release mutations. |
| `krt-release-marshal` | `krt-gitflow-knight`, `krt-rebase-smith`, `krt-jira-scribe` | Clean commits, clean branch history, Jira, and PR handoff. |
| `krt-jira-scribe` | `.krt/env/jira-scribe.env` loaded into env vars | Jira Server/Data Center issue, subtask, sprint, and transition work. |
| `krt-jira-cloud-scribe` | `.krt/env/jira-cloud-scribe.env` loaded into env vars | Jira Cloud issue, subtask, sprint, and transition work via REST API v3. |
| `krt-product-polish-council` | Optional: `krt-frontend-ux-guardian`, `krt-interface-inquisitor`, and `krt-interaction-polisher` | The council owns the cross-product audit; specialists can deepen accepted functional, visual, or interaction findings without blocking the core flow. |
| `krt-frontend-ux-guardian` | Optional: `krt-interface-inquisitor` for adversarial critique; `krt-interface-warden` for visual direction | Works independently; when combined, Guardian defines the UX contract and final functional gate. |
| `krt-interface-inquisitor` | Optional: `krt-frontend-ux-guardian` constraints and `krt-interface-warden` implementation | Works independently; optional handoffs keep visual criticism product-safe and directly actionable. |
| `krt-interface-warden` | Optional: `krt-frontend-ux-guardian` constraints and `krt-interface-inquisitor` critique | Works independently; optional inputs help preserve task flow while implementing visual direction. |
| `krt-interaction-polisher` | Optional: `krt-frontend-ux-guardian` constraints, `krt-interface-inquisitor` critique, and `krt-interface-warden` composition | Works independently; optional inputs keep interaction refinements functionally safe and visually coherent. |
| `krt-skill-arbiter` | Any KRT skill portfolio; optionally `krt-repo-medic` for the diagnostic matrix | Validates corpus and portfolio contracts, then aggregates independently supervised results without executing models. |

For Jira Server/Data Center flows, configure the active checkout's `.krt/env/jira-scribe.env`, load it into environment variables, and verify readiness with `check_jira_env.py` without printing `JIRA_API_TOKEN`, because secrets are not confetti.

For Jira Cloud flows, configure `.krt/env/jira-cloud-scribe.env` and verify readiness with the Cloud skill's `check_jira_env.py` without printing `JIRA_CLOUD_API_TOKEN`.
