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
| `$harness-wise` | Build or review a compact coding harness before implementation. Good for repo reconnaissance, context curation, stale-doc checks, risk estimates, and skill recommendations. |
| `$compound-master` | Orchestrate larger delivery programs: context gate, roadmap, brainstorms, plans, document reviews, work packages, execution gates, code review, and PR/Jira handoff. |

Skills can bring their own auxiliary files: references, templates, assets, adapter configs, or agent definitions. Keep the main `SKILL.md` readable; put the heavy armor in nearby files.

## Quick Examples

Prepare a coding harness before touching a repo:

```text
Use $harness-wise before adding invoice CSV export.
```

Trim noisy docs before a feature:

```text
Use $harness-wise docs-trim before working on billing.
```

Turn a documented initiative into delivery artifacts:

```text
Use $compound-master for docs/specs/reporting.md mode:artifacts
```

Resume execution from existing orchestration state:

```text
Use $compound-master mode:resume jira-policy:optional parallel:false
```

## Install

Install a skill from KRT:

```bash
npx -y skills add ElZaWarudo/krt --skill harness-wise
npx -y skills add ElZaWarudo/krt --skill compound-master
```

Target a specific runtime:

```bash
npx -y skills add ElZaWarudo/krt --skill harness-wise -a codex
npx -y skills add ElZaWarudo/krt --skill compound-master -a codex
```

Update installed skills:

```bash
npx skills update harness-wise
npx skills update compound-master
```

If `npx` wanders into the forest:

```bash
npm exec --yes --package skills -- skills update harness-wise
```

## Components

```text
skills/
  harness-wise/
    SKILL.md
    agents/
    references/
  compound-master/
    SKILL.md
    assets/
      codex-agents/
```

## Local Development

Edit skills in `skills/<name>/`. Keep reusable detail in `references/` or `assets/` so the top-level skill stays compact.

Validate with whichever skill validator your target runtime uses. For manual checks, install the skill into a disposable agent profile and run the quick examples above. If the agent comes back with a quest, a map, and no accidental rewrite of the kingdom, the table is holding.
