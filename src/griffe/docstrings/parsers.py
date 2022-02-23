"""This module imports all the defined parsers."""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Any

from griffe.docstrings.dataclasses import DocstringSection, DocstringSectionText
from griffe.docstrings.google import parse as parse_google
from griffe.docstrings.numpy import parse as parse_numpy
from griffe.docstrings.sphinx import parse as parse_sphinx

if TYPE_CHECKING:
    from griffe.dataclasses import Docstring


# TODO: assert common denominator / feature parity in all parsers
# - named return, yield, receive
# - exploding return tuple
# - picking yield and receive parts in generator
# - exploding tuple of generator yield part
# - sections titles
# - resolving annotations
class Parser(enum.Enum):
    """Enumeration for the different docstring parsers."""

    google = "google"
    sphinx = "sphinx"
    numpy = "numpy"


parsers = {
    Parser.google: parse_google,
    Parser.sphinx: parse_sphinx,
    Parser.numpy: parse_numpy,
}


def parse(docstring: Docstring, parser: Parser | None, **options: Any) -> list[DocstringSection]:
    """Parse the docstring.

    Parameters:
        docstring: The docstring to parse.
        parser: The docstring parser to use. If None, return a single text section.
        **options: The options accepted by the parser.

    Returns:
        A list of docstring sections.
    """
    if parser:
        return parsers[parser](docstring, **options)  # type: ignore[operator]
    return [DocstringSectionText(docstring.value)]
