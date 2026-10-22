# Publication Safety

Load before writing a versionable harness or summary from client,
commercial, internal planning or converted document evidence.

## Remove or generalize

- Personal names: replace with roles (`Project Owner`, `Client IT Contact`).
- Emails, phone numbers, national IDs, IBANs, account numbers.
- Budgets, prices, margins, invoice details, commercial dates, unless the
  implementation depends on them (then state the constraint, not the money).
- Named RACI or escalation paths: keep role-level responsibility only.
- Organizational risks (politics, staffing): keep only technical and delivery
  constraints.
- Private URLs, internal domains, IPs, tenant IDs, customer environment names,
  unless already public in the repo and needed.
- Tokens, keys, passwords, secret-like assignments.
- Source document hashes, manifests, and raw/source/staging/provenance paths.
  Hashes of client documents are sensitive metadata.

## Sidecar fields (`docs/harnesses/provenance/<base>.json`)

```json
{
  "provenance_id": "prov-<uuid4>",
  "classification": "public | internal | confidential | restricted | unknown",
  "redaction_status": "completed",
  "publication_rationale": "<non-empty>",
  "warnings": [],
  "warning_decisions": {"<warning-code>": "<non-empty decision>"}
}
```

The staged summary's frontmatter must carry the same `provenance_id`.
`check_evidence.py` blocks on any detector hit (emails, phones, IDs, secrets,
private URLs, hashes, private paths) and treats exact currency amounts as
warnings that need a recorded decision. `promote_evidence.py` re-runs the
check, refuses path escapes and implicit overwrites, writes atomically to
`docs/harnesses/summaries/`, and rescans the result.

## If something sensitive remains

Sanitize it, or set the harness to `review` or `blocked` with the reason.
The detectors are regexes; read the text yourself as well.
