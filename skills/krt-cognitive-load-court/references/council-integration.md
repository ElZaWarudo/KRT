# Product Polish Council Integration

## Integration Decision

The Cognitive Load Court is a focused sibling of `krt-product-polish-council`, not its thirteenth evaluator.

The Council asks, "How mature and coherent is this product across its important flows?" The Court asks, "What avoidable mental work does this task impose on this user in this context, and what evidence supports that claim?"

The six Court factors cross several Council dimensions and require task profile, expertise, and measurement detail that a single Council evaluator cannot represent. Keep the passes independent, then merge accepted causes at synthesis.

## Ownership

- **Council owns:** the versioned application atlas, broad product coverage, the twelve-dimension quality profile, and the unified polish backlog.
- **Court owns:** the task dossier additions, six-factor burden profile, cognitive-load claim basis, measurement design, and `CL-*` findings.
- **Shared:** stable atlas IDs, environment snapshot, screenshots, recordings, traces, constraints, coverage gaps, and Council-compatible priorities.

Do not create a second permanent application atlas. For a durable Court artifact, store the case report under `docs/audits/cognitive-load/` only when the user or repository workflow calls for versioned audit output. Otherwise return it in the active task.

## Council-Wide Cognitive-Load Overlay

Every one of the twelve Council evaluators applies all six Court factors to every `POL-*` finding:

- `M` - Memory;
- `S` - Search;
- `I` - Integration;
- `D` - Decision;
- `U` - Uncertainty;
- `R` - Recovery.

The evaluator returns applicable factors, a stable role or target profile, rationale, claim basis, profile sensitivity, and whether the finding is a Court candidate. An explicit empty factor list is valid; it records that the lens was applied and found no material cognitive effect.

This overlay remains secondary to the evaluator's product-polish dimension. It is a structured signal, not a `CL-*` finding, Court verdict, measurement, or cognitive score. The Council Lead rejects findings whose overlay remains missing after one contract-only repair pass.

The Lead normalizes all twelve outputs and runs the Council's `scripts/check_cognitive_overlay.py`. Its validated tuples and `court_required` result are the referral authority; semantic evidence quality remains a Lead judgment.

## When to Refer a Case

The Council Lead must refer to the full Court when any condition is true:

- the user explicitly asks about cognitive load, mental effort, overload, or workload measurement;
- an accepted P0 or P1 finding has at least one cognitive-load factor;
- two or more independent evaluators flag the same `FLOW-* x user profile x factor` tuple;
- any accepted finding reports a possible or confirmed expertise/profile reversal;
- a baseline and redesign must be compared with behavioral or workload evidence.

Do not convene the Court for an isolated P2/P3 signal that does not meet another gate, a generic accessibility pass, or a cosmetic issue with an empty factor list. The Council still includes every overlay in its report.

## Combined Workflow

1. The Council Lead validates or bounds the application atlas and prepares the shared evidence packet.
2. All twelve evaluators independently return their primary findings with the required cognitive-load overlay.
3. The Lead runs the deterministic overlay checker, which validates every overlay, aggregates `FLOW x profile x factor` tuples, and applies the referral gate.
4. When the gate fires, the Court receives the triggering tuples and factual packet, but not Council titles, severities, conclusions, or corrections.
5. The Court independently returns its six-factor profile, accepted `CL-*` findings, `Keep` list, measurement status, and later `POL-*` cross-references.
6. The Council Lead performs final synthesis and deduplicates by root cause. Preserve the Court's claim basis and measurement limitations in the unified backlog.
7. One remediation slice may resolve both `CL-*` and `POL-*` findings. Keep both IDs in acceptance criteria.
8. After a change, re-run affected Court assessors and Council evaluators. Update the atlas first when mapped behavior changed.

The Council Lead retains final cross-product prioritization. The Court retains authority over whether a cognitive-load claim is heuristic, observed, or measured.

## Cross-Reference Guide

These are common relationships, not one-to-one mappings:

| Court factor | Frequent Council cross-references |
|---|---|
| Memory | Behavioral consistency, user protection, context continuity |
| Search | Scope and focus, interface hierarchy, content and language, platform conventions |
| Integration | Status and feedback, interface hierarchy, content and language, built-in accessibility |
| Decision | Scope and focus, user protection, interface hierarchy, content and language |
| Uncertainty | Status and feedback, non-ideal states, content and language, context continuity |
| Recovery | Non-ideal states, user protection, status and feedback, context continuity |

Assign the primary owner by root cause. For example, a distant validation message is primarily `Integration`; an actionable message that cannot restore input is primarily `Recovery`; an invisible save outcome is primarily `Uncertainty`.

## Standalone and Degraded Paths

- If the Court runs without the Council, build a bounded task dossier and complete the audit. Record that application-wide coverage and atlas freshness were not established.
- If the Council runs without the Court, every evaluator still returns the overlay. Report any tuples that fire the gate as Court-unavailable verification gaps without blocking the broader audit.
- If the atlas is stale, update it through the Council when available. If update is out of scope, narrow the Court to directly observed tasks and mark atlas-derived facts as unverified.
- If no user measurement is possible, finish a heuristic case and label every workload claim as predicted. Do not present the degraded path as measured evidence.
