"""Code parsing and data extraction utilies.

This module exposes a public function, [`visit()`][griffe.visitor.visit],
which parses the module code using [`parse()`][parse],
and returns a new [`Module`][griffe.dataclasses.Module] instance,
populating its members recursively, by using a custom [`NodeVisitor`][ast.NodeVisitor] class.
"""

from __future__ import annotations

import inspect
from ast import (
    AST,
    AnnAssign,
    Assign,
    Attribute,
    BinOp,
    BitOr,
    Call,
    Constant,
    Dict,
    Expr,
    FormattedValue,
    Index,
    JoinedStr,
    List,
    Name,
    PyCF_ONLY_AST,
    Str,
    Subscript,
    Tuple,
    keyword,
)
from itertools import zip_longest
from pathlib import Path

from griffe.collections import lines_collection
from griffe.dataclasses import Argument, Arguments, Class, Data, Decorator, Docstring, Function, Kind, Module
from griffe.extended_ast import LastNodeError
from griffe.extensions import Extensions
from griffe.extensions.base import _BaseVisitor  # noqa: WPS450


def visit(
    module_name: str,
    filepath: Path,
    code: str,
    extensions: Extensions | None = None,
) -> Module:
    """Parse and visit a module file.

    Parameters:
        module_name: The module name (as when importing [from] it).
        filepath: The module file path.
        code: The module contents.
        extensions: The extensions to use when visiting the AST.

    Returns:
        The module, with its members populated.
    """
    return _MainVisitor(module_name, filepath, code, extensions or Extensions()).get_module()


# ==========================================================
# docstrings
def _get_docstring(node):
    if isinstance(node, Expr):
        doc = node.value
    elif node.body and isinstance(node.body[0], Expr):
        doc = node.body[0].value
    else:
        return None
    if isinstance(doc, Constant) and isinstance(doc.value, str):
        return Docstring(doc.value, doc.lineno, doc.end_lineno)
    if isinstance(doc, Str):
        return Docstring(doc.s, doc.lineno, doc.end_lineno)
    return None


# ==========================================================
# base classes
def _get_base_class_name(node):
    if isinstance(node, Name):
        return node.id
    if isinstance(node, Attribute):
        return f"{_get_base_class_name(node.value)}.{node.attr}"


# ==========================================================
# annotations
def _get_name_annotation(node):
    return node.id


def _get_constant_annotation(node):
    return repr(node.value)


def _get_attribute_annotation(node):
    return f"{_get_annotation(node.value)}.{node.attr}"


def _get_binop_annotation(node):
    if isinstance(node.op, BitOr):
        return f"{_get_annotation(node.left)} | {_get_annotation(node.right)}"


def _get_subscript_annotation(node):
    return f"{_get_annotation(node.value)}[{_get_annotation(node.slice)}]"


def _get_index_annotation(node):
    return _get_annotation(node.value)


def _get_tuple_annotation(node):
    return ", ".join(_get_annotation(el) for el in node.elts)


def _get_list_annotation(node):
    return ", ".join(_get_annotation(el) for el in node.elts)


_node_annotation_map = {
    Name: _get_name_annotation,
    Constant: _get_constant_annotation,
    Attribute: _get_attribute_annotation,
    BinOp: _get_binop_annotation,
    Subscript: _get_subscript_annotation,
    Index: _get_index_annotation,
    Tuple: _get_tuple_annotation,
    List: _get_list_annotation,
}


def _get_annotation(node):
    return _node_annotation_map.get(type(node), lambda _: None)(node)


# ==========================================================
# values
def _get_name_value(node):
    return node.id


def _get_constant_value(node):
    return repr(node.value)


def _get_attribute_value(node):
    return f"{_get_value(node.value)}.{node.attr}"


def _get_binop_value(node):
    if isinstance(node.op, BitOr):
        return f"{_get_value(node.left)} | {_get_value(node.right)}"


def _get_subscript_value(node):
    return f"{_get_value(node.value)}[{_get_value(node.slice).strip('()')}]"


def _get_index_value(node):
    return _get_value(node.value)


def _get_list_value(node):
    return "[" + ", ".join(_get_value(el) for el in node.elts) + "]"


def _get_tuple_value(node):
    return "(" + ", ".join(_get_value(el) for el in node.elts) + ")"


def _get_keyword_value(node):
    return f"{node.arg}={_get_value(node.value)}"


def _get_dict_value(node):
    pairs = zip(node.keys, node.values)
    return "{" + ", ".join(f"{_get_value(key)}: {_get_value(value)}" for key, value in pairs) + "}"


def _get_ellipsis_value(node):
    return "..."


def _get_formatted_value(node):
    return f"{{{_get_value(node.value)}}}"


