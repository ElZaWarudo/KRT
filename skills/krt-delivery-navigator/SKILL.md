---
name: krt-delivery-navigator
description: Turn requirements or existing project docs into a delivery plan, or a phased roadmap, that a team can act on. Use when the user asks how to organize, phase, sequence or schedule the work, wants a delivery plan, backlog, milestones, sprints, release slices or a roadmap, or wants a readiness check before planning; also when krt-compound-master needs a roadmap or readiness report for a documented initiative. Works best from a validated requirements packet (krt-requirements-weaver) or project specs under docs/. Not for clarifying fuzzy requirements (krt-requirements-weaver) or executing work. Runtime aliases may expose this as krt:delivery-navigator.
---

# Delivery Navigator

Turn what the project already knows into a plan someone can execute and
check. A plan is only as trustworthy as its link to its sources. Every item
should say where it came from, and nothing should look more certain than the
evidence behind it.

Load `references/safety.md` first. This skill plans; it does not implement.

## What makes a plan credible

**Trace every item to a source.** Each workstream, slice, backlog item or
roadmap item cites the requirement IDs (FR-x, NFR-x, AC-x) or the doc path
it delivers. Work that traces to nothing is either scope creep or a risk
mitigation; label it as such. Out-of-scope items appear only as exclusions.

**Don't resolve open questions inside the plan.** If the source lists an
open question, carry it forward as a decision with an owner and a deadline
in the sequence ("decide before slice 2"). If work has to start anyway, make
it conditional on the answer. Quietly choosing a default and building it in
means you decided for the stakeholder.

**Dates are forecasts.** Prefer relative sequencing. When the user wants
dates or sprint calendars, give them, and label them in the plan itself as
a forecast that depends on named assumptions. A caveat in a closing line is
not enough. Separate an externally imposed deadline from what the evidence
supports, and propose a scope cut when the two diverge.

**Every risk gets an action.** Each named risk has a mitigation, contingency
or monitoring trigger. Undecided dependencies (a vendor not yet chosen,
docs still pending) are sequencing risks: schedule the decision early and
isolate the work behind an interface or stub so it doesn't block.

**Verification lives inside each slice.** Each slice states how its
acceptance criteria will be checked. That includes non-functional checks
such as performance or security, which do not all wait for a final
hardening phase.

**Ownership matches the stated team.** Assign work by role (or person, if
given) within the stated capacity. If the scope doesn't fit the team, say so.

## Choosing the shape

Use an ordered backlog with release slices when scope may move. Use phases
with milestones when sequencing is externally fixed. Use phases with slices
inside when both apply. Order work by dependency first, then by risk
reduction and value, and say why the first slice comes first.

When there is no validated requirements source, as with a one-line idea,
don't invent a full plan as if one existed. Name the missing inputs that
would change the plan most (team, platform, scope boundary, deadline,
acceptance criteria). Then either give a clearly assumption-labelled draft
or recommend `krt-requirements-weaver` first, depending on what the user
asked for.

## Roadmaps from existing docs

When asked for a roadmap or readiness check across a project's docs:

- Read the specs, plans, ADRs and repo instructions that exist. Cite the
  source of each roadmap item, with a confidence level when the source is weak.
- Order items by hard dependencies (what cannot be built before what), and
  group independent items into parallel waves.
- A draft spec, an undecided approach or pending vendor input is a readiness
  gap or decision point, not ready work. A goal with no spec stays a goal:
  don't invent its scope.
- If too much is missing to sequence the work without inventing product
  behaviour, produce a readiness report instead of a roadmap: what's missing,
  why it blocks, and the exact next prompt to fill the gap.

When the user or `krt-compound-master` wants the roadmap as a file, follow
`references/roadmap-artifacts.md`. It covers the paths, item fields and the
`artifact_kind` closeout that Compound Master consumes. Write exactly one
primary artifact per run: a roadmap or a readiness report, never both.

## Output

Answer in chat unless the user asks for a file. Use repo-relative paths when
writing. Lead with the delivery approach and the first slice, then the
items, dependencies, risks and open decisions. Skip sections the input can't
support. Don't pad them.
