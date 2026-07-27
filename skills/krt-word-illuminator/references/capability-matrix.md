# Capability matrix

## Implemented by bundled tools

| Capability | Level |
|---|---|
| Inspect DOCX structure, styles, metadata, fields, tables, images, comments, revisions | Supported |
| Create a new DOCX or use a template as a style/layout base | Supported |
| Semantic headings, paragraphs, lists, quotes, notes, code, captions | Supported |
| Inline figures with proportional sizing and alt text | Supported |
| Tables with repeated headers and controlled row splitting | Supported |
| Headers, footers, page-number fields, TOC field, page/section breaks | Supported |
| Exact text replacement and heading-relative insertion | Supported with ambiguity guards |
| Structural, placeholder, style, table-header, alt-text, metadata, and PII audits | Supported |
| LibreOffice PDF rendering and page PNG generation | Supported when host tools exist |
| Textual, structural, style, relationship, and optional rendered-page comparison | Supported |
| Core/custom metadata scrubbing and optional comment removal | Supported |

## Requires a specialized OOXML workflow

Do not claim these are handled by the basic scripts:

- authoring reliable comments across arbitrary Word versions;
- creating or preserving tracked changes while editing;
- accepting or rejecting all revisions with semantic guarantees;
- creating cross-references, bookmarks, footnotes, endnotes, or content
  controls;
- updating fields exactly as desktop Word would;
- merging complex numbering definitions;
- preserving macros or editing `.docm`;
- editing floating drawing layouts;
- comparing documents with Word's native legal redline semantics.

For these requests, inspect package parts and relationships, use targeted OOXML
utilities with fixtures, render before and after, and state the compatibility
boundary. If the runtime cannot prove the result, provide a clean alternative
or stop for user direction.

## Not equivalent to visual inspection

Automated validation can find structural defects but cannot certify layout.
`visual_qa: pending_manual_inspection` remains pending until an agent inspects
all rendered pages and records the result.

