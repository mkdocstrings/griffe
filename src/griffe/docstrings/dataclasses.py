"""This module contains the dataclasses related to docstrings."""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from griffe.dataclasses import Expression, Name


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
    deprecated = "deprecated"
    admonition = "admonition"


class DocstringSection:
    """Placeholder."""

    def __init__(self, kind: DocstringSectionKind, value: Any, title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            kind: The section kind.
            value: The section value.
            title: An optional title.
        """
        self.kind: DocstringSectionKind = kind
        self.value: Any = value
        self.title: str | None = title

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this section's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        if hasattr(self.value, "as_dict"):
            serialized_value = self.value.as_dict(**kwargs)
        else:
            serialized_value = self.value
        base = {"kind": self.kind.value, "value": serialized_value}
        if self.title:
            base["title"] = self.title
        return base


class DocstringAdmonition:
    """This base class represents admonitions.

    Attributes:
        kind: The admonition kind.
        contents: The admonition contents.
    """

    def __init__(self, *, kind: str, contents: str) -> None:
        """Initialize the admonition.

        Parameters:
            kind: The admonition kind.
            contents: The admonition contents.
        """
        self.kind: str = kind
        self.contents: str = contents

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this admonition's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        return {
            "kind": self.kind,
            "contents": self.contents,
        }


class DocstringElement:
    """This base class represents annotated, nameless elements.

    Attributes:
        annotation: The element annotation, if any.
        description: The element description.
    """

    def __init__(self, *, description: str, annotation: str | Name | Expression | None = None) -> None:
        """Initialize the element.

        Parameters:
            annotation: The element annotation, if any.
            description: The element description.
        """
        self.description: str = description
        self.annotation: str | Name | Expression | None = annotation

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this element's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        return {
            "annotation": self.annotation,
            "description": self.description,
        }


class DocstringNamedElement(DocstringElement):
    """This base class represents annotated, named elements.

    Attributes:
        name: The element name.
        value: The element value, as a string, if any.
    """

    def __init__(
        self,
        name: str,
        *,
        description: str,
        annotation: str | Name | Expression | None = None,
        value: str | None = None
    ) -> None:
        """Initialize the element.

        Parameters:
            name: The element name.
            description: The element description.
            annotation: The element annotation, if any.
            value: The element value, as a string.
        """
        super().__init__(description=description, annotation=annotation)
        self.name: str = name
        self.value: str | None = value

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this element's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        base = {"name": self.name, **super().as_dict(**kwargs)}
        if self.value is not None:
            base["value"] = self.value
        return base


class DocstringRaise(DocstringElement):
    """This class represents a documented raise value."""


class DocstringWarn(DocstringElement):
    """This class represents a documented warn value."""


class DocstringReturn(DocstringNamedElement):
    """This class represents a documented return value."""


class DocstringYield(DocstringNamedElement):
    """This class represents a documented yield value."""


class DocstringReceive(DocstringNamedElement):
    """This class represents a documented receive value."""


class DocstringParameter(DocstringNamedElement):
    """This class represent a documented function parameter."""

    @property
    def default(self):
        """Return the default value of this parameter.

        Returns:
            The parameter's default.
        """
        return self.value

    @default.setter
    def default(self, value):
        self.value = value


class DocstringAttribute(DocstringNamedElement):
    """This class represents a documented module/class attribute."""
