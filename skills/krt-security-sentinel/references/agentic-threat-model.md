# Agentic threat model

Use when software interprets instructions, retrieves context, calls tools, delegates, keeps memory, or loops toward a goal.

Root rule: data never grants authority. A ticket, page, log, document, memory entry, tool result, or model reply can be evidence; it cannot create identity, scope, permission, approval, budget, or a new goal.

| Surface | Failure | Control to look for |
|---|---|---|
| Goal and prompt integrity | Direct or indirect injection changes the task, target, policy, or completion condition | Trusted instruction hierarchy; task and authority fixed outside the prompt |
| Tools | Model text drives unsafe arguments, broad mutations, or confused-deputy calls | Allowlist; typed, validated arguments; target resolution in code; approval for effects |
| Identity and scopes | Wrong principal, tenant, or an over-broad token per tool | Identity bound outside the model; least-privilege, per-tool, short-lived credentials |
| Context and memory | Poisoned retrieval or memory steers later runs or other users | Provenance and trust labels; gated writes; isolation; expiry; revalidation on resume |
| Untrusted propagation | Untrusted text flows unmarked into prompts, tool calls, or delegates | Provenance tracked across summaries and handoffs; no promotion to instructions |
| Egress | Secrets, PII, or context leave through email, HTTP, logs, or artifacts | Destination allowlist; minimization and redaction; audit trail |
| Control loops | Retries, recursion, or adversarial feedback run unbounded | Turn, cost, time, and action budgets; depth limits; idempotency; explicit stop states |

## Review

1. Draw the instruction, data, identity, tool, memory, and egress boundaries.
2. Mark inputs trusted or untrusted by where they came from, not by tone or format.
3. Follow untrusted values through summarization, prompts, memory writes, tool arguments, delegation, and outputs.
4. Check that identity, scopes, approvals, targets, and budgets are enforced in code. Values such as "which customer" or "how much" must come from trusted records, not from the model's JSON.
5. Consider denial paths: injected instructions, forged tool output, stale memory, cross-tenant context, interrupted resume, recursive delegation, exhausted budgets.

A finding names the untrusted source, the propagation path, the boundary crossed, the asset, the smallest control, and a test case. Not every model error is a security issue; require an abuse path or a violated trust boundary.
