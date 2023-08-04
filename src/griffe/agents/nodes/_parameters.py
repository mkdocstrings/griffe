"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from griffe.expressions import safe_get_expression
from griffe.logger import get_logger

if TYPE_CHECKING:
    import ast

    from griffe.dataclasses import Class, Module


logger = get_logger(__name__)


def get_call_keyword_arguments(node: ast.Call, parent: Module | Class) -> dict[str, Any]:
    """Get the list of keyword argument names and values from a Call node.

    Parameters:
        node: The node to extract the keyword arguments from.

    Returns:
        The keyword argument names and values.
    """
    return {kw.arg: safe_get_expression(kw.value, parent) for kw in node.keywords if kw.arg}


__all__ = ["get_call_keyword_arguments"]
