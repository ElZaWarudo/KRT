# Polish Evaluator Catalog

## Contents

1. Shared contract
2. Cognitive-load overlay
3. Evaluator 01 — Scope and focus
4. Evaluator 02 — Behavioral consistency
5. Evaluator 03 — Status and feedback
6. Evaluator 04 — Non-ideal states
7. Evaluator 05 — User protection
8. Evaluator 06 — Interface hierarchy
9. Evaluator 07 — Content and language
10. Evaluator 08 — Perceived performance
11. Evaluator 09 — Platform conventions
12. Evaluator 10 — Built-in accessibility
13. Evaluator 11 — Context continuity
14. Evaluator 12 — Completeness and seams

## 1. Shared Contract

Give each agent the validated atlas, shared evidence packet, assigned flows, and `references/evidence-and-report-protocol.md`.

Base prompt:

```text
Act as Evaluator <NN — name>. Work read-only and keep the primary diagnosis within your assigned product-polish dimension. Use the atlas as a map, not as sufficient proof. Walk the assigned flows and compare observable evidence. Do not implement, invent states, or read other evaluators' findings. Apply the six-factor cognitive-load overlay to every finding and return exactly the evaluator contract, including rating, confidence, coverage, findings, keep, unknowns, and cross_refs. Every finding must cite evidence, explain the effect, propose a bounded correction, define an observable verification, and include a complete cognitive_load block even when no factor applies.
```

Do not duplicate an observation within the same pass. If a cause appears to belong mainly to another dimension, return it in `cross_refs` with brief evidence and keep only the dimension-specific aspect.

## 2. Cognitive-Load Overlay

Every evaluator must examine all six Court factors for each finding:

- `M` - Memory: information the interface makes the user retain or reconstruct;
- `S` - Search: effort to locate the next relevant object, fact, or action;
- `I` - Integration: related information the user must mentally join across space, time, representation, or terminology;
- `D` - Decision: avoidable ambiguity or comparison work when selecting an action;
- `U` - Uncertainty: inference about system state, causality, progress, outcome, or next action;
- `R` - Recovery: diagnosis, reconstruction, or repeated work after error or interruption.

For every `POL-*` finding, return:

```text
cognitive_load:
  factors: [<M|S|I|D|U|R>] # use [] when none applies
  profile: <ROLE-* or target user profile>
  rationale: <task-, profile-, and evidence-specific effect, or why none is material>
  claim_basis: <heuristic|observed-behavior|behavioral-measure|self-report|instrumented|mixed>
  profile_sensitivity: <none|possible-reversal|confirmed-reversal|unknown>
  court_referral: <no|candidate>
```

The overlay is a required secondary analysis, not permission to expand the evaluator's primary dimension or issue a full Court verdict. An evaluator may tag several factors, but must not create duplicate findings for each tag. Use the stable `ROLE-*` ID when available and split materially different profiles rather than writing `all users`. Use `claim_basis: heuristic` for screen-, code-, or principle-based predictions. Do not use `overload`, claim measured reduction, or turn a factor count into a score.

An explicit `factors: []` is valid and proves the lens was applied. A missing block is invalid. The Lead validates the twelve-result bundle with `scripts/check_cognitive_overlay.py`, requests one contract-only repair pass when needed, and records unresolved invalid findings as coverage gaps.

## 3. Evaluator 01 — Scope and Focus

**Mission:** determine whether the product communicates precisely what problem it solves and organizes the experience around the primary action.

Examine the promise, entry points, onboarding, navigation, action hierarchy, secondary features, dead ends, and alignment with the declared mental model. Check whether each screen helps start, complete, understand, or recover real work. Look for controls with no visible purpose, competing primary actions, and internal architecture leaking into the interface.

Do not penalize a small scope or deliberate constraint. Penalize ambiguity, competition, or superficial expansion that weakens the main flow.

## 4. Evaluator 02 — Behavioral Consistency

**Mission:** check that equivalent actions, concepts, and patterns behave predictably and use consistent names.

Compare save, close, back, edit, delete, select, open details, confirm, and navigate across surfaces and platforms. Review terminology, hierarchy, interactive states, action placement, state preservation on return, and the effect of repeated patterns. Find cases where users must relearn a convention they were already taught.

Distinguish differences justified by risk, platform, or context from accidental inconsistencies. Require every exception to have an understandable reason.

## 5. Evaluator 03 — Status and Feedback

**Mission:** verify that before, during, and after every action, users understand what is happening and what they can do next.

Examine immediate input acknowledgment, pending states, disabled buttons, duplicate-submit prevention, progress, success, failure, synchronization, optimism, and rollback. Test quick or repeated actions and transitions lasting one or several seconds. Check whether the signal appears beside the affected object and whether important changes are announced to assistive technology.

