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

## Documents

Create and visually validate a professional Word report:

```text
Use $krt:word-illuminator to create a grounded technical report from requirements.md and deliver report.docx.
```

Edit an existing Word document without unrelated formatting changes:

```text
Use $krt:word-illuminator to update proposal.docx from corrections.md, compare the result, and deliver a clean final version.
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

Build and safely execute an edge-case campaign:

```text
Use $krt:real-world-edge-testing to exercise this ingestion pipeline across malformed files, attribution errors, dependency timeouts, retries, and recovery using deterministic synthetic fixtures.
```

Design a campaign without touching the environment:

```text
Use $krt:real-world-edge-testing in design mode for the booking workflow. Produce executable cases and strong oracles, but do not run external operations.
```

Update durable docs:

```text
Use $krt:docs-chronicler to update docs and ADRs after this incident fix.
```

## Skill Portfolio Quality

Check structural, metadata, and safety wiring:

```text
Use $krt:skill-arbiter to validate this KRT skill portfolio.
```

Score supervisor-captured results without running a model:

```text
Use $krt:skill-arbiter to validate the corpus and score eval-results.json, preserving inconclusive cases.
```

## Frontend Craft

Run a comprehensive polish audit with cognitive-load coverage:

```text
Use $krt:product-polish-council to audit the application's critical flows. Require every evaluator to apply the six-factor cognitive-load overlay and convene the full Court whenever the referral gate fires.
```

Audit avoidable cognitive workload in a critical task:

```text
Use $krt:cognitive-load-court to audit the project-creation flow for first-time administrators and separate predicted burden from measured evidence.
```

Compare a redesigned flow against its baseline:

```text
Use $krt:cognitive-load-court in measured comparison mode for the current and proposed approval flows. Define equivalent tasks, target profiles, workload evidence, and acceptance criteria before comparing them.
```

Audit an implemented workflow's interaction feel:

```text
Use $krt:interaction-polisher to audit this interface's feedback, motion, latency, state transitions, and reduced-motion behavior.
```

Refine interaction quality after a functional frontend build:

```text
Use $krt:interaction-polisher to inspect the primary workflow in a browser, implement the highest-value interaction refinements, and verify slow, failed, keyboard, touch, and reduced-motion paths.
```
