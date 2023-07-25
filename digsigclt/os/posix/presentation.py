"""Reading of local CMS presentation."""

from contextlib import suppress
from json import load, loads
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


__all__ = ["read_presentation"]


BASE_DIR = Path("/var/lib/digsig/dscms4")
JSON_FILE = BASE_DIR / "presentation.json"
XML_FILE = BASE_DIR / "presentation.xml"


def read_presentation() -> dict[str, Any]:
    """Read the presentation file into a JSON object."""

    with suppress(FileNotFoundError):
        with JSON_FILE.open("r", encoding="utf-8") as file:
            return load(file)

    with suppress(FileNotFoundError):
        # XXX: This returns only a partial representation of the presentation.
        return presentation_to_json(ElementTree.parse(XML_FILE))

    return {}


def presentation_to_json(presentation: ElementTree) -> dict[str, Any]:
    """Convert an XML presentation to JSON."""

    return {"configuration": configuration_to_json(presentation.find("configuration"))}


def configuration_to_json(configuration: ElementTree) -> dict[str, Any]:
    """Convert an XML configuration to JSON."""

    return {
        "design": configuration.find("design").text,
        "rotation": int(configuration.find("rotation").text),
        "portrait": loads(configuration.find("portrait").text),
    }
