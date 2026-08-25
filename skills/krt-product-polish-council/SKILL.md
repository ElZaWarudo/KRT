---
name: krt-product-polish-council
description: Orchestrates a comprehensive, evidence-based polish audit of web, mobile, and desktop applications through a versioned atlas, a cartographer, and twelve evaluators specializing in scope, consistency, feedback, non-ideal states, protection, hierarchy, content, perceived performance, platform conventions, accessibility, continuity, and completeness. Use when asked to polish an application, assess its product maturity, walk end-to-end flows, find rough seams or amateur behavior, produce a prioritized improvement backlog, or verify that a round of changes raised perceived quality.
---

# krt-product-polish-council

Evaluate the application as a system of behavior, not a collection of screens. Treat perceived quality as a nearly multiplicative relationship among consistency, reliability, clarity, responsiveness, and care: one very weak dimension limits the whole even when the average is high.

## Operating Principles

- Use `docs/product/application-atlas.md` as shared, versioned context unless the repository already has an equivalent convention.
- Separate declared intent, observed behavior, and inference. Do not turn an inference into a requirement or defect.
- Audit real end-to-end flows. Use screenshots as partial evidence, never as an automatic substitute for behavior.
- Have all twelve evaluators work read-only from the same evidence packet.
- Reserve synthesis, deduplication, prioritization, and coverage decisions for the lead agent.
- Treat a review request as authorization to audit, not to change code. Implement only when the user asks.

## Choose the Mode

- **Atlas**: create, update, or validate only the versioned atlas.
- **Audit**: build or validate the atlas, run the council, and deliver a diagnosis and backlog. This is the default.
- **Audit and remediation**: complete the audit first, then implement authorized changes and verify them.
- **Polish regression**: compare a new version with an earlier atlas and audit, update the evidence, and reopen only affected findings.

## Load References

- Read `references/application-atlas.md` before checking, creating, or updating the atlas.
- Read `references/evaluator-catalog.md` before dispatching or running any of the twelve roles.
- Read `references/evidence-and-report-protocol.md` before rating findings or synthesizing the report.

## Workflow

### 1. Check Atlas Freshness

Make this the first step of every invocation:

1. Resolve the repository root, current `HEAD`, and atlas path.
2. If the atlas does not exist, mark it `missing` and continue to the intent interview.
3. If it exists, run this skill's `scripts/check_atlas_freshness.py` against `docs/product/application-atlas.md`.
4. Consider the atlas `fresh` only when the fingerprint of covered files matches the current commit tree and no relevant uncommitted changes exist.
5. If the result is `stale`, update the atlas before launching evaluators. Do not mistake an outdated atlas for a product defect.

Use the SHA for provenance and the covered-file fingerprint as the authority on freshness. Exclude the atlas itself from the fingerprint to avoid self-reference.

### 2. Resolve Product Intent

Read briefs, requirements, decisions, available analytics, and product documentation first. If they do not answer the intent questions in `references/application-atlas.md`, ask the product owner one compact round of questions and wait for the response.

Do not ask about facts discoverable in the repository or application. Ask about purpose, user, expected outcome, risks, and deliberate boundaries. If the user insists on continuing without answering, record assumptions and lower confidence; do not penalize a discrepancy against unconfirmed intent as a failure.

### 3. Build or Update the Atlas

Assign the **Cartographer** to explore the application factually. Inventory platforms, actors, roles, surfaces, navigation, flows, states, data, permissions, integrations, destructive actions, real-world conditions, and evidence gaps.

Keep IDs such as `ROLE-01`, `SURF-03`, `FLOW-07`, and `STATE-12` stable. Update by diff; do not reorder or regenerate the whole file without need. Do not put quality judgments or recommendations in the atlas.

Do not convene the council until the coverage gate in the reference passes or the gaps are explicitly accepted.

### 4. Prepare the Shared Evidence Packet

Give every evaluator the same snapshot:

- atlas path and fingerprint;
- commit, environment, platform, viewport, and input methods examined;
- in-scope and out-of-scope flows and roles;
- permitted credentials or test data, without copying secrets;
- available screenshots, recordings, traces, files, and observations;
- restrictions on network access, mutations, destructive actions, and external services;
- gaps and unobserved areas.

Do not give an evaluator another evaluator's findings before their pass is complete; avoid anchoring and artificial consensus.

### 5. Run the Twelve-Evaluator Council

Use one independent agent per dimension when the runtime supports subagents. Run them in waves if fewer than twelve slots are available. Keep them read-only and without mutable shared files. If subagents are unavailable, run all twelve contracts sequentially in the main thread without omitting any.

Each evaluator must:

1. Walk the atlas flows through its exclusive lens.
2. Compare the happy path, transition, failure, and real-world condition when relevant.
3. Cite exact evidence and label it `observed`, `code`, `declared`, `inferred`, or `unverified`.
4. Return a rating, confidence, findings, behaviors to preserve, and gaps.
5. Propose a bounded correction and an observable check for each finding.

### 6. Synthesize Without Diluting Weaknesses

Apply the shared protocol. Assign each problem one primary dimension and cross-reference the others. Merge duplicates by cause and flow, not by matching words.

Do not average the twelve ratings to declare success. Identify the weakest link, systemic failures, and the highest-frequency or highest-consequence flows. Prioritize operability, loss of work, trust, and recovery before ornament.

Deliver one coherent report, not twelve juxtaposed mini-reports.

### 7. Remediate and Reverify When Authorized

Turn the accepted backlog into small units with files, acceptance criteria, and tests. Reuse the application's conventions and components. For optional deeper work, use `krt-frontend-ux-guardian` for functional UX, `krt-interface-inquisitor` for visual composition, or `krt-interaction-polisher` for temporal response when available; their absence must not block the flow.

After changing routes, roles, navigation, states, or flows, update the atlas and its fingerprint. Rerun affected evaluators and make a short pass across all twelve dimensions to catch cross-cutting regressions.

## Agent Topology

- **Lead**: sets scope, protects constraints, accepts the coverage gate, and synthesizes.
- **Cartographer**: interviews for intent when needed and maintains the factual atlas.
- **Evaluators 01-12**: independently apply the contracts in `references/evaluator-catalog.md`.
- **Verifier**: in remediation mode, reproduces acceptance criteria without reopening product decisions.

The Lead must not delegate final synthesis or allow an evaluator to implement during a diagnostic pass.

## Non-Negotiables

- Do not invent routes, states, roles, permissions, data, or behavior that was not observed or declared.
- Do not rate an inaccessible area as a failure; mark it `unverified` and explain what is missing.
- Do not test destructive, financial, external, or production actions without authorization and safe data.
- Do not hide the weakest link behind an average, an aesthetic score, or a long list of minor improvements.
- Do not recommend new features when a clarity, consistency, feedback, or recovery fix solves the problem.
- Do not accept a finding without evidence, user effect, a concrete correction, and observable verification.
- Do not declare the application polished when the atlas is absent, stale, or materially incomplete.
