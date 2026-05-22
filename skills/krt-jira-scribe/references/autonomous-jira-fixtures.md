# Autonomous Jira Fixtures

Load when reviewing or extending Jira-side autonomous validators.

Fixture directory:

```text
skills/krt-jira-scribe/scripts/fixtures/jira-autonomy/
```

Validator coverage:

| Scenario | Fixture | Validator outcome |
|---|---|---|
| Spanish issue create/update payload with parent subtask shape | `issue_valid.json` | Allows `jira_create` |
| Jira text contains planning IDs, commit prefix, and PR chatter | `issue_bad_text.json` | Blocks text fields |
| PR remote link already exists with deterministic global ID | `binding_existing.json` | Allows no-op/update with warning |
| Jira issue points to a different PR | `binding_conflict.json` | Blocks `jira-linked-to-different-pr` |
| Linked PR merged and exact done transition is available | `transition_done.json` | Allows `jira_transition_done` |
| Multiple done-like transitions exist | `transition_multiple_done.json` | Blocks unless ledger names exact transition ID |
| Issue already done and linked to merged PR | `transition_already_done.json` | Allows no-op success |

The validators deliberately reject Markdown state as authority. Exact Jira key binding must come from the ledger, live Jira/PR remote-link evidence, or a same-contract audit event. Completion to `Hecho` requires GitHub merge evidence for the linked PR.
