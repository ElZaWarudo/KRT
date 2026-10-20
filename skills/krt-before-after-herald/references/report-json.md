# report.json contract

Start from `assets/report.example.json`.

| Field | Purpose |
|---|---|
| `lang` | `en` or `es`; sets the toolbar labels. Override single labels with `ui_text`. |
| `title`, `heading` | Browser tab title (two to four words) and the visible H1. |
| `intro_html` | One sentence: what was changed and where its rules live. |
| `meta` | `[label, html]` pairs: date, screen count, exact code (branch + commit, or "uncommitted in …"), data used. |
| `changes` | HTML bullets, each `<b>Short claim.</b> One sentence of detail.` Patterns, not file lists. |
| `checks` | `{status, html}` with status `ok` (green), `note` (amber) or `fail` (red). |
| `footer_html` | What "before" is exactly, how screenshots were taken, that images are embedded. |
| `sides` | Usually Before/After. Three sides (for example Before / Round 1 / Round 2) also work. |
| `dimensions` | Toggles that select the image. Each value has `value`, `label`, optional `tag` (shown in the caption) and `narrow: true` for phone-width images. |
| `screens` | `{group, key, label, note}` in the order a reviewer should walk them. |
| `storage_key` | localStorage key that remembers the reviewer's toggles; unique per report. |

Image file names are the screen key followed by the chosen value of each dimension, in order:
`<key>-<dim1>-<dim2>.webp`. Fields ending in `_html` and `meta` values are inserted as HTML, so write
them yourself and escape anything copied from outside. Notes, labels and titles are inserted as text.
