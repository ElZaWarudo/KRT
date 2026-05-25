# Conversion Policy

Use these rules when converting PDFs and DOCX files into harness-ready Markdown.

## Artifact Location

Default output path:

```text
docs/harnesses/sources/<source-stem>.md
```

Use a different directory when the user provides one or the project already has a clearer harness-source location.

## Markdown Shape

Generated files should start with frontmatter-like provenance:

```yaml
---
source_path: path/to/source.pdf
source_type: pdf
converted_at: 2026-05-25T10:30:00+00:00
converter: krt-document-forge
conversion_method: pdftotext
---
```

After provenance, use:

- `# <document title or filename>` as the top heading.
- Source headings when present.
- Plain paragraphs for body text.
- Markdown tables for DOCX tables when structure is detectable.
- Page separators for PDFs when the extraction method provides page boundaries.
- Linked image references when `--extract-images` is used.

## Image Assets

Do not embed images as base64 in Markdown. Store them as normal files so they can be reviewed, diffed by path, and carried into a harness handoff.

Default layout:

```text
docs/harnesses/
├── sources/
│   └── brief.md
└── images/
    └── brief/
        ├── brief-image-001.png
        └── brief-page-003-image-002.jpeg
```

Use relative Markdown links from the generated `.md` file:

```markdown
![brief image 001](../images/brief/brief-image-001.png)
```

For DOCX files, extract embedded `word/media/*` images and place links near the paragraph or table where the image relationship appears.

For PDF files, extract embedded image objects when PyMuPDF is available. Name PDF images with page numbers when possible. Do not OCR image content.

Use `--clean-assets` only during regeneration. It deletes the generated asset folder for each source document before extracting new images:

```text
docs/harnesses/images/<source-stem>/
```

It does not delete source documents or unrelated image folders.

## Manifest And Check Mode

Use `--manifest <path>` to write a reproducibility manifest. The manifest is a versioned JSON object with:

- converter identity and generation timestamp.
- output and images directories.
- summary directory and summary hashes when summaries exist.
- source path and source SHA-256 per file.
- generated Markdown path and SHA-256 per file.
- conversion status, method, and message.
- extracted asset paths and SHA-256 hashes.

Use `--check` to validate an existing conversion without rewriting artifacts. Check mode validates:

- expected Markdown output exists and is non-empty.
- Markdown image links point to existing files.
- source, output, and asset hashes match the manifest when one is supplied.

Check mode accepts both the current object manifest and the earlier list-shaped summary for backward compatibility.

## Quality Rules

- Treat empty extraction as a failed conversion unless the user explicitly accepts an empty shell artifact.
- Treat image-only PDFs as documents with no extractable text. With `--extract-images`, preserve embedded images as linked assets; without it, report the limitation.
- Preserve ambiguous source wording. Summaries, normalization, and conflict resolution belong in `krt-harness-wise`.
- If layout is complex, prefer readable Markdown over pixel-perfect formatting.
- Keep tables compact. If a table is too irregular for Markdown, preserve rows as plain text blocks and mention the limitation.

## Dependency Strategy

For PDFs, prefer installed deterministic extractors in this order:

1. `pdftotext` from Poppler.
2. Python `pypdf`.
3. Python `pdfplumber`.

Use `--install-missing` only when the user accepts local dependency installation. It creates or reuses:

```text
.krt/document-forge/venv
```

and installs optional Python packages there. It does not install system packages such as Poppler.

For PDF image extraction, use PyMuPDF when available or when installed through `--install-missing`.

For DOCX, the bundled script can extract document text, headings, basic lists, and tables with the Python standard library.
