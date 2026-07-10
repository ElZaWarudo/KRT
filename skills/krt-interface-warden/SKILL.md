---
name: krt-interface-warden
description: Independently design or implement distinctive, functional frontend interfaces that avoid generic AI/SaaS patterns through working-surface metaphors, purposeful layout, state language, and accessible code. Use for visual direction, redesign, polish, or implementation; honor a krt-frontend-ux-guardian contract and consume a krt-interface-inquisitor brief when supplied, without requiring either companion.
---

# krt-interface-warden

Use this skill when designing, implementing, or reviewing a frontend interface that must feel specific, functional, and intentionally designed instead of generic, AI-generated, or template-like.

The mission is not to make screens "pretty." The mission is to shape a working surface: a dossier, map, logbook, control table, workshop, archive, or report that helps people inspect, decide, operate, compare, validate, or navigate real information.

## Collaboration Role

Warden operates independently and owns the visual system and implementation decisions. It must infer the user task, constraints, and visual direction itself when no companion artifact exists.

When the companion skills are also active:

- Guardian supplies the functional UX contract and owns its verification gate.
- Inquisitor supplies evidence-based critique and prioritized change inputs.
- Warden records the rationale for accepted, adapted, or deferred findings.

Consume a Guardian UX contract or Inquisitor critique brief only when supplied. Otherwise derive the same minimum product constraints from the request and existing interface. Preserve the primary task, completion signal, persistent context, required states, accessibility/responsive constraints, and established mechanics. Visual distinctiveness must not reduce operability.

For critique-and-fix work with Inquisitor active, implement only after its brief is complete and record which findings were accepted, adapted, or deferred. Without Inquisitor, perform Warden's own pre-design diagnosis and continue. Do not reopen supplied product constraints; surface a conflict when the requested visual change cannot satisfy them.

## Core Rule

Do not design the interface as a collection of cards.

Design it as a working surface with structure, hierarchy, rhythm, useful density, and visual tension. If a card is used, it must behave like an independent object with a clear functional reason. Otherwise replace it with bands, rails, annotated margins, tables, rows, panels, layers, or section systems.

## Required Pre-Design Pass

Before proposing UI or code, decide internally:

1. What supplied Guardian constraints, explicit product requirements, or inferred functional needs are immutable?
2. If an Inquisitor brief exists, which findings are accepted, adapted, deferred, or not applicable?
3. What surface is this screen: dossier, map, logbook, control table, workshop, archive, or report?
4. What is the user's primary action?
5. What information must stay visible at all times?
6. What information belongs in a margin, rail, status band, or inspection panel?
7. What generic AI/SaaS pattern are you tempted to use?
8. What working-surface pattern replaces it?
9. Where is the screen's visual tension: density, asymmetry, contrast, sequence, timeline, comparison, or status?
10. What would make this interface recognizable without a logo?

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
- Reuse established components, tokens, and interaction mechanics unless evidence or a supplied critique identifies them as the source of the problem. Explain any deliberate departure.

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

1. UX and product constraints honored, whether supplied or inferred.
2. Inquisitor findings accepted, adapted, or deferred with concise reasons, only when a brief exists.
3. Selected visual surface and layout decision.
4. Visual rules and main components applied.
5. Replacements made to avoid generic cards or other AI/SaaS patterns.
6. Clean, accessible, maintainable frontend code when implementation is requested.
7. Visual and interaction evidence gathered for verification or an optional Guardian final gate.
8. A short note explaining why the UI avoids generic AI aesthetics.

Keep the explanation brief when the user primarily asked for code; the interface itself should carry the design argument.

## Final Checklist

Before delivery, verify:

- Any supplied Guardian UX contract remains satisfied; otherwise the inferred functional baseline remains intact.
- When an Inquisitor brief exists, every finding is accepted, adapted, deferred with reason, or explicitly not applicable.
- The screen does not read as a generic SaaS template.
- Cards are absent or functionally justified.
- Bento grids, glassmorphism, decorative gradients, and filler icons are avoided.
- Margins, rails, bands, tables, or layers do real work.
- The chosen surface metaphor is visible in the layout.
- Hierarchy works without decorative clutter.
- States have a recognizable system language.
- The design would still be identifiable without a logo.
- Accessibility and responsiveness remain intact.
