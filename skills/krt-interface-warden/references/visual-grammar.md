# Editorial Product UI Visual Grammar

Use this reference to compose product interfaces with content-led hierarchy, rigorous alignment, purposeful density, and few artificial surfaces. The objective is a page designed for its specific information and task, not a consistent-looking collection of widgets.

## Contents

1. Composition order
2. Surface budget
3. Layout archetypes
4. Component decisions
5. Typography and identity
6. Spacing, borders, elevation, and color
7. Responsive composition
8. Forms, iconography, motion, and states
9. Pattern replacements
10. Final self-critique
11. Source basis

## 1. Composition Order

Create hierarchy in this order:

1. Type size, family, weight, and line length.
2. Position and alignment.
3. Vertical space and grouping.
4. Column width and proportion.
5. Dividers and indentation.
6. Subtle background changes.
7. Partial or complete borders.
8. Elevation.

Before drawing a rectangle around content, try a clearer heading, more space before the section, column alignment, a divider, indentation, or a subtle background shift. Use a closed surface only when it expresses an independent semantic object or functional layer.

Prefer clarity over symmetry. Do not give every module equal visual weight. Establish one dominant information element, one primary action, and a deliberate path of attention.

## 2. Surface Budget

Apply these constraints by default:

- Keep the base background visible across roughly 60-70% of the viewport when product context permits.
- Use at most one dominant contained surface per viewport.
- Use at most two visible elevation levels.
- Never nest cards inside cards.
- Do not combine a border, contrasting fill, and shadow on the same container unless the layer genuinely floats and needs separation.
- Do not wrap headings, filters, metrics, forms, or section groups in cards by reflex.
- Use shadows only for menus, popovers, dialogs, drawers that float, and draggable objects.

A section does not need a card because it contains multiple related elements. Proximity, alignment, headings, and dividers already express grouping.

### Card decision

Use a card only when the content is:

- An independent entity among equivalent peers.
- Selectable, movable, draggable, or reorderable as one object.
- A summary that opens a more detailed view.
- An object with its own primary action.
- A stateful item that needs a clear semantic boundary.

Ask: **Would this remain understandable with only a title, space, alignment, and a divider?** If yes, do not use a card.

Record the reason for every retained card in the composition brief. “Groups related content” is not sufficient.

## 3. Layout Archetypes

Choose one primary archetype from the user task. Combine archetypes only when their regions and responsibilities are distinct.

### Editorial page

Use for executive dashboards, reports, and summaries. Lead with a large title or finding, one protagonist metric or conclusion, supporting facts separated by alignment or rules, then a main narrative with a contextual side rail.

### Master-detail

Use for projects, clients, invoices, documents, messages, and other entities users scan while inspecting one selection. Keep list context and selected detail visible together when space permits. Avoid routing every inspection through a modal.

### Canvas with inspector

Use for agents, automations, diagrams, editors, and configurators. Keep the center open for the work. Put tools in a compact rail and only selected-object properties in the inspector.

### Staged flow

Use for onboarding, creation, review, and consequential multi-step processes. Show stage, current task, completion signal, and a persistent summary. Avoid one giant form divided into many cards.

### Document with contextual rail

Use for reports, evaluations, agent results, evidence, and documentation. Preserve a readable main column, document navigation, and a secondary evidence/comment rail without boxing every section.

### Operational list

Use for tasks, incidents, inboxes, queues, and activity. Organize with group headings, aligned fields, horizontal separators, and stable row actions. Do not use a card per row.

### Narrative dashboard

Use when measures must tell a story. Lead with one dominant measure, place secondary measures in an aligned band, show one principal visualization, and annotate why the data matters. Avoid a KPI-card grid.

### Split view

Use when two work zones directly inform each other and must remain visible together, such as source/preview, query/results, or request/response. Give the primary side more space; do not force false symmetry.

### Timeline or feed

Use when sequence, provenance, or activity matters more than column comparison. Use time anchors, connectors, groups, and expandable detail rather than repeated event cards.

## 4. Component Decisions

### Tables

Use a table when users need one or more of these capabilities:

- Compare values vertically across rows and columns.
- Sort or filter many records.
- Perform bulk selection or action.
- Inspect genuinely dense structured data.
- Recognize patterns across stable columns.

If users do not need column comparison, they probably do not need a table. Consider rich lists, master-detail, timelines, activity feeds, grouped states, visual matrices, charts with detail on demand, or definition lists.

Do not use tables for one entity's metadata, simple title-description-status lists, sequential processes, recent activity, hierarchical information, or data whose primary purpose is change/distribution.

When a table is justified, use clear typographic hierarchy, fine separators, sticky context where useful, stable numeric alignment, sensible density, semantic markup, and responsive preservation of the comparison task.

### Metrics

Do not place every KPI in an identical card. Prefer:

- One protagonist metric or conclusion.
- Supporting measures in an aligned horizontal band.
- Subtle vertical separators.
- Type scale and weight differences.
- One main visualization.
- Annotations that interpret the number.

Metrics must build a narrative or enable a decision, not merely occupy a grid.

### Lists and metadata

Use rich rows for equivalent operational objects. Use definition lists for one entity's metadata. Use group headings, indentation, or side marks for hierarchy. Keep state, owner, time, risk, and next action aligned for scanning.

### Layers

Create depth through functional layers: main work zone, inspector, drawer, review overlay, comparison view, or timeline detail. A layer must change context or interaction, not merely decorate a section.

## 5. Typography and Identity

Let typography carry more identity than containers, shadows, gradients, or icons.

Suggested roles:

