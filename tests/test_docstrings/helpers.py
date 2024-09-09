"""This module contains helpers for testing docstring parsing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator, List, Protocol, Tuple, Union

from griffe import (
    Attribute,
    Class,
    Docstring,
    DocstringSection,
    Function,
    LogLevel,
    Module,
)

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
    ) -> ParseResultType: ...


def parser(parser_module: ModuleType) -> Iterator[ParserType]:
    """Wrap a parser to help testing.

    Parameters:
        parser_module: The parser module containing a `parse` function.

    Yields:
        The wrapped function.
    """
    original_warn = parser_module.docstring_warning

    def parse(docstring: str, parent: ParentType | None = None, **parser_opts: Any) -> ParseResultType:
        """Parse a docstring.

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
        parser_module.docstring_warning = (  # type: ignore[attr-defined]
            lambda _docstring, _offset, message, log_level=LogLevel.warning: warnings.append(message)
        )
        func_name = f"parse_{parser_module.__name__.split('.')[-1]}"
        func = getattr(parser_module, func_name)
        sections = func(docstring_object, **parser_opts)
        return sections, warnings

    yield parse

    parser_module.docstring_warning = original_warn  # type: ignore[attr-defined]
