# This module imports all the defined parsers
# and provides a generic function to parse docstrings.

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Literal, Union

from griffe._internal.docstrings.google import GoogleOptions, parse_google
from griffe._internal.docstrings.models import DocstringSection, DocstringSectionText
from griffe._internal.docstrings.numpy import NumpyOptions, parse_numpy
from griffe._internal.docstrings.sphinx import SphinxOptions, parse_sphinx
from griffe._internal.enumerations import Parser

if TYPE_CHECKING:
    from griffe._internal.models import Docstring


# This is not our preferred order, but the safest order for proper detection
# using heuristics. Indeed, Google style sections sometimes appear in otherwise
# plain markup docstrings, which could lead to false positives. Same for Numpy
# sections, whose syntax is regular rST markup, and which can therefore appear
# in plain markup docstrings too, even more often than Google sections.
_default_style_order = [Parser.sphinx, Parser.google, Parser.numpy]


DocstringStyle = Literal["google", "numpy", "sphinx", "auto"]
"""The supported docstring styles (literal values of the Parser enumeration)."""
DocstringDetectionMethod = Literal["heuristics", "max_sections"]
"""The supported methods to infer docstring styles."""
DocstringOptions = Union[GoogleOptions, NumpyOptions, SphinxOptions]
"""The options for each docstring style."""


def infer_docstring_style(
    docstring: Docstring,  # noqa: ARG001
    *,
    method: DocstringDetectionMethod = "heuristics",  # noqa: ARG001
    style_order: list[Parser] | list[DocstringStyle] | None = None,
    default: Parser | DocstringStyle | None = None,
    **options: Any,  # noqa: ARG001
) -> tuple[Parser | None, list[DocstringSection] | None]:
    """Infer the parser to use for the docstring.

    [:octicons-heart-fill-24:{ .pulse } Sponsors only](../../../insiders/index.md){ .insiders } &mdash;
    [:octicons-tag-24: Insiders 1.3.0](../../../insiders/changelog.md#1.3.0).

    The 'heuristics' method uses regular expressions. The 'max_sections' method
    parses the docstring with all parsers specified in `style_order` and returns
    the one who parsed the most sections.

    If heuristics fail, the `default` parser is returned. If multiple parsers
    parsed the same number of sections, `style_order` is used to decide which
    one to return. The `default` parser is never used with the 'max_sections' method.

    For non-Insiders versions, `default` is returned if specified, else the first
    parser in `style_order` is returned. If `style_order` is not specified,
    `None` is returned.

    Additional options are parsed to the detected parser, if any.

    Parameters:
        docstring: The docstring to parse.
        method: The method to use to infer the parser.
        style_order: The order of the styles to try when inferring the parser.
        default: The default parser to use if the inference fails.
        **options: Additional parsing options.

    Returns:
        The inferred parser, and optionally parsed sections (when method is 'max_sections').
    """
    if default:
        return default if isinstance(default, Parser) else Parser(default), None
    if style_order:
        style = style_order[0]
        return style if isinstance(style, Parser) else Parser(style), None
    return None, None


def parse_auto(
    docstring: Docstring,
    *,
    method: DocstringDetectionMethod = "heuristics",
    style_order: list[Parser] | list[DocstringStyle] | None = None,
    default: Parser | DocstringStyle | None = None,
    **options: Any,
) -> list[DocstringSection]:
    """Parse a docstring by automatically detecting the style it uses.

    [:octicons-heart-fill-24:{ .pulse } Sponsors only](../../../insiders/index.md){ .insiders } &mdash;
    [:octicons-tag-24: Insiders 1.3.0](../../../insiders/changelog.md#1.3.0).

    See [`infer_docstring_style`][griffe.infer_docstring_style] for more information
    on the available parameters.

    Parameters:
        docstring: The docstring to parse.
        method: The method to use to infer the parser.
        style_order: The order of the styles to try when inferring the parser.
        default: The default parser to use if the inference fails.
        **options: Additional parsing options.

    Returns:
        A list of docstring sections.
    """
    style, sections = infer_docstring_style(
        docstring,
        method=method,
        style_order=style_order,
        default=default,
        **options,
    )
    if sections is None:
        return parse(docstring, style, **options)
    return sections


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
