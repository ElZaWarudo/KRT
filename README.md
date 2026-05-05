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

| Skill | Purpose |
|---|---|
| `$krt:harness-wise` | Build or review a compact coding harness before implementation. Good for repo reconnaissance, context curation, stale-doc checks, risk estimates, and skill recommendations. |
| `$krt:compound-master` | Orchestrate larger delivery programs: context gate, roadmap, brainstorms, plans, document reviews, work packages, execution gates, code review, and PR/Jira handoff. |
| `$krt:release-marshal` | Direct the final delivery march: commits, rebase, Jira, push, PR creation, reviewer requests, and Jira review follow-up. |
| `$krt:gitflow-knight` | Keep branch hygiene and atomic commits in formation. |
| `$krt:rebase-smith` | Re-forge branch history onto the correct base without dragging old steel into the PR. |
| `$krt:jira-scribe` | Manage Jira Server/Data Center issues, subtasks, sprints, and transitions in Spanish. |

Skills can bring their own auxiliary files: references, templates, assets, adapter configs, or agent definitions. Keep the main `SKILL.md` readable; put the heavy armor in nearby files.

## Quick Examples

Prepare a coding harness before touching a repo:

```text
Use $krt:harness-wise before adding invoice CSV export.
```

Trim noisy docs before a feature:

```text
Use $krt:harness-wise docs-trim before working on billing.
```

Turn a documented initiative into delivery artifacts:

```text
Use $krt:compound-master for docs/specs/reporting.md mode:artifacts
```

Resume execution from existing orchestration state:

```text
Use $krt:compound-master mode:resume jira-policy:optional parallel:false
```

## Install

Install one skill:

```bash
npx -y skills add ElZaWarudo/krt --skill krt:<skill-name>
```

Install the whole table:

```bash
npx -y skills add ElZaWarudo/krt --all
```

Install the release court:

```bash
npx -y skills add ElZaWarudo/krt \
  --skill krt:release-marshal \
  --skill krt:gitflow-knight \
  --skill krt:rebase-smith \
  --skill krt:jira-scribe
```

`krt:release-marshal` expects those three companions to be available. The skills CLI supports repeated `--skill` flags and `--all`; KRT does not currently rely on automatic dependency resolution in skill frontmatter. The Mariscal can read the room, but he still needs the room installed.

Target a specific runtime when needed:

```bash
npx -y skills add ElZaWarudo/krt --skill krt:<skill-name> -a <agent>
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
  harness-wise/
    SKILL.md
    references/
  compound-master/
    SKILL.md
    assets/
      codex-agents/
  release-marshal/
    SKILL.md
  gitflow-knight/
    SKILL.md
  rebase-smith/
    SKILL.md
  jira-scribe/
    SKILL.md
```

## Local Development

Edit skills in `skills/<name>/`. Keep reusable detail in `references/` or `assets/` so the top-level skill stays compact.

Validate with whichever skill validator your target runtime uses. For manual checks, install the skill into a disposable agent profile and run the quick examples above. If the agent comes back with a quest, a map, and no accidental rewrite of the kingdom, the table is holding.
