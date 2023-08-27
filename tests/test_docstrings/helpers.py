"""This module contains helpers for testing docstring parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator, List, Protocol, Tuple, Union

from griffe.dataclasses import Attribute, Class, Docstring, Function, Module
from griffe.docstrings.dataclasses import DocstringAttribute, DocstringElement, DocstringParameter, DocstringSection
from griffe.logger import LogLevel

if TYPE_CHECKING:
    from types import ModuleType


ParentType = Union[Module, Class, Function, Attribute, None]
ParseResultType = Tuple[List[DocstringSection], List[str]]


class ParserType(Protocol):  # noqa: D101
    def __call__(  # noqa: D102
        self,
        docstring: str,
        parent: ParentType | None = None,
        **parser_opts: Any,
    ) -> ParseResultType:
        ...


def parser(parser_module: ModuleType) -> Iterator[ParserType]:
    """Wrap a parser to help testing.

    Parameters:
        parser_module: The parser module containing a `parse` function.

    Yields:
        The wrapped function.
    """
    original_warn = parser_module._warn

    def parse(docstring: str, parent: ParentType | None = None, **parser_opts: Any) -> ParseResultType:
        """Parse a doctring.

        Parameters:
            docstring: The docstring to parse.
            parent: The docstring's parent object.
            **parser_opts: Additional options accepted by the parser.

        Returns:
            The parsed sections, and warnings.
        """
        docstring_object = Docstring(docstring, lineno=1, endlineno=None)
        docstring_object.endlineno = len(docstring_object.lines) + 1
        if parent is not None:
            docstring_object.parent = parent
            parent.docstring = docstring_object
        warnings = []
        parser_module._warn = lambda _docstring, _offset, message, log_level=LogLevel.warning: warnings.append(message)  # type: ignore[attr-defined]
        sections = parser_module.parse(docstring_object, **parser_opts)
        return sections, warnings

    yield parse

    parser_module._warn = original_warn  # type: ignore[attr-defined]


def assert_parameter_equal(actual: DocstringParameter, expected: DocstringParameter) -> None:
    """Help assert docstring parameters are equal.

    Parameters:
        actual: The actual parameter.
        expected: The expected parameter.
    """
    assert actual.name == expected.name
    assert_element_equal(actual, expected)
    assert actual.value == expected.value


def assert_attribute_equal(actual: DocstringAttribute, expected: DocstringAttribute) -> None:
    """Help assert docstring attributes are equal.

    Parameters:
        actual: The actual attribute.
        expected: The expected attribute.
    """
    assert actual.name == expected.name
    assert_element_equal(actual, expected)


def assert_element_equal(actual: DocstringElement, expected: DocstringElement) -> None:
    """Help assert docstring elements are equal.

    Parameters:
        actual: The actual element.
        expected: The expected element.
    """
    assert isinstance(actual, type(expected))

    for k in actual.as_dict():
        src = getattr(actual, k)
        dst = getattr(expected, k)

        assert src == dst, f"attribute {k!r}, {src!r} != {dst!r}"
