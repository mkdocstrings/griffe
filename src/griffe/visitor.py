"""Code parsing and data extraction utilies.

This module exposes a public function, [`visit()`][griffe.visitor.visit],
which parses the module code using [`ast.parse()`][ast.parse],
and returns a new [`Module`][griffe.dataclasses.Module] instance,
populating its members recursively, by using a custom [`NodeVisitor`][ast.NodeVisitor] class.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

from griffe.collections import lines_collection
from griffe.dataclasses import Argument, Class, Docstring, Function, Module
from griffe.extended_ast import link_tree
from griffe.extensions import Extensions


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
    return _Visitor(module_name, filepath, code, extensions or Extensions()).get_module()


def _get_docstring(node):
    if not (node.body and isinstance(node.body[0], ast.Expr)):
        return None
    doc = node.body[0].value
    if isinstance(doc, ast.Constant) and isinstance(doc.value, str):
        return Docstring(doc.value, doc.lineno, doc.end_lineno)
    if isinstance(doc, ast.Str):
        return Docstring(doc.s, doc.lineno, doc.end_lineno)
    return None


class _Visitor(ast.NodeVisitor):
    def __init__(
        self,
        module_name: str,
        filepath: Path,
        code: str,
        extensions: Extensions,
    ) -> None:
        super().__init__()
        self.module_name = module_name
        self.filepath = filepath
        self.code = code
        self.extensions = extensions.instantiate(self)
        # self.scope = defaultdict(dict)
        self.root = None
        self.node = None
        self.current: Module | Class | Function = None  # type: ignore

    def get_module(self) -> Module:
        top_node = ast.parse(self.code)
        link_tree(top_node)
        self.visit(top_node)
        return self.current.module  # type: ignore  # there's always a module after the visit

    def visit(self, node: ast.AST) -> None:
        for start_visitor in self.extensions.when_visit_starts:
            start_visitor.visit(node)
        super().visit(node)
        for stop_visitor in self.extensions.when_visit_stops:
            stop_visitor.visit(node)

    def generic_visit(self, node: ast.AST) -> None:
        for start_visitor in self.extensions.when_children_visit_starts:
            start_visitor.visit(node)
        super().generic_visit(node)
        for stop_visitor in self.extensions.when_children_visit_stops:
            stop_visitor.visit(node)

    def visit_Module(self, node) -> None:
        self.current = Module(self.module_name, filepath=self.filepath, docstring=_get_docstring(node))
        self.generic_visit(node)

    def visit_ClassDef(self, node) -> None:
        class_ = Class(node.name, lineno=node.lineno, endlineno=node.end_lineno, docstring=_get_docstring(node))
        self.current[node.name] = class_
        self.current = class_
        self.generic_visit(node)
        self.current = self.current.parent  # type: ignore

    def visit_FunctionDef(self, node) -> None:  # noqa: WPS231
        # include decorating lines
        if node.decorator_list:
            lineno = node.decorator_list[0].lineno
        else:
            lineno = node.lineno

        # handle arguments
        arguments = []
        for arg in node.args.args:
            annotation: str | None
            kind = inspect.Parameter.POSITIONAL_OR_KEYWORD
            if isinstance(arg.annotation, ast.Name):
                annotation = arg.annotation.id
            elif isinstance(arg.annotation, ast.Constant):
                annotation = arg.annotation.value
            elif isinstance(arg.annotation, ast.Attribute):
                annotation = arg.annotation.attr
            else:
                annotation = None
            arguments.append(Argument(arg.arg, annotation, kind, None))

        # handle arguments defaults
        for index, default in enumerate(reversed(node.args.defaults), 1):
            if isinstance(default, ast.Constant):
                arguments[-index].default = repr(default.value)
            elif isinstance(default, ast.Name):
                arguments[-index].default = default.id
            elif default.lineno == default.end_lineno:
                value = lines_collection[self.filepath][default.lineno - 1][default.col_offset : default.end_col_offset]
                arguments[-index].default = value
            # TODO: handle multiple line defaults

        # handle return annotation
        if isinstance(node.returns, ast.Constant):
            returns = node.returns.value
        elif isinstance(node.returns, ast.Name):
            returns = node.returns.id
        elif isinstance(node.returns, ast.Attribute):
            returns = node.returns.attr
        else:
            returns = None

        function = Function(
            node.name,
            lineno=lineno,
            endlineno=node.end_lineno,
            arguments=arguments,
            returns=returns,
            docstring=_get_docstring(node),
        )
        self.current[node.name] = function

    def visit_Import(self, node) -> None:
        # for alias in node.names:
        #     self.scope[self.path][alias.asname or alias.name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node) -> None:
        # for alias in node.names:
        #     self.scope[self.path][alias.asname or alias.name] = f"{node.module}.{alias.name}"
        self.generic_visit(node)
