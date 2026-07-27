"""Targeted package-level OOXML cleanup helpers."""

from __future__ import annotations

import copy
import re
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

ET.register_namespace("w", W_NS)
ET.register_namespace("cp", CP_NS)
ET.register_namespace("dc", DC_NS)


def _tag(namespace: str, name: str) -> str:
    return f"{{{namespace}}}{name}"


def _scrub_core(xml: bytes) -> bytes:
    root = ET.fromstring(xml)
    for name, namespace in (
        ("creator", DC_NS),
        ("lastModifiedBy", CP_NS),
        ("keywords", CP_NS),
    ):
        node = root.find(_tag(namespace, name))
        if node is not None:
            node.text = ""
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _remove_comment_anchors(xml: bytes) -> bytes:
    root = ET.fromstring(xml)
    parent_map = {child: parent for parent in root.iter() for child in parent}
    comment_tags = {
        _tag(W_NS, "commentRangeStart"),
        _tag(W_NS, "commentRangeEnd"),
        _tag(W_NS, "commentReference"),
    }
    for element in list(root.iter()):
        if element.tag in comment_tags and element in parent_map:
            parent_map[element].remove(element)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _is_comment_relationship(relation_type: str, target: str) -> bool:
    relationship_names = {
        "comments",
        "commentsExtended",
        "commentsIds",
        "commentsExtensible",
        "people",
    }
    return any(
        relation_type.endswith(f"/{name}") for name in relationship_names
    ) or bool(
        re.search(
            r"(?:^|/)(?:comments(?:Extended|Ids|Extensible)?|people)\d*\.xml$",
            target,
        )
    )


def _remove_comment_relationships(xml: bytes) -> bytes:
    root = ET.fromstring(xml)
    for relation in list(root):
        relation_type = relation.get("Type", "")
        target = relation.get("Target", "")
        if _is_comment_relationship(relation_type, target):
            root.remove(relation)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _remove_custom_property_relationships(xml: bytes) -> bytes:
    root = ET.fromstring(xml)
    for relation in list(root):
        relation_type = relation.get("Type", "")
        target = relation.get("Target", "")
        if relation_type.endswith("/custom-properties") or target.endswith(
            "docProps/custom.xml"
        ):
            root.remove(relation)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _remove_comment_content_types(xml: bytes) -> bytes:
    root = ET.fromstring(xml)
    for override in list(root):
        part_name = override.get("PartName", "")
        if re.search(
            r"/word/(?:comments(?:Extended|Ids|Extensible)?|people)\d*\.xml$",
            part_name,
        ):
            root.remove(override)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def scrub_package(
    source: Path,
    output: Path,
    *,
    remove_comments: bool,
    remove_custom_properties: bool,
) -> dict[str, int | bool]:
    removed_parts = 0
    changed_parts = 0
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        dir=output.parent, prefix=f".{output.name}.", suffix=".tmp", delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)

    try:
        with zipfile.ZipFile(source) as source_zip, zipfile.ZipFile(
            temporary_path, "w", compression=zipfile.ZIP_DEFLATED
        ) as output_zip:
            for info in source_zip.infolist():
                name = info.filename
                data = source_zip.read(name)
                remove = False

                if remove_custom_properties and name == "docProps/custom.xml":
                    remove = True
                if remove_comments and re.fullmatch(
                    r"word/(?:comments(?:Extended|Ids|Extensible)?|people)\d*\.xml",
                    name,
                ):
                    remove = True
                if remove:
                    removed_parts += 1
                    continue

                new_data = data
                if name == "docProps/core.xml":
                    new_data = _scrub_core(data)
                elif remove_comments and (
                    name == "word/document.xml"
                    or re.fullmatch(r"word/(?:header|footer)\d+\.xml", name)
                    or name in {"word/footnotes.xml", "word/endnotes.xml"}
                ):
                    new_data = _remove_comment_anchors(data)
                elif remove_comments and name.endswith(".rels"):
                    new_data = _remove_comment_relationships(data)
                if remove_custom_properties and name == "_rels/.rels":
                    new_data = _remove_custom_property_relationships(new_data)
                if name == "[Content_Types].xml":
                    new_data = _remove_comment_content_types(data) if remove_comments else data
                    if remove_custom_properties:
                        root = ET.fromstring(new_data)
                        for override in list(root):
                            if override.get("PartName") == "/docProps/custom.xml":
                                root.remove(override)
                        new_data = ET.tostring(
                            root, encoding="utf-8", xml_declaration=True
                        )
                if new_data != data:
                    changed_parts += 1
                output_zip.writestr(copy.copy(info), new_data)
        temporary_path.replace(output)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    return {
        "removed_parts": removed_parts,
        "changed_parts": changed_parts,
        "comments_removed": remove_comments,
        "custom_properties_removed": remove_custom_properties,
    }
