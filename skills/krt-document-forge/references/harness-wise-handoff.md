# Harness Wise Handoff

After conversion, hand the Markdown artifacts to `krt-harness-wise` as source evidence.

Use this handoff shape:

```text
Use krt-harness-wise to create or update a coding harness from:
- docs/harnesses/sources/<converted-file>.md

Objective:
<user's implementation or planning goal>

Notes:
- Source was converted by krt-document-forge.
- Check conversion warnings before relying on any missing sections, tables, or image-only pages.
- Prefer handoff after `krt-document-forge --check` passes for the converted batch.
- Preserve linked image assets when moving or reviewing the Markdown files.
```

Do not ask Harness Wise to re-convert the original binary documents. Its job is to synthesize compact implementation context from the Markdown evidence and project initialization files.
