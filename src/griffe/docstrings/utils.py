"""This module contains utilities for docstrings parsers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from griffe.logger import get_logger

if TYPE_CHECKING:
    from griffe.dataclasses import Docstring


def warning(name: str) -> Callable[[Docstring, int, str], None]:
    """Create and return a warn function.

    Arguments:
        name: The logger name.

    Returns:
        A function used to log parsing warnings.
    """
    logger = get_logger(name)

    def warn(docstring: Docstring, offset: int, message: str) -> None:  # noqa: WPS430
        """Log a warning message by prefixing it with the filepath and line number.

        Arguments:
            docstring: The docstring object.
            offset: The offset in the docstring lines.
            message: The message to log.
        """
        try:
            prefix = docstring.parent.filepath  # type: ignore
        except AttributeError:
            prefix = "<module>"
        logger.warning(f"{prefix}:{docstring.lineno+offset}: {message}")  # type: ignore

    return warn
