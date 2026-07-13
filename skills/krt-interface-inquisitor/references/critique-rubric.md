# Editorial Product UI Critique Rubric

Use this rubric to make visual critique precise, adversarial, evidence-based, and directly useful to implementation. Judge the screen as one composition before judging individual components.

## Contents

1. Task and dominant element
2. Identity and surface metaphor
3. Layout archetype
4. Hierarchy ladder
5. Surface budget and cards
6. Tables, metrics, lists, and forms
7. Typography, spacing, color, and iconography
8. Density, states, and interaction
9. Responsive composition
10. Accessibility
11. Generic-pattern challenge
12. Implementation inputs and verification

## 1. Task and Dominant Element

Identify the user's primary task, next action, and completion signal. Then identify what the eye sees first.

Ask:

- Does the visual lead support the primary task?
- Is one fact, action, work zone, or conclusion clearly dominant?
- What context must remain visible during the task?
- Are secondary modules quieter, or does everything compete at the same weight?

Flag a structural failure when the primary task cannot be inferred or when all modules receive identical card treatment, padding, heading weight, and prominence.

## 2. Identity and Surface Metaphor

Ask:

- Could this UI belong to any startup with the logo swapped?
- Does the domain appear through structure, density, labels, states, and operations?
- Is the screen recognizably a dossier, map, logbook, control table, workshop, archive, or report?
- Would its identity survive removal of brand color, icons, and logo?

Strong evidence includes domain-specific structure, persistent contextual anchors, state marks tied to workflow, and interaction patterns that would not make sense in a generic landing page.

Weak evidence includes generic cards, hero copy, bento grids, stock illustrations, soft shadows, vague icons, and novelty decoration unrelated to the task.

## 3. Layout Archetype

Classify the spatial composition independently from its surface metaphor:

- **Editorial page**: one lead fact/conclusion, supporting measures, narrative, contextual rail.
- **Master-detail**: scannable entity list plus persistent selected detail.
- **Canvas with inspector**: open work area, compact tools, selected-object properties.
- **Staged flow**: visible stage, focused task, persistent summary and completion path.
- **Document with contextual rail**: readable main column with evidence, comments, or metadata alongside.
- **Operational list**: grouped rich rows, separators, aligned state/time/action fields.
- **Narrative dashboard**: protagonist metric, supporting band, principal visualization, interpretation.
- **Split view**: two directly related work zones visible together with deliberate proportion.
- **Timeline or feed**: sequence and provenance expressed through time anchors and connection.

Name the archetype as chosen, missing, or mismatched. Recommend a replacement only when it materially improves the task. A sidebar is navigation infrastructure, not an archetype.

## 4. Hierarchy Ladder

Audit how grouping and priority are expressed. The preferred order is:

1. Typography.
2. Space.
3. Alignment.
4. Column proportion.
5. Dividers or indentation.
6. Subtle background shifts.
7. Borders.
8. Elevation.

Flag interfaces that begin at steps 7-8: full borders, filled boxes, and shadows around every group. For each major container, test whether typography, spacing, alignment, or a divider could do the same job with less chrome.

## 5. Surface Budget and Cards

Audit the visible surface stack:

- Is roughly 60-70% of the viewport allowed to remain the base surface when context permits?
- Is there more than one dominant contained surface?
- Are more than two elevation levels visible?
- Are cards nested?
- Does one container combine a full border, contrasting fill, and shadow?
- Are headings, filters, metrics, forms, or ordinary sections wrapped by reflex?

### Card test

A card is justified only when it represents an independent entity, selectable/reorderable object, summary entry into detail, object with its own primary action, or stateful item needing a semantic boundary.

Ask: **Would this remain understandable using only a title, space, alignment, and a divider?** If yes, mark the card unjustified.

Always name at least one candidate container to remove. If none exists, explicitly state why the surface budget is already disciplined.

## 6. Tables, Metrics, Lists, and Forms

### Table test

Retain a table only when users compare columns, sort/filter many records, perform bulk actions, inspect dense structured data, or recognize patterns across stable columns.

Flag a table used for one entity's metadata, simple title-description-status items, sequential processes, recent activity, hierarchy, or primarily temporal/distribution data. Recommend a rich list, master-detail, timeline, feed, grouped states, definition list, matrix, or chart with detail on demand.

Do not criticize a dense table merely for being a table. When comparison is the task, improve hierarchy, separators, alignment, sticky context, actions, semantics, and narrow-screen behavior without destroying density.

### Metric test

Ask whether metrics form a narrative or merely fill a grid. Look for one protagonist measure or conclusion, supporting measures in an aligned band, a main visualization, and annotations explaining meaning. Flag identical KPI cards with no priority.

### List test

Operational rows should align the fields users scan: state, owner, date/time, risk, and next action. Flag a card-per-row conversion that breaks comparison or wastes space.

### Form test

