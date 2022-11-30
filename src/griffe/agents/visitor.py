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
from typing import Any, Iterable

from griffe.agents.base import BaseVisitor
from griffe.agents.extensions import Extensions
from griffe.agents.nodes import (
    ASTNode,
    get_annotation,
    get_docstring,
    get_instance_names,
    get_names,
    get_parameter_default,
    parse__all__,
    relative_to_absolute,
    safe_get_annotation,
    safe_get_value,
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
from griffe.exceptions import LastNodeError, NameResolutionError
from griffe.expressions import Expression, Name

builtin_decorators = {
    "property": "property",
    "staticmethod": "staticmethod",
    "classmethod": "classmethod",
}

stdlib_decorators = {
    "abc.abstractmethod": {"abstractmethod"},
    "functools.cache": {"cached"},
    "functools.cached_property": {"cached", "property"},
    "cached_property.cached_property": {"cached", "property"},
    "functools.lru_cache": {"cached"},
    "dataclasses.dataclass": {"dataclass"},
}
typing_overload = {"typing.overload", "typing_extensions.overload"}


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
        self.docstring_parser: Parser | None = docstring_parser
        self.docstring_options: dict[str, Any] = docstring_options or {}
        self.lines_collection: LinesCollection = lines_collection or LinesCollection()
        self.modules_collection: ModulesCollection = modules_collection or ModulesCollection()
        self.type_guarded: bool = False

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
        for child in node.children:  # type: ignore[attr-defined]  # noqa: WPS437
            self.visit(child)
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
            for decorator_node in node.decorator_list:
                decorators.append(
                    Decorator(
                        safe_get_value(decorator_node, self.current.relative_filepath),  # type: ignore[arg-type]
                        lineno=decorator_node.lineno,
                        endlineno=decorator_node.end_lineno,  # type: ignore[attr-defined]
                    )
                )
        else:
            lineno = node.lineno

        # handle base classes
        bases = []
        if node.bases:
            for base in node.bases:
                bases.append(safe_get_annotation(base, parent=self.current))

        class_ = Class(
            name=node.name,
            lineno=lineno,
            endlineno=node.end_lineno,  # type: ignore[attr-defined]
            docstring=self._get_docstring(node),
            decorators=decorators,
            bases=bases,  # type: ignore[arg-type]
            runtime=not self.type_guarded,
        )
        class_.labels |= self.decorators_to_labels(decorators)
        self.current[node.name] = class_
        self.current = class_
        self.generic_visit(node)
        self.current = self.current.parent  # type: ignore[assignment]

    def decorators_to_labels(self, decorators: list[Decorator]) -> set[str]:  # noqa: WPS231
        """Build and return a set of labels based on decorators.

        Parameters:
            decorators: The decorators to check.

        Returns:
            A set of labels.
        """
        labels = set()
        for decorator in decorators:
            decorator_value = decorator.value.split("(", 1)[0]
            if decorator_value in builtin_decorators:
                labels.add(builtin_decorators[decorator_value])
            else:
                names = decorator_value.split(".")
                with suppress(NameResolutionError):
                    resolved_first = self.current.resolve(names[0])
                    resolved_name = ".".join([resolved_first, *names[1:]])
                    if resolved_name in stdlib_decorators:
                        labels |= stdlib_decorators[resolved_name]
        return labels

    def get_base_property(self, decorators: list[Decorator]) -> tuple[Function | None, str | None]:
        """Check decorators to return the base property in case of setters and deleters.

        Parameters:
            decorators: The decorators to check.

        Returns:
            base_property: The property for which the setter/deleted is set.
            property_function: Either `"setter"` or `"deleter"`.
        """
        for decorator in decorators:
            names = decorator.value.split(".")
            with suppress(ValueError):
                base_name, base_function = names
                property_setter_or_deleter = (
                    base_function in {"setter", "deleter"}
                    and base_name in self.current.members
                    and self.current[base_name].has_labels({"property"})
                )
                if property_setter_or_deleter:
                    return self.current[base_name], base_function
        return None, None

    def handle_function(self, node: ast.AsyncFunctionDef | ast.FunctionDef, labels: set | None = None):  # noqa: WPS231
        """Handle a function definition node.

        Parameters:
            node: The node to visit.
            labels: Labels to add to the data object.
        """
        labels = labels or set()

        # handle decorators
        decorators = []
        overload = False
        if node.decorator_list:
            lineno = node.decorator_list[0].lineno
            for decorator_node in node.decorator_list:
                decorator_value = safe_get_value(decorator_node, self.filepath)
                overload = (
                    decorator_value in typing_overload
                    or decorator_value == "overload"
                    and self.current.resolve("overload") in typing_overload
                )
                decorators.append(
                    Decorator(
                        decorator_value,  # type: ignore[arg-type]
                        lineno=decorator_node.lineno,
                        endlineno=decorator_node.end_lineno,  # type: ignore[attr-defined]
                    )
                )
        else:
            lineno = node.lineno

        labels |= self.decorators_to_labels(decorators)

        if "property" in labels:
            attribute = Attribute(
                name=node.name,
                value=None,
                annotation=safe_get_annotation(node.returns, parent=self.current),
                lineno=node.lineno,
                endlineno=node.end_lineno,  # type: ignore[union-attr]
                docstring=self._get_docstring(node),
                runtime=not self.type_guarded,
            )
            attribute.labels |= labels
            self.current[node.name] = attribute
            return

        base_property, property_function = self.get_base_property(decorators)

        # handle parameters
        parameters = Parameters()
        annotation: str | Name | Expression | None

        # TODO: remove once Python 3.7 support is dropped
        try:
            posonlyargs = node.args.posonlyargs  # type: ignore[attr-defined]
        except AttributeError:
            posonlyargs = []

        # TODO: probably some optimizations to do here
        args_kinds_defaults: Iterable = reversed(
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
        arg: ast.arg
        kind: ParameterKind
        arg_default: ast.AST | None
        for (arg, kind), arg_default in args_kinds_defaults:
            annotation = safe_get_annotation(arg.annotation, parent=self.current)
            default = get_parameter_default(arg_default, self.filepath, self.lines_collection)
            parameters.add(Parameter(arg.arg, annotation=annotation, kind=kind, default=default))

        if node.args.vararg:
            annotation = safe_get_annotation(node.args.vararg.annotation, parent=self.current)
            parameters.add(
                Parameter(
                    node.args.vararg.arg,
                    annotation=annotation,
                    kind=ParameterKind.var_positional,
                    default="()",
                )
            )

        # TODO: probably some optimizations to do here
        kwargs_defaults: Iterable = reversed(
            (
                *zip_longest(  # noqa: WPS356
                    reversed(node.args.kwonlyargs),
                    reversed(node.args.kw_defaults),
                    fillvalue=None,
                ),
            )
        )
        kwarg: ast.arg
        kwarg_default: ast.AST | None
        for kwarg, kwarg_default in kwargs_defaults:  # noqa: WPS440
            annotation = safe_get_annotation(kwarg.annotation, parent=self.current)
            default = get_parameter_default(kwarg_default, self.filepath, self.lines_collection)
            parameters.add(
                Parameter(kwarg.arg, annotation=annotation, kind=ParameterKind.keyword_only, default=default)
            )

        if node.args.kwarg:
            annotation = safe_get_annotation(node.args.kwarg.annotation, parent=self.current)
            parameters.add(
                Parameter(
                    node.args.kwarg.arg,
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
            returns=safe_get_annotation(node.returns, parent=self.current),
            decorators=decorators,
            docstring=self._get_docstring(node),
            runtime=not self.type_guarded,
            parent=self.current,
        )

        if overload:
            self.current.overloads[function.name].append(function)
        elif base_property is not None:
            if property_function == "setter":
                base_property.setter = function
                base_property.labels.add("writable")
            elif property_function == "deleter":
                base_property.deleter = function
                base_property.labels.add("deletable")
        else:
            self.current[node.name] = function
            if self.current.kind in {Kind.MODULE, Kind.CLASS} and self.current.overloads[function.name]:
                function.overloads = self.current.overloads[function.name]
                del self.current.overloads[function.name]  # noqa: WPS420

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
            alias_path = name.name
            alias_name = name.asname or alias_path.split(".", 1)[0]
            self.current.imports[alias_name] = alias_path
            self.current[alias_name] = Alias(
                alias_name,
                alias_path,
                lineno=node.lineno,
                endlineno=node.end_lineno,  # type: ignore[attr-defined]
                runtime=not self.type_guarded,
            )

    def visit_importfrom(self, node: ast.ImportFrom) -> None:  # noqa: WPS231
        """Visit an "import from" node.

        Parameters:
            node: The node to visit.
        """
        for name in node.names:
            if not node.module and node.level == 1:
                if not name.asname:
                    # special case: when being in `a` and doing `from . import b`,
                    # we are effectively creating a member `b` in `a` that is pointing to `a.b`
                    # -> cyclic alias! in that case, we just skip it, as both the member and module
                    # have the same name and can be accessed the same way
                    continue

            alias_path = relative_to_absolute(node, name, self.current.module)
            if name.name == "*":
                alias_name = alias_path.replace(".", "/")  # type: ignore[union-attr]
                alias_path = alias_path.replace(".*", "")
            else:
                alias_name = name.asname or name.name
                self.current.imports[alias_name] = alias_path
            self.current[alias_name] = Alias(
                alias_name,
                alias_path,  # type: ignore[arg-type]
                lineno=node.lineno,
                endlineno=node.end_lineno,  # type: ignore[attr-defined]
                runtime=not self.type_guarded,
            )

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
            labels.add("module-attribute")
        elif parent.kind is Kind.CLASS:
            try:
                names = get_names(node)
            except KeyError:  # unsupported nodes, like subscript
                return
            labels.add("class-attribute")
        elif parent.kind is Kind.FUNCTION:
            if parent.name != "__init__":
                return
            try:
                names = get_instance_names(node)
            except KeyError:  # unsupported nodes, like subscript
                return
            parent = parent.parent  # type: ignore[assignment]
            labels.add("instance-attribute")

        if not names:
            return

        value = safe_get_value(node.value, self.filepath)  # type: ignore[arg-type]

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
                # assigning multiple times
                # TODO: might be better to inspect
                if isinstance(node.parent, (ast.If, ast.ExceptHandler)):  # type: ignore[union-attr]
                    continue  # prefer "no-exception" case

            attribute = Attribute(
                name=name,
                value=value,
                annotation=annotation,
                lineno=node.lineno,
                endlineno=node.end_lineno,  # type: ignore[union-attr]
                docstring=docstring,
                runtime=not self.type_guarded,
            )
            attribute.labels |= labels
            parent[name] = attribute

            if name == "__all__":
                with suppress(AttributeError):
                    parent.exports = parse__all__(node, self.current)  # type: ignore[assignment,arg-type]

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
        self.handle_attribute(node, safe_get_annotation(node.annotation, parent=self.current))

    def visit_augassign(self, node: ast.AugAssign) -> None:
        """Visit an augmented assignment node.

        Parameters:
            node: The node to visit.
        """
        with suppress(AttributeError):
            all_augment = (
                node.target.id == "__all__"  # type: ignore[attr-defined]
                and self.current.is_module
                and isinstance(node.op, ast.Add)
            )
            if all_augment:
                # we assume exports is not None at this point
                self.current.exports.extend(parse__all__(node, self.current))  # type: ignore[arg-type,union-attr]

    def visit_if(self, node: ast.If) -> None:
        """Visit an "if" node.

        Parameters:
            node: The node to visit.
        """
        if isinstance(node.parent, (ast.Module, ast.ClassDef)):  # type: ignore[attr-defined]
            with suppress(KeyError):  # unhandled AST nodes
                condition = get_annotation(node.test, parent=self.current)
                if str(condition) in {"typing.TYPE_CHECKING", "TYPE_CHECKING"}:
                    self.type_guarded = True
        self.generic_visit(node)
        self.type_guarded = False


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
