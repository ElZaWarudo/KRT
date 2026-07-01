---
name: krt-interface-inquisitor
description: Critique frontend interfaces with adversarial visual rigor, identifying generic AI/SaaS patterns, weak hierarchy, layout drift, and concrete changes another agent can implement.
---

# krt-interface-inquisitor

Use this skill to run an adversarial visual critique of a frontend interface and produce actionable input for a separate implementation pass.

This skill does not beautify, redesign, or write code by default. It interrogates the interface, identifies what is visually weak or generic, and returns a prioritized change brief that another agent can use to improve the UI.

## Relationship to krt-interface-warden

- `krt-interface-warden` designs or implements distinctive working-surface interfaces.
- `krt-interface-inquisitor` critiques an existing or proposed interface from an antagonistic visual-review stance.

Use both when possible: first let the Inquisitor produce a critical brief, then let the Warden implement or redesign from that brief.

## Trigger Conditions

Apply this skill when the user asks to:

- Critique, review, audit, or judge a frontend visually.
- Make a UI less generic, less AI-looking, less SaaS-template-like, or less card-heavy.
- Produce feedback for another agent or implementation pass.
- Inspect screenshots, browser-rendered pages, mockups, HTML/CSS, React/Vue/Svelte components, dashboards, tools, reports, or design drafts.
- Find why an interface feels bland, unclear, over-decorated, incoherent, or unprofessional.

## Evidence First

Base critique on concrete evidence:

- Screenshot observations.
- DOM/component structure.
- CSS/layout choices.
- Text hierarchy and density.
- State design.
- Responsive behavior.
- Interaction affordances.
- Accessibility signals.

If no visual artifact is available, critique the described design or code and clearly label assumptions.

When practical for implemented frontends, inspect the actual page in a browser before final critique. For static design text, use the provided description as the source of truth.

## Adversarial Review Pass

Interrogate the interface in this order:

1. **Identity**: Does it look specific to this product/workflow, or could it belong to any SaaS startup?
2. **Surface Metaphor**: Is the screen a dossier, map, logbook, control table, workshop, archive, report, or an undefined pile of modules?
3. **Hierarchy**: Can the eye identify primary action, persistent context, secondary context, and detail zones immediately?
4. **Layout Integrity**: Are there real bands, rails, margins, tables, layers, or connection systems, or just isolated boxes?
5. **Generic AI Patterns**: Identify cards, bento grids, decorative gradients, glassmorphism, soft-shadow boxes, filler icons, hero boilerplate, and repeated three-column sections.
6. **Information Density**: Is the screen too sparse, too crowded, or dense in the wrong places?
7. **State Language**: Do statuses look like system marks or generic badges?
8. **Typography**: Does type communicate precision and hierarchy, or default landing-page scale?
9. **Color Semantics**: Does color encode action/state/risk/navigation, or merely decorate?
10. **Interaction Readiness**: Do controls feel like tools for inspecting, comparing, marking, filtering, validating, or operating?
11. **Accessibility Risk**: Flag contrast, focus, keyboard, semantics, table readability, responsive overflow, and color-only signaling issues.

## Severity Model

Use these levels:

- **P0 Visual blocker**: The interface cannot be understood, operated, or trusted visually.
- **P1 Identity failure**: The interface strongly reads as generic AI/SaaS, or the layout metaphor is incoherent.
- **P2 Structural weakness**: Hierarchy, density, states, or layout systems are weak enough to harm use.
- **P3 Polish debt**: Specific improvements would sharpen craft without changing the structure.

Prefer fewer, sharper findings over broad aesthetic commentary.

## Output Format

Return the critique in this structure:

```text
Verdict: <one sentence>
Surface diagnosis: <chosen or missing surface metaphor>
Generic-pattern risk: <low|medium|high>

Findings:
- [P1] <short title>
  Evidence: <specific observation>
  Why it matters: <workflow/user impact>
  Change input: <concrete instruction another agent can implement>

Implementation brief:
1. <highest-leverage change>
2. <next change>
3. <next change>

Do not change:
- <parts that are working and should be preserved>

Verification:
- <how the next agent should verify the fix visually/accessibly>
```

When reviewing code, include file and line references where available. When reviewing screenshots, reference visible regions such as top band, left rail, main table, inspector panel, empty state, or mobile header.

## Change Input Rules

Every critical finding must include a concrete implementation input.

Good:

- "Replace the four metric cards with a single status band above the table; keep totals in mono labels aligned to the right edge."
- "Move owner, date, and review state into a right metadata rail so the main column can focus on the case narrative."
- "Convert the project cards into rich rows grouped by risk level with a persistent action column."

Bad:

- "Make it more modern."
- "Improve spacing."
- "Add visual interest."
- "Make it pop."

## Anti-Generic Checks

Flag these aggressively unless they have a clear functional reason:

- Repeated cards with identical radius, shadow, and padding.
- Bento grids that only decorate content.
- Decorative gradients or blobs.
- Glass panels.
- Generic SaaS icons.
- Large centered hero copy in a tool UI.
- Metrics hidden in isolated boxes.
- Badges that do not look connected to the system.
- Empty white space with no structural role.
- Layouts where all modules have equal importance.

Use `references/critique-rubric.md` for detailed review prompts.

## Collaboration Boundary

This skill produces a critique artifact. It should not implement the changes unless the user explicitly asks for fixes in the same turn.

If asked to run as another agent, keep the output implementation-ready: clear priorities, concrete changes, preserved elements, and verification steps.
