# Documentation Rubric

Use this rubric to keep documentation durable and small.

## Document Types

| Type | Purpose | Good Signals | Bad Signals |
|---|---|---|---|
| Tutorial | Teach a newcomer by walking through a learning path | Safe sample flow, low assumptions | Mixed with production runbook steps |
| How-to | Help a user accomplish a specific task | Goal-oriented steps, prerequisites, verification | Explains broad concepts instead of actions |
| Reference | Provide exact facts | Complete commands/options/config tables | Hidden narrative, stale examples |
| Explanation | Build understanding | Why, tradeoffs, mental model | Pretends to be an executable runbook |
| ADR | Preserve a significant decision | Context, decision, consequences, status | Decision scattered through chat/PR comments |
| Runbook | Operate or recover a system | Preconditions, diagnostics, action, rollback, smoke checks | Dangerous commands without guardrails |
| Changelog | Communicate user/operator-visible change | Added/changed/fixed grouping | Internal commit log dump |
| Learning | Preserve a reusable lesson | Trigger, insight, durable change | Blame, vague morals, no next action |

## Placement Rules

- Update the nearest existing canonical document first.
- Create a new doc only when the topic needs its own lifecycle, owner, or link target.
- Link summaries to canonical sources instead of repeating long content.
- Keep volatile facts near the code/config that owns them.
- Put reusable agent procedure in skill references; put project history in project docs.

## Quality Checklist

- Current: paths, commands, env vars, dependencies, and examples match repo reality.
- Findable: title, path, and links match how someone would search.
- Actionable: commands and next steps are explicit.
- Scoped: the doc answers one job without becoming a junk drawer.
- Owned: future update trigger is clear, even if no person is named.
- Safe: destructive or production actions require warnings and verification.
- Traceable: decisions and lessons include enough context to understand why.

## Edit Choices

- **Patch:** small update to an otherwise healthy doc.
- **Consolidate:** multiple docs say overlapping or conflicting things.
- **Archive/delete:** doc is stale and no longer has a trustworthy role.
- **Escalate to ADR:** the change records a decision with long-term architectural consequences.
- **Escalate to runbook:** the change affects operational recovery or deployment.
