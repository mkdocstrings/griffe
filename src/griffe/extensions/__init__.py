"""This module is the public interface to import elements from the base."""

from griffe.extensions.base import (
    Extension,
    Extensions,
    ExtensionType,
    InspectorExtension,
    VisitorExtension,
    When,
    load_extension,
    load_extensions,
)

__all__ = [
    "Extension",
    "Extensions",
    "ExtensionType",
    "InspectorExtension",
    "load_extension",
    "load_extensions",
    "VisitorExtension",
    "When",
]
