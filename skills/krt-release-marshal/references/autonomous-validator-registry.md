# Autonomous Validator Registry

Load when Release Marshal receives an autonomous mutation handoff.

Every autonomous external mutation must name one mutation class and pass the ledger validator plus the owning class validator. Missing validators block the mutation.

The executor resolves validators from this registry. Do not accept caller-provided validator paths for autonomous execution.

| Mutation class | Owning skill | Validator |
|---|---|---|
| `branch_push` | `krt-release-marshal` | `scripts/check_branch_mutation.py` |
| `branch_force_push` | `krt-release-marshal` | `scripts/check_branch_mutation.py` |
| `branch_cleanup` | `krt-release-marshal` | `scripts/check_branch_mutation.py` |
| `pr_create` | `krt-release-marshal` | `scripts/check_pr_mutation.py` |
| `pr_update` | `krt-release-marshal` | `scripts/check_pr_mutation.py` |
| `pr_ready` | `krt-release-marshal` | `scripts/check_pr_mutation.py` |
| `reviewer_request` | `krt-release-marshal` | `scripts/check_reviewer_request.py` |
| `pr_merge` | `krt-release-marshal` | `scripts/check_merge_eligibility.py` |
| `pr_merge_queue` | `krt-release-marshal` | `scripts/check_merge_eligibility.py` |
| `pr_auto_merge` | `krt-release-marshal` | `scripts/check_merge_eligibility.py` |
| `jira_create` | `krt-jira-scribe` | `scripts/check_jira_issue_mutation.py` |
| `jira_update` | `krt-jira-scribe` | `scripts/check_jira_issue_mutation.py` |
| `jira_backlink` | `krt-jira-scribe` | `scripts/check_jira_binding.py` |
| `jira_transition_review` | `krt-jira-scribe` | `scripts/check_jira_transition.py` |
| `jira_transition_done` | `krt-jira-scribe` | `scripts/check_jira_transition.py` |

Resolve validators from the repository first, then from the installed runtime path such as `/home/teb/.agents/skills/<skill>/...`. Do not substitute free-form agent judgment for a missing validator.

Fixture references for reviewing/extending validators:

- GitHub PR, branch, reviewer, merge, and stack scenarios: `references/autonomous-github-fixtures.md`
- Jira text, issue, binding, and transition scenarios: `../krt-jira-scribe/references/autonomous-jira-fixtures.md` in a repository checkout, or the installed `krt-jira-scribe` reference in runtime.
