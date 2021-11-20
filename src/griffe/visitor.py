"""Code parsing and data extraction utilies.

This module exposes a public function, [`visit()`][griffe.visitor.visit],
which parses the module code using [`parse()`][ast.parse],
and returns a new [`Module`][griffe.dataclasses.Module] instance,
populating its members recursively, by using a custom [`NodeVisitor`][ast.NodeVisitor] class.
"""

from __future__ import annotations

from ast import AST as Node
from ast import PyCF_ONLY_AST
from contextlib import suppress
from itertools import zip_longest
from pathlib import Path
from typing import Any

from griffe.collections import LinesCollection
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
from griffe.expressions import Expression, Name
from griffe.extended_ast import LastNodeError
from griffe.extensions import Extensions
from griffe.extensions.base import _BaseVisitor  # noqa: WPS450
from griffe.node_utils import (
    get_annotation,
    get_baseclass,
    get_docstring,
    get_instance_names,
    get_names,
    get_parameter_default,
    get_value,
)


def visit(
    module_name: str,
    filepath: Path,
    code: str,
    extensions: Extensions | None = None,
    parent: Module | None = None,
    docstring_parser: Parser | None = None,
    docstring_options: dict[str, Any] | None = None,
    lines_collection: LinesCollection | None = None,
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

    Returns:
        The module, with its members populated.
    """
    return _MainVisitor(
        module_name,
        filepath,
        code,
        extensions or Extensions(),
        parent,
        docstring_parser=docstring_parser,
        docstring_options=docstring_options,
        lines_collection=lines_collection,
    ).get_module()


class _MainVisitor(_BaseVisitor):  # noqa: WPS338
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
    ) -> None:
        super().__init__()
        self.module_name: str = module_name
        self.filepath: Path = filepath
        self.code: str = code
        self.extensions: Extensions = extensions.instantiate(self)
        self.root: Node | None = None
        self.parent: Module | None = parent
        self.current: Module | Class = None  # type: ignore
        self.in_decorator: bool = False
        self.docstring_parser: Parser | None = docstring_parser
        self.docstring_options: dict[str, Any] = docstring_options or {}
        self.lines_collection: LinesCollection = lines_collection or LinesCollection()

    def _visit(self, node: Node, parent: Node | None = None) -> None:
        node.parent = parent  # type: ignore
        self._run_specific_or_generic(node)

    def _get_docstring(self, node: Node, strict: bool = False) -> Docstring | None:
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
        # optimization: equivalent to ast.parse, but with optimize=1 to remove assert statements
        # TODO: with options, could use optimize=2 to remove docstrings
        top_node = compile(self.code, mode="exec", filename=str(self.filepath), flags=PyCF_ONLY_AST, optimize=1)
        self.visit(top_node)
        return self.current.module  # type: ignore  # there's always a module after the visit

    def visit(self, node: Node, parent: Node | None = None) -> None:
        for start_visitor in self.extensions.when_visit_starts:
            start_visitor.visit(node, parent)
        super().visit(node, parent)
        for stop_visitor in self.extensions.when_visit_stops:
            stop_visitor.visit(node, parent)

    def generic_visit(self, node: Node) -> None:  # noqa: WPS231
        for start_visitor in self.extensions.when_children_visit_starts:
            start_visitor.visit(node)
        super().generic_visit(node)
        for stop_visitor in self.extensions.when_children_visit_stops:
            stop_visitor.visit(node)

    def visit_Module(self, node) -> None:
        self.current = Module(
            name=self.module_name,
            filepath=self.filepath,
            parent=self.parent,
            docstring=self._get_docstring(node),
            lines_collection=self.lines_collection,
        )
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
                bases.append(get_baseclass(base, self.current))

        class_ = Class(
            name=node.name,
            lineno=lineno,
            endlineno=node.end_lineno,
            docstring=self._get_docstring(node),
            decorators=decorators,
            bases=bases,
        )
        self.current[node.name] = class_
        self.current = class_
        self.generic_visit(node)
        self.current = self.current.parent  # type: ignore

    def handle_function(self, node, labels: set | None = None):  # noqa: WPS231
        labels = labels or set()

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

        # handle parameters
        parameters = Parameters()
        annotation: str | Name | Expression | None

        # TODO: probably some optimizations to do here
        args_kinds_defaults = reversed(
            (
                *zip_longest(  # noqa: WPS356
                    reversed(
                        (
                            *zip_longest(node.args.posonlyargs, [], fillvalue=ParameterKind.positional_only),
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
            endlineno=node.end_lineno,
            parameters=parameters,
            returns=get_annotation(node.returns, parent=self.current),
            decorators=decorators,
            docstring=self._get_docstring(node),
        )
        self.current[node.name] = function

        function.labels |= labels

        if self.current.kind is Kind.CLASS and function.name == "__init__":
            self.current = function  # type: ignore
            self.generic_visit(node)
            self.current = self.current.parent  # type: ignore

    def visit_FunctionDef(self, node) -> None:
        self.handle_function(node)

    def visit_AsyncFunctionDef(self, node) -> None:
        self.handle_function(node, labels={"async"})

    def visit_Import(self, node) -> None:
        for name in node.names:
            alias_path = name.name.split(".", 1)[0]
            alias_name = name.asname or alias_path
            self.current.imports[alias_name] = alias_path
            self.current[alias_name] = Alias(alias_name, alias_path, lineno=node.lineno, endlineno=node.end_lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node) -> None:
        for name in node.names:
            alias_name = name.asname or name.name
            alias_path = f"{node.module}.{name.name}"
            self.current.imports[name.asname or name.name] = alias_path
            self.current[alias_name] = Alias(alias_name, alias_path, lineno=node.lineno, endlineno=node.end_lineno)
        self.generic_visit(node)

    def handle_attribute(self, node, annotation: str | Name | Expression | None = None):  # noqa: WPS231
        parent = self.current
        labels = set()

        if parent.kind is Kind.MODULE:
            names = get_names(node)
            labels.add("module")
        elif parent.kind is Kind.CLASS:
            names = get_names(node)
            labels.add("class")
        elif parent.kind is Kind.FUNCTION:
            if parent.name != "__init__":
                return
            names = get_instance_names(node)
            parent = parent.parent  # type: ignore
            labels.add("instance")

        if not names:
            return

        value = get_value(node.value)

        try:
            docstring = self._get_docstring(node.next, strict=True)
        except (LastNodeError, AttributeError):
            docstring = None

        for name in names:
            # TODO: handle assigns like x.y = z
            # we need to resolve x.y and add z in its member
            if "." in name:
                continue

            attribute = Attribute(
                name=name,
                value=value,
                annotation=annotation,
                lineno=node.lineno,
                endlineno=node.end_lineno,
                docstring=docstring,
            )
            attribute.labels |= labels
            parent[name] = attribute  # type: ignore

            if name == "__all__":
                with suppress(AttributeError):
                    parent.exports = {elt.value for elt in node.value.elts}

    def visit_Assign(self, node) -> None:
        self.handle_attribute(node)

    def visit_AnnAssign(self, node) -> None:
        self.handle_attribute(node, get_annotation(node.annotation, parent=self.current))
