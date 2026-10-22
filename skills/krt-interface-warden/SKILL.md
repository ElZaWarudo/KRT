---
name: krt-interface-warden
description: "Design, build, redesign, or critique frontend interfaces with the Editorial Product UI doctrine: content-led hierarchy, a working-surface metaphor, a deliberate layout archetype, few containers, and purposeful typography instead of generic AI/SaaS card grids. Use when building or restyling a screen, page, dashboard, or app view; when a UI looks generic, templated, or AI-generated; and for visual critique, design review, or visual audit requests such as 'critique this UI', 'why does this look generic', 'visual audit', or 'make this feel less like a SaaS template'. For motion and interaction feel use krt-interaction-polisher."
---

# krt-interface-warden

The goal is an interface composed for its specific content and task, so it reads as a dossier, logbook, or control table for this domain rather than a pile of widgets that could belong to any startup. The left-to-right default (sidebar, header, a row of identical KPI cards, a table, everything boxed with border plus shadow) is what models produce unprompted and what users call "generic". Identity should come from content and composition, not from decoration.

The same doctrine serves two modes: **design** (build or redesign) and **critique** (audit and hand off). Operability always wins over distinctiveness: never trade away the primary task, required states, accessibility, or established product mechanics for a look.

## The doctrine

**Lead with one thing.** Decide what the user's task is and which single element (a figure, a decision, a queue, a work zone) should dominate. Give it type size, position, and space. Everything else is quieter. Equal visual weight for every module is the most common failure.

**Pick a surface metaphor** that fits the work, and let the layout follow it:

- Dossier: reviewing one entity, case, claim, or record.
- Map: relationships, dependencies, flows, topology.
- Logbook: events, history, incidents, audit trails.
- Control table: monitoring queues, workloads, live states.
- Workshop: creating, editing, configuring.
- Archive: searching, filtering, comparing many records.
- Report: findings, evidence, recommendations.

**Pick one layout archetype** (combine two only when each owns a distinct region): editorial page, master-detail, canvas with inspector, staged flow, document with contextual rail, operational list, narrative dashboard, split view, timeline/feed. A persistent sidebar is navigation infrastructure, not a design concept.

**Build hierarchy with the cheapest tool that works**, in this order: typography, space, alignment, proportion, dividers, subtle background shifts, borders, elevation. Reach for a closed surface only when the earlier tools cannot express a real boundary.

**Cards must earn their place.** A card is justified for an independent object among peers, something selectable or draggable as a unit, a summary that opens detail, an object with its own primary action, or a stateful item needing a boundary. "Groups related content" is not a reason; headings, proximity, and rules already do that. Test: would it still be clear with only a title, space, alignment, and a divider? Then drop the card. No nested cards, and no container combining full border, contrasting fill, and shadow.

**Tables are for comparison.** Keep one when users compare columns, sort or filter many records, recognize patterns, or act in bulk, and then improve it (numeric alignment, sticky header, fine rules, a clear bulk-action bar) rather than replacing it. One entity's metadata belongs in a definition list; history belongs in a timeline; simple title-status lists belong in rich rows. Do not "fix" a justified table by turning rows into cards.

**Metrics tell a story.** One protagonist figure, supporting measures in an aligned band, an annotation that says why the number matters. Not a grid of identical KPI boxes.

**Surface budget.** Keep the base background visible over most of the viewport (roughly 60-70% when the product allows), at most one dominant contained surface per viewport, at most two elevation levels. Shadows are for things that float: menus, popovers, dialogs, drag objects.

**Color and type as signage.** Color marks action, state, risk, selection, or data, never atmosphere; no decorative gradients, glass, or blobs. Typography carries identity: a work sans, optionally a serif for a protagonist figure or editorial title, mono for codes, dates, and IDs. Don't swap a mature product's typeface; build hierarchy with what exists.

**States belong to the surface.** Empty, loading, error, blocked, partial, and conflict states should speak the same language as the metaphor. Status never relies on color alone.

**Recompose for narrow screens.** Reprioritize the task: master-detail becomes list then detail, rails become disclosures or drawers, and tables scroll horizontally only when the columns are the task. Mechanically stacking every desktop box, or turning every row into a card, is the failure.

**Reuse before inventing.** Keep the product's components, tokens, and mechanics unless they are the cause of the problem, and say why when you depart.

The generic patterns to recognize and replace (not merely delete) are listed in `references/visual-grammar.md`, together with replacements, typography and spacing ranges, and archetype detail. Read it for any material design or audit.

## Design mode

Decide the task, dominant element, metaphor, and archetype before writing markup; let those choices show in the result. Then ask what can be removed: at least one container usually can. Check the subtraction test before finishing: mentally strip borders, shadows, icons, and accent color. If the hierarchy collapses, it was carried by chrome.

Keep the explanation short when the user mainly wants code; the interface should carry the argument. A few lines on the chosen metaphor and archetype, any card or table kept and why, and what generic pattern was replaced are enough.

If a functional or accessibility contract exists (from the user or the codebase), treat it as fixed. If a requested visual change cannot satisfy it, say so instead of quietly breaking it.

## Critique mode

When asked to critique, review, or audit, produce a report and leave files untouched unless the user also asked for the fix. Ground every point in evidence: the code (cite file, selector, or line), a screenshot region, or the rendered page if you can open it. Label anything inferred.

Aim for a few sharp findings, ordered by impact, rather than broad aesthetic commentary. Severity that has worked well:

- **P0 operability**: the screen cannot be understood, operated, or trusted.
- **P1 identity**: it reads as a generic template, or the metaphor is incoherent.
- **P2 structure**: hierarchy, density, states, or layout weak enough to slow work.
- **P3 polish**: craft improvements that don't change structure.

Each material finding needs a concrete, implementable change, shaped as: *replace <observed pattern> with <specific structure> so <workflow outcome>, while preserving <constraint>.* "Make it more modern", "improve spacing", or "add visual interest" are not findings. Also say what is working and should be kept, so the implementer doesn't redesign it away, and name at least one container to remove (or why the surface budget is already disciplined). Accessibility problems you notice (contrast, focus, labels, color-only state) are operability findings, not polish.

If the user asks for critique and fix together, finish the critique first, then implement against it and note which findings you adopted, adapted, or deferred.
