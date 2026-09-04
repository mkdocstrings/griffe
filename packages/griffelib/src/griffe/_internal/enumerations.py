# SPDX-License-Identifier: ISC

# Copyright (c) 2021, Timothée Mazzucotelli and contributors

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# This module contains all the enumerations of the package.

from __future__ import annotations

from enum import Enum


class LogLevel(str, Enum):
    """Enumeration of available log levels."""

    trace = "trace"
    """The TRACE log level."""
    debug = "debug"
    """The DEBUG log level."""
    info = "info"
    """The INFO log level."""
    success = "success"
    """The SUCCESS log level."""
    warning = "warning"
    """The WARNING log level."""
    error = "error"
    """The ERROR log level."""
    critical = "critical"
    """The CRITICAL log level."""


class DocstringSectionKind(str, Enum):
    """Enumeration of the possible docstring section kinds."""

    text = "text"
    """Text section."""
    parameters = "parameters"
    """Parameters section."""
    other_parameters = "other parameters"
    """Other parameters (keyword arguments) section."""
    type_parameters = "type parameters"
    """Type parameters section."""
    raises = "raises"
    """Raises (exceptions) section."""
    warns = "warns"
    """Warnings section."""
    returns = "returns"
    """Returned value(s) section."""
    yields = "yields"
    """Yielded value(s) (generators) section."""
    receives = "receives"
    """Received value(s) (generators) section."""
    examples = "examples"
    """Examples section."""
    attributes = "attributes"
    """Attributes section."""
    functions = "functions"
    """Functions section."""
    classes = "classes"
    """Classes section."""
    type_aliases = "type aliases"
    """Type aliases section."""
    modules = "modules"
    """Modules section."""
    deprecated = "deprecated"
    """Deprecation section."""
    admonition = "admonition"
    """Admonition block."""


class ParameterKind(str, Enum):
    """Enumeration of the different parameter kinds."""

    positional_only = "positional-only"
    """Positional-only parameter."""
    positional_or_keyword = "positional or keyword"
    """Positional or keyword parameter."""
    var_positional = "variadic positional"
    """Variadic positional parameter."""
    keyword_only = "keyword-only"
    """Keyword-only parameter."""
    var_keyword = "variadic keyword"
    """Variadic keyword parameter."""


class TypeParameterKind(str, Enum):
    """Enumeration of the different type parameter kinds."""

    type_var = "type-var"
    """Type variable."""
    type_var_tuple = "type-var-tuple"
    """Type variable tuple."""
    param_spec = "param-spec"
    """Parameter specification variable."""


class Kind(str, Enum):
    """Enumeration of the different object kinds."""

    MODULE = "module"
    """Modules."""
    CLASS = "class"
    """Classes."""
    FUNCTION = "function"
    """Functions and methods."""
    ATTRIBUTE = "attribute"
    """Attributes and properties."""
    ALIAS = "alias"
    """Aliases (imported objects)."""
    TYPE_ALIAS = "type alias"
    """Type aliases."""


class ExplanationStyle(str, Enum):
    """Enumeration of the possible styles for explanations."""

    ONE_LINE = "oneline"
    """Explanations on one-line."""
    VERBOSE = "verbose"
    """Explanations on multiple lines."""
    MARKDOWN = "markdown"
    """Explanations in Markdown, adapted to changelogs."""
    GITHUB = "github"
    """Explanation as GitHub workflow commands warnings, adapted to CI."""
    AZURE_DEVOPS = "azdo"
    """Explanations as Azure DevOps / Azure Pipelines logging commands."""


class ChangeFlag(str, Enum):
    """Enumeration of flags attached to API changes."""

    HINT = "hint"
    """The change suggests a possible API improvement."""
    WARNING = "warning"
    """The change might require attention."""
    DEPRECATION = "deprecation"
    """The change deprecates part of the API."""
    BREAKING = "breaking"
    """The change is backward-incompatible."""


