---
name: krt-delivery-navigator
description: Turn validated software requirements into a practical project delivery plan. Use when a user has a requirements packet, especially one produced by krt-requirements-weaver, and needs project planning artifacts such as scope framing, major tasks, prioritized backlog, milestones or iteration slices, schedule outline, team responsibilities, technology choices, dependencies, risks, and partial deliveries. Also use when the user asks how to build the system, how to organize the work, how to phase delivery, or how to plan the backlog before implementation. Runtime aliases may expose this as krt:delivery-navigator.
---

# Delivery Navigator

Turn a validated requirements packet into a delivery plan that a team can execute and inspect.

Build from the output of `krt-requirements-weaver` whenever it exists. Do not re-invent product behavior during planning, and do not implement code while using this skill.

## Load References

- Load `references/planning-workflow.md` before structuring the plan or deciding whether planning is ready.
- Load `references/plan-quality-checklist.md` when reviewing a delivery plan, prioritizing work, or checking whether the plan is credible.
- Load `references/source-literature.md` when the user asks what the method is based on, wants citations, or challenges the planning model.

## Workflow

1. Confirm the planning source.
   - Prefer a validated requirements packet from `krt-requirements-weaver`.
   - If the source is only a rough brief or ambiguous request, recommend `krt-requirements-weaver` first.
   - If the user still wants to continue, proceed with explicit assumptions and lower confidence.

2. Assess planning readiness.
   - Check whether the source makes these items visible:
     - problem and goal
     - stakeholders or actors
     - scope in and scope out
     - functional requirements
     - non-functional requirements or explicit constraints
     - assumptions and open questions
     - acceptance criteria or another testable finish line
   - If key planning inputs are missing, stop and produce a planning-readiness note instead of inventing the plan.

3. Choose the planning shape.
   - Use **agile backlog** when iterative delivery, changing scope, or incremental value matters most.
   - Use **phase-based plan** when the project is small, externally fixed, or better understood as sequential stages.
   - Use **hybrid plan** when the project needs clear milestones but should still deliver incrementally inside each phase.
   - State why the chosen shape fits the requirements and constraints.

4. Build the plan.
   - Carry forward the scope boundary, assumptions, and constraints from the requirements packet.
   - Break the work into major deliverables or workstreams before listing fine-grained tasks.
   - Order work using value, dependency, risk reduction, and learning value.
   - Define:
     - project scope and non-goals
     - major tasks or work packages
     - priorities
     - schedule outline, milestones, or sprint/release slices
     - responsible roles or team shape
     - technology choices or technology decision constraints
     - dependencies
     - risks and mitigations
     - partial deliveries or increments
   - When using backlog form, derive backlog items from requirements instead of freehand ideation.
   - When dates or durations are unknown, use relative sequencing rather than fake precision.

5. Validate the plan.
   - Confirm that each major task traces back to a requirement, constraint, or risk.
   - Check that the plan is feasible for the named team and delivery model.
   - Surface blockers, unresolved technology decisions, and assumption-heavy areas.
   - Ask one focused question at a time only when a missing answer changes plan safety or sequencing materially.

6. Capture the deliverable.
   - Default to one of these primary outputs:
     - `delivery-plan`
     - `planning-readiness-note`
   - Keep file paths repo-relative if writing into the repository.

## Output Rules

- Treat the requirements packet as the source of truth for what is being built.
- Do not silently widen scope during planning.
- Do not confuse a backlog with a random task list; backlog items should reflect deliverable value or requirement slices.
- Do not present speculative dates as commitments.
- Make ownership visible even if only role-level ownership is known.
- Keep risks actionable: each meaningful risk should have at least one mitigation or monitoring action.
- When the user asks only for analysis, return findings and a proposed planning shape without writing files.

## Final Output

Return one of these shapes:

```text
artifact_kind: delivery-plan | planning-readiness-note
planning_status: ready-to-plan | planned | blocked

Planning source:
- ...

Delivery approach:
- agile backlog | phase-based | hybrid

Key plan elements:
- ...

Risks / blockers:
- ...

Next step:
- ...
```
