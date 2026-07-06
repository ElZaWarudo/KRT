---
name: krt-frontend-ux-guardian
description: Guard frontend-building agents toward functional, accessible, responsive, task-centered UX/UI and browser-verified implementation quality. Use when building, changing, or reviewing frontend apps, dashboards, tools, forms, data tables, editors, landing pages, or interactive product surfaces where user workflows must actually work.
---

# krt-frontend-ux-guardian

Use this skill when frontend work must protect product functionality: users should understand the task, complete it, recover from mistakes, and trust the system state.

The mission is not aesthetics-first polish. The mission is functional UX: task flow, interaction model, data handling, state coverage, accessibility, responsiveness, and browser verification. Visual decisions matter only when they improve comprehension, speed, confidence, or error recovery.

## Operating Workflow

1. Inspect the existing frontend before changing it: framework, routes, data flow, nearby screens, components, forms, tables, navigation, permissions, tokens, theme, and responsive patterns.
2. Define the user's job: goal, entry point, primary action, secondary actions, required context, risky decisions, completion signal, and likely failure modes.
3. Map the functional path: happy path, empty state, loading state, validation failure, backend/API failure, partial data, permission denied, destructive action, conflict, success, and return path.
4. Reuse existing product mechanics first: components, controls, tables, filters, forms, icons, layout utilities, keyboard patterns, accessibility helpers, and local state conventions.
5. Design from behavior outward: controls near the thing they affect, persistent context where decisions require it, explicit status, recoverable errors, and clear next actions.
6. Implement with semantic HTML, keyboard support, visible focus, responsive constraints, stable dimensions, accessible names, and data-heavy cases in mind.
7. Verify the workflow in a browser when visual behavior, routing, or interaction changed. Check desktop, mobile, focus, overflow, supported themes, and at least one non-happy state when feasible.
8. Report what changed and what was verified. State any functional, accessibility, responsive, or browser checks that could not be run.

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

## Companion Skills

- Use `krt-interface-warden` only when the product also needs stronger visual surface direction or must avoid generic AI/SaaS aesthetics.
- Use `krt-interface-inquisitor` when the user asks for critique, review, or adversarial UI feedback.

## Delivery Requirements

When implementation is requested, deliver code changes plus a short closeout covering:

1. Primary workflow supported.
2. Important states handled.
3. Accessibility and responsive behavior considered.
4. Browser or visual checks run.
5. Remaining checks not run, if any.
