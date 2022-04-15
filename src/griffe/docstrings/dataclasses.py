"""This module contains the dataclasses related to docstrings."""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Literal  # type: ignore[attr-defined]

    from griffe.dataclasses import Expression, Name


# Elements -----------------------------------------------
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
        value: str | None = None,
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


class DocstringAdmonition(DocstringElement):
    """This class represents an admonition."""

    @property
    def kind(self) -> str | Name | Expression | None:
        """Return the kind of this admonition.

        Returns:
            The admonition's kind.
        """
        return self.annotation

    @kind.setter
    def kind(self, value: str | Name | Expression) -> None:
        self.annotation = value

    @property
    def contents(self) -> str:
        """Return the contents of this admonition.

        Returns:
            The admonition's contents.
        """
        return self.description

    @contents.setter
    def contents(self, value: str) -> None:
        self.description = value


class DocstringDeprecated(DocstringElement):
    """This class represents a documented deprecated item."""

    @property
    def version(self) -> str:
        """Return the version of this deprecation.

        Returns:
            The deprecation version.
        """
        return self.annotation  # type: ignore[return-value]

    @version.setter
    def version(self, value: str) -> None:
        self.annotation = value


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
    def default(self) -> str | None:
        """Return the default value of this parameter.

        Returns:
            The parameter's default.
        """
        return self.value

    @default.setter
    def default(self, value: str) -> None:
        self.value = value


class DocstringAttribute(DocstringNamedElement):
    """This class represents a documented module/class attribute."""


# Sections -----------------------------------------------
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
    """This class represents a docstring section."""

    kind: DocstringSectionKind

    def __init__(self, title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            title: An optional title.
        """
        self.title: str | None = title

    def as_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Return this section's data as a dictionary.

        Parameters:
            **kwargs: Additional serialization options.

        Returns:
            A dictionary.
        """
        if hasattr(self.value, "as_dict"):  # type: ignore[attr-defined]
            serialized_value = self.value.as_dict(**kwargs)  # type: ignore[attr-defined]
        else:
            serialized_value = self.value  # type: ignore[attr-defined]
        base = {"kind": self.kind.value, "value": serialized_value}
        if self.title:
            base["title"] = self.title
        return base


class DocstringSectionText(DocstringSection):
    """This class represents a text section."""

    kind: DocstringSectionKind = DocstringSectionKind.text

    def __init__(self, value: str, title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section text.
            title: An optional title.
        """
        super().__init__(title)
        self.value: str = value


class DocstringSectionParameters(DocstringSection):
    """This class represents a parameters section."""

    kind: DocstringSectionKind = DocstringSectionKind.parameters

    def __init__(self, value: list[DocstringParameter], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section parameters.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringParameter] = value


class DocstringSectionOtherParameters(DocstringSectionParameters):
    """This class represents an other parameters section."""

    kind: DocstringSectionKind = DocstringSectionKind.other_parameters


class DocstringSectionRaises(DocstringSection):
    """This class represents a raises section."""

    kind: DocstringSectionKind = DocstringSectionKind.raises

    def __init__(self, value: list[DocstringRaise], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section exceptions.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringRaise] = value


class DocstringSectionWarns(DocstringSection):
    """This class represents a warns section."""

    kind: DocstringSectionKind = DocstringSectionKind.warns

    def __init__(self, value: list[DocstringWarn], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section warnings.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringWarn] = value


class DocstringSectionReturns(DocstringSection):
    """This class represents a returns section."""

    kind: DocstringSectionKind = DocstringSectionKind.returns

    def __init__(self, value: list[DocstringReturn], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section returned items.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringReturn] = value


class DocstringSectionYields(DocstringSection):
    """This class represents a yields section."""

    kind: DocstringSectionKind = DocstringSectionKind.yields

    def __init__(self, value: list[DocstringYield], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section yielded items.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringYield] = value


class DocstringSectionReceives(DocstringSection):
    """This class represents a receives section."""

    kind: DocstringSectionKind = DocstringSectionKind.receives

    def __init__(self, value: list[DocstringReceive], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section received items.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringReceive] = value


class DocstringSectionExamples(DocstringSection):
    """This class represents an examples section."""

    kind: DocstringSectionKind = DocstringSectionKind.examples

    def __init__(
        self,
        value: list[tuple[Literal[DocstringSectionKind.text] | Literal[DocstringSectionKind.examples], str]],
        title: str | None = None,
    ) -> None:
        """Initialize the section.

        Parameters:
            value: The section examples.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[
            tuple[Literal[DocstringSectionKind.text] | Literal[DocstringSectionKind.examples], str]
        ] = value


class DocstringSectionAttributes(DocstringSection):
    """This class represents an attributes section."""

    kind: DocstringSectionKind = DocstringSectionKind.attributes

    def __init__(self, value: list[DocstringAttribute], title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            value: The section attributes.
            title: An optional title.
        """
        super().__init__(title)
        self.value: list[DocstringAttribute] = value


class DocstringSectionDeprecated(DocstringSection):
    """This class represents a deprecated section."""

    kind: DocstringSectionKind = DocstringSectionKind.deprecated

    def __init__(self, version: str, text: str, title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            version: The deprecation version.
            text: The deprecation text.
            title: An optional title.
        """
        super().__init__(title)
        self.value: DocstringDeprecated = DocstringDeprecated(annotation=version, description=text)


class DocstringSectionAdmonition(DocstringSection):
    """This class represents an admonition section."""

    kind: DocstringSectionKind = DocstringSectionKind.admonition

    def __init__(self, kind: str, text: str, title: str | None = None) -> None:
        """Initialize the section.

        Parameters:
            kind: The admonition kind.
            text: The admonition text.
            title: An optional title.
        """
        super().__init__(title)
        self.value: DocstringAdmonition = DocstringAdmonition(annotation=kind, description=text)
