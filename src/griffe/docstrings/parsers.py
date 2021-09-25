"""This module imports all the defined parsers."""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from griffe.docstrings.dataclasses import DocstringSection
from griffe.docstrings.google import parse as parse_google

if TYPE_CHECKING:
    from griffe.dataclasses import Docstring


class Parser(enum.Enum):
    """Enumeration for the different docstring parsers."""

    google = "google"


parsers = {
    Parser.google: parse_google,
}


def parse(docstring: Docstring, docstring_parser: Parser, **options) -> list[DocstringSection]:
    """Parse the docstring.

    Arguments:
        docstring: The docstring to parse.
        docstring_parser: The parsing docstring_parser to use.
        **options: The options accepted by the parser.

    Returns:
        A list of docstring sections.
    """
    return parsers[docstring_parser](docstring, **options)
