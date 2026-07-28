# Safety Notes

KRT's root rule: read-only discovery before mutation, explicit approval before risky external effects, and no secret-shaped fireworks in logs or docs.

Each skill owns the detailed guardrails closest to its procedure:

| Skill | Safety note |
|---|---|
| `krt-requirements-weaver` | [`skills/krt-requirements-weaver/references/safety.md`](../skills/krt-requirements-weaver/references/safety.md) |
| `krt-harness-wise` | [`skills/krt-harness-wise/references/safety.md`](../skills/krt-harness-wise/references/safety.md) |
| `krt-roadmap-cartographer` | [`skills/krt-roadmap-cartographer/references/safety.md`](../skills/krt-roadmap-cartographer/references/safety.md) |
| `krt-delivery-navigator` | [`skills/krt-delivery-navigator/references/safety.md`](../skills/krt-delivery-navigator/references/safety.md) |
| `krt-compound-master` | [`skills/krt-compound-master/references/safety.md`](../skills/krt-compound-master/references/safety.md) |
| `krt-state-archivist` | [`skills/krt-state-archivist/references/safety.md`](../skills/krt-state-archivist/references/safety.md) |
| `krt-word-illuminator` | [`skills/krt-word-illuminator/references/safety.md`](../skills/krt-word-illuminator/references/safety.md) |
| `krt-release-marshal` | [`skills/krt-release-marshal/references/safety.md`](../skills/krt-release-marshal/references/safety.md) |
| `krt-review-herald` | [`skills/krt-review-herald/references/safety.md`](../skills/krt-review-herald/references/safety.md) |
| `krt-security-sentinel` | [`skills/krt-security-sentinel/references/safety.md`](../skills/krt-security-sentinel/references/safety.md) |
| `krt-ci-questor` | [`skills/krt-ci-questor/references/safety.md`](../skills/krt-ci-questor/references/safety.md) |
| `krt-deploy-summoner` | [`skills/krt-deploy-summoner/references/safety.md`](../skills/krt-deploy-summoner/references/safety.md) |
| `krt-docs-chronicler` | [`skills/krt-docs-chronicler/references/safety.md`](../skills/krt-docs-chronicler/references/safety.md) |
| `krt-document-forge` | [`skills/krt-document-forge/references/safety.md`](../skills/krt-document-forge/references/safety.md) |
| `krt-gitflow-knight` | [`skills/krt-gitflow-knight/references/safety.md`](../skills/krt-gitflow-knight/references/safety.md) |
| `krt-rebase-smith` | [`skills/krt-rebase-smith/references/safety.md`](../skills/krt-rebase-smith/references/safety.md) |
| `krt-jira-cloud-scribe` | [`skills/krt-jira-cloud-scribe/references/safety.md`](../skills/krt-jira-cloud-scribe/references/safety.md) |
| `krt-jira-scribe` | [`skills/krt-jira-scribe/references/safety.md`](../skills/krt-jira-scribe/references/safety.md) |
| `krt-repo-medic` | [`skills/krt-repo-medic/references/safety.md`](../skills/krt-repo-medic/references/safety.md) |
| `krt-skill-arbiter` | [`skills/krt-skill-arbiter/references/safety.md`](../skills/krt-skill-arbiter/references/safety.md) |

## Shared Rules

- Remote, destructive, notification-causing, production-impacting, or credential-sensitive actions need explicit approval unless an active autonomous ledger and deterministic validator authorize the exact mutation.
- Merge approval is not bundled into release-plan approval.
- Internal agent review never substitutes for GitHub-visible merge gates. On normal/protected bases that still means human reviewer approval; experimental bases may be review-optional only when branch protection/rulesets visibly allow it.
- Secrets, tokens, credentials, kubeconfigs, full env dumps, and masked CI values must not be printed, copied into docs, or moved into archives.
