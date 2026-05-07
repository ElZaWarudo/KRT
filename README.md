# KRT

KRT means **Knights of the Round Table**: portable agent skills for keeping the whole Camelot of a codebase in order without asking one overcaffeinated linux squire to remember everything.

## Philosophy

KRT exists because skills need a proper keep: one place for focused agent workflows that inspect, plan, review, and coordinate work before the diff starts making royal decrees.

Each skill should cover its part of Camelot cleanly:

- small enough to load only when useful
- explicit enough that another agent can follow it
- portable across agent runtimes where possible
- opinionated enough to stop bad context from becoming bad code

The bit is medieval. The contract is not.

## Skills

Formal skill IDs use the Every-style hyphen form (`krt-*`). Some runtimes may expose the friendlier `$krt:*` alias used below.

| Alias | Formal skill ID | Purpose |
|---|---|---|
| `$krt:harness-wise` | `krt-harness-wise` | Build or review a compact coding harness before implementation. Good for repo reconnaissance, context curation, stale-doc checks, risk estimates, and skill recommendations. |
| `$krt:roadmap-cartographer` | `krt-roadmap-cartographer` | Generate exactly one roadmap or readiness report from existing project context before compound delivery. |
| `$krt:compound-master` | `krt-compound-master` | Orchestrate larger delivery programs: context gate, roadmap, brainstorms, plans, document reviews, work packages, execution gates, code review, and PR/Jira handoff. |
| `$krt:release-marshal` | `krt-release-marshal` | Direct the final delivery march: commits, rebase, Jira, push, PR creation, reviewer requests, and Jira review follow-up. |
| `$krt:review-herald` | `krt-review-herald` | Triage PR review feedback, plan fixes, and draft clear reviewer replies. |
| `$krt:ci-questor` | `krt-ci-questor` | Investigate failing CI runs and produce concise cause reports. |
| `$krt:gitflow-knight` | `krt-gitflow-knight` | Keep branch hygiene and atomic commits in formation. |
| `$krt:rebase-smith` | `krt-rebase-smith` | Re-forge branch history onto the correct base without dragging old steel into the PR. |
| `$krt:jira-scribe` | `krt-jira-scribe` | Manage Jira Server/Data Center issues, subtasks, sprints, and transitions in Spanish. |
| `$krt:repo-medic` | `krt-repo-medic` | Diagnose repository health, stale docs, broken workflows, and maintenance risks. |

Skills can bring their own auxiliary files: references, templates, assets, adapter configs, or agent definitions. Keep the main `SKILL.md` readable; put the heavy armor in nearby files.

## How They Fit Together

KRT skills are meant to compose without turning one skill into the whole system:

```text
krt-harness-wise
  -> prepare compact context before coding

krt-roadmap-cartographer
  -> produce one roadmap or readiness report

krt-compound-master
  -> consume roadmap, run brainstorm/plan/review/package/execution gates

krt-release-marshal
  -> commit, rebase, Jira, push, PR, reviewers, Jira review transition

krt-review-herald
  -> triage review feedback and prepare fixes/replies

krt-ci-questor
  -> investigate CI failures and report likely cause

krt-repo-medic
  -> diagnose repo health and prescribe focused maintenance
```

`krt-compound-master` treats a **work package** as the PR/Jira unit, but preserves the plan's implementation units inside that package. A package can ship as one PR while still reporting per-unit execution, verification, review, and commit grouping.

## Skill Dependencies

Some skills are useful standalone; others expect companions.

| Skill | Expected companions | Why |
|---|---|---|
| `krt-compound-master` | Required: `krt-roadmap-cartographer`, `ce-brainstorm`, `ce-plan`, `document-review`, `ce-work`, `ce-review`, `krt-release-marshal`. Optional: `krt-ci-questor` | Full artifact, execution, and release pipeline. `krt-ci-questor` handles CI incident escalation when available; otherwise Compound Master resolves another CI investigator or triages inline. |
| `krt-release-marshal` | `krt-gitflow-knight`, `krt-rebase-smith`, `krt-jira-scribe` | Clean commits, clean branch history, Jira, and PR handoff. |
| `krt-jira-scribe` | Jira env vars | Jira Server/Data Center issue, subtask, sprint, and transition work. |

