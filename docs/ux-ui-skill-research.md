# UX/UI Frontend Skill Research

Date: 2026-07-06

## Goal

Create a KRT skill that gives frontend-building agents practical UX/UI guidance centered on functionality. The skill should help agents make strong product-interface decisions, preserve task flow, handle states and errors, produce accessible and responsive code, and verify the result in a browser. Visual polish is secondary to comprehension, completion, recovery, and trust.

## Internal Reference Basis

External links should not be part of the operational skill. The useful material is the synthesized, task-ready guidance that agents can apply without browsing or re-researching.

Use these internal sources as the working basis:

- `skills/krt-interface-warden/`: visual direction, working-surface metaphors, and avoidance of generic AI/SaaS UI.
- `skills/krt-interface-inquisitor/`: critique rubric for identity, hierarchy, density, state language, accessibility, and implementation input.
- This research document: synthesized frontend UX/UI rules to convert into compact `SKILL.md` workflow and focused `references/` files.

## Research Findings

### 1. The Skill Should Be a Decision Framework, Not a UI Textbook

The skill should keep `SKILL.md` short and procedural. Detailed guidance belongs in `references/`, especially accessibility checks, visual grammar, and verification rubrics.

The core flow should be:

1. Identify the product surface, user role, primary task, and risk.
2. Reuse the repo's existing design system and component conventions.
3. Design the workflow states before styling the happy path.
4. Implement with semantic, accessible, responsive code.
5. Verify in browser across desktop and mobile.

### 2. Accessibility Must Be a Baseline Constraint

Use a WCAG-informed AA accessibility baseline for product UI unless the project states another standard. Important agent-facing constraints:

- Keyboard operation for every interactive element.
- Visible, persistent, predictable focus order.
- Logical DOM order aligned with visual reading order.
- Semantic HTML before ARIA; APG patterns when custom widgets are necessary.
- Color contrast for text, icons, borders, and controls.
- Do not rely on color alone for meaning.
- Support 200% text zoom and reflow down to 320px without content loss.
- Use accessible names that match visible labels.
- Provide non-drag alternatives for drag interactions.
- Avoid authentication or verification patterns that depend only on cognitive puzzles.
- Target size: controls should have at least 24x24 CSS px hit areas, with 44x44 or 48x48 preferred for touch-heavy product UI.

### 3. Modern UI Means Systematic, Not Trendy

Modern frontend output should be driven by system rules:

- Design tokens for color, spacing, type, radius, elevation, motion, and themes.
- Semantic tokens for state and intent instead of hardcoded hex values.
- Light, dark, high-contrast, and reduced-motion behavior where the project supports it.
- A type scale with clear semantic roles and readable line heights.
- A spacing ramp, often 4px or 8px based, applied flexibly instead of mechanically.
- Responsive layout decisions based on content, not only device presets.

Avoid trend-chasing as a skill rule. Glass effects, gradients, oversized cards, bento grids, AI-style orbs, and decorative icons are acceptable only when they serve the product surface and do not harm clarity, performance, or accessibility.

### 4. The Existing KRT Interface Thesis Is Strong and Should Be Reused

`krt-interface-warden` already has a useful principle: design working surfaces, not collections of cards. The new skill should incorporate that as a default visual strategy while broadening the scope to implementation quality and verification.

Useful reusable concepts:

- Surface metaphors: dossier, map, logbook, control table, workshop, archive, report.
- Prefer bands, rails, annotated margins, tables, layers, legends, and status marks over generic cards.
- Make empty, loading, error, blocked, success, conflict, and partial-data states part of the design identity.
- Keep visual identity visible without relying on a logo.

The new skill should not replace `krt-interface-warden`; it should be the general frontend UX/UI baseline. `krt-interface-warden` remains the deeper visual-direction skill, and `krt-interface-inquisitor` remains the critique/audit skill.

### 5. Usability Heuristics Should Become Concrete Agent Checks

General usability heuristics translate well into frontend agent instructions:

- System status: loading, saving, syncing, offline, success, and failure states must be visible.
- Match user language: labels, actions, and concepts should follow the domain, not database names.
- Control and freedom: support cancel, undo, back, edit, and safe exits for risky flows.
- Consistency: follow platform, product, and repo conventions before inventing new patterns.
- Error prevention: constrain invalid input, provide good defaults, and confirm destructive actions.
- Recognition over recall: keep relevant context, choices, and field labels visible.
- Efficiency: support shortcuts, bulk actions, filters, saved views, and repeat workflows when relevant.
- Minimalism: remove decorative or redundant UI that competes with the primary task.
- Error recovery: place messages near the source, explain the issue plainly, and give a next action.
- Help: provide contextual assistance when needed, not tutorial walls.

Additional usability research reinforced that the skill should treat usability as workflow reliability:

