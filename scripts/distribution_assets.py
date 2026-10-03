"""Passive SVG validation shared by skill and plugin packagers."""

from pathlib import Path
import xml.etree.ElementTree as ET


ASSETS = {"icon.svg": True, "icon-dark.svg": True, "wordmark.svg": False, "wordmark-dark.svg": False}


def validate_svg(path: Path, square: bool = True) -> None:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 5 * 1024 * 1024:
        raise ValueError("SVG must be a regular file no larger than 5 MiB")
    content = path.read_bytes()
    if b"<!" in content:
        raise ValueError("SVG declarations are not allowed")
    svg = ET.fromstring(content)
    namespace = "{http://www.w3.org/2000/svg}"
    if svg.tag != namespace + "svg":
        raise ValueError("SVG must have an SVG root element")
    tags = {namespace + tag for tag in ("svg", "g", "path", "rect", "ellipse", "title", "text")}
    attributes = {
        "width", "height", "viewBox", "role", "aria-labelledby", "id", "rx", "ry", "fill",
        "d", "stroke", "stroke-width", "stroke-linecap", "cx", "cy", "x", "y", "transform",
        "font-family", "font-size", "font-weight", "letter-spacing",
    }
    for node in svg.iter():
        if node.tag not in tags:
            raise ValueError("SVG contains active or unsupported elements")
        for key, value in node.attrib.items():
            if key not in attributes or "url(" in value.lower() or "://" in value:
                raise ValueError("SVG contains active or external references")
    dimensions = [float(value) for value in svg.attrib.get("viewBox", "").split()]
    if len(dimensions) != 4 or dimensions[:2] != [0, 0] or not all(0 < size <= 4096 for size in dimensions[2:]):
        raise ValueError("SVG needs a bounded numeric viewBox starting at zero")
    if square and not (48 <= dimensions[2] == dimensions[3]):
        raise ValueError("Listing icons must be square and at least 48 px")
