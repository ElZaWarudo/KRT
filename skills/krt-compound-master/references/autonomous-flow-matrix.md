# Autonomous Flow Matrix

Load when deciding whether an autonomous blocker allows safe independent work.

| Blocked condition | External mutation allowed? | Safe independent continuation |
|---|---:|---|
| Ledger missing, expired, revoked, superseded, or hash-mismatched | No | Local analysis and docs only |
| Runtime enforcement boundary unconfirmed | No | Validation-only and local work |
| Pre-execution audit write failed | No | None until audit path is fixed |
| Post-execution audit write failed after side effect | No | Reconciliation only |
| Merge blocked by missing approval/check/protection state | No merge | Independent review units may continue if ledger scope permits |
| Merge queue required but queue mutation not allowed | No merge | Independent PR/Jira prep may continue |
| PR body, PR create, or PR update blocked | No PR mutation | Implementation/review may continue |
| Reviewer request blocked | No reviewer request | PR can remain open without duplicate/spam requests |
| Jira completion blocked | No done transition | PR/reviewer work may continue |
| Jira backlink blocked by ambiguous binding | No Jira mutation | GitHub work may continue |
| Branch push or cleanup blocked | No branch mutation | Non-branch local work only |
| Stack retarget blocked | No downstream merge | Upstream review/merge candidates may continue |

## Validation Order

1. Run fixture tests for ledger, executor, GitHub validators, and Jira validators.
2. Run quick skill validation for each modified skill.
3. Run `git diff --check`.
4. Sync edited skills to `/home/teb/.agents/skills/` when immediate runtime availability is expected.

## Scenario Links

- Ledger lifecycle fixtures: `skills/krt-compound-master/scripts/fixtures/autonomy-ledgers/`
- GitHub merge/branch/reviewer/stack fixtures: `skills/krt-release-marshal/scripts/fixtures/github-autonomy/`
- Jira text/binding/transition fixtures: `skills/krt-jira-scribe/scripts/fixtures/jira-autonomy/`
- Historical stacked PR/Jira/CI patterns: `docs/orchestration/archive/compound-master-state/2026-05-11-productpass-delegated-architecture-full-state.md`