Look for field groups expressed through headings, descriptions, space, and alignment. Flag a card per field group, unstable actions, remote help/error text, premature advanced options, and long-attention workflows trapped in modals.

## 7. Typography, Spacing, Color, and Iconography

### Typography

Check whether type carries identity and hierarchy. Flag generic semibold-everywhere treatment, landing-page scale inside tools, weak numeric alignment, excessive font weights, poor line length, and metadata that competes with content.

An editorial serif or mono data face can add character, but do not demand a new font when an established product family can create the needed hierarchy.

### Spacing and borders

Look for a coherent 4/8px rhythm with varied grouping: tight inside one control/task, medium inside a section, broad between concepts, and usually more space before a heading than after it. Flag uniform padding everywhere and full borders around every section.

### Color

Color should encode action, state, risk, grouping, navigation, priority, or data. Flag atmosphere-only gradients, excessive brand fill, semantic conflicts, weak contrast, and color-only state communication.

### Iconography

Flag icons added where text is already clear, mixed visual styles, large icons in every heading, and repeated rounded-square icon containers. Preserve icons that improve rapid recognition or operate without ambiguity.

## 8. Density, States, and Interaction

Critique density by function, not taste:

- **Too sparse**: users scroll or scan too much for a simple decision.
- **Too dense**: users cannot isolate priority, state, or action.
- **Wrong density**: decorative regions are spacious while operational data is cramped.

Inspect empty, loading, error, blocked, success, partial-data, too-much-data, review, and conflict states when present. States should belong to the selected surface language, preserve context, and expose recovery. Flag disconnected badges, generic spinners, and state communicated only by color.

Controls should map to the work: inspect, compare, filter, mark, validate, archive, expand, pin, edit, or review history. Flag generic CTA styling that obscures operational hierarchy.

Motion should explain state change, contextual appearance, or spatial reorganization. Flag ambient or decorative animation that competes with the task.

## 9. Responsive Composition

Inspect a narrow viewport whenever evidence permits.

Ask:

- Is the primary task and critical action preserved?
- Is secondary context moved behind disclosure, into a panel, or into a separate view?
- Does master-detail become navigable list -> detail with a clear return path?
- Does an inspector become a sheet or dedicated view without hiding current selection?
- Are tables allowed horizontal overflow only when comparison genuinely requires it?
- Were desktop rows converted into wasteful cards?
- Do long labels, localization, touch targets, focus order, sticky regions, and overflow remain usable?

Flag mechanical stacking when every desktop container simply becomes a full-width block without reprioritization.

## 10. Accessibility

Always check available evidence for:

- Contrast.
- Visible focus.
- Keyboard path and focus order.
- Semantic heading order and landmarks.
- Table headers, captions, and understandable overflow.
- Color-independent state cues.
- Touch-target size.
- Text clipping and zoom/reflow.
- Accessible names for icon-only controls.
- Error/status announcement and recovery.

Treat accessibility risks as operability findings, not aesthetic polish.

## 11. Generic-Pattern Challenge

Flag these unless a clear functional reason exists:

- `sidebar + header + KPI card grid + table` as an unexamined default.
- Repeated cards with identical radius, shadow, fill, and padding.
- Nested cards or bento grids used only to decorate grouping.
- Decorative gradients, blobs, glass panels, and soft-shadow boxes.
- Large centered hero copy inside a product tool.
- Metrics isolated in equal-weight boxes.
- Generic badges disconnected from the scan path.
- Rounded-square filler icons.
- Empty whitespace with no structural role.
- Oversized radii on ordinary containers.
- Mobile cardification of every list or table row.

Run the subtraction test: mentally remove shadows, borders, icons, and accent color. If hierarchy collapses, the composition depends on chrome rather than structure.

## 12. Implementation Inputs and Verification

Write every material finding with this pattern:

```text
Replace <observed weak pattern> with <specific structural pattern> so <workflow outcome improves>, while preserving <named constraint>.
```

Examples:

- Replace four equal KPI cards with one protagonist figure and an aligned supporting band so the trend and decision threshold read first, while preserving all four values.
- Replace project cards with grouped rich rows so priority, owner, due date, and next action can be compared quickly, while preserving row-level navigation.
- Replace nested settings cards with titled form sections and fine horizontal rules so the page reads as one flow, while preserving validation and advanced-option disclosure.
- Keep the invoice table because users compare amount, due date, state, and owner and reconcile in bulk; reduce container chrome and strengthen sticky headers instead.
- Replace mechanical mobile stacking with list -> detail navigation so the selected record gains usable space, while preserving filters and a clear return path.

Avoid vague inputs such as “make it modern,” “improve spacing,” “add visual interest,” or “make it pop.”

For verification, name the exact viewport, region, state, and behavior to inspect. Include a subtraction check, surface count, table/card justification, primary task visibility, focus path, and narrow-screen transformation when relevant.
