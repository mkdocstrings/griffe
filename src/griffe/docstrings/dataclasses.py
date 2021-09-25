"""This module contains the dataclasses related to docstrings."""

from __future__ import annotations

import enum
from typing import Any


class DocstringSectionKind(enum.Enum):
    """The possible section kinds."""

    text = "text"
    arguments = "arguments"
    raises = "raises"
    returns = "returns"
    yields = "yields"
    examples = "examples"
    attributes = "attributes"
    keyword_arguments = "keyword arguments"


class DocstringSection:
    """Placeholder."""

    def __init__(self, kind: DocstringSectionKind, value: Any) -> None:
        """Initialize the section.

        Arguments:
            kind: The section kind.
            value: The section value.
        """
        self.kind: DocstringSectionKind = kind
        self.value: Any = value

    def as_dict(self, **kwargs) -> dict[str, Any]:
        """Return this section's data as a dictionary.

        Arguments:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        if hasattr(self.value, "as_dict"):
            serialized_value = self.value.as_dict(**kwargs)
        else:
            serialized_value = self.value
        return {"kind": self.kind.value, "value": serialized_value}


class DocstringElement:
    """This base class represents annotated, nameless elements.

    Attributes:
        annotation: The element annotation, if any.
        description: The element description.
    """

    def __init__(self, annotation: str | None, description: str) -> None:
        """Initialize the element.

        Arguments:
            annotation: The element annotation, if any.
            description: The element description.
        """
        self.annotation: str | None = annotation
        self.description: str = description

    def as_dict(self, **kwargs) -> dict[str, Any]:
        """Return this element's data as a dictionary.

        Arguments:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        return {
            "annotation": self.annotation,
            "description": self.description,
        }


class DocstringException(DocstringElement):
    """This class represents a documented exception."""


class DocstringReturn(DocstringElement):
    """This class represents a documented return value."""


class DocstringYield(DocstringElement):
    """This class represents a documented yield value."""


class DocstringNamedElement(DocstringElement):
    """This base class represents annotated, named elements.

    Attributes:
        name: The element name.
        value: The element value, as a string, if any.
    """

    def __init__(self, name: str, annotation: str | None, description: str, value: str | None = None) -> None:
        """Initialize the element.

        Arguments:
            name: The element name.
            annotation: The element annotation, if any.
            description: The element description.
            value: The element value, as a string.
        """
        super().__init__(annotation, description)
        self.name: str = name
        self.value: str | None = value

    def as_dict(self, **kwargs) -> dict[str, Any]:
        """Return this element's data as a dictionary.

        Arguments:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = {"name": self.name, **super().as_dict(**kwargs)}
        if self.value is not None:
            base["value"] = self.value
        return base


class DocstringArgument(DocstringNamedElement):
    """This class represent a documented function argument."""


class DocstringAttribute(DocstringNamedElement):
    """This class represents a documented module/class attribute."""
