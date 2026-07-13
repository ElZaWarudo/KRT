---
name: krt-interface-warden
description: "Independently design or implement distinctive, functional frontend interfaces using Editorial Product UI: content-led hierarchy, working-surface metaphors, deliberate layout archetypes, restrained containers, purposeful typography, and accessible code. Use for visual direction, redesign, polish, or implementation when a screen risks generic AI/SaaS cards, dashboard templates, unnecessary tables, weak hierarchy, or decorative chrome; honor a krt-frontend-ux-guardian contract and consume a krt-interface-inquisitor brief when supplied, without requiring either companion."
---

# krt-interface-warden

Use this skill when designing, implementing, or reviewing a frontend interface that must feel specific, functional, and intentionally designed instead of generic, AI-generated, or template-like.

The mission is not to make screens "pretty." Compose a complete product surface around real content and work: a dossier, map, logbook, control table, workshop, archive, or report that helps people inspect, decide, operate, compare, validate, or navigate.

Use **Editorial Product UI** as the default design stance: typographic hierarchy, open space, rigorous alignment, purposeful density, and very few artificial surfaces. Identity should come from the content and composition before decoration.

## Collaboration Role

Warden operates independently and owns the visual system and implementation decisions. It must infer the user task, constraints, and visual direction itself when no companion artifact exists.

When the companion skills are also active:

- Guardian supplies the functional UX contract and owns its verification gate.
- Inquisitor supplies evidence-based critique and prioritized change inputs.
- Warden records the rationale for accepted, adapted, or deferred findings.

Consume a Guardian UX contract or Inquisitor critique brief only when supplied. Otherwise derive the same minimum product constraints from the request and existing interface. Preserve the primary task, completion signal, persistent context, required states, accessibility/responsive constraints, and established mechanics. Visual distinctiveness must not reduce operability.

For critique-and-fix work with Inquisitor active, implement only after its brief is complete and record which findings were accepted, adapted, or deferred. Without Inquisitor, perform Warden's own pre-design diagnosis and continue. Do not reopen supplied product constraints; surface a conflict when the requested visual change cannot satisfy them.

## Core Rules

Do not design the interface as a collection of cards or start by selecting components.

Build hierarchy in this order:

**Typography -> space -> alignment -> proportion -> dividers -> subtle background shifts -> borders -> elevation.**

Use a closed surface only when those earlier tools cannot express a real semantic boundary. If a card is used, it must behave like an independent object with a clear functional reason. Otherwise replace it with sections, bands, rails, annotated margins, rich rows, definition lists, tables when comparison requires them, or functional layers.

## Required Composition Brief

Before choosing components or writing JSX/CSS, record a compact composition brief. Do not skip it for autonomous implementation and do not turn it into an approval checkpoint unless the user asks.

1. What supplied Guardian constraints, explicit product requirements, or inferred functional needs are immutable?
2. If an Inquisitor brief exists, which findings are accepted, adapted, deferred, or not applicable?
3. What is the user's primary task and completion signal?
4. What single information element must dominate visually?
5. What working-surface metaphor fits the domain?
6. Which layout archetype fits the task: editorial page, master-detail, canvas with inspector, staged flow, document with contextual rail, operational list, narrative dashboard, split view, or timeline/feed?
7. How do main content, navigation, and contextual information relate?
8. Which elements need a closed surface? For each one, state the semantic reason.
9. Does the user need to compare columns, sort dense records, or perform bulk actions? If not, do not default to a table.
10. What remains visible, what moves behind disclosure, and what becomes a separate view on narrow screens?
11. What generic AI/SaaS pattern are you avoiding, and what content-led structure replaces it?
12. What makes the composition recognizable without a logo?

If an answer is unclear, infer the most useful composition from the data and workflow. Do not block unless the missing choice would materially change the product behavior.

## Surface Metaphors

- **Dossier**: reviewing one entity, case, user, client, asset, claim, or record.
- **Map**: navigating relationships, dependencies, flows, ownership, or topology.
- **Logbook**: reading events, history, activity, changes, incidents, or audit trails.
- **Control table**: monitoring operations, queues, workloads, states, or live metrics.
- **Workshop**: creating, editing, composing, transforming, or configuring.
- **Archive**: searching, filtering, comparing, and retrieving many records.
- **Report**: explaining findings, recommendations, conclusions, or evidence.

The layout must follow the selected metaphor.

## Layout Archetypes

Select one primary archetype before implementation; combine two only when each owns a distinct region.

- **Editorial page**: executive summary, report, or overview with one dominant fact and a contextual rail.
- **Master-detail**: entities that must be scanned while one remains open for inspection.
- **Canvas with inspector**: builders, agents, diagrams, automations, and configurators.
- **Staged flow**: onboarding, creation, review, and other consequential multi-step work.
- **Document with contextual rail**: readable evidence, evaluations, agent output, or documentation with annotations.
- **Operational list**: inboxes, tasks, incidents, queues, and activity organized through rows and separators.
- **Narrative dashboard**: a metric story led by one measure, supporting measures, visualization, and interpretation.
- **Split view**: two directly related work zones that must remain visible together.
- **Timeline or feed**: sequence, provenance, activity, and history where order matters more than column comparison.

