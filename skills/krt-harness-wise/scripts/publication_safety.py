#!/usr/bin/env python3
"""Shared publication-safety detection for Harness Wise artifacts."""

from __future__ import annotations

import re


EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE = re.compile(r"(?:\+?\d[\d .()-]{7,}\d)")
IBAN = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")
PII = re.compile(
    r"\b(?:\d{8}[A-Z]|[XYZ]\d{7}[A-Z])\b"
    r"|\b(?:dni|nie|passport|national[_ -]?id)\s*[:=]\s*[A-Z0-9-]{5,}\b",
    re.I,
)
SECRET_ASSIGNMENT = re.compile(
    r"\b(?:api[_-]?key|token|secret|password|passwd|pwd)\s*[:=]\s*['\"]?[^'\"\s]+",
    re.I,
)
SECRET_VALUE = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    r"|\bAKIA[0-9A-Z]{16}\b"
    r"|\bgh[pousr]_[A-Za-z0-9_]{20,}\b"
    r"|\bBearer\s+[A-Za-z0-9._~+/=-]{16,}",
    re.I,
)
CURRENCY_AMOUNT = re.compile(
    r"(?:\b\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{2})?\s?(?:€|EUR|USD|\$)\b"
    r"|\b(?:€|EUR|USD|\$)\s?\d{1,3}(?:[.,]\d{3})+)",
    re.I,
)
PRIVATE_URL = re.compile(
    r"https?://(?:localhost|127\.0\.0\.1|10\.|172\.(?:1[6-9]|2\d|3[01])\."
    r"|192\.168\.|[^/\s]*(?:internal|intranet|corp|local))[^)\s]*",
    re.I,
)
SOURCE_HASH = re.compile(r"\bsource_sha256\b|\b[a-f0-9]{64}\b", re.I)
GENERATED_SOURCE = re.compile(r"docs/harnesses/sources/[^\s)`]+", re.I)
GENERATED_IMAGE = re.compile(r"docs/harnesses/images/[^\s)`]+", re.I)
PRIVATE_ARTIFACT_PATH = re.compile(
    r"(?:docs/raw|docs/harnesses/(?:staging|provenance))/[^\s)`]+",
    re.I,
)
SOURCE_METADATA = re.compile(
    r"\b(?:source_path|original_path|original_sha256|manifest_path)\s*[:=]",
    re.I,
)
ABSOLUTE_SOURCE_PATH = re.compile(
    r"(?<![\w.:/-])/(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+"
)
WINDOWS_ABSOLUTE_SOURCE_PATH = re.compile(
    r"\b[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)+[^\\/:*?\"<>|\r\n\s]+"
)


def phone_like_value_present(text: str) -> bool:
    for match in PHONE.finditer(text):
        value = match.group(0)
        digits = re.sub(r"\D", "", value)
        if len(digits) >= 9 and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return True
    return False


def scan_publication(text: str) -> dict[str, list[str]]:
    """Return deduplicated blocking findings and review warnings."""
    scanned = re.sub(
        r"\bprov-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
        "",
        text,
        flags=re.I,
    )
    blocking: list[str] = []
    warnings: list[str] = []

    checks = (
        ("email", EMAIL),
        ("iban-like-value", IBAN),
        ("pii-like-value", PII),
        ("secret-like-assignment", SECRET_ASSIGNMENT),
        ("secret-like-value", SECRET_VALUE),
        ("private-url", PRIVATE_URL),
        ("source-hash-or-raw-digest", SOURCE_HASH),
        ("generated-source-fallback-reference", GENERATED_SOURCE),
        ("generated-image-reference", GENERATED_IMAGE),
        ("private-artifact-path", PRIVATE_ARTIFACT_PATH),
        ("source-metadata", SOURCE_METADATA),
        ("absolute-source-path", ABSOLUTE_SOURCE_PATH),
        ("windows-absolute-source-path", WINDOWS_ABSOLUTE_SOURCE_PATH),
    )
    for code, pattern in checks:
        if pattern.search(scanned):
            blocking.append(code)
    if phone_like_value_present(scanned):
        blocking.append("phone-like-value")
    if CURRENCY_AMOUNT.search(scanned):
        warnings.append("exact-currency-amount")

    return {
        "blocking": sorted(set(blocking)),
        "warnings": sorted(set(warnings)),
    }
