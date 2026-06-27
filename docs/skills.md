# KRT Skills

Formal skill IDs use lowercase hyphenated `krt-*` names. Some runtimes may expose friendlier `$krt:*` aliases, because apparently even a command name can wear court clothes.

## Catalog

| Alias | Formal skill ID | Purpose |
|---|---|---|
| `$krt:requirements-weaver` | `krt-requirements-weaver` | Clarify rough software requirements before planning or coding. |
| `$krt:harness-wise` | `krt-harness-wise` | Create versionable coding harnesses from project docs and agent initialization context, or diagnose and improve an existing harness. |
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
| `$krt:repo-medic` | `krt-repo-medic` | Diagnose repository health, stale docs, broken workflows, and maintenance risks. |
| `$krt:bicentennial-writer` | `krt-bicentennial-writer` | Draft and revise text so it sounds natural, specific, and less formulaic. |

Skills can bring their own references, templates, scripts, assets, or agent definitions. Keep the main `SKILL.md` readable; put the heavy armor nearby.

## Dependencies

| Skill | Expected companions | Why |
|---|---|---|
| `krt-delivery-navigator` | `krt-requirements-weaver` output when available | Turns validated requirements into delivery shape without re-litigating discovery. |
| `krt-compound-master` | Required: `krt-roadmap-cartographer`, `ce-brainstorm`, `ce-plan`, `document-review`, `ce-work`, `ce-review`, `krt-release-marshal`. Optional: `krt-state-archivist`, `krt-security-sentinel`, `krt-ci-questor` | Full artifact, execution, and release pipeline. Optional specialists are used when present and skipped with a recorded fallback when missing. |
| `krt-swarm-seneschal` | `krt-compound-master`, `krt-release-marshal`, and optional subagent/worktree/cloud runtime support | Meta-orchestrates ready work packages, backlog items, or issue queues into bounded execution waves without changing Compound Master or owning release mutations. |
| `krt-release-marshal` | `krt-gitflow-knight`, `krt-rebase-smith`, `krt-jira-scribe` | Clean commits, clean branch history, Jira, and PR handoff. |
| `krt-jira-scribe` | `.krt/env/jira-scribe.env` loaded into env vars | Jira Server/Data Center issue, subtask, sprint, and transition work. |

For Jira flows, configure the active checkout's `.krt/env/jira-scribe.env`, load it into environment variables, and verify readiness with `check_jira_env.py` without printing `JIRA_API_TOKEN`, because secrets are not confetti.
