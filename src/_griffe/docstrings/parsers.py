# This module imports all the defined parsers
# and provides a generic function to parse docstrings.

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from _griffe.docstrings.google import parse_google
from _griffe.docstrings.models import DocstringSection, DocstringSectionText
from _griffe.docstrings.numpy import parse_numpy
from _griffe.docstrings.sphinx import parse_sphinx
from _griffe.enumerations import Parser

if TYPE_CHECKING:
    from _griffe.models import Docstring

DocstringStyle = Literal["google", "numpy", "sphinx"]
"""The supported docstring styles (literal values of the Parser enumeration)."""
parsers: dict[Parser, Callable[[Docstring], list[DocstringSection]]] = {
    Parser.auto: parse_auto,
    Parser.google: parse_google,
    Parser.sphinx: parse_sphinx,
    Parser.numpy: parse_numpy,
}


def parse(
    docstring: Docstring,
    parser: DocstringStyle | Parser | None,
    **options: Any,
) -> list[DocstringSection]:
    """Parse the docstring.

    Parameters:
        docstring: The docstring to parse.
        parser: The docstring parser to use. If None, return a single text section.
        **options: The options accepted by the parser.

    Returns:
        A list of docstring sections.
    """
    if parser:
        if not isinstance(parser, Parser):
            parser = Parser(parser)
        return parsers[parser](docstring, **options)
    return [DocstringSectionText(docstring.value)]
