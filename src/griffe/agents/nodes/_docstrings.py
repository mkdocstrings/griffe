"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

from ast import AST
from ast import Constant as NodeConstant
from ast import Expr as NodeExpr
from ast import Str as NodeStr

from griffe.logger import get_logger

logger = get_logger(__name__)


def get_docstring(
    node: AST,
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
    if isinstance(node, NodeExpr):
        doc = node.value
    elif node.body and isinstance(node.body[0], NodeExpr) and not strict:  # type: ignore[attr-defined]
        doc = node.body[0].value  # type: ignore[attr-defined]
    else:
        return None, None, None
    if isinstance(doc, NodeConstant) and isinstance(doc.value, str):
        return doc.value, doc.lineno, doc.end_lineno
    if isinstance(doc, NodeStr):
        lineno = doc.lineno
        return doc.s, lineno, doc.end_lineno
    return None, None, None


__all__ = ["get_docstring"]
