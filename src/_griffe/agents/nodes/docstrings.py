# This module contains utilities for extracting docstrings from nodes.

from __future__ import annotations

import ast

# YORE: Bump 1: Replace `_logger` with `logger` within file.
# YORE: Bump 1: Replace `get_logger` with `logger` within line.
from _griffe.logger import get_logger

# YORE: Bump 1: Remove line.
_logger = get_logger("griffe.agents.nodes._docstrings")


def get_docstring(
    node: ast.AST,
    *,
    strict: bool = False,
) -> tuple[str | None, int | None, int | None]:
    """Extract a docstring.

    Parameters:
        node: The node to extract the docstring from.
        strict: Whether to skip searching the body (functions).

    Returns:
        A tuple with the value and line numbers of the docstring.
    """
    # TODO: possible optimization using a type map
    if isinstance(node, ast.Expr):
        doc = node.value
    elif not strict and node.body and isinstance(node.body, list) and isinstance(node.body[0], ast.Expr):  # type: ignore[attr-defined]
        doc = node.body[0].value  # type: ignore[attr-defined]
    else:
        return None, None, None
    if isinstance(doc, ast.Constant) and isinstance(doc.value, str):
        return doc.value, doc.lineno, doc.end_lineno
    return None, None, None
