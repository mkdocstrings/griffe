"""This module contains the base classes for dealing with extensions."""

from __future__ import annotations

import ast

from griffe.agents.nodes import ObjectNode


class BaseVisitor:
    """The base class for visitors."""

    def visit(self, node: ast.AST) -> None:
        """Visit a node.

        Parameters:
            node: The node to visit.
        """
        getattr(self, f"visit_{node.kind}", self.generic_visit)(node)  # type: ignore[attr-defined]

    def generic_visit(self, node: ast.AST) -> None:
        """Visit the children of a node.

        Parameters:
            node: The node to visit (its children).
        """


class BaseInspector:
    """The base class for inspectors."""

    def inspect(self, node: ObjectNode) -> None:
        """Inspect a node.

        Parameters:
            node: The node to inspect.
        """
        getattr(self, f"inspect_{node.kind}", self.generic_inspect)(node)

    def generic_inspect(self, node: ObjectNode) -> None:
        """Inspect the children of a node.

        Parameters:
            node: The node to inspect (its children).
        """
