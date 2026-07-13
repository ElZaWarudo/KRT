---
name: krt-interface-inquisitor
description: Independently critique frontend interfaces with adversarial Editorial Product UI rigor, identifying generic AI/SaaS patterns, unjustified cards or tables, weak typographic hierarchy, excessive surfaces, layout-archetype drift, and concrete implementation changes. Use for visual audits, review requests, or critique-and-fix workflows; consume krt-frontend-ux-guardian constraints when supplied and produce a brief that krt-interface-warden or any implementation workflow can use, without requiring either companion.
---

# krt-interface-inquisitor

Use this skill to run an adversarial visual critique of a frontend interface and produce actionable input for a separate implementation pass.

This skill does not beautify, redesign, or write code by default. It interrogates the interface as a complete composition, identifies what is visually weak, generic, or structurally unjustified, and returns a prioritized change brief that another agent can implement.

## Collaboration Role

Inquisitor operates independently and owns evidence-based visual diagnosis and prioritization. It must return a useful critique without requiring Guardian or Warden.

When the companion skills are also active:

- Guardian supplies the functional UX contract and owns its verification gate.
- Inquisitor turns evidence into a prioritized critique brief.
- Warden owns visual direction and implementation decisions.

When a Guardian UX contract exists, consume it before critiquing. Treat it as a constraint, not another design opinion. If it is absent, infer only the minimum user task and functional constraints needed for the review and label them as assumptions.

For critique-and-fix work, complete the critique brief before implementation. Apply Warden only when it is selected or otherwise in scope; any capable implementation workflow may consume the brief. Inquisitor must not quietly become the implementer. After implementation, re-review once only when requested or when visual identity is a material acceptance criterion.

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
- Guardian UX contract or explicit product constraints, when supplied.

If no visual artifact is available, critique the described design or code and clearly label assumptions.

When practical for implemented frontends, inspect the actual page in a browser before final critique. For static design text, use the provided description as the source of truth.

## Adversarial Review Pass

Interrogate the interface in this order:

1. **Constraint Fit**: Does the interface preserve the primary task, completion signal, persistent context, required states, and product mechanics?
2. **Task and Dominance**: Is one task, action, metric, conclusion, or work zone visibly dominant, or does every module have equal weight?
3. **Identity**: Does it look specific to this product/workflow, or could it belong to any SaaS startup?
4. **Surface Metaphor**: Is the screen a dossier, map, logbook, control table, workshop, archive, report, or an undefined pile of modules?
5. **Layout Archetype**: Does it clearly use an editorial page, master-detail, canvas with inspector, staged flow, document with rail, operational list, narrative dashboard, split view, or timeline/feed? Does that archetype fit the task?
6. **Hierarchy Ladder**: Is hierarchy created first through typography, space, alignment, and proportion, or primarily through borders, fills, and shadows?
7. **Surface Budget**: Is the base surface predominant? Is there more than one dominant contained surface, more than two elevation levels, nested cards, or containers combining border, fill, and shadow?
8. **Cards and Tables**: Does every card represent an independent object? Does every table support column comparison, dense sorting/filtering, pattern recognition, or bulk action?
9. **Layout Integrity**: Are bands, rails, margins, rows, tables, layers, and separators part of one composition, or are modules independently boxed and styled?
10. **Generic AI Patterns**: Identify KPI card grids, bento layouts, decorative gradients, glassmorphism, soft-shadow boxes, rounded-square filler icons, hero boilerplate, repeated three-column sections, and oversized radii.
11. **Information Density**: Is the screen too sparse, too crowded, or dense in the wrong places?
12. **Typography**: Does type create identity and hierarchy, or does the screen rely on generic semibold headings and container chrome?
13. **Color and Icon Semantics**: Do color and icons encode action/state/risk/navigation and recognition, or merely decorate?
14. **State and Interaction Language**: Do states and controls feel integrated with the work surface and its operations?
15. **Responsive Transformation**: Does the narrow layout preserve and reprioritize the task, or merely stack containers and convert rows into cards?
16. **Accessibility Risk**: Flag contrast, focus, keyboard, semantics, table readability, responsive overflow, touch targets, and color-only signaling issues.

