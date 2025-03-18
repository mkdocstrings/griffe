# This module contains utilities for extracting exports from `__all__` assignments.

from __future__ import annotations

import ast
from contextlib import suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from _griffe.agents.nodes.values import get_value
from _griffe.enumerations import LogLevel
from _griffe.expressions import ExprName
from _griffe.logger import logger

if TYPE_CHECKING:
    from _griffe.models import Module


# YORE: Bump 2: Remove block.
@dataclass
class ExportedName:
    """Deprecated. An intermediate class to store names.

    The [`get__all__`][griffe.get__all__] function now returns instances of [`ExprName`][griffe.ExprName] instead.
    """

    name: str
    """The exported name."""
    parent: Module
    """The parent module."""


def _extract_attribute(node: ast.Attribute, parent: Module) -> list[str | ExprName]:
    return [ExprName(name=node.attr, parent=_extract(node.value, parent)[0])]


def _extract_binop(node: ast.BinOp, parent: Module) -> list[str | ExprName]:
    left = _extract(node.left, parent)
    right = _extract(node.right, parent)
    return left + right


def _extract_constant(node: ast.Constant, parent: Module) -> list[str | ExprName]:
    return [node.value]


def _extract_name(node: ast.Name, parent: Module) -> list[str | ExprName]:
    return [ExprName(node.id, parent)]


def _extract_sequence(node: ast.List | ast.Set | ast.Tuple, parent: Module) -> list[str | ExprName]:
    sequence = []
    for elt in node.elts:
        sequence.extend(_extract(elt, parent))
    return sequence


def _extract_starred(node: ast.Starred, parent: Module) -> list[str | ExprName]:
    return _extract(node.value, parent)


_node_map: dict[type, Callable[[Any, Module], list[str | ExprName]]] = {
    ast.Attribute: _extract_attribute,
    ast.BinOp: _extract_binop,
    ast.Constant: _extract_constant,
    ast.List: _extract_sequence,
    ast.Name: _extract_name,
    ast.Set: _extract_sequence,
    ast.Starred: _extract_starred,
    ast.Tuple: _extract_sequence,
}


def _extract(node: ast.AST, parent: Module) -> list[str | ExprName]:
    return _node_map[type(node)](node, parent)


def get__all__(node: ast.Assign | ast.AnnAssign | ast.AugAssign, parent: Module) -> list[str | ExprName]:
    """Get the values declared in `__all__`.

    Parameters:
        node: The assignment node.
        parent: The parent module.

    Returns:
        A set of names.
    """
    if node.value is None:
        return []
    return _extract(node.value, parent)


def safe_get__all__(
    node: ast.Assign | ast.AnnAssign | ast.AugAssign,
    parent: Module,
    log_level: LogLevel = LogLevel.debug,  # TODO: Set to error when we handle more things?
) -> list[str | ExprName]:
    """Safely (no exception) extract values in `__all__`.

    Parameters:
        node: The `__all__` assignment node.
        parent: The parent used to resolve the names.
        log_level: Log level to use to log a message.

    Returns:
        A list of strings or resolvable names.
    """
    try:
        return get__all__(node, parent)
    except Exception as error:  # noqa: BLE001
        message = f"Failed to extract `__all__` value: {get_value(node.value)}"
        with suppress(Exception):
            message += f" at {parent.relative_filepath}:{node.lineno}"
        if isinstance(error, KeyError):
            message += f": unsupported node {error}"
        else:
            message += f": {error}"
        getattr(logger, log_level.value)(message)
        return []
