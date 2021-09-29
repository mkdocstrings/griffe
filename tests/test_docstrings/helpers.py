"""This module contains helpers for testing docstring parsing."""

from __future__ import annotations

from typing import Any, Callable, List, Tuple, Union

from griffe.dataclasses import Class, Data, Docstring, Function, Module
from griffe.docstrings.dataclasses import DocstringSection

ParentType = Union[Module, Class, Function, Data, None]
ParseResultType = Tuple[List[DocstringSection], List[str]]


def parser(parser_module) -> Callable[[str, ParentType, Any], ParseResultType]:
    """Wrap a parser to help testing.

    Arguments:
        parser_module: The parser module containing a `parse` function.

    Returns:
        The wrapped function.
    """

    def parse(docstring: str, parent: ParentType = None, **parser_opts: Any) -> ParseResultType:  # noqa: WPS430
        """Parse a doctring.

        Arguments:
            docstring: The docstring to parse.
            parent: The docstring's parent object.
            **parser_opts: Additional options accepted by the parser.

        Returns:
            The parsed sections, and warnings.
        """
        docstring_object = Docstring(docstring, lineno=1, endlineno=None)
        docstring_object.endlineno = len(docstring_object.lines) + 1
        if parent:
            docstring_object.parent = parent
            parent.docstring = docstring_object
        warnings = []
        parser_module._warn = lambda _docstring, _offset, message: warnings.append(message)  # noqa: WPS437
        sections = parser_module.parse(docstring_object, **parser_opts)
        return sections, warnings

    return parse  # type: ignore
