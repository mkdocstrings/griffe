"""This module, when imported, will patch the [`ast.AST`][] class.

It will add the following attributes and properties to it:

- `node.parent` (attribute): The parent node, or None
- `node.children` (attribute): A list of children nodes.
- `node.siblings` (cached property): A list of siblings nodes.
- `node.position` (cached property): The position of the node within its siblings.
- `node.previous_siblings` (cached property): The siblings appearing before this node, starting from the closest.
- `node.next_siblings` (cached property): The siblings appearing after this node, starting from the closest.
- `node.previous` (cached property): The immediate previous node.
- `node.next` (cached property): The immediate next node.

All these properties will raise a `RootNodeError` if they are accessed from the root node.
The `next` and `previous` properties will raise a `LastNodeError` if there is no next or previous node.
"""

from __future__ import annotations

import ast
import inspect
from collections import defaultdict
from functools import cached_property


class LastNodeError(Exception):
    """Exception raised when trying to access a next or previous node."""


class RootNodeError(Exception):
    """Exception raised when trying to use siblings properties on a root node."""


class _ExtendedAST:
    @cached_property
    def position(self) -> int:
        try:
            return self.parent.children.index(self)  # type: ignore
        except AttributeError as error:
            raise RootNodeError("the root node does not have a parent, nor siblings, nor a position") from error

    @cached_property
    def previous_siblings(self) -> list[ast.AST]:
        if self.position == 0:
            return []
        return self.parent.children[self.position - 1 :: -1]  # type: ignore

    @cached_property
    def next_siblings(self) -> list[ast.AST]:
        if self.position == len(self.parent.children) - 1:  # type: ignore
            return []
        return self.parent.children[self.position + 1 :]  # type: ignore

    @cached_property
    def siblings(self) -> list[ast.AST]:
        return reversed(self.previous_siblings) + self.next_siblings  # type: ignore

    @cached_property
    def previous(self) -> ast.AST:
        try:
            return self.previous_siblings[0]
        except IndexError as error:
            raise LastNodeError("there is no previous node") from error

    @cached_property
    def next(self) -> ast.AST:  # noqa: A003
        try:
            return self.next_siblings[0]
        except IndexError as error:
            raise LastNodeError("there is no next node") from error

    @cached_property
    def first_child(self) -> ast.AST:
        try:
            return self.children[0]  # type: ignore
        except IndexError as error:
            raise LastNodeError("there are no children node") from error

    @cached_property
    def last_child(self) -> ast.AST:  # noqa: A003
        try:
            return self.children[-1]  # type: ignore
        except IndexError as error:
            raise LastNodeError("there are no children node") from error


_patched = False


def extend_ast(force: bool = False) -> None:
    """Extend the base `ast.AST` class to provide more functionality.

    Arguments:
        force: Whether to force re-patching if it was already done.
    """
    global _patched  # noqa: WPS420
    if _patched and not force:
        return
    for name, member in inspect.getmembers(ast):
        if name != "AST" and inspect.isclass(member):
            if ast.AST in member.__bases__:  # noqa: WPS609
                member.__bases__ = (*member.__bases__, _ExtendedAST)  # noqa: WPS609
    _patched = True  # noqa: WPS122,WPS442


def _tree():
    return defaultdict(_tree)


def link_tree(root_node: ast.AST) -> None:
    """Link nodes between them.

    This will set the `parent` and `children` attributes on every node in the tree.

    Arguments:
        root_node: The root node, to start from.
    """
    _NodeLinker().link(root_node)


class _NodeLinker(ast.NodeVisitor):
    def __init__(self) -> None:
        super().__init__()
        self._tree = _tree()
        self._tree_node = self._tree
        self._node = None

    def visit(self, node):
        node.parent = self._node
        parent_tree_node = self._tree_node
        self._tree_node = self._tree_node[node]
        parent_node = self._node
        self._node = node
        self.generic_visit(node)
        self._node = parent_node
        self._tree_node = parent_tree_node

    def link(self, node):
        self.visit(node)
        self._link_children()

    def _link_children(self, tree=None):
        if tree is None:
            tree = self._tree
        for parent, children in tree.items():
            parent.children = list(children.keys())
            self._link_children(children)
