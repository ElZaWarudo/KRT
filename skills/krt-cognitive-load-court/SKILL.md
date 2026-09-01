---
name: krt-cognitive-load-court
description: Diagnose avoidable cognitive workload in software task flows through six independent lenses covering memory, search, integration, decision, uncertainty, and recovery. Use when asked to audit cognitive load or mental effort, compare workflow variants, investigate an interface that feels mentally taxing, or verify that a redesign reduced workload. Do not use for broad product-polish audits or clinical cognitive assessment.
---

# krt-cognitive-load-court

Judge the avoidable cognitive burden imposed by an interface on a particular user performing a particular task in a particular context. Preserve useful complexity and decision quality; the goal is not to make every interface sparse.

## Operating Principles

- Use `task x user profile x context` as the unit of analysis, not the screen or component.
- Separate necessary task complexity from avoidable interface burden. Mental effort can be productive in learning, analysis, and high-consequence review.
- Keep predicted risk, observed behavior, self-reported workload, and instrumented measurement distinct.
- Treat the six dimensions as an engineering decomposition, not a validated psychometric scale. Do not sum them into a universal cognitive-load score.
- Compare realistic end-to-end tasks. A screenshot, DOM count, choice count, or working-memory rule is never sufficient proof of overload.
- Treat a review request as authorization to diagnose, not to change code or recruit, record, or test people. Remediate or conduct user research only when authorized.

## Choose the Mode

- **Case audit**: diagnose one or more named task flows with the best available evidence. This is the default.
- **Measured comparison**: compare a baseline and candidate using a controlled behavioral, subjective, or instrumented protocol.
- **Audit and remediation**: complete the case audit first, then implement authorized changes and verify them.
- **Regression**: re-run affected dimensions and prior verification criteria after a change.
- **Council referral**: independently test task-specific factor signals produced by the required Council overlay without repeating the full council.

## Load References

- Read `references/cognitive-load-model.md` before framing the case or recommending a cognitive-load correction.
- Read `references/assessor-catalog.md` before dispatching or sequentially running the six assessors.
- Read `references/evidence-and-measurement-protocol.md` before assigning verdicts, designing measurement, or synthesizing the report.
- Read `references/council-integration.md` only when an application atlas exists, the Product Polish Council is also in scope, or a handoff between the two skills is needed.

## Workflow

### 1. Frame the Docket

Resolve these facts from product documentation, the application, and the repository before asking the user:

- target task and success signal;
- target user, domain knowledge, product familiarity, and relevant abilities;
- frequency, time pressure, interruptions, device, input method, and environment;
- consequence of delay, error, abandonment, or incorrect confidence;
- complexity that the domain deliberately requires;
- baseline, candidate, or earlier report when comparison is requested.

Ask one compact round only for material intent that cannot be discovered. If the user continues without an answer, record the assumption as `inferred`, narrow the claim, and lower confidence. Do not issue high-severity product-alignment findings from unconfirmed intent alone.

### 2. Build or Reuse the Task Dossier

When a fresh `docs/product/application-atlas.md` exists, reuse its stable `FLOW-*`, `SURF-*`, `ROLE-*`, and `STATE-*` IDs. Validate freshness through `krt-product-polish-council` when that skill is available. A stale atlas is a lead, not current evidence.

For a Council referral, accept the triggering `FLOW x user profile x factor` tuples as scope only. Do not treat Council factor tags, titles, severities, conclusions, or corrections as Court evidence. Run the six assessors independently before comparing results.

When no usable atlas exists, build a bounded task dossier in the evidence packet. Map the entry, steps, information dependencies, decisions, system states, failure paths, recovery, preserved context, and realistic conditions for only the in-scope tasks. Do not block a focused Court audit solely because the broader atlas is unavailable.

### 3. Capture a Shared Baseline

Walk each task from before entry through completion and recovery. Record the version, environment, platform, viewport, input, data conditions, and evidence gaps. Include the happy path, meaningful transitions, at least one applicable failure, and realistic interruption or volume conditions.

Use runtime behavior when available. Use code and tests to locate hidden states or explain causality, not to claim that an interaction is understandable. Screenshots are valid evidence for layout and visible context but not for time, uncertainty, recovery, or task completion.

### 4. Convene the Six Assessors

Give every assessor the same dossier, evidence packet, assigned tasks, and reporting protocol. Use one independent read-only agent per dimension when the runtime supports authorized subagents. If not, run all six contracts sequentially in the main thread without omitting a dimension.

Do not expose one assessor's findings to another before all first passes finish. Each assessor must identify necessary complexity, cite exact evidence, state the claim basis, preserve successful behavior, propose a bounded correction, and define an observable verification.

### 5. Deliberate by Root Cause

Assign every accepted finding one primary dimension and cross-reference secondary effects. Merge only findings that share a cause, task, and correction. Keep distinct causes separate even when they appear on the same screen.

Do not average dimension verdicts. State the weakest material burden, the affected user profile and task, the evidence strength, and the consequence. A severe heuristic risk remains a prediction until behavioral or measurement evidence supports it.

### 6. Measure Only to the Required Claim

Use the lightest method that can answer the decision:

- heuristic inspection for finding plausible interface-imposed burden;
- direct observation and task metrics for showing where performance degrades;
- post-task self-report for perceived workload;
- controlled or instrumented methods for stronger comparative claims when expertise and equipment are available.

For claims that a redesign *reduced* cognitive load, compare against a baseline under equivalent tasks, data, profiles, and conditions. Follow the measurement protocol; do not invent participants, scores, norms, statistical confidence, or causal certainty.

### 7. Remediate and Reverify When Authorized

Translate accepted findings into small changes with preserved behavior, acceptance criteria, and tests. Prefer removing interface-imposed work over hiding domain information. Check that a correction for one profile does not burden another.

Reproduce each finding's verification criterion. Re-run its primary assessor and cross-referenced assessors, then make a short pass over all six dimensions for the modified task. When a combined Council audit exists, return the results through the integration contract.

## Agent Topology

- **Presiding agent**: sets scope, protects evidence boundaries, accepts coverage, and synthesizes the verdict.
- **Clerk**: creates or updates only the factual task dossier and evidence packet.
- **Assessors 01-06**: independently inspect memory, search, integration, decision, uncertainty, and recovery.
- **Verifier**: in remediation or comparison mode, reproduces acceptance criteria without changing the product decision.

The Presiding agent must not delegate final synthesis. The Clerk and assessors remain read-only during diagnosis.

## Non-Negotiables

- Do not call an interface overloaded because it has more than four items, many choices, high density, or progressive disclosure.
- Do not assume fewer visible options, fewer steps, or less text means less cognitive burden.
- Do not hide information that users need to form an accurate mental model or make a high-consequence decision.
- Do not confuse task duration, eye movement, pupil change, error rate, or a workload score with cognitive load in isolation.
- Do not generalize from experts to novices, from one participant to a population, or from one task to the whole product.
- Do not test destructive, financial, public, sensitive, or production actions without explicit authority and safe data.
- Do not accept a finding without evidence, user effect, bounded correction, and observable verification.
- Do not promote a Council cognitive-load overlay tag into a `CL-*` finding or Court verdict without an independent Court pass.
- Do not claim measured improvement from a heuristic-only pass.
