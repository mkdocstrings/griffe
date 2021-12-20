"""Code parsing and data extraction utilies.

This module exposes a public function, [`visit()`][griffe.agents.visitor.visit],
which parses the module code using [`parse()`][ast.parse],
and returns a new [`Module`][griffe.dataclasses.Module] instance,
populating its members recursively, by using a [`NodeVisitor`][ast.NodeVisitor]-like class.
"""

from __future__ import annotations

import ast
import inspect
from contextlib import suppress
from itertools import zip_longest
from pathlib import Path
from typing import Any

from griffe.agents.base import BaseVisitor
from griffe.agents.extensions import Extensions
from griffe.agents.nodes import (
    ASTNode,
    get_annotation,
    get_baseclass,
    get_docstring,
    get_instance_names,
    get_names,
    get_parameter_default,
    get_value,
)
from griffe.collections import LinesCollection, ModulesCollection
from griffe.dataclasses import (
    Alias,
    Attribute,
    Class,
    Decorator,
    Docstring,
    Function,
    Kind,
    Module,
    Parameter,
    ParameterKind,
    Parameters,
)
from griffe.docstrings.parsers import Parser
from griffe.exceptions import LastNodeError
from griffe.expressions import Expression, Name


def visit(
    module_name: str,
    filepath: Path,
    code: str,
    *,
    extensions: Extensions | None = None,
    parent: Module | None = None,
    docstring_parser: Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
    modules_collection: ModulesCollection | None = None,
) -> Module:
    """Parse and visit a module file.

    Parameters:
        module_name: The module name (as when importing [from] it).
        filepath: The module file path.
        code: The module contents.
        extensions: The extensions to use when visiting the AST.
        parent: The optional parent of this module.
        docstring_parser: The docstring parser to use. By default, no parsing is done.
        docstring_options: Additional docstring parsing options.
        lines_collection: A collection of source code lines.
        modules_collection: A collection of modules.

    Returns:
        The module, with its members populated.
    """
    return Visitor(
        module_name,
        filepath,
        code,
        extensions or Extensions(),
        parent,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        lines_collection=lines_collection,
        modules_collection=modules_collection,
    ).get_module()


