# Gates And Reconciliation

Use this reference after dispatching workers, when reviewing outputs, and before release handoff.

## Gate Ladder

For each unit:

1. **Scope gate**
   - Worker stayed inside included scope.
   - Excluded work remains untouched.
   - Any necessary scope expansion is recorded. Manual flow requires approval; autonomous flow marks broad expansion `split-required` unless the ledger allows it.

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
   - Production-sensitive units preserve compatibility unless manual approval or autonomy ledger policy explicitly allows a breaking change.

5. **State gate**
   - Queue status, branch/base facts, blockers, verification evidence, and downstream-fix notes are current.
   - Jira issue/subtask state, when relevant, is reconciled through the selected Jira provider skill.
   - Non-fatal blockers are recorded in `docs/swarm/blockers.yaml`.

6. **Release handoff gate**
   - `krt-release-marshal` receives the completed unit context.
   - The swarm seneschal does not commit, push, open PRs, mutate Jira, request reviewers, or merge unless routed through the release skill and a manual approval or autonomy ledger permits it.
   - Jira handoff context must name `jira_provider` as `cloud`, `server-datacenter`, or `none`. There is no default provider.

## Reconciliation Checklist

For each worker result:

- Fetch or inspect the actual changed files.
- Compare changes to the unit contract.
- Identify shared files touched by multiple workers.
- Detect public contract, auth, data, dependency, config, or generated-artifact changes.
- Record verification commands and outcomes.
- Record blockers and whether they affect sibling units.
- Decide: `release-ready`, `needs-fix`, `blocked`, `deferred`, or `split-required`.
- Update `docs/swarm/queue-state.yaml` and `docs/swarm/blockers.yaml` when statuses or blockers change.

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

## Blocker Reconciliation

Use `blocker-ledger.md` when a worker reports a blocker.

- If the blocker affects only one unit, record it, mark that unit `blocked` or `deferred`, and continue with unrelated ready units.
- If the blocker affects a dependency, public contract, auth, data, or central technical foundation, stop dependent dispatch and continue only with independent work.
- If the blocker affects security, real DIAN compliance, productive accounting, productive payroll, or legal production exposure, record it as high risk and require resolution before production release.
- In manual flow, ask only when no ready independent work remains or the blocker can make the wave implement the wrong foundation.
- In autonomous flow, do not ask; record the blocker, stop dependent work, and continue unrelated units until no safe work remains.

## Release Handoff Packet

For each release-ready unit, prepare:

```text
Work package or source: <path/link>
Review unit or queue ID: <id>
Jira key: <key or none>
Current branch: <branch>
Intended base: <branch>
PR grouping: standalone | grouped | stacked
Covered units: <ids>
Jira policy: required | optional | skip
jira_provider: cloud | server-datacenter | none
Suggested PR title: <semantic title>
Suggested PR body bullets:
- <user-facing change>
Release notes:
- <user-facing release note>
Suggested commit grouping:
- <type(scope): summary> -- <surfaces> -- <reason>
Verification results for readiness:
- <command/result>
Impact/CI risk:
- <summary or not required>
Downstream-fix notes:
- <none or PR/finding mapping>
Suggested Jira transition:
- <transition name or none>
```

Pass this to `krt-release-marshal`. Do not include internal queue mechanics in public PR copy unless repo convention requires it.

Include the resolved `jira_provider` and matching skill in every handoff. Do not silently switch providers. Suggested Jira transitions are context only; Release Marshal and the selected Jira provider skill own confirmed or ledger-covered execution.

## Closeout Shape

Factory closeout should say:

```text
Factory status: <mode/status>
Wave: <name>
Completed:
- <unit>
Blocked:
- <unit>: <reason>
Blockers recorded:
- <blocker id>: <type>/<owner>/<status>
Release-ready:
- <unit>
Handed off:
- <unit>: <PR/Jira if available>
Updated state:
- <files>
Next invocation:
Use krt-swarm-seneschal ...
```
