"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

from ast import AST
from ast import Assign as NodeAssign
from ast import AugAssign as NodeAugAssign
from ast import BinOp as NodeBinOp
from ast import Constant as NodeConstant
from ast import List as NodeList
from ast import Name as NodeName
from ast import Set as NodeSet
from ast import Starred as NodeStarred
from ast import Tuple as NodeTuple
from contextlib import suppress
from functools import partial
from typing import TYPE_CHECKING, Any, Callable

from griffe.agents.nodes._values import get_value
from griffe.expressions import Name
from griffe.logger import LogLevel, get_logger

if TYPE_CHECKING:
    from griffe.dataclasses import Module


logger = get_logger(__name__)


def _extract_constant(node: NodeConstant, parent: Module) -> list[str | Name]:
    return [node.value]


def _extract_name(node: NodeName, parent: Module) -> list[str | Name]:
    return [Name(node.id, partial(parent.resolve, node.id))]


def _extract_starred(node: NodeStarred, parent: Module) -> list[str | Name]:
    return _extract(node.value, parent)


def _extract_sequence(node: NodeList | NodeSet | NodeTuple, parent: Module) -> list[str | Name]:
    sequence = []
    for elt in node.elts:
        sequence.extend(_extract(elt, parent))
    return sequence


def _extract_binop(node: NodeBinOp, parent: Module) -> list[str | Name]:
    left = _extract(node.left, parent)
    right = _extract(node.right, parent)
    return left + right


_node_map: dict[type, Callable[[Any, Module], list[str | Name]]] = {
    NodeConstant: _extract_constant,
    NodeName: _extract_name,
    NodeStarred: _extract_starred,
    NodeList: _extract_sequence,
    NodeSet: _extract_sequence,
    NodeTuple: _extract_sequence,
    NodeBinOp: _extract_binop,
}


def _extract(node: AST, parent: Module) -> list[str | Name]:
    return _node_map[type(node)](node, parent)


def get__all__(node: NodeAssign | NodeAugAssign, parent: Module) -> list[str | Name]:
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
    node: NodeAssign | NodeAugAssign,
    parent: Module,
    log_level: LogLevel = LogLevel.debug,  # TODO: set to error when we handle more things
) -> list[str | Name]:
    """Safely (no exception) extract values in `__all__`.

    Parameters:
        node: The `__all__` assignment node.
        parent: The parent used to resolve the names.
        log_level: Log level to use to log a message.

    Returns:
        A list of strings or resovable names.
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


__all__ = ["get__all__", "safe_get__all__"]
