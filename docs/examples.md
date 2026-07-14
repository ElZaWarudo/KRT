# Examples

These prompts are meant to be copied, adjusted, and then blamed on good taste.

## Discovery

Clarify a rough requirement:

```text
Use $krt:requirements-weaver for this client brief before making a plan.
```

Turn requirements into delivery shape:

```text
Use $krt:delivery-navigator for docs/requirements/billing-export.md.
```

## Harness

Prepare context before touching code:

```text
Use $krt:harness-wise before adding invoice CSV export.
```

Create a versionable harness artifact:

```text
Use $krt:harness-wise and generate a harness file for adding invoice CSV export.
```

Improve an existing harness:

```text
Use $krt:harness-wise to improve docs/harnesses/billing-refactor.md.
```

## Delivery

Turn a documented initiative into artifacts:

```text
Use $krt:compound-master for docs/specs/reporting.md mode:artifacts
```

Resume execution from orchestration state:

```text
Use $krt:compound-master mode:resume jira-policy:optional parallel:false
```

Compact noisy Compound Master state:

```text
Use $krt:state-archivist on docs/orchestration/compound-master-state.md
```

## Operations

Triage PR feedback:

```text
Use $krt:review-herald to classify review comments and draft replies for PR #42.
```

Resolve PR feedback:

```text
Use $krt:review-herald to address review comments on PR #42, apply safe fixes, verify them, and prepare replies.
```

Investigate CI:

```text
Use $krt:ci-questor to explain why the latest GitHub Actions run failed and what to do next.
```

Prepare deployment:

```text
Use $krt:deploy-summoner to review Helm values and produce a safe rollout and rollback plan.
```

Update durable docs:

```text
Use $krt:docs-chronicler to update docs and ADRs after this incident fix.
```

## Frontend Craft

Audit an implemented workflow's interaction feel:

```text
Use $krt:interaction-polisher to audit this interface's feedback, motion, latency, state transitions, and reduced-motion behavior.
```

Refine interaction quality after a functional frontend build:

```text
Use $krt:interaction-polisher to inspect the primary workflow in a browser, implement the highest-value interaction refinements, and verify slow, failed, keyboard, touch, and reduced-motion paths.
```