def _get_joinedstr_value(node):
    return "".join(_get_value(value) for value in node.values)


def _get_call_value(node):
    posargs = ", ".join(_get_value(arg) for arg in node.args)
    kwargs = ", ".join(_get_value(kwarg) for kwarg in node.keywords)
    if posargs and kwargs:
        args = f"{posargs}, {kwargs}"
    elif posargs:
        args = posargs
    elif kwargs:
        args = kwargs
    else:
        args = ""
    return f"{_get_value(node.func)}({args})"


_node_value_map = {
    type(None): lambda _: repr(None),
    Name: _get_name_value,
    Constant: _get_constant_value,
    Attribute: _get_attribute_value,
    BinOp: _get_binop_value,
    Subscript: _get_subscript_value,
    Index: _get_index_value,
    List: _get_list_value,
    Tuple: _get_tuple_value,
    keyword: _get_keyword_value,
    Dict: _get_dict_value,
    FormattedValue: _get_formatted_value,
    JoinedStr: _get_joinedstr_value,
    Call: _get_call_value,
}


def _get_value(node):
    return _node_value_map.get(type(node), lambda _: None)(node)


# ==========================================================
# names
def _get_attribute_name(node):
    return f"{node.attr}.{_get_names(node.value)}"


def _get_name_name(node):
    return node.id


def _get_assign_names(node):
    return [_get_names(target) for target in node.targets]


def _get_annassign_names(node):
    return [_get_names(node.target)]


_node_names_map = {
    Assign: _get_assign_names,
    AnnAssign: _get_annassign_names,
    Name: _get_name_name,
    Attribute: _get_attribute_name,
}


def _get_names(node):
    return _node_names_map.get(type(node), lambda _: None)(node)


def _get_instance_names(node):
    return [name.split(".", 1)[1] for name in _get_names(node) if name.startswith("self.")]


# ==========================================================
# arguments
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


# ==========================================================
# visitor
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

    def _visit(self, node: AST, parent: AST | None = None) -> None:
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
            arguments.add(Argument(arg.arg, annotation=annotation, kind=kind, default=default))

        if node.args.vararg:
            annotation = _get_annotation(node.args.vararg.annotation)
            arguments.add(
                Argument(
                    f"*{node.args.vararg.arg}",
                    annotation=annotation,
                    kind=inspect.Parameter.VAR_POSITIONAL,
                    default=None,
                )
            )

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
            arguments.add(
                Argument(kwarg.arg, annotation=annotation, kind=inspect.Parameter.KEYWORD_ONLY, default=default)
            )

        if node.args.kwarg:
            annotation = _get_annotation(node.args.kwarg.annotation)
            arguments.add(
                Argument(
                    f"**{node.args.kwarg.arg}", annotation=annotation, kind=inspect.Parameter.VAR_KEYWORD, default=None
                )
            )

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

        function.labels |= labels

        if self.current.kind is Kind.CLASS and function.name == "__init__":
            self.current = function
            self.generic_visit(node)
            self.current = self.current.parent  # type: ignore

    def visit_FunctionDef(self, node) -> None:
        self.handle_function(node)

    def visit_AsyncFunctionDef(self, node) -> None:
        self.handle_function(node, labels={"async"})

    def visit_Import(self, node) -> None:
        # for alias in node.names:
        #     self.scope[self.path][alias.asname or alias.name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node) -> None:
        # for alias in node.names:
        #     self.scope[self.path][alias.asname or alias.name] = f"{node.module}.{alias.name}"
        self.generic_visit(node)

    def handle_data(self, node, annotation: str | None = None):  # noqa: WPS231
        parent = self.current
        labels = set()

        if parent.kind is Kind.MODULE:
            names = _get_names(node)
            labels.add("module")
        elif parent.kind is Kind.CLASS:
            names = _get_names(node)
            labels.add("class")
        elif parent.kind is Kind.FUNCTION:
            if parent.name != "__init__":
                return
            names = _get_instance_names(node)
            parent = parent.parent  # type: ignore
            labels.add("instance")

        if not names:
            return

        value = _get_value(node.value)

        try:
            docstring = _get_docstring(node.next)
        except (LastNodeError, AttributeError):
            docstring = None

        # TODO: handle assigns like x.y = z
        # we need to resolve x.y and add z in its member
        for name in names:
            data = Data(
                name=name,
                value=value,
                annotation=annotation,
                lineno=node.lineno,
                endlineno=node.end_lineno,
                docstring=docstring,
            )
            data.labels |= labels
            parent[name] = data  # type: ignore

    def visit_Assign(self, node) -> None:
        self.handle_data(node)

    def visit_AnnAssign(self, node) -> None:
        self.handle_data(node, _get_annotation(node))
