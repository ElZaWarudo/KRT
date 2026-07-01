# Critique Rubric

Use this rubric to make the visual critique precise, adversarial, and useful for implementation.

## Identity

Ask:

- Could this UI belong to any startup with the logo swapped?
- Is there a recognizable visual system beyond colors and rounded cards?
- Does the page communicate its domain through structure, density, labels, states, and interaction patterns?

Strong evidence:

- Domain-specific surface metaphor.
- Persistent contextual anchors.
- Visual marks tied to workflow states.
- Layout decisions that would not make sense in a generic marketing page.

Weak evidence:

- Generic cards, hero copy, bento grid, stock-like illustration, soft shadows, vague icons.

## Surface Metaphor

Classify the screen:

- Dossier: one entity or case under review.
- Map: relationships, dependencies, topology, flows.
- Logbook: events, audit trail, history, changes.
- Control table: operational monitoring, queues, live work.
- Workshop: creating, editing, transforming, configuring.
- Archive: search, filter, retrieve, compare.
- Report: findings, evidence, conclusions.

If none fits, name the mismatch and recommend one.

## Layout

Inspect:

- Dominant working zone.
- Persistent rails or bands.
- Margin metadata.
- Inspection or detail panel.
- Table/row structure.
- Responsive behavior.
- Whether equal-weight modules flatten priority.

Look for layout drift: modules that seem independently styled rather than part of one system.

## Hierarchy

Ask:

- What is the first thing the user should see?
- What action should they take next?
- What must remain visible while scrolling or inspecting?
- Are status, ownership, timing, and risk placed where they support decisions?

Common failures:

- Primary action competes with decorative content.
- Important metadata is buried inside cards.
- Section headings are too similar.
- Typography uses landing-page scale inside a tool.

## Density

Critique density by function, not taste.

- Too sparse: the user must scroll or scan too much for simple decisions.
- Too dense: the user cannot isolate priority, state, or action.
- Wrong density: decorative areas are spacious while operational data is cramped.

## State Language

Strong status systems use marks, rails, lines, stamps, table-side signals, or typographic codes.

Weak status systems use disconnected badges, arbitrary colors, or labels that do not affect layout or workflow.

## Color

Color should encode:

- Action.
- State.
- Risk.
- Grouping.
- Navigation.
- Priority.

Flag color used only as atmosphere. Flag semantic conflicts, weak contrast, and color-only state communication.

## Typography

Look for:

- Readable body scale.
- Strong but not bloated headings.
- Mono or semi-mono metadata for dates, IDs, codes, states, and technical values.
- Consistent alignment and rhythm.
- No negative letter spacing unless already established by a mature design system.

## Interaction

Controls should map to tool actions:

- Inspect.
- Compare.
- Filter.
- Mark.
- Validate.
- Archive.
- Expand.
- Pin.
- Review history.

Flag controls that are styled as generic CTAs but belong to a work surface.

## Accessibility

Always check:

- Contrast.
- Focus visibility.
- Keyboard path.
- Semantic heading order.
- Table readability.
- Responsive overflow.
- Color-independent status cues.
- Touch target size.
- Text fitting in compact containers.

## Implementation Input Pattern

Use this formula:

```text
Replace <weak pattern> with <specific structural pattern> so <workflow outcome improves>.
```

Examples:

- Replace metric cards with a single operational status band so totals remain visible while the table drives the page.
- Replace project cards with grouped rich rows so priority, owner, due date, and next action can be compared quickly.
- Replace generic badges with left-edge state marks so review state becomes part of the scanning path.