- Functional sans: Instrument Sans, IBM Plex Sans, Geist, or an established product face.
- Optional editorial serif: Newsreader, Source Serif 4, or Lora for selected page titles, protagonist figures, quotations, conclusions, empty states, or report covers.
- Code/data: IBM Plex Mono, Geist Mono, or the product's established monospace.

Do not introduce a new font when the existing product typography is mature and replacing it would fragment the system. Create hierarchy with the available family first.

Use these ranges as guidance, adjusted to context and viewport:

- Page title: 36-48px desktop.
- Section title: 20-28px.
- Functional text: 14-16px.
- Metadata: 12-13px.
- Protagonist figure: 40-64px.
- Narrative line length: roughly 65-75 characters.
- Font weights: no more than four.

Avoid making every heading semibold. Use size, family, placement, whitespace, and contrast as well as weight. Avoid landing-page scale inside dense product tools.

## 6. Spacing, Borders, Elevation, and Color

Use a 4px base with primary 8px rhythms:

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 24px;
--space-6: 32px;
--space-7: 48px;
--space-8: 64px;
--space-9: 96px;

--radius-sm: 4px;
--radius-md: 8px;
--radius-lg: 12px;

--border-subtle: 1px solid var(--border-muted);
--shadow-floating: 0 8px 30px rgb(0 0 0 / 0.08);
```

Allow small optical adjustments. Do not assign identical padding to every component. Keep controls within one task close, leave medium space within a section, and create broad separation between conceptual sections. Usually place more space before a heading than after it.

Reserve radii above 12px for circles, pills, or explicit brand forms. Use low-intensity horizontal rules to organize lists. Avoid full borders around every section.

Use mostly neutral colors. Apply brand color to primary action, current selection, active state, visualization, or a small editorial accent. Reserve semantic colors for real success, warning, error, and information states. Do not use large decorative gradients by default.

## 7. Responsive Composition

Recompose; do not merely shrink or stack the desktop layout.

- Preserve the primary task and critical action.
- Move secondary context behind disclosure, into a panel, or into a separate view.
- Turn side rails into accessible drawers or routed views when needed.
- Preserve comparison for genuinely tabular data; allow horizontal scrolling only when the columns are the task.
- Do not convert every table row or list item into a card.
- Reduce decorative or redundant metadata before compressing essential controls.
- Verify long labels, localization, touch targets, focus order, sticky regions, and overflow.

For master-detail, mobile may become list -> detail navigation. For canvas/inspector, the inspector may become a sheet or dedicated view. For document/rail, annotations may become anchored disclosures. Preserve context and a clear return path.

## 8. Forms, Iconography, Motion, and States

### Forms

Group fields with headings, descriptions, spacing, and alignment rather than one card per group. Keep help and validation near their field. Use progressive disclosure for advanced options. Keep primary actions stable. Avoid modals for flows requiring sustained attention.

### Iconography

Do not place every icon in a rounded square. Do not add an icon when the label is already unmistakable. Keep one style and stroke weight. Use icons for recognition and operation, not to fill empty headings.

### Motion

Use brief motion to explain state change, contextual appearance, or spatial reorganization. Avoid ambient or decorative animation. A transition should clarify what changed and where it came from.

### States

Design empty, loading, error, blocked, success, partial-data, too-much-data, review, and conflict states in the chosen surface language. Prefer contextual progress and recovery actions over generic spinners or isolated badges. Never rely on color alone.

## 9. Pattern Replacements

- Metric card -> protagonist figure plus aligned supporting band.
- Dashboard card grid -> editorial page or narrative dashboard.
- Project/user card -> rich operational row or master-detail list.
- Feature card -> editorial section with a rule, number, example, or workflow step.
- Task card -> operational line with priority, state, owner, and action.
- Activity card -> timeline/logbook entry.
- Settings cards -> titled form sections with spacing and dividers.
- Metadata table -> definition list or contextual rail.
- Generic badge -> flat status mark integrated into the scan path.
- Floating white panel -> docked work zone or subtle background band.
- Ten-card form -> staged flow with persistent summary.

## 10. Final Self-Critique

Before delivery, answer:

- Is the primary task immediately recognizable?
- Is there one dominant visual element or decision?
- Does the selected archetype fit this content and workflow?
- Is every card backed by an independent-object reason?
- Can at least one container be removed?
- Can a border be replaced by space, alignment, or a divider?
- Is every table necessary for comparison, density, sorting, patterns, or bulk action?
- Do too many elements have equal visual weight?
- Is color carrying semantics or merely atmosphere?
- Does the screen remain understandable without icons?
- Does the layout feel specific to this content?
- Does mobile preserve the task rather than stack the desktop?
- Could the result be mistaken for a generic dashboard template?

When two solutions are equally functional, choose the one with fewer surfaces, fewer borders, and clearer typographic hierarchy.

## 11. Source Basis

This grammar synthesizes durable guidance from:

- [Material Design cards](https://m3.material.io/components/cards/guidelines): cards contain content and actions about one subject.
- [U.S. Web Design System cards](https://designsystem.digital.gov/components/card/): cards summarize or link into a larger idea.
- [Primer layout foundations](https://primer.style/product/getting-started/foundations/layout/): responsive layouts preserve functionality through purposeful recomposition.
- [Primer Design System](https://primer.style/): foundations precede component selection.
- [Atlassian spacing](https://atlassian.design/foundations/spacing): consistent spacing rhythms with intentional exceptions.
- [Untidy Data: The Unreasonable Effectiveness of Tables](https://arxiv.org/abs/2106.15005): tables remain valuable when direct inspection and manipulation of data is the task.
