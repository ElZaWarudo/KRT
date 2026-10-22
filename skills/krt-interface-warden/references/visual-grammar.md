# Editorial Product UI: visual grammar

Lookup detail for `krt-interface-warden`. SKILL.md holds the doctrine; this file holds the catalogs.

## Contents

1. Generic patterns and replacements
2. Layout archetypes in detail
3. Component decisions
4. Typography, spacing, and color
5. Responsive recomposition
6. Forms, icons, motion
7. Critique examples
8. Source basis

## 1. Generic patterns and replacements

Flag these unless a clear functional reason exists, and always propose the replacement.

| Generic pattern | Replacement |
|---|---|
| Sidebar + header + KPI card grid + table, unexamined | Editorial page or narrative dashboard built around one lead fact |
| Row of identical metric cards | Protagonist figure plus an aligned supporting band, or a dense summary row |
| Gradient "Welcome back" hero inside a tool | Page title plus the one fact that needs attention today |
| Feature cards / repeated three-column sections | Editorial block with a rule line, number, concrete example, or workflow step |
| Project, user, or task cards | Rich operational row: status, owner, date, risk, next action aligned |
| Activity or news cards | Timeline or logbook entry with time anchors |
| Settings cards / ten-card form | Titled form sections with spacing and rules; staged flow with persistent summary |
| Metadata table for one entity | Definition list or contextual rail |
| Pricing cards | Comparison table or contract-like plan sheet |
| Product card | Technical sheet or inventory record |
| Floating white panel | Docked work zone or subtle background band |
| Pill badge disconnected from the scan path | Flat status mark (text plus shape) aligned in the row |
| Rounded-square emoji or icon tiles | Remove, or a plain icon only where it aids recognition |
| Bento grid, glass panels, blobs, soft-shadow boxes | Bands, rails, rules, and type scale |
| Oversized radii on ordinary containers | 4-8px, or none; reserve large radii for pills and circles |
| Whitespace with no structural role | Space that separates concepts, more above a heading than below |
| Mobile cardification of every row | Keep rows; reprioritize columns; list then detail |

## 2. Layout archetypes in detail

- **Editorial page**: large title or finding, one protagonist metric or conclusion, supporting facts separated by alignment or rules, main narrative with a contextual rail. For summaries, executive views, reports.
- **Master-detail**: scannable list with the selected item's detail visible alongside. Avoid routing every inspection through a modal.
- **Canvas with inspector**: open centre for the work, compact tool rail, inspector showing only the selected object's properties. For builders, diagrams, automations.
- **Staged flow**: visible stage, focused current task, persistent summary, clear completion. For onboarding, creation, consequential review.
- **Document with contextual rail**: readable main column (65-75 characters), navigation, and an evidence or comment rail, without boxing each section.
- **Operational list**: group headings, aligned fields, horizontal separators, stable row actions. No card per row.
- **Narrative dashboard**: one dominant measure, an aligned secondary band, one principal visualization, an annotation of why it matters.
- **Split view**: two directly related zones (source/preview, query/results); give the primary side more room.
- **Timeline or feed**: sequence and provenance via time anchors, connectors, groups, expandable detail.

## 3. Component decisions

**Tables.** Justified for column comparison, sort/filter of many records, bulk action, dense structured data, or pattern recognition across stable columns. Not for one entity's metadata, title-description-status lists, sequential processes, recent activity, hierarchies, or data whose point is change over time. When justified: tabular numerals right-aligned, fine separators, sticky header or first column where useful, semantic `<th>`/`scope`, a visible bulk-action bar tied to selection, and narrow-screen behaviour that preserves comparison.

**Metrics.** One lead figure, a supporting band with subtle vertical separators, type-scale and weight differences, one main visualization, and an interpretive annotation (threshold, trend, what to do).

**Lists and metadata.** Rich rows for equivalent operational objects; definition lists for one entity; group headings or indentation for hierarchy; keep state, owner, time, risk, and next action aligned.

**Layers.** Depth comes from functional layers that change context: main zone, inspector, drawer, review overlay, comparison view. Not from decorative shadows.

## 4. Typography, spacing, and color

- Functional sans (Instrument Sans, IBM Plex Sans, Geist, or the product's face); optional editorial serif (Newsreader, Source Serif 4, Lora) for selected titles, protagonist figures, or empty states; mono (IBM Plex Mono, Geist Mono) for IDs, codes, dates, and technical values.
- Desktop guide: page title 36-48px, section title 20-28px, body 14-16px, metadata 12-13px, protagonist figure 40-64px; no more than four weights. Avoid semibold-everything and landing-page scale inside dense tools.
- Spacing on a 4px base with 8px rhythm (4, 8, 12, 16, 24, 32, 48, 64, 96). Tight inside a control group, medium inside a section, broad between concepts. Not identical padding everywhere.
- Radii 4/8/12px; rules at low contrast; one floating shadow token such as `0 8px 30px rgb(0 0 0 / .08)`.
- Mostly neutral palette. Brand color on primary action, selection, active state, data, or one small editorial accent. Semantic colors only for real success, warning, error, info, always paired with text or shape.

## 5. Responsive recomposition

- Preserve the primary task and critical action first; cut decorative or redundant metadata before compressing controls.
- Master-detail becomes list then detail with a clear return path. Inspector becomes a sheet or a dedicated view without losing the selection. Document rails become anchored disclosures. Side rails become accessible drawers or routes.
- Tables may scroll horizontally only when the columns are the task; otherwise drop or merge low-priority columns.
- Check long labels, localization, touch targets, focus order, sticky regions, and overflow.

## 6. Forms, icons, motion

- Forms: group with headings, descriptions, and space, not one card per group. Help and validation sit by their field. Advanced options behind disclosure. Stable primary action. No modals for sustained work.
- Icons: one style and stroke weight; no icon where the label is unmistakable; no icon in every heading.
- Motion: brief, explaining a state change or where something came from. No ambient animation.

## 7. Critique examples

Good change inputs:

- Replace the four metric cards with one protagonist figure (incidents breaching SLA) and an aligned band for the other three, so on-call sees what needs action first, while keeping all four values.
- Replace project cards with rich rows grouped by risk with a persistent action column, so priority, owner, and due date compare at a glance, while keeping row-level navigation.
- Keep the shipment table because dispatchers compare ETA, carrier, and weight and reassign in bulk; remove the wrapping cards and strengthen the sticky header and bulk-action bar instead.
- Replace nested settings cards with titled sections on the base page separated by 32px and fine rules, while keeping validation and advanced-option disclosure.
- Replace mechanical mobile stacking with list then detail so the selected record gets usable space, while keeping filters and a return path.

Not findings: "make it more modern", "improve spacing", "add visual interest", "make it pop".

For verification, name the viewport, region, state, and behaviour to inspect: subtraction check, surface count, card and table justification, primary-task visibility, focus path, narrow-screen transformation.

## 8. Source basis

Material Design and USWDS card guidance (a card is about one subject and links into more); Primer layout foundations (recompose responsively to preserve function); Atlassian spacing (consistent rhythm with intentional exceptions); Bartram et al., "Untidy Data: The Unreasonable Effectiveness of Tables" (2021) (tables stay valuable when direct inspection is the task).
