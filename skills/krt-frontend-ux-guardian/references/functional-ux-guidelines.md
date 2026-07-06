# Functional UX Guidelines

Use this reference to turn a frontend request into a working user flow.

## Start With The Job

Before layout or styling, identify:

- User role and permission level.
- Entry point into the flow.
- Primary job to complete.
- Information required to decide.
- Action that completes the task.
- Confirmation that the task succeeded.
- Most likely errors, blockers, and recovery paths.

If these are unclear, infer from nearby screens, route names, API shape, fixtures, labels, and existing product patterns. Ask only when a wrong assumption would produce the wrong workflow.

## Product Surfaces By Function

- Tool/app: optimize repeated action, speed, state visibility, and clear navigation.
- Dashboard: support monitoring, comparison, filtering, drill-down, and "what needs attention now".
- Form flow: reduce invalid input, preserve work, show progress, and make recovery obvious.
- Data table/archive: support scan, sort, filter, search, compare, select, batch action, and detail inspection.
- Editor/workshop: keep creation controls close to the artifact and make preview/state changes visible.
- Content/report: guide reading order, evidence, conclusions, recommendations, and next action.
- Landing/product page: make the offer, product, proof, and conversion path visible without blocking inspection.
- Game/interactive scene: make the primary play surface first, responsive, visible, and interactive.

## Interaction Model

- Put controls near the content they affect.
- Keep the primary action clear and stable.
- Make secondary actions available without competing with the primary task.
- Confirm destructive or irreversible actions.
- Provide cancel, undo, back, edit, retry, or safe exit when the flow can fail or be reversed.
- Keep selected items, filters, search terms, current step, and unsaved changes visible when they affect decisions.
- Avoid dead ends: every error or empty state needs a useful next action.

## Data And State

Design these before final polish:

- Empty: what this surface is for and how to start.
- Loading: reserve space and avoid layout shift.
- Partial data: show what loaded and what did not.
- Error: explain what failed and what to do next.
- Validation: keep user input and point to the correction.
- Blocked: explain who or what can unblock.
- Permission denied: explain the missing access and next step.
- Conflict: show competing versions or choices clearly.
- Success: confirm the result without hiding the next workflow.
- High-volume data: keep filters, search, paging/virtualization, and selected context usable.

## Layout For Use

- Start from the primary workflow, then place support information around it.
- Decide what stays persistent, what moves to a rail/drawer, what collapses, and what can disappear on narrow screens.
- Prefer stable structures: bands, rails, rows, tables, panels, inspectors, timelines, split panes, and toolbars.
- Use cards only for independent repeated objects, modals, or genuinely framed tools.
- Avoid nesting cards inside cards.
- Use stable dimensions for boards, tiles, counters, grids, toolbars, and icon buttons so hover, loading, and dynamic labels do not shift the layout.
- Do not scale font size with viewport width.

## Forms

- Use persistent visible labels, not placeholder-only labels.
- Mark required and optional fields consistently.
- Put help text before validation when it prevents errors.
- Validate at the right time; avoid blaming before the user has had a chance to complete the field.
- Keep inline errors near fields and add an error summary for long forms.
- Preserve entered data after errors.
- Use autocomplete, input modes, masks, and constraints for known data types.
- Avoid asking for data already available.
- Write errors in plain language with a concrete recovery path.

## Copy

- Use domain language, not database names.
- Button labels should describe the outcome: "Invite user", "Save draft", "Export CSV".
- Avoid vague actions like "Submit" when the outcome is specific.
- Status text should distinguish loading, saving, saved, failed, offline, queued, and blocked.
- Remove explanatory UI copy that only describes how to use a poorly structured screen.
