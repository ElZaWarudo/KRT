---
name: krt-document-forge
description: Convert PDF and DOCX source documents into versionable Markdown artifacts for coding harnesses. Use when a user needs to extract project briefs, requirements, client notes, architecture documents, contracts, or other .pdf/.docx inputs into .md so krt-harness-wise or another planning skill can use them as harness evidence. Runtime aliases may expose this as krt:document-forge.
---

# Document Forge

Convert source documents into Markdown evidence that can be read, diffed, cited, and passed to `krt-harness-wise`. This skill prepares the source material; it does not diagnose or author the final coding harness unless the user explicitly asks to continue with Harness Wise afterward.

## Arguments

```text
[input file or directory]
[output-dir:<path>]
[recursive:true|false]
[overwrite:true|false]
[extract-images:true|false]
[clean-assets:true|false]
[check:true|false]
[summary-dir:<path>]
[install-missing:true|false]
[handoff:true|false]
```

Defaults:

- `output-dir:docs/harnesses/sources`
- `recursive:false`
- `overwrite:false`
- `extract-images:true` when the user wants visual evidence retained; otherwise `false`
- `clean-assets:false`
- `check:false`
- `summary-dir:docs/harnesses/summaries`
- `install-missing:false`
- `handoff:true`

## Core Rules

- Preserve provenance. Every generated Markdown file must identify the original source path, file type, conversion method, and conversion timestamp.
- Never invent text for unreadable pages, image-only PDFs, failed extraction, or corrupt documents. Report the gap and preserve embedded images when requested.
- Keep generated Markdown close to the source: headings, paragraphs, lists, and tables are useful; broad rewriting belongs in `krt-harness-wise`.
- Use summaries as the preferred agent-facing layer when they exist. Keep extracted source Markdown for audit and exceptional fallback only.
- Store extracted images as versionable assets, not base64 blobs. By default, Markdown goes under `docs/harnesses/sources/` and images go under `docs/harnesses/images/<source-stem>/`.
- Use `--clean-assets` with `--overwrite --extract-images` when regenerating a document whose embedded images may have changed; it removes only that source document's generated image folder.
- Use `--check` before Harness Wise handoff when a manifest or generated Markdown already exists.
- Do not perform OCR in this skill. Image-only content remains an image reference for a later human or vision-capable review step.
- Use the host runtime's command wrapper when the current repository requires one.
- Do not delete or overwrite source documents.
- Do not create a final harness inside this skill. If the user asks for a harness, hand off the converted Markdown paths to `krt-harness-wise`.
- Prefer deterministic scripts for conversion over ad hoc copy/paste.

## Progressive Loading

Load only what the current flow needs:

| Need | Load |
|---|---|
| Conversion quality and artifact rules | `references/conversion-policy.md` |
| Create or validate compact summaries | `references/summarization-policy.md` |
| Hand off converted files to Harness Wise | `references/harness-wise-handoff.md` |

Bundled script:

```text
scripts/convert_to_markdown.py
```

Resolve `<document-forge-skill-dir>` to the directory containing this `SKILL.md`; in installed runtimes this may not be the repository checkout.

## Workflow

1. Resolve input files. Accept `.pdf` and `.docx`; ignore unsupported files unless the user explicitly asks about them.
2. Load `references/conversion-policy.md` when conversion quality, naming, images, or table/list treatment matters.
3. Run the converter:

   ```bash
   rtk python3 <document-forge-skill-dir>/scripts/convert_to_markdown.py <inputs> --output-dir docs/harnesses/sources
   ```

   Add `--recursive` for directory trees, `--extract-images` to preserve embedded images as linked assets, `--install-missing` to install optional Python extractors into `.krt/document-forge/venv`, `--manifest docs/harnesses/sources/manifest.json` for reproducibility, and `--overwrite --clean-assets` only when the user approved regeneration.
4. Inspect the script summary. If any file failed, report the exact source and reason.
5. When compact context is useful, load `references/summarization-policy.md` and write `docs/harnesses/summaries/<base>.md` from the generated source Markdown. Do not delete or replace the source Markdown.
6. Run `--check` when a manifest is available or before handing off a converted batch. The check validates summaries when they exist, but conversion without summaries remains valid:

   ```bash
   rtk python3 <document-forge-skill-dir>/scripts/convert_to_markdown.py <inputs> --output-dir docs/harnesses/sources --summary-dir docs/harnesses/summaries --manifest docs/harnesses/sources/manifest.json --check
   ```

7. Read a small sample of each generated Markdown file when feasible to verify the output is not empty or obviously garbled. If images were extracted, verify the linked asset paths exist.
8. When `handoff:true`, load `references/harness-wise-handoff.md` and summarize how `krt-harness-wise` should consume summaries first and sources only as fallback evidence.

## Output Discipline

For completed conversions, report:

- Generated Markdown path(s).
- Summary Markdown path(s), if any, as preferred handoff inputs.
- Source document path(s).
- Conversion method(s).
- Manifest path and check result, when used.
- Extracted image asset path(s), if any.
- Failures, skipped files, or manual follow-up.
- Harness Wise handoff note when applicable.

If no readable text can be extracted, lead with that blocker and do not claim the document was converted.
