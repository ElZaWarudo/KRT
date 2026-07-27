# Harness Wise Handoff

After conversion and redaction, hand the staged summary plus its private sidecar to `krt-harness-wise`. Generated source Markdown remains local audit evidence and is never a versionable read target.

Use this handoff shape:

```text
Use krt-harness-wise to validate and promote:
- Staged Summary: docs/harnesses/staging/<converted-file>.md
- Private Sidecar: docs/harnesses/provenance/<converted-file>.json

Objective:
<user's implementation or planning goal>

Notes:
- Source was converted by krt-document-forge.
- Run check_evidence.py before publication.
- Resolve every sidecar warning with an explicit, non-empty decision.
- Run promote_evidence.py; only its docs/harnesses/summaries/<converted-file>.md result is versionable.
- Prefer handoff after krt-document-forge --check passes.
- Never copy raw sources, images, manifests, hashes, or provenance sidecars during promotion.
```

Do not ask Harness Wise to re-convert the original binary documents.
