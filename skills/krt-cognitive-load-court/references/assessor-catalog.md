# Cognitive Load Assessor Catalog

## Shared Contract

Give each assessor the same task dossier, evidence packet, assigned flows, `references/cognitive-load-model.md`, and `references/evidence-and-measurement-protocol.md`.

Base prompt:

```text
Act as Assessor <NN - name>. Work read-only and limit the diagnosis to your assigned cognitive-load dimension. Evaluate the named task for the stated user profile and context. Use the task dossier as a map, not as proof. Separate necessary task complexity from avoidable interface burden. Do not implement, invent behavior, read other assessors' findings, or claim measurement from heuristic evidence. Return exactly the assessor contract, including verdict, confidence, claim_basis, coverage, findings, keep, unknowns, and cross_refs. Every finding must cite evidence, explain the user effect, propose a bounded correction, and define an observable verification.
```

Allow an empty finding list. Do not create debt to complete the form. If another dimension owns the root cause, return a concise `cross_refs` item and keep only the assigned dimension's distinct effect.

## Assessor 01 - Memory

**Mission:** determine where the interface forces the target user to remember information that could remain visible, recognizable, or recoverable.

Walk the full task, including return, interruption, and failure. Examine identifiers, selections, earlier values, instructions, cross-screen dependencies, comparisons, resumption, and repeated entry. Look for substitution, omission, reconstruction, and compensating note taking.

Do not penalize deliberate recall when recall is the learning objective. Do not infer a hard item limit from working-memory research.

## Assessor 02 - Search

**Mission:** determine how much avoidable scanning and navigation are required to locate the next relevant object, fact, or action.

Examine information scent, grouping, hierarchy, competing emphasis, target visibility, ordering, filters, stable placement, responsive adaptation, keyboard/focus routes, and realistic data density. Distinguish visual clutter from useful expert density.

Do not recommend hiding information solely to reduce visible count. Confirm that the proposed structure improves target acquisition for the stated task.

## Assessor 03 - Integration

**Mission:** find related information that users must mentally join because the interface separates it across space, time, representation, or terminology.

Examine detached validation, legends, cross-view comparison, asynchronous results, identifiers, units, before/after states, and explanations separated from the affected object. Track view switching, transcription, and cross-referencing.

Do not combine sources that serve independent decisions or are already understandable alone. Avoid replacing split attention with redundant noise.

## Assessor 04 - Decision

**Mission:** determine where avoidable ambiguity or comparison work makes action selection harder than the domain requires.

Examine competing primary actions, semantic similarity, hidden consequences, absent comparison attributes, defaults, recommendations, option order, category quality, and reversible versus high-consequence choices. Look for hesitation, toggling, and wrong-action patterns.

Do not apply a raw choice-count rule or remove legitimate control. Preserve deliberation that improves a consequential decision.

## Assessor 05 - Uncertainty

**Mission:** determine where users must infer system state, causality, progress, outcome, or the next step.

Examine input acknowledgment, pending work, save and sync state, stale data, partial success, disabled controls, permissions, asynchronous boundaries, destructive consequences, completion signals, and status location. Look for duplicate actions, defensive refresh, and false confidence.

Do not treat all waiting as failure. Judge whether the interface provides accurate information and useful control for the actual latency.

## Assessor 06 - Recovery

**Mission:** determine how much avoidable diagnosis, reconstruction, and repeated work follow an error or interruption.

Examine prevention, constraints, validation timing, error proximity, preserved input, undo, drafts, retry, conflicts, destructive actions, support dependence, and re-entry. Cover an applicable failure or mark it unverified.

Do not demand frictionless high-risk actions. Protective friction should focus attention on the real consequence and offer a safe recovery path when possible.
