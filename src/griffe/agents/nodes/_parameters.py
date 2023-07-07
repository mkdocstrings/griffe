"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from griffe.agents.nodes._values import safe_get_value
from griffe.logger import get_logger

if TYPE_CHECKING:
    from ast import AST
    from pathlib import Path

    from griffe.collections import LinesCollection


logger = get_logger(__name__)


def get_parameter_default(node: AST | None, filepath: Path, lines_collection: LinesCollection) -> str | None:
    """Extract the default value of a function parameter.

    Parameters:
        node: The node to extract the default value from.
        filepath: The filepath in which the parameter is written.
            It allows to retrieve the actual code directly from the lines collection.
        lines_collection: A collection of source code lines.

    Returns:
        The default value as a string.
    """
    if node is None:
        return None
    default = safe_get_value(node)
    if default is not None:
        return default
    if node.lineno == node.end_lineno:
        return lines_collection[filepath][node.lineno - 1][node.col_offset : node.end_col_offset]
    # TODO: handle multiple line defaults
    return None