- State must be visible near the action or object affected.
- The interface should speak in the user's domain language, not implementation terms.
- Users need exits and recovery paths: cancel, undo, retry, edit, save draft, or safe back navigation.
- Consistency should cover words, controls, state meanings, keyboard behavior, and platform conventions.
- The best error handling prevents likely mistakes before they happen.
- Interfaces should reduce memory load by keeping labels, current step, selected filters, and required context visible.
- Repeated work needs efficiency features such as bulk actions, saved views, shortcuts, defaults, and duplication.
- Minimalism is functional: remove anything that does not help users decide, act, inspect, compare, recover, or navigate.
- Forms should ask only necessary questions, branch early when that saves time, and preserve answers through errors.

### 6. Forms Need Special Treatment

Forms are a common failure mode for generated frontend work. The skill should require:

- Persistent visible labels, not placeholder-only labels.
- Clear required/optional semantics.
- Field-level help before validation where it prevents errors.
- Validation timing that avoids premature blame.
- Error summaries for long forms plus inline errors near each field.
- Preservation of entered data after errors.
- Autocomplete and input modes for known data types.
- Avoid redundant entry when previous data is available.
- Plain-language error copy with a concrete recovery path.

### 7. Responsive Design Is a Content Strategy

Responsive guidance should go beyond breakpoints:

- Define what stays visible, compresses, moves to a rail/drawer, or becomes secondary.
- Use reflow, resize, reposition, show/hide, and re-architect techniques intentionally.
- Maintain task continuity across mobile, tablet, and desktop.
- Avoid horizontal scroll except for intentionally scrollable data tables with clear affordances.
- Prevent text clipping and overlapping at common and narrow viewport widths.
- Use stable dimensions for boards, grids, counters, controls, and other fixed-format UI.

### 8. Performance Is Part of UX

The skill should make agents verify perceived quality:

- Largest visible content should render quickly enough for the interface to feel ready.
- User interactions should respond without noticeable delay.
- Layout should remain stable during loading and updates.
- Reserve image/media dimensions to prevent layout shift.
- Avoid unnecessary animation, oversized assets, and blocking scripts.
- Prefer skeletons or meaningful loading states over blank screens.
- Keep interactions responsive under realistic content volume.

### 9. AI/Agent-Specific Guidance Matters

Because this skill is for coding agents, it needs explicit constraints that human design docs often omit:

- Inspect existing UI before creating new patterns.
- Use existing components, tokens, and icons before inventing replacements.
- Do not create a landing page when the user asked for an app, tool, dashboard, or game.
- Do not add explanatory in-app text that describes how the UI was designed.
- Verify with screenshots, not only code review.
- Check both data-rich and empty states.
- Check light/dark modes when supported.
- Detect text overflow, occlusion, broken focus, missing labels, and hidden content.
- Report what was verified and what could not be verified.

## Proposed Skill Shape

Recommended folder:

```text
skills/krt-frontend-ux-guardian/
  SKILL.md
  agents/openai.yaml
  references/
    functional-ux-guidelines.md
    usability-guidelines.md
    accessibility-verification.md
    functional-quality-rubric.md
    frontend-verification.md
```

Recommended metadata:

```yaml
name: krt-frontend-ux-guardian
description: Guard frontend agents toward functional, accessible, responsive, task-centered UX/UI and browser-verified implementation quality.
```

Recommended `agents/openai.yaml`:

```yaml
interface:
  display_name: "krt-frontend-ux-guardian"
  short_description: "Guard functional frontend UX quality"
  default_prompt: "Use krt-frontend-ux-guardian to build task-centered, accessible, responsive frontend workflows and verify the result."
```

## Proposed SKILL.md Workflow

1. Read the existing frontend surface: framework, routes, components, tokens, icons, theme, responsive patterns, and adjacent screens.
2. Classify the surface: tool, dashboard, content page, form flow, data table, editor, game, landing page, or commerce/product page.
3. Define user task and hierarchy: primary action, secondary actions, persistent context, risky actions, and state language.
4. Apply non-negotiables: WCAG-informed accessibility, semantic structure, keyboard/focus behavior, responsive layout, no text overlap, no decorative clutter.
5. Design with the repo's system: components first, tokens first, domain-specific visual language, states before polish.
6. Implement the smallest coherent UI that satisfies the workflow.
7. Verify with browser screenshots and, where available, automated accessibility/performance checks.
8. Final response: summarize what changed and what was verified.

## What Not To Include

- Long explanations of design theory.
- External-source bibliographies or link lists.
- Fixed universal palettes or one-size-fits-all typography.
- Large copied checklists from standards or design systems.
- Trend catalogues.
- Generic "make it clean and modern" language without operational tests.
- A script unless it provides deterministic verification that agents can actually run in this repo.

## Open Decisions

1. Create a new broad skill, `krt-frontend-ux-guardian`, or extend `krt-interface-warden`.
2. Decide whether the skill should auto-invoke `krt-interface-warden` for visual direction and `krt-interface-inquisitor` for review, or simply reference them as companions.
3. Decide whether to include a lightweight browser-verification script later, or keep verification as instructions only.
