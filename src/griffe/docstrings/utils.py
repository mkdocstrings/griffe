"""This module contains utilities for docstrings parsers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from griffe.logger import get_logger

logger = get_logger(__name__)


if TYPE_CHECKING:
    from griffe.dataclasses import Docstring


def warn(docstring: Docstring, offset: int, message: str) -> None:
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
