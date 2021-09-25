"""Code parsing and data extraction utilies.

This module exposes a public function, [`visit()`][griffe.visitor.visit],
which parses the module code using [`parse()`][parse],
and returns a new [`Module`][griffe.dataclasses.Module] instance,
populating its members recursively, by using a custom [`NodeVisitor`][ast.NodeVisitor] class.
"""

from __future__ import annotations

import inspect
from ast import AST, Attribute, BinOp, BitOr, Constant, Expr, Index, Name, PyCF_ONLY_AST, Str, Subscript
from itertools import zip_longest
from pathlib import Path

from griffe.collections import lines_collection
from griffe.dataclasses import Argument, Arguments, Class, Decorator, Docstring, Function, Module
from griffe.extensions import Extensions
from griffe.extensions.base import _BaseVisitor  # noqa: WPS450


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
    return _MainVisitor(module_name, filepath, code, extensions or Extensions()).get_module()


def _get_docstring(node):
    if not (node.body and isinstance(node.body[0], Expr)):
        return None
    doc = node.body[0].value
    if isinstance(doc, Constant) and isinstance(doc.value, str):
        return Docstring(doc.value, doc.lineno, doc.end_lineno)
    if isinstance(doc, Str):
        return Docstring(doc.s, doc.lineno, doc.end_lineno)
    return None


def _get_base_class_name(node):
    if isinstance(node, Name):
        return node.id
    if isinstance(node, Attribute):
        return f"{_get_base_class_name(node.value)}.{node.attr}"


def _get_annotation(node):
    if node is None:
        return None
    if isinstance(node, Name):
        return node.id
    if isinstance(node, Constant):
        return node.value
    if isinstance(node, Attribute):
        return f"{_get_annotation(node.value)}.{node.attr}"
    if isinstance(node, BinOp) and isinstance(node.op, BitOr):
        return f"{_get_annotation(node.left)} | {_get_annotation(node.right)}"
    if isinstance(node, Subscript):
        return f"{_get_annotation(node.value)}[{_get_annotation(node.slice)}]"
    if isinstance(node, Index):  # python 3.8
        return _get_annotation(node.value)
    return None


def _get_argument_default(node, filepath):
    if node is None:
        return None
    if isinstance(node, Constant):
        return repr(node.value)
    if isinstance(node, Name):
        return node.id
    if node.lineno == node.end_lineno:
        return lines_collection[filepath][node.lineno - 1][node.col_offset : node.end_col_offset]
    # TODO: handle multiple line defaults


