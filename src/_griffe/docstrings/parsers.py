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

parsers = {
    Parser.google: parse_google,
    Parser.sphinx: parse_sphinx,
    Parser.numpy: parse_numpy,
}


def parse(
    docstring: Docstring,
    parser: Literal["google", "numpy", "sphinx"] | Parser | None,
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
        if isinstance(parser, str):
            parser = Parser(parser)
        return parsers[parser](docstring, **options)  # type: ignore[operator]
    return [DocstringSectionText(docstring.value)]