For Jira flows, configure `JIRA_HOST`, `JIRA_API_TOKEN`, and `JIRA_PROJECT_KEY`. When checking those variables, prefer direct shell presence checks over filtered environment searches; wrappers such as `rtk` can summarize output and make existing variables look absent. Never print `JIRA_API_TOKEN`.

## Quick Examples

Prepare a coding harness before touching a repo:

```text
Use $krt:harness-wise before adding invoice CSV export.
```

Save the harness as a markdown artifact for the next agent:

```text
Use $krt:harness-wise and generate a harness file for adding invoice CSV export.
```

Trim noisy docs before a feature:

```text
Use $krt:harness-wise docs-trim before working on billing.
```

Audit repository health:

```text
Use $krt:repo-medic for a standard health check before planning the next maintenance sprint.
```

Turn a documented initiative into delivery artifacts:

```text
Use $krt:compound-master for docs/specs/reporting.md mode:artifacts
```

`krt-compound-master` expects `krt-roadmap-cartographer` to be available as its required roadmap generator. Install both when you want the full artifact pipeline.

Resume execution from existing orchestration state:

```text
Use $krt:compound-master mode:resume jira-policy:optional parallel:false
```

Triage PR feedback:

```text
Use $krt:review-herald to classify review comments and draft replies for PR #42.
```

Investigate a failed pipeline:

```text
Use $krt:ci-questor to explain why the latest GitHub Actions run failed and what to do next.
```

## Install

Install globally so KRT follows you between projects:

```bash
npx -y skills add ElZaWarudo/krt --skill krt-<skill-name> -g
```

Install the whole table globally:

```bash
npx -y skills add ElZaWarudo/krt --all -g
```

Install the Compound Master pipeline globally:

```bash
npx -y skills add ElZaWarudo/krt \
  --skill krt-roadmap-cartographer \
  --skill krt-compound-master \
  --skill krt-release-marshal \
  --skill krt-gitflow-knight \
  --skill krt-rebase-smith \
  --skill krt-jira-scribe \
  -g
```

This installs the KRT side of the artifact and release pipeline. `krt-compound-master` also expects the Compound Engineering skills it resolves at runtime, such as `ce-brainstorm`, `ce-plan`, `document-review`, `ce-work`, and `ce-review`. Add `--skill krt-ci-questor` when you want the optional CI incident specialist installed too.

Install the release court globally:

```bash
npx -y skills add ElZaWarudo/krt \
  --skill krt-release-marshal \
  --skill krt-gitflow-knight \
  --skill krt-rebase-smith \
  --skill krt-jira-scribe \
  -g
```

`krt-release-marshal` expects those three companions to be available. The skills CLI supports repeated `--skill` flags and `--all`; KRT does not currently rely on automatic dependency resolution in skill frontmatter. The Mariscal can read the room, but he still needs the room installed.

Omit `-g` only when you want the skill installed into the current project. Without it, the skill may stay in this castle and fail to appear when you ride into the next repo.

Target a specific runtime when needed:

```bash
npx -y skills add ElZaWarudo/krt --skill krt-<skill-name> -g -a <agent>
```

Use `-a <agent>` when you want the skill wired into a particular agent instead of trusting autodetection. Some agents read `.agents/skills/` directly; others need the CLI to place a symlink or copy in their own directory. Name the knight you expect to answer.

Update installed skills:

```bash
npx skills update
```

If `npx` wanders into the forest:

```bash
npm exec --yes --package skills -- skills update
```

## Components

```text
skills/
  krt-harness-wise/
    SKILL.md
    references/
  krt-roadmap-cartographer/
    SKILL.md
    references/
  krt-compound-master/
    SKILL.md
    references/
    assets/
      codex-agents/
  krt-release-marshal/
    SKILL.md
    references/
  krt-review-herald/
    SKILL.md
    references/
  krt-ci-questor/
    SKILL.md
    references/
  krt-gitflow-knight/
    SKILL.md
  krt-rebase-smith/
    SKILL.md
  krt-jira-scribe/
    SKILL.md
    references/
  krt-repo-medic/
    SKILL.md
    references/
```

## Local Development

Edit skills in `skills/<name>/`. Keep reusable detail in `references/` or `assets/` so the top-level skill stays compact.

Validate with whichever skill validator your target runtime uses. For manual checks, install the skill into a disposable agent profile and run the quick examples above. If the agent comes back with a quest, a map, and no accidental rewrite of the kingdom, the table is holding.
