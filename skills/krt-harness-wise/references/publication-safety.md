# Publication Safety

Load before writing a versionable harness from client, commercial, internal planning, or converted document evidence.

## Default Publication Policy

Keep only minimum operational context in git. Versionable harnesses and summaries must help an implementation agent work safely without exposing unnecessary business, client, or personal detail.

Use this artifact policy:

| Artifact | Default |
|---|---|
| `docs/raw/` | local only, ignored |
| `docs/harnesses/sources/` | local only, ignored |
| `docs/harnesses/images/` | local only, ignored |
| `docs/harnesses/staging/` | local-only sanitized candidate |
| `docs/harnesses/provenance/` | local-only sidecars, manifests, hashes, warnings |
| `docs/harnesses/summaries/` | versionable only after deterministic promotion |
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

## Inspect, Classify, Redact, Promote

1. Inspect ignored source evidence and extraction warnings locally.
2. Classify secrets, personal data, commercial values, private URLs, source paths, hashes, and uncertainty.
3. Redact a candidate under `docs/harnesses/staging/` and record private traceability under `docs/harnesses/provenance/`.
4. Check it:

   ```bash
   rtk python3 <harness-wise-skill-dir>/scripts/check_evidence.py docs/harnesses/staging/<base>.md --sidecar docs/harnesses/provenance/<base>.json
   ```

5. Record a classification (`public`, `internal`, `confidential`, `restricted`, or `unknown`), `redaction_status: completed`, and a non-empty publication rationale. Add a non-empty sidecar decision for every warning. Never accept warnings silently.
6. Promote it:

   ```bash
   rtk python3 <harness-wise-skill-dir>/scripts/promote_evidence.py docs/harnesses/staging/<base>.md --sidecar docs/harnesses/provenance/<base>.json
   ```

Use `--overwrite` only with explicit approval. Promotion accepts only a random UUID4 `provenance_id` shared by the staged summary and sidecar, restricts the destination to `docs/harnesses/summaries/`, copies only the summary, writes atomically, and rescans the destination.

## Versionable Harness Safety Checklist

Before marking a harness `ready`, check for:

- personal names beyond generic roles;
- emails, phone numbers, DNI/passport/national IDs, IBANs, account numbers;
- exact budgets, prices, or commercial quantities;
- private URLs, internal domains, IPs, tokens, credentials, and secret-like assignments;
- source document hashes or any raw/source/staging/provenance paths;
- client-specific risks that are organizational rather than implementation-relevant.

If any item remains, either sanitize it or mark the harness `review`/`blocked` with a clear reason.
