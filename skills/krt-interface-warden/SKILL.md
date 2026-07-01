---
name: krt-interface-warden
description: Design distinctive, functional frontend interfaces that avoid generic AI/SaaS visual patterns by choosing a working-surface metaphor, replacing unnecessary cards, and enforcing strong layout, state, and accessibility decisions.
---

# krt-interface-warden

Use this skill when designing, implementing, or reviewing a frontend interface that must feel specific, functional, and intentionally designed instead of generic, AI-generated, or template-like.

The mission is not to make screens "pretty." The mission is to shape a working surface: a dossier, map, logbook, control table, workshop, archive, or report that helps people inspect, decide, operate, compare, validate, or navigate real information.

## Core Rule

Do not design the interface as a collection of cards.

Design it as a working surface with structure, hierarchy, rhythm, useful density, and visual tension. If a card is used, it must behave like an independent object with a clear functional reason. Otherwise replace it with bands, rails, annotated margins, tables, rows, panels, layers, or section systems.

## Trigger Conditions

Apply this skill when the task involves:

- Building a frontend app, dashboard, tool, report, admin surface, workflow UI, or prototype.
- Polishing UI that feels generic, AI-generated, too SaaS-like, too card-heavy, or too decorative.
- Creating visual direction for a product surface before implementation.
- Reviewing whether a UI has a recognizable identity and functional layout logic.

## Required Pre-Design Pass

Before proposing UI or code, decide internally:

1. What surface is this screen: dossier, map, logbook, control table, workshop, archive, or report?
2. What is the user's primary action?
3. What information must stay visible at all times?
4. What information belongs in a margin, rail, status band, or inspection panel?
5. What generic AI/SaaS pattern are you tempted to use?
6. What working-surface pattern replaces it?
7. Where is the screen's visual tension: density, asymmetry, contrast, sequence, timeline, comparison, or status?
8. What would make this interface recognizable without a logo?

If the answer is unclear, choose the most useful surface metaphor from the data and workflow. Do not block unless the user has not provided enough product context to choose safely.

## Surface Metaphors

- **Dossier**: reviewing one entity, case, user, client, asset, claim, or record.
- **Map**: navigating relationships, dependencies, flows, ownership, or topology.
- **Logbook**: reading events, history, activity, changes, incidents, or audit trails.
- **Control table**: monitoring operations, queues, workloads, states, or live metrics.
- **Workshop**: creating, editing, composing, transforming, or configuring.
- **Archive**: searching, filtering, comparing, and retrieving many records.
- **Report**: explaining findings, recommendations, conclusions, or evidence.

The layout must follow the selected metaphor.

## Design Directives

- Prefer bands, rails, annotated margins, expressive tables, status marks, layers, legends, and connection lines over standalone cards.
- Use color as signage: action, state, risk, grouping, navigation, priority. Do not use decorative gradients unless they encode real information.
- Use typography to signal system and craft: readable sans for content, mono or semi-mono for metadata, codes, dates, statuses, and technical values.
- Make states part of the identity: empty, loading, error, blocked, success, partial data, too much data, review, and conflict states should match the surface metaphor.
- Use depth through functional layers: main panel, inspector, drawer, review overlay, timeline, comparison view. Do not rely on soft shadows for personality.
- Keep accessibility non-negotiable: contrast, keyboard navigation, visible focus, semantic structure, responsive behavior, tables that remain understandable, and signals that do not depend on color alone.

For the extended visual grammar and card-replacement map, read `references/visual-grammar.md`.

## Default Replacements

- Metric card -> margin counter, status band, dense summary row, or table header value.
- Feature card -> editorial block with a rule line, number, concrete example, or workflow step.
- User card -> compact dossier record with metadata and state marks.
- Project card -> rich row with status, owner, date, risk, and next action.
- Dashboard card -> integrated control-table module.
- Pricing card -> comparison table or contract-like plan sheet.
- News card -> logbook entry.
- Task card -> operational line with priority, state, and owner.
- Product card -> technical sheet or inventory record.

## Delivery Requirements

When generating or materially changing an interface, include:

1. Selected visual surface.
2. Layout decision.
3. Visual rules applied.
4. Main components.
5. Replacements made to avoid generic cards or other AI/SaaS patterns.
6. Clean, accessible, maintainable frontend code when implementation is requested.
7. A short note explaining why the UI avoids generic AI aesthetics.

Keep the explanation brief when the user primarily asked for code; the interface itself should carry the design argument.

## Final Checklist

Before delivery, verify:

- The screen does not read as a generic SaaS template.
- Cards are absent or functionally justified.
- Bento grids, glassmorphism, decorative gradients, and filler icons are avoided.
- Margins, rails, bands, tables, or layers do real work.
- The chosen surface metaphor is visible in the layout.
- Hierarchy works without decorative clutter.
- States have a recognizable system language.
- The design would still be identifiable without a logo.
- Accessibility and responsiveness remain intact.