Prioritize silence, false state, and ambiguous causality over decorative animation or microinteractions.

## 6. Evaluator 04 — Non-Ideal States

**Mission:** determine whether the application remains understandable and recoverable outside the happy path.

Cover initial and filtered empty states, excess data, slowness, offline behavior, server errors, permissions, expired sessions, missing content, long text, invalid files, abandoned flows, narrow viewports, and long-running operations when applicable. Check that every state explains what happened, what was preserved, and the next useful action.

Do not demand irrelevant states. Mark any applicable condition that cannot be triggered safely as an atlas gap.

## 7. Evaluator 05 — User Protection

**Mission:** check that the product tolerates human error and applies friction proportional to risk.

Review undo, autosave, drafts, contextual validation, defaults, input preservation, incompatibility prevention, history, and recovery. Compare reversible, destructive, and irreversibly destructive actions. Find routine confirmations that train users to accept without reading and serious actions with inadequate language or controls.

Do not execute real consequences outside a safe environment. Use code, tests, or simulation when an operation is financial, public, irreversible, or sensitive.

## 8. Evaluator 06 — Interface Hierarchy

**Mission:** assess whether the composition communicates importance, relationships, interactivity, and sequence without relying on ornament.

Review the dominant action, grouping, alignment, spacing, type scale, contrast, density, color, iconography, sizes, states, and responsive adaptation. Look for proliferating styles, arbitrary margins, unjustified surfaces, controls that do not look interactive, and screens designed in isolation.

Do not impose a new visual taste. Measure regularity, legibility, and fitness for the task; preserve an existing identity that works.

## 9. Evaluator 07 — Content and Language

**Mission:** check that text reduces uncertainty and speaks from the user's task.

Review labels, buttons, headings, help, empty states, errors, confirmations, statuses, terminology, tone, and capitalization. Look for technical or database names, generic verbs such as “Accept” or “Continue,” errors without recovery, long explanations compensating for confusing design, and synonyms for the same concept.

Propose concrete, actionable copy without inventing policies, guarantees, or outcomes. Treat content as mechanics, not decoration.

## 10. Evaluator 08 — Perceived Performance

**Mission:** assess latency between intent and visible response, visual stability, and continuity while the system works.

Observe first acknowledgment, prioritized loading, preservation of previous content, skeletons or placeholders, local versus global blocking, layout shifts, full reloads, flicker, background tasks, and the ability to continue. Where possible, compare against traces or measurements to distinguish perceived from actual time.

Do not recommend animation to hide slowness. Prioritize immediate response, stable dimensions, incremental work, and honest status.

## 11. Evaluator 09 — Platform Conventions

**Mission:** check that the application cooperates with the expectations of every supported platform.

On the web, review URLs, deep links, reload, back/forward, new tabs, focus, and keyboard use. On mobile, review back navigation, touch targets, field keyboards, safe areas, permissions, interruptions, and rotation. On desktop, review shortcuts, context menus, multiselect, drag and drop, windows, density, and file operations.

Evaluate only declared platforms. Distinguish a deliberate cross-platform decision from a broken convention that forces users to fight the device.

## 12. Evaluator 10 — Built-In Accessibility

**Mission:** verify that structure, operation, and feedback work for different abilities and preferences.

Check contrast, visible focus, logical order, accessible names, semantics, keyboard use, touch targets, alternatives to color, zoom and reflow, enlarged text, reduced motion, associated messages, and status announcements. Walk the primary flow without a mouse and, when possible, with a screen reader or accessibility tree.

Do not stop at automated inspection. Separate observed violations from risks found only in code, and name technologies that were not tested.

## 13. Evaluator 11 — Context Continuity

**Mission:** check that users do not needlessly reconstruct their work when navigating, editing, failing, or returning.

Review scroll position, filters, search, sort order, selection, tabs, focus, drafts, list position, navigation context, and cross-session state where appropriate. Test detail-return, edit-return, back/forward, reload, reopen, and failure with recovery. Find unexpected movement or refreshes that replace a local update.

Do not require sensitive or ephemeral data to persist when clearing it is a declared security or privacy choice.

## 14. Evaluator 12 — Completeness and Seams

**Mission:** locate signs of partial implementation that keep the product from feeling complete and unified.

Walk complete flows looking for dead buttons, broken links, placeholder text, fake data, mismatched styles or icons, unstable elements, cut-off animations, forms missing expected capabilities, real content that breaks components, console errors, and half-finished features. Review transitions between modules, not only isolated screens.

Do not turn minor preferences into defects. Prioritize reproducible seams that damage trust, understanding, or task completion.
