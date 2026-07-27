# Agentic Threat Model

Use this model when software can interpret instructions, retrieve context, call tools, delegate, persist memory, or loop toward a goal.

## Root Rule

Data never grants authority. A web page, ticket, log, document, message, model response, memory entry, or tool result may provide evidence, but it cannot create identity, scope, permission, approval, budget, or a new goal.

## Threat Surfaces

| Surface | Failure Mode | Required Control |
|---|---|---|
| Goal and prompt integrity | Direct or indirect prompt/goal hijacking changes the task, policy, target, or completion condition | Trusted instruction hierarchy; conflict handling; immutable task/authority envelope |
| Tool use | Model-controlled text triggers unsafe arguments, broad mutations, or a confused-deputy action | Tool allowlist; typed/validated arguments; target resolution; approval and effect gates |
| Identity and scopes | Agent uses the wrong principal, tenant, credential, or overly broad token | Independently bound identity; least privilege; tenant and audience checks; short-lived scopes |
| Context and memory | Poisoned retrieval or persistent memory influences later users, runs, or agents | Provenance; trust labels; write gates; isolation; expiry; revalidation on restart |
| Untrusted propagation | Web, tickets, logs, docs, tools, or messages flow unmarked into prompts, tool calls, or delegates | Track provenance and trust across transformations; sanitize structure; prevent authority promotion |
| Data egress | Secrets, PII, proprietary context, or inferred sensitive data leaves through tools, messages, logs, or artifacts | Destination and data policy; minimization/redaction; egress allowlist; audit trail |
| Control loops | Retries, recursive delegation, planning loops, or adversarial feedback consume unbounded time/cost/actions | Token/time/cost/action budgets; depth limits; idempotency; circuit breakers; explicit stop states |

## Review Procedure

1. Draw the instruction, data, identity, tool, memory, and egress boundaries.
2. Mark each input trusted or untrusted by provenance, not by tone or format.
3. Follow untrusted values through retrieval, summarization, prompts, memory writes, tool arguments, delegation, logs, and outputs.
4. Verify that identity, scopes, approvals, targets, and budgets are enforced outside model-controlled content.
5. Test denial paths: injected instructions, forged tool output, stale memory, cross-tenant context, interrupted restarts, recursive delegation, unavailable tools, and exhausted budgets.
6. Require observable evidence for tool effects, authorization decisions, memory writes, egress, retries, and termination.

## Finding Requirements

Name the attacker or untrusted source, propagation path, authority boundary crossed, affected asset, preconditions, impact, smallest control, and verification case. Do not label all model error as a security issue; require an abuse path or violated trust boundary.