class Visitor(BaseVisitor):  # noqa: WPS338
    """This class is used to instantiate a visitor.

    Visitors iterate on AST nodes to extract data from them.
    """

    def __init__(
        self,
        module_name: str,
        filepath: Path,
        code: str,
        extensions: Extensions,
        parent: Module | None = None,
        docstring_parser: Parser | None = None,
        docstring_options: dict[str, Any] | None = None,
        lines_collection: LinesCollection | None = None,
        modules_collection: ModulesCollection | None = None,
    ) -> None:
        """Initialize the visitor.

        Parameters:
            module_name: The module name.
            filepath: The module filepath.
            code: The module source code.
            extensions: The extensions to use when visiting.
            parent: An optional parent for the final module object.
            docstring_parser: The docstring parser to use.
            docstring_options: The docstring parsing options.
            lines_collection: A collection of source code lines.
            modules_collection: A collection of modules.
        """
        super().__init__()
        self.module_name: str = module_name
        self.filepath: Path = filepath
        self.code: str = code
        self.extensions: Extensions = extensions.attach_visitor(self)
        self.parent: Module | None = parent
        self.current: Module | Class = None  # type: ignore[assignment]
        self.in_decorator: bool = False
        self.docstring_parser: Parser | None = docstring_parser
        self.docstring_options: dict[str, Any] = docstring_options or {}
        self.lines_collection: LinesCollection = lines_collection or LinesCollection()
        self.modules_collection: ModulesCollection = modules_collection or ModulesCollection()

    def _get_docstring(self, node: ast.AST, strict: bool = False) -> Docstring | None:
        value, lineno, endlineno = get_docstring(node, strict=strict)
        if value is None:
            return None
        return Docstring(
            value,
            lineno=lineno,
            endlineno=endlineno,
            parser=self.docstring_parser,
            parser_options=self.docstring_options,
        )

    def get_module(self) -> Module:
        """Build and return the object representing the module attached to this visitor.

        This method triggers a complete visit of the module nodes.

        Returns:
            A module instance.
        """
        # optimization: equivalent to ast.parse, but with optimize=1 to remove assert statements
        # TODO: with options, could use optimize=2 to remove docstrings
        top_node = compile(self.code, mode="exec", filename=str(self.filepath), flags=ast.PyCF_ONLY_AST, optimize=1)
        self.visit(top_node)
        return self.current.module

    def visit(self, node: ast.AST) -> None:
        """Extend the base visit with extensions.

        Parameters:
            node: The node to visit.
        """
        for before_visitor in self.extensions.before_visit:
            before_visitor.visit(node)
        super().visit(node)
        for after_visitor in self.extensions.after_visit:
            after_visitor.visit(node)

    def generic_visit(self, node: ast.AST) -> None:  # noqa: WPS231
        """Extend the base generic visit with extensions.

        Parameters:
            node: The node to visit.
        """
        for before_visitor in self.extensions.before_children_visit:
            before_visitor.visit(node)
        super().generic_visit(node)
        for after_visitor in self.extensions.after_children_visit:
            after_visitor.visit(node)

    def visit_module(self, node: ast.Module) -> None:
        """Visit a module node.

        Parameters:
            node: The node to visit.
        """
        self.current = Module(
            name=self.module_name,
            filepath=self.filepath,
            parent=self.parent,
            docstring=self._get_docstring(node),
            lines_collection=self.lines_collection,
            modules_collection=self.modules_collection,
        )
        self.generic_visit(node)

    def visit_classdef(self, node: ast.ClassDef) -> None:
        """Visit a class definition node.

        Parameters:
            node: The node to visit.
        """
        # handle decorators
        decorators = []
        if node.decorator_list:
            lineno = node.decorator_list[0].lineno
            self.in_decorator = True
            for decorator_node in node.decorator_list:
                decorators.append(Decorator(decorator_node.lineno, decorator_node.end_lineno))  # type: ignore[attr-defined]
                self.visit(decorator_node)
            self.in_decorator = False
        else:
            lineno = node.lineno

        # handle base classes
        bases = []
        if node.bases:
            for base in node.bases:
                bases.append(get_baseclass(base, self.current))

        class_ = Class(
            name=node.name,
            lineno=lineno,
            endlineno=node.end_lineno,  # type: ignore[attr-defined]
            docstring=self._get_docstring(node),
            decorators=decorators,
            bases=bases,
        )
        self.current[node.name] = class_
        self.current = class_
        self.generic_visit(node)
        self.current = self.current.parent  # type: ignore[assignment]

    def handle_function(self, node: ast.AsyncFunctionDef | ast.FunctionDef, labels: set | None = None):  # noqa: WPS231
        """Handle a function definition node.

        Parameters:
            node: The node to visit.
            labels: Labels to add to the data object.
        """
        labels = labels or set()

        # handle decorators
        decorators = []
        if node.decorator_list:
            lineno = node.decorator_list[0].lineno
            self.in_decorator = True
            for decorator_node in node.decorator_list:
                decorators.append(Decorator(decorator_node.lineno, decorator_node.end_lineno))  # type: ignore[attr-defined]
                self.visit(decorator_node)
            self.in_decorator = False
        else:
            lineno = node.lineno

        # handle parameters
        parameters = Parameters()
        annotation: str | Name | Expression | None

        # TODO: remove once Python 3.7 support is dropped
        try:
            posonlyargs = node.args.posonlyargs  # type: ignore[attr-defined]
        except AttributeError:
            posonlyargs = []

        # TODO: probably some optimizations to do here
        args_kinds_defaults = reversed(
            (
                *zip_longest(  # noqa: WPS356
                    reversed(
                        (
                            *zip_longest(
                                posonlyargs,  # type: ignore[attr-defined]
                                [],
                                fillvalue=ParameterKind.positional_only,
                            ),
                            *zip_longest(node.args.args, [], fillvalue=ParameterKind.positional_or_keyword),
                        ),
                    ),
                    reversed(node.args.defaults),
                    fillvalue=None,
                ),
            )
        )
        for (arg, kind), default in args_kinds_defaults:
            annotation = get_annotation(arg.annotation, parent=self.current)
            default = get_parameter_default(default, self.filepath, self.lines_collection)
            parameters.add(Parameter(arg.arg, annotation=annotation, kind=kind, default=default))

        if node.args.vararg:
            annotation = get_annotation(node.args.vararg.annotation, parent=self.current)
            parameters.add(
                Parameter(
                    f"*{node.args.vararg.arg}",
                    annotation=annotation,
                    kind=ParameterKind.var_positional,
                    default="()",
                )
            )

        # TODO: probably some optimizations to do here
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
            annotation = get_annotation(kwarg.annotation, parent=self.current)
            default = get_parameter_default(default, self.filepath, self.lines_collection)
            parameters.add(
                Parameter(kwarg.arg, annotation=annotation, kind=ParameterKind.keyword_only, default=default)
            )

        if node.args.kwarg:
            annotation = get_annotation(node.args.kwarg.annotation, parent=self.current)
            parameters.add(
                Parameter(
                    f"**{node.args.kwarg.arg}",
                    annotation=annotation,
                    kind=ParameterKind.var_keyword,
                    default="{}",  # noqa: P103
                )
            )

        function = Function(
            name=node.name,
            lineno=lineno,
            endlineno=node.end_lineno,  # type: ignore[union-attr]
            parameters=parameters,
            returns=get_annotation(node.returns, parent=self.current),
            decorators=decorators,
            docstring=self._get_docstring(node),
        )
        self.current[node.name] = function

        function.labels |= labels

        if self.current.kind is Kind.CLASS and function.name == "__init__":
            self.current = function  # type: ignore[assignment]  # temporary assign a function
            self.generic_visit(node)
            self.current = self.current.parent  # type: ignore[assignment]

    def visit_functiondef(self, node: ast.FunctionDef) -> None:
        """Visit a function definition node.

        Parameters:
            node: The node to visit.
        """
        self.handle_function(node)

    def visit_asyncfunctiondef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit an async function definition node.

        Parameters:
            node: The node to visit.
        """
        self.handle_function(node, labels={"async"})

    def visit_import(self, node: ast.Import) -> None:
        """Visit an import node.

        Parameters:
            node: The node to visit.
        """
        for name in node.names:
            alias_path = name.name.split(".", 1)[0]
            alias_name = name.asname or alias_path
            self.current.imports[alias_name] = alias_path
            self.current[alias_name] = Alias(
                alias_name,
                alias_path,
                lineno=node.lineno,
                endlineno=node.end_lineno,  # type: ignore[attr-defined]
            )
        self.generic_visit(node)

    def visit_importfrom(self, node: ast.ImportFrom) -> None:
        """Visit an "import from" node.

        Parameters:
            node: The node to visit.
        """
        for name in node.names:
            alias_name = name.asname or name.name
            alias_path = f"{node.module}.{name.name}"
            self.current.imports[name.asname or name.name] = alias_path
            self.current[alias_name] = Alias(
                alias_name,
                alias_path,
                lineno=node.lineno,
                endlineno=node.end_lineno,  # type: ignore[attr-defined]
            )
        self.generic_visit(node)

    def handle_attribute(  # noqa: WPS231
        self,
        node: ast.Assign | ast.AnnAssign,
        annotation: str | Name | Expression | None = None,
    ):
        """Handle an attribute (assignment) node.

        Parameters:
            node: The node to visit.
            annotation: A potential annotation.
        """
        parent = self.current
        labels = set()

        if parent.kind is Kind.MODULE:
            try:
                names = get_names(node)
            except KeyError:  # unsupported nodes, like subscript
                return
            labels.add("module")
        elif parent.kind is Kind.CLASS:
            try:
                names = get_names(node)
            except KeyError:  # unsupported nodes, like subscript
                return
            labels.add("class")
        elif parent.kind is Kind.FUNCTION:
            if parent.name != "__init__":
                return
            try:
                names = get_instance_names(node)
            except KeyError:  # unsupported nodes, like subscript
                return
            parent = parent.parent  # type: ignore[assignment]
            labels.add("instance")

        if not names:
            return

        value = get_value(node.value)  # type: ignore[arg-type]

        try:
            docstring = self._get_docstring(node.next, strict=True)  # type: ignore[union-attr]
        except (LastNodeError, AttributeError):
            docstring = None

        for name in names:
            # TODO: handle assigns like x.y = z
            # we need to resolve x.y and add z in its member
            if "." in name:
                continue

            if name in parent.members:
                # assigning multiple times: check for try/excepts
                # TODO: might be better to inspect
                if isinstance(node.parent, ast.ExceptHandler):  # type: ignore[union-attr]
                    continue  # prefer "no-exception" case

            attribute = Attribute(
                name=name,
                value=value,
                annotation=annotation,
                lineno=node.lineno,
                endlineno=node.end_lineno,  # type: ignore[union-attr]
                docstring=docstring,
            )
            attribute.labels |= labels
            parent[name] = attribute

            if name == "__all__":
                with suppress(AttributeError):
                    parent.exports = {elt.value for elt in node.value.elts}  # type: ignore[union-attr]

    def visit_assign(self, node: ast.Assign) -> None:
        """Visit an assignment node.

        Parameters:
            node: The node to visit.
        """
        self.handle_attribute(node)

    def visit_annassign(self, node: ast.AnnAssign) -> None:
        """Visit an annotated assignment node.

        Parameters:
            node: The node to visit.
        """
        self.handle_attribute(node, get_annotation(node.annotation, parent=self.current))


_patched = False


def patch_ast() -> None:
    """Extend the base `ast.AST` class to provide more functionality."""
    global _patched  # noqa: WPS420
    if _patched:
        return
    for name, member in inspect.getmembers(ast):
        if name != "AST" and inspect.isclass(member):
            if ast.AST in member.__bases__:  # noqa: WPS609
                member.__bases__ = (*member.__bases__, ASTNode)  # noqa: WPS609
    _patched = True  # noqa: WPS122,WPS442