class _MainVisitor(_BaseVisitor):  # noqa: WPS338
    def __init__(
        self,
        module_name: str,
        filepath: Path,
        code: str,
        extensions: Extensions,
    ) -> None:
        super().__init__()
        self.module_name: str = module_name
        self.filepath: Path = filepath
        self.code: str = code
        self.extensions: Extensions = extensions.instantiate(self)
        # self.scope = defaultdict(dict)
        self.root: AST | None = None
        self.parent: AST | None = None
        self.current: Module | Class | Function = None  # type: ignore
        self.in_decorator: bool = False
        if self.extensions.need_parents:
            self._visit = self._visit_set_parents  # type: ignore

    def _visit_set_parents(self, node: AST, parent: AST | None = None) -> None:
        node.parent = parent  # type: ignore
        self._run_specific_or_generic(node)

    def get_module(self) -> Module:
        # optimisation: equivalent to ast.parse, but with optimize=1 to remove assert statements
        # TODO: with options, could use optimize=2 to remove docstrings
        top_node = compile(self.code, mode="exec", filename=str(self.filepath), flags=PyCF_ONLY_AST, optimize=1)
        self.visit(top_node)
        return self.current.module  # type: ignore  # there's always a module after the visit

    def visit(self, node: AST, parent: AST | None = None) -> None:
        for start_visitor in self.extensions.when_visit_starts:
            start_visitor.visit(node, parent)
        super().visit(node, parent)
        for stop_visitor in self.extensions.when_visit_stops:
            stop_visitor.visit(node, parent)

    def generic_visit(self, node: AST) -> None:  # noqa: WPS231
        for start_visitor in self.extensions.when_children_visit_starts:
            start_visitor.visit(node)
        super().generic_visit(node)
        for stop_visitor in self.extensions.when_children_visit_stops:
            stop_visitor.visit(node)

    def visit_Module(self, node) -> None:
        self.current = Module(name=self.module_name, filepath=self.filepath, docstring=_get_docstring(node))
        self.generic_visit(node)

    def visit_ClassDef(self, node) -> None:
        # handle decorators
        decorators = []
        if node.decorator_list:
            lineno = node.decorator_list[0].lineno
            self.in_decorator = True
            for decorator_node in node.decorator_list:
                decorators.append(Decorator(decorator_node.lineno, decorator_node.end_lineno))
                self.visit(decorator_node)
            self.in_decorator = False
        else:
            lineno = node.lineno

        # handle base classes
        bases = []
        if node.bases:
            for base in node.bases:
                bases.append(_get_base_class_name(base))

        class_ = Class(
            name=node.name,
            lineno=lineno,
            endlineno=node.end_lineno,
            docstring=_get_docstring(node),
            decorators=decorators,
            bases=bases,
        )
        self.current[node.name] = class_
        self.current = class_
        self.generic_visit(node)
        self.current = self.current.parent  # type: ignore

    def visit_FunctionDef(self, node) -> None:  # noqa: WPS231
        # handle decorators
        decorators = []
        if node.decorator_list:
            lineno = node.decorator_list[0].lineno
            self.in_decorator = True
            for decorator_node in node.decorator_list:
                decorators.append(Decorator(decorator_node.lineno, decorator_node.end_lineno))
                self.visit(decorator_node)
            self.in_decorator = False
        else:
            lineno = node.lineno

        # handle arguments
        arguments = Arguments()
        annotation: str | None

        # TODO: probably some optimisations to do here
        args_kinds_defaults = reversed(
            (
                *zip_longest(  # noqa: WPS356
                    reversed(
                        (
                            *zip_longest(node.args.posonlyargs, [], fillvalue=inspect.Parameter.POSITIONAL_ONLY),
                            *zip_longest(node.args.args, [], fillvalue=inspect.Parameter.POSITIONAL_OR_KEYWORD),
                        ),
                    ),
                    reversed(node.args.defaults),
                    fillvalue=None,
                ),
            )
        )
        for (arg, kind), default in args_kinds_defaults:
            annotation = _get_annotation(arg.annotation)
            default = _get_argument_default(default, self.filepath)
            arguments.add(Argument(arg.arg, annotation, kind, default))

        if node.args.vararg:
            annotation = _get_annotation(node.args.vararg.annotation)
            arguments.add(Argument(f"*{node.args.vararg.arg}", annotation, inspect.Parameter.VAR_POSITIONAL, None))

        # TODO: probably some optimisations to do here
        kwargs_defaults = reversed(
            (
                *zip_longest(  # noqa: WPS356
                    reversed(node.args.kwonlyargs),
                    reversed(node.args.kw_defaults),
                    fillvalue=None,
                ),
            )
        )
        for kwarg, default in kwargs_defaults:  # noqa: WPS440
            annotation = _get_annotation(kwarg.annotation)
            default = _get_argument_default(default, self.filepath)
            arguments.add(Argument(kwarg.arg, annotation, inspect.Parameter.KEYWORD_ONLY, default))

        if node.args.kwarg:
            annotation = _get_annotation(node.args.kwarg.annotation)
            arguments.add(Argument(f"**{node.args.kwarg.arg}", annotation, inspect.Parameter.VAR_KEYWORD, None))

        function = Function(
            name=node.name,
            lineno=lineno,
            endlineno=node.end_lineno,
            arguments=arguments,
            returns=_get_annotation(node.returns),
            decorators=decorators,
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