Do not default to `sidebar + header + KPI card grid + table`. Treat a persistent sidebar as navigation infrastructure, not the page's design concept.

## Design Directives

- Prefer bands, rails, annotated margins, expressive tables, status marks, layers, legends, and connection lines over standalone cards.
- Keep the base background visible across roughly 60-70% of the viewport when the product context permits.
- Allow at most one dominant contained surface per viewport and two visible elevation levels.
- Never nest cards. Do not combine border, contrasting background, and shadow on the same container without an exceptional functional reason.
- Use color as signage: action, state, risk, grouping, navigation, priority. Do not use decorative gradients unless they encode real information.
- Use typography as the primary identity: readable sans for work, optional serif for selected editorial titles or protagonist figures, and mono or semi-mono for metadata, codes, dates, statuses, and technical values.
- Give one metric narrative priority. Place supporting measures in aligned rows or bands instead of identical KPI cards.
- Use tables only for column comparison, sorting/filtering dense records, pattern recognition, or bulk action. Otherwise prefer rich lists, master-detail, timelines, grouped states, definition lists, or charts with detail on demand.
- Make states part of the identity: empty, loading, error, blocked, success, partial data, too much data, review, and conflict states should match the surface metaphor.
- Use depth through functional layers: main panel, inspector, drawer, review overlay, timeline, comparison view. Do not rely on soft shadows for personality.
- On narrow screens, reprioritize the task and move secondary context into disclosure, panels, or separate views. Do not merely stack every desktop container or turn every row into a card.
- Keep accessibility non-negotiable: contrast, keyboard navigation, visible focus, semantic structure, responsive behavior, tables that remain understandable, and signals that do not depend on color alone.
- Reuse established components, tokens, and interaction mechanics unless evidence or a supplied critique identifies them as the source of the problem. Explain any deliberate departure.

For every material design, redesign, or implementation, read `references/visual-grammar.md` before completing the composition brief. It contains the surface budget, component decisions, typography/tokens, responsive transformations, and final self-critique.

## Default Replacements

- Metric card -> protagonist figure with an aligned supporting band, margin counter, or dense summary row.
- Feature card -> editorial block with a rule line, number, concrete example, or workflow step.
- User card -> compact dossier record with metadata and state marks.
- Project card -> rich row with status, owner, date, risk, and next action.
- Dashboard card -> editorial section, narrative data view, or integrated operational region.
- Pricing card -> comparison table or contract-like plan sheet.
- News card -> logbook entry.
- Task card -> operational line with priority, state, and owner.
- Product card -> technical sheet or inventory record.

## Delivery Requirements

When generating or materially changing an interface, include:

1. UX and product constraints honored, whether supplied or inferred.
2. Inquisitor findings accepted, adapted, or deferred with concise reasons, only when a brief exists.
3. Composition brief: task, dominant information, surface metaphor, layout archetype, region relationship, and responsive transformation.
4. Surface and table ledger: each card/table retained and its semantic reason.
5. Visual rules and main components applied.
6. Replacements made to avoid generic cards or other AI/SaaS patterns.
7. Clean, accessible, maintainable frontend code when implementation is requested.
8. Visual and interaction evidence gathered for verification or an optional Guardian final gate.
9. A short note explaining why the UI avoids generic AI aesthetics.

Keep the explanation brief when the user primarily asked for code; the interface itself should carry the design argument.

## Final Checklist

Before delivery, verify:

- Any supplied Guardian UX contract remains satisfied; otherwise the inferred functional baseline remains intact.
- When an Inquisitor brief exists, every finding is accepted, adapted, deferred with reason, or explicitly not applicable.
- The screen does not read as a generic SaaS template.
- Cards are absent or functionally justified.
- At least one unnecessary container was considered for removal; no retained surface exists merely to group related content.
- The base surface remains visually predominant and elevation is reserved for content that truly floats.
- Any table exists because users compare columns, sort/filter dense data, recognize patterns, or act in bulk.
- One task, action, or information element clearly dominates instead of every module receiving equal weight.
- Bento grids, glassmorphism, decorative gradients, and filler icons are avoided.
- Margins, rails, bands, tables, or layers do real work.
- The chosen surface metaphor and layout archetype are visible in the composition.
- Hierarchy works without decorative clutter.
- The hierarchy still works when borders, icons, and accent color are mentally removed.
- States have a recognizable system language.
- The design would still be identifiable without a logo.
- The narrow-screen layout preserves the primary task through reprioritization, not mechanical stacking.
- Accessibility and responsiveness remain intact.
