"""Code parsing and data extraction utilies.

This module exposes a public function, [`visit()`][griffe.visitor.visit],
which creates a new [`Module`][griffe.dataclasses.Module] instance,
parses the module code using [`ast.parse()`][ast.parse],
and populates the module and its members, recursively,
by using a custom [`NodeVisitor`][ast.NodeVisitor] class.

We do not publicly expose the custom node visitor class
to prevent usage mistakes: its instances are disposable
as they maintain an internal state while walking
the Abstract Syntax Tree, and therefore must not be reused.
We make this transparent to the developer through
[`visit()`][griffe.visitor.visit] function.
"""

from __future__ import annotations

import ast
from pathlib import Path

from griffe.dataclasses import Class, Function, Module
from griffe.extensions.base import Extensions

# from typing import List


class Node:
    """This class is a wrapper around [AST nodes][ast.AST].

    It allows each node of the AST to know to its parent and siblings.

    Attributes:
        node: The actual AST node.
        parent: The parent wrapped node (or a reference to self for the root).
        children: The children wrapped node.
    """

    def __init__(self, ast_node: ast.AST, parent: Node | None = None) -> None:
        """Initialize the node.

        Arguments:
            ast_node: The actual AST node.
            parent: The parent wrapped node.
        """
        if parent is None:
            parent = self
        self.node: ast.AST = ast_node
        self.parent: Node = parent
        self.children: list[Node] = []

    @property
    def is_root(self):
        return self.parent is self

    def graft(self, ast_node: ast.AST) -> Node:
        node = Node(ast_node, self)
        self.children.append(node)
        return node


def visit(
    module_name: str,
    filepath: Path,
    code: str,
    extensions: Extensions | None = None,
) -> Module:
    """Parse and visit a module file.

    Arguments:
        module_name: The module name (as when importing [from] it).
        filepath: The module file path.
        code: The module contents.
        extensions: The extensions to use when visiting the AST.

    Returns:
        The module, with its members populated.
    """
    module = Module(module_name, filepath=filepath)
    # instantiating the visitor side-effects the module,
    # populating its members
    _Visitor(module, ast.parse(code), extensions or Extensions())
    return module


class _Visitor(ast.NodeVisitor):
    def __init__(self, module, base_node, extensions) -> None:
        super().__init__()
        self.extensions = extensions.instantiate(self)
        # self.scope = defaultdict(dict)
        self.current = module
        self.root = Node(base_node)
        self.node = self.root
        self.generic_visit(base_node)

    def visit(self, node: ast.AST) -> None:
        self.node = self.node.graft(node)
        for start_visitor in self.extensions.when_visit_starts:
            start_visitor.visit(node)
        super().visit(node)
        for stop_visitor in self.extensions.when_visit_stops:
            stop_visitor.visit(node)
        self.node = self.node.parent

    def generic_visit(self, node: ast.AST) -> None:
        self.node = self.node.graft(node)
        for start_visitor in self.extensions.when_children_visit_starts:
            start_visitor.visit(node)
        super().generic_visit(node)
        for stop_visitor in self.extensions.when_children_visit_stops:
            stop_visitor.visit(node)
        self.node = self.node.parent

    def visit_Import(self, node):
        # for alias in node.names:
        #     self.scope[self.path][alias.asname or alias.name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        # for alias in node.names:
        #     self.scope[self.path][alias.asname or alias.name] = f"{node.module}.{alias.name}"
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if node.decorator_list:
            lineno = node.decorator_list[0].lineno
        else:
            lineno = node.lineno
        function = Function(node.name, lineno=lineno, endlineno=node.end_lineno)
        self.current[node.name] = function

    def visit_ClassDef(self, node):
        class_ = Class(node.name, lineno=node.lineno, endlineno=node.end_lineno)
        self.current[node.name] = class_
        self.current = class_
        self.generic_visit(node)
        self.current = self.current.parent
