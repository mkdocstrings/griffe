"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

from ast import AST
from ast import AnnAssign as NodeAnnAssign
from ast import Assign as NodeAssign
from ast import Attribute as NodeAttribute
from ast import Name as NodeName
from typing import Any, Callable

from griffe.logger import get_logger

logger = get_logger(__name__)


def _get_attribute_name(node: NodeAttribute) -> str:
    return f"{get_name(node.value)}.{node.attr}"


def _get_name_name(node: NodeName) -> str:
    return node.id


_node_name_map: dict[type, Callable[[Any], str]] = {
    NodeName: _get_name_name,
    NodeAttribute: _get_attribute_name,
}


def get_name(node: AST) -> str:
    """Extract name from an assignment node.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return _node_name_map[type(node)](node)


def _get_assign_names(node: NodeAssign) -> list[str]:
    names = (get_name(target) for target in node.targets)
    return [name for name in names if name]


def _get_annassign_names(node: NodeAnnAssign) -> list[str]:
    name = get_name(node.target)
    return [name] if name else []


_node_names_map: dict[type, Callable[[Any], list[str]]] = {
    NodeAssign: _get_assign_names,
    NodeAnnAssign: _get_annassign_names,
}


def get_names(node: AST) -> list[str]:
    """Extract names from an assignment node.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return _node_names_map[type(node)](node)


def get_instance_names(node: AST) -> list[str]:
    """Extract names from an assignment node, only for instance attributes.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return [name.split(".", 1)[1] for name in get_names(node) if name.startswith("self.")]


__all__ = ["get_instance_names", "get_name", "get_names"]
