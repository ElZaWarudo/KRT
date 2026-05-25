# Publication Safety

Load before writing a versionable harness from client, commercial, internal planning, or converted document evidence.

## Default Publication Policy

Keep only minimum operational context in git. Versionable harnesses and summaries must help an implementation agent work safely without exposing unnecessary business, client, or personal detail.

Use this artifact policy:

| Artifact | Default |
|---|---|
| `docs/raw/` | local only, ignored |
| `docs/harnesses/sources/` | local only, ignored |
| `docs/harnesses/images/` | local only, ignored unless explicitly sanitized |
| `docs/harnesses/summaries/` | versionable only after sanitation |
| `docs/harnesses/*.md` | versionable canonical harnesses only after sanitation |
| manifests and conversion hashes | local only unless explicitly scrubbed |

Do not put source document hashes in versioned summaries or harnesses. Treat hashes of proprietary/client documents as potentially sensitive metadata.

## Sanitation Rules

Before writing or updating a versionable harness:

- Replace personal names with roles, such as `Project Owner`, `Technical Lead`, or `Client IT Contact`.
- Remove personal emails, phone numbers, national IDs, IBANs, and exact personal identifiers.
- Remove exact budgets, prices, margins, invoice details, and commercial dates unless implementation truly depends on them.
- Remove named RACI/escalation paths; keep role-level responsibility only.
- Generalize internal organizational risks; keep only technical risks and delivery constraints needed by the agent.
- Remove private URLs, internal endpoints, tenant IDs, and customer-specific environment names unless they are required for implementation and already public in the repo.
- Prefer references to sanitized summaries over generated source Markdown.

If a detail is needed but sensitive, describe the technical implication without the sensitive value.

## Source And Summary Handling

- Prefer `docs/harnesses/summaries/*.md` as `Read First` evidence.
- Treat `docs/harnesses/sources/*.md` as `Inspect If Needed` and local-only fallback evidence.
- Read generated source Markdown only when the summary marks uncertainty, a required detail is missing, or exact wording is needed.
- If using a source-only fact, copy only the sanitized implication into the harness.

## Versionable Harness Safety Checklist

Before marking a harness `ready`, check for:

- personal names beyond generic roles;
- emails, phone numbers, DNI/passport/national IDs, IBANs, account numbers;
- exact budgets, prices, or commercial quantities;
- private URLs, internal domains, IPs, tokens, credentials, and secret-like assignments;
- source document hashes or direct raw/source paths promoted as normal read targets;
- client-specific risks that are organizational rather than implementation-relevant.

If any item remains, either sanitize it or mark the harness `review`/`blocked` with a clear reason.
