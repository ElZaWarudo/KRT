# Harness Wise Handoff

After conversion, hand summaries to `krt-harness-wise` as the preferred evidence. Keep generated source Markdown as auditable fallback evidence.

Use this handoff shape:

```text
Use krt-harness-wise to create or update a coding harness from:
- Read First: docs/harnesses/summaries/<converted-file>.md
- Inspect If Needed: docs/harnesses/sources/<converted-file>.md

Objective:
<user's implementation or planning goal>

Notes:
- Source was converted by krt-document-forge.
- Prefer the summary. Open the source only if the summary marks uncertainty, a required detail is missing, or direct wording is needed.
- Check conversion warnings before relying on any missing sections, tables, or image-only pages.
- Prefer handoff after `krt-document-forge --check` passes for the converted batch.
- Preserve linked image assets when moving or reviewing the Markdown files.
```

Do not ask Harness Wise to re-convert the original binary documents. Its job is to synthesize compact implementation context from summaries, fallback source Markdown, and project initialization files.
