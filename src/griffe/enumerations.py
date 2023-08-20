"""This module contains all the enumerations of the package."""

from __future__ import annotations

import enum


class DocstringSectionKind(enum.Enum):
    """The possible section kinds."""

    text = "text"
    parameters = "parameters"
    other_parameters = "other parameters"
    raises = "raises"
    warns = "warns"
    returns = "returns"
    yields = "yields"
    receives = "receives"
    examples = "examples"
    attributes = "attributes"
    functions = "functions"
    classes = "classes"
    modules = "modules"
    deprecated = "deprecated"
    admonition = "admonition"


class ParameterKind(enum.Enum):
    """Enumeration of the different parameter kinds.

    Attributes:
        positional_only: Positional-only parameter.
        positional_or_keyword: Positional or keyword parameter.
        var_positional: Variadic positional parameter.
        keyword_only: Keyword-only parameter.
        var_keyword: Variadic keyword parameter.
    """

    positional_only: str = "positional-only"
    positional_or_keyword: str = "positional or keyword"
    var_positional: str = "variadic positional"
    keyword_only: str = "keyword-only"
    var_keyword: str = "variadic keyword"


class Kind(enum.Enum):
    """Enumeration of the different objects kinds.

    Attributes:
        MODULE: The module kind.
        CLASS: The class kind.
        FUNCTION: The function kind.
        ATTRIBUTE: The attribute kind.
    """

    MODULE: str = "module"
    CLASS: str = "class"
    FUNCTION: str = "function"
    ATTRIBUTE: str = "attribute"
    ALIAS: str = "alias"


class ExplanationStyle(enum.Enum):
    """An enumeration of the possible styles for explanations."""

    ONE_LINE: str = "oneline"
    VERBOSE: str = "verbose"


class BreakageKind(enum.Enum):
    """An enumeration of the possible breakages."""

    PARAMETER_MOVED: str = "Positional parameter was moved"
    PARAMETER_REMOVED: str = "Parameter was removed"
    PARAMETER_CHANGED_KIND: str = "Parameter kind was changed"
    PARAMETER_CHANGED_DEFAULT: str = "Parameter default was changed"
    PARAMETER_CHANGED_REQUIRED: str = "Parameter is now required"
    PARAMETER_ADDED_REQUIRED: str = "Parameter was added as required"
    RETURN_CHANGED_TYPE: str = "Return types are incompatible"
    OBJECT_REMOVED: str = "Public object was removed"
    OBJECT_CHANGED_KIND: str = "Public object points to a different kind of object"
    ATTRIBUTE_CHANGED_TYPE: str = "Attribute types are incompatible"
    ATTRIBUTE_CHANGED_VALUE: str = "Attribute value was changed"
    CLASS_REMOVED_BASE: str = "Base class was removed"


class Parser(enum.Enum):
    """Enumeration for the different docstring parsers."""

    google = "google"
    sphinx = "sphinx"
    numpy = "numpy"


class ObjectKind(enum.Enum):
    """Enumeration for the different kinds of objects."""

    MODULE: str = "module"
    """Modules."""
    CLASS: str = "class"
    """Classes."""
    STATICMETHOD: str = "staticmethod"
    """Static methods."""
    CLASSMETHOD: str = "classmethod"
    """Class methods."""
    METHOD_DESCRIPTOR: str = "method_descriptor"
    """Method descriptors."""
    METHOD: str = "method"
    """Methods."""
    BUILTIN_METHOD: str = "builtin_method"
    """Built-in ethods."""
    COROUTINE: str = "coroutine"
    """Coroutines"""
    FUNCTION: str = "function"
    """Functions."""
    BUILTIN_FUNCTION: str = "builtin_function"
    """Built-in functions."""
    CACHED_PROPERTY: str = "cached_property"
    """Cached properties."""
    PROPERTY: str = "property"
    """Properties."""
    ATTRIBUTE: str = "attribute"
    """Attributes."""

    def __str__(self) -> str:
        return self.value


class When(enum.Enum):
    """This enumeration contains the different times at which an extension is used.

    Attributes:
        before_all: For each node, before the visit/inspection.
        before_children: For each node, after the visit has started, and before the children visit/inspection.
        after_children: For each node, after the children have been visited/inspected, and before finishing the visit/inspection.
        after_all: For each node, after the visit/inspection.
    """

    before_all: int = 1
    before_children: int = 2
    after_children: int = 3
    after_all: int = 4