## Severity Model

Use these levels:

- **P0 Operability blocker**: The interface cannot be understood, operated, or trusted visually. Mark it as blocking; include it in the Guardian final gate only when Guardian is active.
- **P1 Identity failure**: The interface strongly reads as generic AI/SaaS, or the layout metaphor is incoherent.
- **P2 Structural weakness**: Hierarchy, density, states, or layout systems are weak enough to harm use.
- **P3 Polish debt**: Specific improvements would sharpen craft without changing the structure.

Prefer fewer, sharper findings over broad aesthetic commentary.

## Output Format

Return the critique in this structure:

```text
Verdict: <one sentence>
Surface diagnosis: <chosen or missing surface metaphor>
Layout archetype: <chosen, missing, or mismatched archetype>
Generic-pattern risk: <low|medium|high>
UX constraints: <received|inferred>; <constraints or assumptions that matter>

Composition audit:
- Dominant element: <what leads, or missing>
- Surface budget: <pass|risk>; <specific count/stacking observation>
- Cards: <justified|mixed|unjustified>; <reason>
- Table: <necessary|unnecessary|not present>; <comparison/bulk-action reason>
- Removable container: <specific candidate or none>
- Mobile transformation: <preserves task|mechanically stacks|not observed>

Findings:
- [P1] <short title>
  Evidence: <specific observation>
  Why it matters: <workflow/user impact>
  Change input: <concrete instruction another agent can implement>
  Constraint impact: <preserves|supports|risks> <named UX constraint>

Implementation brief:
1. <highest-leverage change>
2. <next change>
3. <next change>

Do not change:
- <parts that are working and should be preserved>

Verification:
- <how the next agent should verify the fix visually/accessibly>

Handoff: <implementation-ready|needs product clarification>; <scope and permitted visual freedom>
```

When reviewing code, include file and line references where available. When reviewing screenshots, reference visible regions such as top band, left rail, main table, inspector panel, empty state, or mobile header.

## Change Input Rules

Every critical finding must include a concrete implementation input.

Change inputs must preserve supplied or inferred UX constraints. If a visually stronger option would alter the primary task, required state, accessibility behavior, or established product mechanic, describe the tradeoff instead of presenting it as an unconditional instruction.

Good:

- "Replace the four metric cards with a single status band above the table; keep totals in mono labels aligned to the right edge."
- "Move owner, date, and review state into a right metadata rail so the main column can focus on the case narrative."
- "Convert the project cards into rich rows grouped by risk level with a persistent action column."
- "Keep the base page open and replace the nested settings cards with titled form sections separated by 32px rhythm and fine rules."
- "Retain a table for the invoice register because users compare amount, due date, owner, and state and perform bulk reconciliation."

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
- Tables used where no column comparison or bulk action exists.
- Badges that do not look connected to the system.
- Empty white space with no structural role.
- Layouts where all modules have equal importance.
- Nested cards, excessive elevation, and containers combining full border, contrast fill, and shadow.
- Mobile layouts that turn every desktop row into a card.

Read `references/critique-rubric.md` for every material visual audit. It contains the Editorial Product UI composition test, surface/card/table decisions, archetype checks, responsive transformations, and implementation-input patterns.

## Collaboration Boundary

This skill produces a critique artifact. It should not implement the changes. When the user asks for fixes in the same turn, finish the artifact and pass it to `krt-interface-warden` when that skill is active, or to the current implementation workflow otherwise.

Keep the output implementation-ready: clear priorities, concrete changes, preserved elements, affected constraints, permitted visual freedom, and verification steps. Recommend a structural replacement, not merely the removal of a weak pattern. If an implementer defers a finding with a concrete reason, carry it as a recorded decision rather than reopening it without new evidence.
