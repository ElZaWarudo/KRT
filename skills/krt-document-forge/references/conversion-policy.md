# Conversion Policy

Details for `scripts/convert_to_markdown.py` output. Look up when output shape,
images, the manifest, or extractor choice matters.

## Source Markdown shape

The converter writes `docs/harnesses/sources/<base>.md` starting with private
provenance frontmatter:

```yaml
---
source_path: "docs/inbox/brief.pdf"
source_type: "pdf"
converted_at: "2026-05-25T10:30:00+00:00"
converter: "krt-document-forge"
conversion_method: "pdftotext"
---
```

Then a top heading, source headings, paragraphs, Markdown tables for DOCX tables
when the structure is detectable, page separators for PDFs when the extractor
provides them, and image links when `--extract-images` is used. This
frontmatter is private: never copy it into a staged summary.

If a table is too irregular for Markdown, keep rows as plain text and mention
the limitation. Prefer readable Markdown over pixel-faithful layout.

## Images

Images are files, never base64, linked relatively from the source Markdown:

```text
docs/harnesses/images/<base>/<base>-image-001.png
docs/harnesses/images/<base>/<base>-page-003-image-002.jpeg
```

```markdown
![brief image 001](../images/brief/brief-image-001.png)
```

DOCX images come from `word/media/*` and are placed near the paragraph or table
that references them. PDF images need PyMuPDF and are named by page. No OCR.

`--clean-assets` (with `--overwrite --extract-images`) deletes only
`docs/harnesses/images/<base>/` for the documents being regenerated.

## Manifest and check mode

`--manifest docs/harnesses/provenance/conversion-manifest.json` records, per
file: source path and SHA-256, output path and SHA-256, method, status,
message, extracted assets with hashes, and staged-summary hashes when present.

`--check` validates without rewriting: outputs exist and are non-empty, image
links resolve, staged summaries have valid frontmatter (`summary_type:
harness-ready`, UUID4 `provenance_id`, no private source metadata), and hashes
match the manifest when one is given. It also accepts the older list-shaped
manifest.

## Extractors

PDF text, in order: `pdftotext` (Poppler), `pypdf`, `pdfplumber`. PDF images:
PyMuPDF. DOCX: standard library only (text, headings, basic lists, tables).

`--install-missing` (user approval required) creates or reuses
`.krt/document-forge/venv` and installs the optional Python packages there. It
does not install system packages such as Poppler.
