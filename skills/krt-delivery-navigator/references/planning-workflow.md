# Planning Workflow

Use this workflow to convert a validated requirements packet into an executable project plan.

## 1. Use Requirements As The Planning Boundary

Start from the requirements output, ideally from `krt-requirements-weaver`.

Carry forward:

- problem and goal
- stakeholders and users
- scope in
- scope out
- functional requirements
- non-functional requirements
- business rules
- acceptance criteria
- assumptions and open questions

If these elements are missing or unstable, create a planning-readiness note instead of pretending the project is ready.

## 2. Decide The Planning Shape

Choose the lightest planning structure that still makes execution manageable.

### Agile backlog

Use when:

- value can be delivered incrementally
- priorities may change
- feedback is expected during development
- estimates are uncertain and should be revised as learning happens

Typical outputs:

- ordered backlog
- release slices
- sprint or iteration candidates
- dependencies
- team ownership

### Phase-based plan

Use when:

- work is well understood
- scope or sequencing is externally constrained
- the project is small enough that explicit phases are clearer than backlog mechanics

Typical outputs:

- phases
- milestones
- deliverables per phase
- handoff points

### Hybrid plan

Use when:

- external milestones matter
- delivery should still happen in increments
- the team needs both management visibility and agile flexibility

Typical outputs:

- phases or releases as the outer frame
- backlog slices within each phase
- milestone reviews

## 3. Build The Work Structure

Plan from deliverables and workstreams first, then tasks.

Recommended order:

1. Define major workstreams or deliverables.
2. Break each workstream into work packages or backlog items.
3. Sequence by dependency, value, and risk reduction.
4. Assign ownership by role or team.
5. Define checkpoints and partial deliveries.

Use this minimum structure:

- scope summary
- workstreams or major deliverables
- ordered backlog or phased tasks
- dependencies
- responsibilities
- risks
- delivery slices or milestones

## 4. Prioritize Intentionally

Do not order work arbitrarily. Use a visible rationale:

- user value
- dependency order
- risk reduction
- learning value
- regulatory or contractual necessity

For agile forms, earlier backlog items should either deliver value directly or unlock later work safely.

## 5. Handle Schedule Carefully

Schedules in early planning are forecasts, not promises.

- Use relative order when duration confidence is low.
- Use milestones when stakeholders need visibility.
- Use iterations or release slices when incremental planning is more honest than a calendar commitment.
- Separate commitment from aspiration when the deadline is externally imposed but poorly supported.

## 6. Plan Team And Technology Explicitly

Make the team model visible:

- product or stakeholder owner
- delivery lead or project lead
- implementation roles
- QA or verification role
- external approvers when relevant

Make technology handling visible:

- confirmed technologies already constrained by the project
- technology choices still pending
- architectural or integration dependencies that affect sequencing

Do not pretend technology is "decided" when the requirements packet only implies constraints.

## 7. Risks And Partial Deliveries

Every serious plan should show:

- main delivery risks
- mitigation or contingency
- what can be delivered early for feedback, validation, or de-risking

Examples of useful partial deliveries:

- clickable prototype
- authentication slice
- reporting MVP
- integration stub
- pilot release for a small user group

## 8. Default Deliverables

### Delivery plan

Use when the source is planning-ready.

Suggested sections:

1. Planning source
2. Scope summary
3. Delivery approach
4. Major workstreams
5. Prioritized backlog or phased task list
6. Milestones or release slices
7. Team and ownership
8. Technology and dependencies
9. Risks and mitigations
10. Partial deliveries
11. Open decisions

### Planning-readiness note

Use when the source is not planning-ready.

Suggested sections:

1. Missing inputs
2. Why planning is unsafe or low-confidence
3. Exact questions to resolve
4. Recommended next prompt for `krt-requirements-weaver`

## 9. Handoff Rule

Stop at a plan that a team can review and adopt.

Do not continue into implementation unless the user explicitly asks for planning plus execution.
