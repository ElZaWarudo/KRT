#!/usr/bin/env python3
"""Build a single-file before/after comparison report.

Usage:
    python3 assemble_report.py report.json IMAGES_DIR OUTPUT.html [--allow-missing]

report.json describes the page (see ../assets/report.example.json). IMAGES_DIR holds one folder per side
(for example before/ and after/) with files named <screen-key>-<dimension values joined by "-">.<ext>,
such as dashboard-light-desktop.webp. Every image is embedded as a data URI, so the output works offline
and can be sent as one file.
"""
import argparse
import base64
import html
import json
import os
import sys
from itertools import product
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"
MIME = {".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".avif": "image/avif"}
DEFAULT_SIDES = [{"key": "before", "label": "Before"}, {"key": "after", "label": "After"}]
UI_TEXT = {
    "en": {
        "settings": "Comparison settings", "report_theme": "Report theme", "auto": "Auto", "light": "Light", "dark": "Dark",
        "screen": "Screen", "previous": "← Previous", "next": "Next →", "count": "{n} of {total} · ← → keys",
        "missing": "No capture for this combination.", "changes": "What changed", "checks": "Verification",
    },
    "es": {
        "settings": "Opciones de comparación", "report_theme": "Tema del informe", "auto": "Auto", "light": "Claro", "dark": "Oscuro",
        "screen": "Pantalla", "previous": "← Anterior", "next": "Siguiente →", "count": "{n} de {total} · teclas ← →",
        "missing": "No hay captura para esta combinación.", "changes": "Qué cambió", "checks": "Verificación",
    },
}


def script_json(value):
    """JSON that is safe inside a <script> element."""
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def fail(message):
    sys.exit(f"error: {message}")


def validate(report):
    for field in ("title", "screens", "dimensions"):
        if not report.get(field):
            fail(f'report.json needs "{field}"')
    keys = [screen.get("key") for screen in report["screens"]]
    if not all(keys) or len(set(keys)) != len(keys):
        fail("every screen needs a unique key")
    for screen in report["screens"]:
        if not screen.get("label"):
            fail(f'screen "{screen["key"]}" needs a label')
    for dimension in report["dimensions"]:
        if not dimension.get("key") or not dimension.get("values"):
            fail("every dimension needs a key and values")
        for value in dimension["values"]:
            if not value.get("value") or not value.get("label"):
                fail(f'dimension "{dimension["key"]}" has a value without "value" or "label"')
    for check in report.get("checks", []):
        if check.get("status") not in ("ok", "note", "fail"):
            fail('each check needs "status": "ok", "note" or "fail"')


def load_images(images_dir, sides):
    images = {}
    for side in sides:
        folder = Path(images_dir) / side["key"]
        if not folder.is_dir():
            fail(f"missing image folder {folder}")
        images[side["key"]] = {}
        for path in sorted(folder.iterdir()):
            mime = MIME.get(path.suffix.lower())
            if mime:
                images[side["key"]][path.stem] = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()
    return images


def summary_html(report, text):
    changes = report.get("changes", [])
    checks = report.get("checks", [])
    if not changes and not checks:
        return ""
    left = "".join(f"<li>{item}</li>" for item in changes)
    right = "".join(f'<li><span class="dot {item["status"]}"></span><span>{item["html"]}</span></li>' for item in checks)
    return (
        '<section class="grid-2">'
        f'<div><h2>{html.escape(report.get("changes_title", text["changes"]))}</h2><ul class="tight">{left}</ul></div>'
        f'<div><h2>{html.escape(report.get("checks_title", text["checks"]))}</h2><ul class="checks">{right}</ul></div>'
        "</section>"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("report")
    parser.add_argument("images_dir")
    parser.add_argument("output")
    parser.add_argument("--allow-missing", action="store_true", help="show a placeholder instead of failing on missing images")
    args = parser.parse_args()

    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    validate(report)
    lang = report.get("lang", "en")
    text = {**UI_TEXT.get(lang, UI_TEXT["en"]), **report.get("ui_text", {})}
    sides = report.get("sides", DEFAULT_SIDES)
    images = load_images(args.images_dir, sides)

    combos = list(product(*[[value["value"] for value in dimension["values"]] for dimension in report["dimensions"]]))
    expected = {"-".join([screen["key"], *combo]) for screen in report["screens"] for combo in combos}
    missing = sorted(f"{side['key']}/{name}" for side in sides for name in expected if name not in images[side["key"]])
    unused = sorted(f"{side}/{name}" for side, files in images.items() for name in files if name not in expected)
    if missing and not args.allow_missing:
        fail(f"{len(missing)} missing images (use --allow-missing to show placeholders): {missing[:20]}")

    meta = "".join(f"<span><b>{html.escape(label)}</b> {value}</span>" for label, value in report.get("meta", []))
    replacements = {
        "__LANG__": html.escape(lang),
        "__TITLE__": html.escape(report["title"]),
        "__HEADING__": html.escape(report.get("heading", report["title"])),
        "__INTRO__": report.get("intro_html", ""),
        "__META__": meta,
        "__SUMMARY__": summary_html(report, text),
        "__FOOTER__": report.get("footer_html", ""),
        "__UI_SETTINGS__": html.escape(text["settings"]),
        "__UI_REPORT_THEME__": html.escape(text["report_theme"]),
        "__UI_AUTO__": html.escape(text["auto"]),
        "__UI_LIGHT__": html.escape(text["light"]),
        "__UI_DARK__": html.escape(text["dark"]),
        "__UI_SCREEN__": html.escape(text["screen"]),
        "__UI_PREVIOUS__": html.escape(text["previous"]),
        "__UI_NEXT__": html.escape(text["next"]),
        # Script data last, so author text cannot inject a placeholder into it.
        "__SCREENS__": script_json(report["screens"]),
        "__DIMENSIONS__": script_json(report["dimensions"]),
        "__SIDES__": script_json(sides),
        "__TEXT__": script_json({"count": text["count"], "missing": text["missing"]}),
        "__STORAGE_KEY__": script_json(report.get("storage_key", "before-after:" + report["title"])),
        "__IMAGES__": script_json(images),
    }
    page = TEMPLATE.read_text(encoding="utf-8")
    for placeholder, value in replacements.items():
        page = page.replace(placeholder, value)
    Path(args.output).write_text(page, encoding="utf-8")

    size_mb = os.path.getsize(args.output) / 1024 / 1024
    print(f"{len(report['screens'])} screens × {len(combos)} variants × {len(sides)} sides, {size_mb:.1f} MB -> {args.output}")
    if missing:
        print(f"warning: {len(missing)} missing images shown as placeholders: {missing[:10]}")
    if unused:
        print(f"warning: {len(unused)} images not referenced by any screen: {unused[:10]}")
    if size_mb > 15:
        print("warning: over 15 MB; resize desktop captures (for example 1200px wide) and use WebP at quality 65-70")


if __name__ == "__main__":
    main()
