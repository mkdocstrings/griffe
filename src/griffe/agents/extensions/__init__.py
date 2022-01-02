"""This module is the public interface to import elements from the base."""

from griffe.agents.extensions.base import (
    Extension,
    Extensions,
    InspectorExtension,
    VisitorExtension,
    When,
    load_extension,
    load_extensions,
)

__all__ = [  # noqa: WPS410
    "Extensions",
    "Extension",
    "InspectorExtension",
    "VisitorExtension",
    "When",
    "load_extension",
    "load_extensions",
]
