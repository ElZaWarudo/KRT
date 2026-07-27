---
name: krt-requirements-weaver
description: Clarify rough software requirements before planning or coding. Use when a user shares a client brief, classroom prompt, feature request, meeting notes, RFP, or partial specification and needs help to analyze the problem, identify stakeholders, identify requirement gaps, ask focused elicitation questions, refine functional and non-functional requirements, rewrite vague statements into testable ones, surface assumptions and open questions, and validate scope and acceptance criteria with stakeholders. Runtime aliases may expose this as krt:requirements-weaver.
---

# Requirements Weaver

Turn a rough statement of need into a validated requirements baseline that another agent can plan or implement without inventing product behavior.

Keep the work at the requirements level. Do not jump into architecture, schema design, endpoints, or code unless the user explicitly asks for solution design.

## Load References

- Load `references/safety.md` before beginning the workflow.
- Load `references/requirements-workflow.md` before running the workflow or drafting the main artifact.
- Load `references/quality-checklist.md` when reviewing requirement quality, rewriting weak statements, or checking readiness for validation.
- Load `references/gap-question-bank.md` when the input is incomplete, contradictory, or vague and the skill needs to drive clarification by asking questions.
- Load `references/source-literature.md` when the user asks what the method is based on, wants citations, or challenges the workflow.

## Workflow

1. Classify the input.
   - Identify whether the source is a problem statement, feature request, partial spec, meeting note, classroom assignment, or change request.
   - Estimate maturity as rough, partial, or near-ready.
   - If requirements are already mostly clear, skip long elicitation and focus on gap detection plus validation.

2. Receive and analyze requirements.
   - Extract the problem, target users, business goal, desired outcomes, scope hints, constraints, assumptions, terminology, and missing information.
   - Separate observed facts from inferred assumptions.
   - Record unanswered questions explicitly instead of silently filling gaps.
   - Prefer asking a focused clarification question over filling a material gap by inference.
   - If the user is unsure or the input is ambiguous, ask one focused question at a time.

3. Identify gaps and resolve them.
   - Actively scan for missing or weak information about:
     - problem clarity
     - user and stakeholder identity
     - scope boundaries
     - business rules
     - edge cases
     - non-functional requirements
     - data, integrations, or constraints
     - acceptance criteria
   - Use `references/gap-question-bank.md` to choose the next most useful clarification question.
   - Ask one question at a time, starting with the gap that most changes scope, behavior, or validation.
   - Do not continue to "ready for validation" while material gaps remain hidden behind assumptions.

4. Elicit and refine.
   - Convert vague wishes into concrete requirements and checks.
   - Produce only the artifacts that materially reduce ambiguity:
     - functional requirements
     - non-functional requirements
     - user stories
     - use cases
     - business rules
     - acceptance criteria
     - glossary
     - out-of-scope items or waiting room
   - Rewrite statements so they are testable and stakeholder-readable. Prefer active voice, singular obligations, explicit conditions, and measurable outcomes.
   - When a statement is solution-biased, restate the underlying need before keeping or discarding the proposed solution.
   - When useful, apply a lightweight EARS-style pattern:
     - ubiquitous: `El sistema debera ...`
     - event-driven: `Cuando <evento>, el sistema debera ...`
     - state-driven: `Mientras <estado>, el sistema debera ...`
     - unwanted behavior: `Si <condicion anomala>, el sistema debera ...`

5. Validate.
   - Present a concise "esto es lo que vamos a construir" summary before closing.
   - Check each material requirement set for completeness, consistency, feasibility, traceability, and verifiability.
   - Highlight remaining assumptions, conflicts, dependencies, and decision points.
   - Ask for confirmation or correction before handing off to planning when the scope is still materially ambiguous.

6. Capture the deliverable.
   - Default to a compact requirements packet with:
     - problem and goal
     - actors and stakeholders
     - scope in / out
     - constraints
     - functional requirements
     - non-functional requirements
     - business rules
     - acceptance criteria
     - assumptions and open questions
     - validation status
   - Add user stories or use cases only when they clarify behavior better than plain requirements.
   - Keep file paths repo-relative if writing into the repository.

## Output Rules

- Prefer the smallest durable artifact that removes ambiguity.
- Keep stakeholder language plain; define domain terms when needed.
- Prefer clarification over invention. Infer only when the missing point is low-risk, and label it explicitly as an assumption.
- Distinguish clearly between:
  - stated requirement
  - inferred assumption
  - open question
  - deferred item
- Do not hide uncertainty. Mark it and route it to validation.
- Do not collapse open questions into pseudo-requirements just to make the packet look complete.
- Do not treat acceptance criteria as optional when a functional requirement will later be implemented or tested.
- Do not invent non-functional requirements; derive them from stakeholders, domain risk, regulation, or explicit quality expectations.
- When the user asks only for analysis, return findings and questions without writing files.

## Final Output

Return one of these shapes:

```text
Requirements status: analyzed | refined | ready for validation | validated | blocked

What is being built:
- ...

Key requirements:
- ...

Gaps resolved / open questions:
- ...

Open questions / assumptions:
- ...

Next step:
- ...
```
