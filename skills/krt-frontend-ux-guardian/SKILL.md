---
name: krt-frontend-ux-guardian
description: Guard frontend work toward functional, accessible, responsive, task-centered UX/UI and browser-verified quality. Use independently when building, changing, or functionally reviewing apps, dashboards, tools, forms, data tables, editors, landing pages, or interactive surfaces; optionally coordinate with krt-interface-inquisitor for adversarial visual critique or krt-interface-warden for distinctive visual direction.
---

# krt-frontend-ux-guardian

Use this skill when frontend work must protect product functionality: users should understand the task, complete it, recover from mistakes, and trust the system state.

The mission is not aesthetics-first polish. The mission is functional UX: task flow, interaction model, data handling, state coverage, accessibility, responsiveness, and browser verification. Visual decisions matter only when they improve comprehension, speed, confidence, or error recovery.

Guardian owns the functional contract and final UX gate for work in its scope. It can operate alone. When visual companions are also active, it does not replace their roles: Inquisitor diagnoses and prioritizes visual problems; Warden chooses and implements the visual system.

## Operating Workflow

1. Inspect the existing frontend before changing it: framework, routes, data flow, nearby screens, components, forms, tables, navigation, permissions, tokens, theme, and responsive patterns.
2. Define the user's job: goal, entry point, primary action, secondary actions, required context, risky decisions, completion signal, and likely failure modes.
3. Map the functional path: happy path, empty state, loading state, validation failure, backend/API failure, partial data, permission denied, destructive action, conflict, success, and return path.
4. Write a compact UX contract: user/job, primary action and completion signal, persistent context, required states and recovery, existing mechanics to preserve, accessibility/responsive constraints, and acceptance checks.
5. Reuse existing product mechanics first: components, controls, tables, filters, forms, icons, layout utilities, keyboard patterns, accessibility helpers, and local state conventions.
6. Route visual work through the collaboration protocol below when critique or stronger visual direction is in scope.
7. Design from behavior outward: controls near the thing they affect, persistent context where decisions require it, explicit status, recoverable errors, and clear next actions.
8. Implement with semantic HTML, keyboard support, visible focus, responsive constraints, stable dimensions, accessible names, and data-heavy cases in mind.
9. Verify the workflow in a browser when visual behavior, routing, or interaction changed. Check desktop, mobile, focus, overflow, supported themes, and at least one non-happy state when feasible.
10. Report what changed and what was verified. State any functional, accessibility, responsive, or browser checks that could not be run.

## Collaboration Protocol

This protocol is optional. Do not invoke, require, or block on a companion merely because it is referenced here. Every skill must remain useful when installed or selected alone.

Choose the smallest route that fits the request:

- **Functional build or fix**: Guardian alone.
- **Distinctive visual design or implementation with Warden active**: Guardian writes the UX contract; Warden designs or implements within it; Guardian runs the final gate.
- **Visual critique only**: Inquisitor reviews the artifact. Include the UX contract when functional constraints matter.
- **Critique and fix with all three active**: Guardian contract -> Inquisitor critique brief -> Warden implementation record -> Guardian final gate.
- **High-stakes visual review**: after the final gate, let Inquisitor re-review the rendered result once against the original brief. Do not create an unbounded critique loop.

Use the artifacts as handoffs:

1. **UX contract — Guardian**: the fields defined in workflow step 4.
2. **Critique brief — Inquisitor**: composition audit, evidence, prioritized findings, concrete structural replacements, preserved elements, and verification targets.
3. **Implementation record — Warden**: composition brief, selected surface metaphor and layout archetype, card/table ledger, accepted or deferred findings with reasons, preserved constraints, and verification evidence.
4. **Final gate — Guardian**: workflow completion, states, accessibility, responsiveness, and browser evidence.

If a companion is inactive or unavailable, continue without it. Produce Guardian's normal functional result and include only the handoff fields useful to the user's requested workflow.

When multiple roles are active, resolve conflicts in this order: explicit user and product requirements; Guardian functional and accessibility constraints; established product mechanics; Warden visual direction; Inquisitor polish recommendations. A lower-priority concern may refine a higher-priority one but must not silently break it.

## Reference Routing

- Read `references/functional-ux-guidelines.md` for any frontend build, redesign, or substantial UI change.
- Read `references/usability-guidelines.md` when shaping workflows, navigation, forms, error recovery, repeated tasks, or learnability.
- Read `references/accessibility-verification.md` for forms, tables, navigation, custom widgets, modals, menus, keyboard interactions, or status/error messaging.
- Read `references/functional-quality-rubric.md` when deciding whether the interface actually supports the user's workflow.
- Read `references/frontend-verification.md` before final delivery for browser QA, screenshots, responsive checks, theme checks, performance feel, and failure-state review.

## Non-Negotiables

- Do not create a decorative or marketing surface when the user asked for an app, tool, dashboard, editor, game, or operational workflow.
- Do not add in-app explanatory text that compensates for unclear interaction design.
- Do not invent a new component or visual system when existing product mechanics solve the task.
- Do not hide system state: loading, saving, saved, failed, offline, queued, empty, blocked, and partial-data states must be understandable where relevant.
- Do not rely on color alone for meaning.
- Do not ship hidden focus, placeholder-only labels, clipped text, overlapping content, unreachable controls, dead-end errors, or mouse-only interaction.
- Do not finish without checking the primary workflow and at least one narrow viewport when behavior or layout changed.

## Delivery Requirements

When implementation is requested, deliver code changes plus a short closeout covering:

1. Primary workflow supported.
2. Important states handled.
3. Accessibility and responsive behavior considered.
4. Browser or visual checks run.
5. Remaining checks not run, if any.
