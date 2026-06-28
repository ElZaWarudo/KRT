# Gates And Reconciliation

Use this reference after dispatching workers, when reviewing outputs, and before release handoff.

## Gate Ladder

For each unit:

1. **Scope gate**
   - Worker stayed inside included scope.
   - Excluded work remains untouched.
   - Any necessary scope expansion is recorded and approved.

2. **Verification gate**
   - Required commands passed, or a material verification gap is recorded.
   - Changed contracts have consumer-aware checks.
   - Generated artifacts or docs were inspected when relevant.

3. **Review gate**
   - Code review ran for implementation changes.
   - Findings at or above threshold were fixed or explicitly deferred.
   - Review output maps to the unit contract, not a generic code audit.

4. **Security/production gate**
   - Security-sensitive units ran the security specialist or an explicit fallback.
   - Production-sensitive units preserve compatibility unless the user approved a breaking change.

5. **State gate**
   - Queue status, branch/base facts, blockers, verification evidence, and downstream-fix notes are current.
   - Jira Cloud issue/subtask state, when relevant, is reconciled through `krt-jira-cloud-scribe`.

6. **Release handoff gate**
   - `krt-release-marshal` receives the completed unit context.
   - The swarm seneschal does not commit, push, open PRs, mutate Jira, request reviewers, or merge unless routed through the release skill and an explicit approval/ledger permits it.
   - Jira handoff context must name whether it is Jira Cloud or Server/Data Center. Default is Jira Cloud with `krt-jira-cloud-scribe`.

## Reconciliation Checklist

For each worker result:

- Fetch or inspect the actual changed files.
- Compare changes to the unit contract.
- Identify shared files touched by multiple workers.
- Detect public contract, auth, data, dependency, config, or generated-artifact changes.
- Record verification commands and outcomes.
- Record blockers and whether they affect sibling units.
- Decide: `release-ready`, `needs-fix`, `blocked`, or `split-required`.

## Conflict Handling

If two workers changed the same surface:

1. Stop new dispatch for dependent units.
2. Identify which unit owns the surface.
3. Choose one of:
   - rebase child onto parent after parent merge
   - collapse into one reviewable PR if that improves reviewability
   - split one worker's change into a follow-up unit
4. Record the decision in queue state.

Do not resolve conflicts by creating one large unreviewable PR.

## Release Handoff Packet

For each release-ready unit, prepare:

```text
Work package or source: <path/link>
Review unit or queue ID: <id>
Current branch: <branch>
Intended base: <branch>
PR grouping: standalone | grouped | stacked
Covered units: <ids>
Jira policy: required | optional | skip
Jira mode: cloud | server-datacenter | none
Suggested PR title: <semantic title>
Suggested PR body bullets:
- <user-facing change>
Suggested commit grouping:
- <type(scope): summary> -- <surfaces> -- <reason>
Verification results for readiness:
- <command/result>
Impact/CI risk:
- <summary or not required>
Downstream-fix notes:
- <none or PR/finding mapping>
```

Pass this to `krt-release-marshal`. Do not include internal queue mechanics in public PR copy unless repo convention requires it.

When `Jira mode: cloud`, include that Jira lookup, issue/subtask mapping, and readiness came from `krt-jira-cloud-scribe`. Do not silently downgrade to `krt-jira-scribe`.

## Closeout Shape

Factory closeout should say:

```text
Factory status: <mode/status>
Wave: <name>
Completed:
- <unit>
Blocked:
- <unit>: <reason>
Release-ready:
- <unit>
Handed off:
- <unit>: <PR/Jira if available>
Updated state:
- <files>
Next invocation:
Use krt-swarm-seneschal ...
```
