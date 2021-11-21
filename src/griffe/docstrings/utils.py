"""This module contains utilities for docstrings parsers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from griffe.logger import get_logger

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
        except AttributeError:
            prefix = "<module>"
        logger.warning(f"{prefix}:{(docstring.lineno or 0)+offset}: {message}")

    return warn
