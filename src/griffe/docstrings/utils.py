"""This module contains utilities for docstrings parsers."""

from __future__ import annotations

from ast import PyCF_ONLY_AST
from contextlib import suppress
from typing import TYPE_CHECKING, Callable

from griffe.agents.nodes import safe_get_annotation
from griffe.expressions import Expression, Name
from griffe.logger import LogLevel, get_logger

if TYPE_CHECKING:
    from griffe.dataclasses import Docstring


def warning(name: str) -> Callable[[Docstring, int, str], None]:
    """Create and return a warn function.

    Parameters:
        name: The logger name.

    Returns:
        A function used to log parsing warnings.

    This function logs a warning message by prefixing it with the filepath and line number.

    Other parameters: Parameters of the returned function:
        docstring (Docstring): The docstring object.
        offset (int): The offset in the docstring lines.
        message (str): The message to log.
    """
    logger = get_logger(name)

    def warn(docstring: Docstring, offset: int, message: str) -> None:  # noqa: WPS430
        try:
            prefix = docstring.parent.relative_filepath  # type: ignore[union-attr]
        except (AttributeError, ValueError):
            prefix = "<module>"
        logger.warning(f"{prefix}:{(docstring.lineno or 0)+offset}: {message}")

    return warn


def parse_annotation(
    annotation: str,
    docstring: Docstring,
    log_level: LogLevel = LogLevel.error,
) -> str | Name | Expression:
    """Parse a string into a true name or expression that can be resolved later.

    Parameters:
        annotation: The annotation to parse.
        docstring: The docstring in which the annotation appears.
            The docstring's parent is accessed to bind a resolver to the resulting name/expression.
        log_level: Log level to use to log a message.

    Returns:
        The string unchanged, or a new name or expression.
    """
    with suppress(
        AttributeError,  # docstring has no parent that can be used to resolve names
        SyntaxError,  # annotation contains syntax errors
    ):
        code = compile(annotation, mode="eval", filename="", flags=PyCF_ONLY_AST, optimize=2)
        if code.body:
            name_or_expr = safe_get_annotation(
                code.body,
                parent=docstring.parent,  # type: ignore[arg-type]
                log_level=log_level,
            )
            return name_or_expr or annotation
    return annotation
