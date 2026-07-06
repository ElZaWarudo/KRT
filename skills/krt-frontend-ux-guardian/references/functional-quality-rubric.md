# Functional Quality Rubric

Use this reference to decide whether the interface works for the user's task.

## Task Clarity

- The user can tell what this surface is for within a few seconds.
- The primary action is obvious.
- Secondary actions do not compete with the primary action.
- Required context is visible before the user must decide.
- The completion signal is clear after the action succeeds.

## Flow Continuity

- The user has a clear entry point and next step.
- Back, cancel, retry, edit, or undo exists where the workflow needs it.
- Long flows show progress or current step.
- The user does not lose entered data after errors.
- The interface avoids dead ends after empty, blocked, failed, or permission-denied states.

## State Coverage

Check whether the changed surface handles:

- Empty data.
- Loading.
- Saving or processing.
- Success.
- Validation failure.
- API/backend failure.
- Partial data.
- Permission or role restriction.
- Conflict or stale data.
- Destructive action.
- Large or long content.

## Data Usability

- Tables support scan, sort, filter, search, compare, select, and act when the data type requires it.
- Dense data keeps labels, units, dates, ownership, status, and next action close to the value.
- Long values wrap, truncate, or reveal safely.
- Filters and selections remain visible after navigation or refresh when the product pattern expects it.
- Empty and filtered-empty states are distinct.

## Interaction Reliability

- All interactive elements have clear affordance.
- Controls are close to the content they affect.
- Disabled controls explain why when the reason is not obvious.
- Risky actions use confirmation or friction appropriate to the damage.
- Repeated workflows are efficient enough for real use.
- Keyboard and pointer interactions reach the same outcomes.

## Visual Decisions As Functional Support

Visual choices are acceptable when they improve:

- Reading order.
- Scannability.
- Grouping.
- Priority.
- State recognition.
- Error prevention.
- Recovery.
- Trust in the current system state.

Visual choices are suspect when they mainly add:

- Decoration.
- Generic SaaS polish.
- Extra cards.
- Low-density whitespace in operational tools.
- Icons without meaning.
- Gradients or effects that do not encode useful information.

## Final Gate

Before delivery, verify:

- The primary workflow can be completed.
- Important non-happy states are represented or intentionally out of scope.
- Text does not overlap, clip, or overflow at tested widths.
- The layout still works with realistic data.
- Accessibility and responsive behavior remain intact.