class ChangeKind(str, Enum):
    """Enumeration of detectable API changes."""

    OBJECT_ADDED = "Public object was added"
    """A public object was added."""
    OBJECT_REMOVED = "Public object was removed"
    """A public object was removed."""
    OBJECT_CHANGED_KIND = "Public object points to a different kind of object"
    """A public object changed kind."""
    OBJECT_DEPRECATED = "Public object was deprecated"
    """A public object was deprecated."""
    OBJECT_UNDEPRECATED = "Public object is no longer deprecated"
    """A public object is no longer deprecated."""
    OBJECT_CHANGED_DEPRECATION = "Public object deprecation was changed"
    """A public object's deprecation message was changed."""
    CLASS_BASE_ADDED = "Base class was added"
    """A base class was added."""
    CLASS_BASE_REMOVED = "Base class was removed"
    """A base class was removed."""
    PARAMETER_ADDED = "Parameter was added"
    """A parameter was added."""
    PARAMETER_REMOVED = "Parameter was removed"
    """A parameter was removed."""
    PARAMETER_MOVED = "Positional parameter was moved"
    """A positional parameter was moved."""
    PARAMETER_CHANGED_KIND = "Parameter kind was changed"
    """A parameter changed kind."""
    PARAMETER_CHANGED_DEFAULT = "Parameter default was changed"
    """A parameter default was changed."""
    PARAMETER_CHANGED_TYPE = "Parameter type was changed"
    """A parameter type was changed."""
    RETURN_CHANGED_TYPE = "Return type was changed"
    """A return type was changed."""
    ATTRIBUTE_CHANGED_TYPE = "Attribute type was changed"
    """An attribute type was changed."""
    ATTRIBUTE_CHANGED_VALUE = "Attribute value was changed"
    """An attribute value was changed."""


class BreakageKind(str, Enum):
    """Enumeration of the possible API breakages."""

    PARAMETER_MOVED = "Positional parameter was moved"
    """Positional parameter was moved"""
    PARAMETER_REMOVED = "Parameter was removed"
    """Parameter was removed"""
    PARAMETER_CHANGED_KIND = "Parameter kind was changed"
    """Parameter kind was changed"""
    PARAMETER_CHANGED_DEFAULT = "Parameter default was changed"
    """Parameter default was changed"""
    PARAMETER_CHANGED_REQUIRED = "Parameter is now required"
    """Parameter is now required"""
    PARAMETER_ADDED_REQUIRED = "Parameter was added as required"
    """Parameter was added as required"""
    RETURN_CHANGED_TYPE = "Return types are incompatible"
    """Return types are incompatible"""
    OBJECT_REMOVED = "Public object was removed"
    """Public object was removed"""
    OBJECT_CHANGED_KIND = "Public object points to a different kind of object"
    """Public object points to a different kind of object"""
    ATTRIBUTE_CHANGED_TYPE = "Attribute types are incompatible"
    """Attribute types are incompatible"""
    ATTRIBUTE_CHANGED_VALUE = "Attribute value was changed"
    """Attribute value was changed"""
    CLASS_REMOVED_BASE = "Base class was removed"
    """Base class was removed"""


class Parser(str, Enum):
    """Enumeration of the different docstring parsers."""

    auto = "auto"
    """Infer docstring parser."""
    google = "google"
    """Google-style docstrings parser."""
    sphinx = "sphinx"
    """Sphinx-style docstrings parser."""
    numpy = "numpy"
    """Numpydoc-style docstrings parser."""


class ObjectKind(str, Enum):
    """Enumeration of the different runtime object kinds."""

    MODULE = "module"
    """Modules."""
    CLASS = "class"
    """Classes."""
    STATICMETHOD = "staticmethod"
    """Static methods."""
    CLASSMETHOD = "classmethod"
    """Class methods."""
    METHOD_DESCRIPTOR = "method_descriptor"
    """Method descriptors."""
    METHOD = "method"
    """Methods."""
    BUILTIN_METHOD = "builtin_method"
    """Built-in methods."""
    COROUTINE = "coroutine"
    """Coroutines"""
    FUNCTION = "function"
    """Functions."""
    BUILTIN_FUNCTION = "builtin_function"
    """Built-in functions."""
    CACHED_PROPERTY = "cached_property"
    """Cached properties."""
    GETSET_DESCRIPTOR = "getset_descriptor"
    """Get/set descriptors."""
    PROPERTY = "property"
    """Properties."""
    TYPE_ALIAS = "type_alias"
    """Type aliases."""
    ATTRIBUTE = "attribute"
    """Attributes."""

    def __str__(self) -> str:
        return self.value
