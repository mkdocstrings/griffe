"""Code parsing and data extraction utilies.

This module exposes a public function, [`visit()`][griffe.visitor.visit],
which parses the module code using [`parse()`][parse],
and returns a new [`Module`][griffe.dataclasses.Module] instance,
populating its members recursively, by using a custom [`NodeVisitor`][ast.NodeVisitor] class.
"""

from __future__ import annotations

import inspect
from ast import AST as Node
from ast import And as NodeAnd
from ast import AnnAssign as NodeAnnAssign
from ast import Assign as NodeAssign
from ast import Attribute as NodeAttribute
from ast import BinOp as NodeBinOp
from ast import BitOr as NodeBitOr
from ast import BoolOp as NodeBoolOp
from ast import Call as NodeCall
from ast import Compare as NodeCompare
from ast import Constant as NodeConstant
from ast import Dict as NodeDict
from ast import DictComp as NodeDictComp
from ast import Expr as NodeExpr
from ast import FormattedValue as NodeFormattedValue
from ast import GeneratorExp as NodeGeneratorExp
from ast import IfExp as NodeIfExp
from ast import Index as NodeIndex
from ast import JoinedStr as NodeJoinedStr
from ast import Lambda as NodeLambda
from ast import List as NodeList
from ast import ListComp as NodeListComp
from ast import Mult as NodeMult
from ast import Name as NodeName
from ast import Not as NodeNot
from ast import NotEq as NodeNotEq
from ast import Or as NodeOr
from ast import PyCF_ONLY_AST
from ast import Set as NodeSet
from ast import Slice as NodeSlice
from ast import Starred as NodeStarred
from ast import Str as NodeStr
from ast import Subscript as NodeSubscript
from ast import Tuple as NodeTuple
from ast import UAdd as NodeUAdd
from ast import UnaryOp as NodeUnaryOp
from ast import USub as NodeUSub
from ast import comprehension as NodeComprehension
from ast import keyword as NodeKeyword
from itertools import zip_longest
from pathlib import Path

from griffe.collections import lines_collection
from griffe.dataclasses import Attribute, Class, Decorator, Docstring, Function, Kind, Module, Parameter, Parameters
from griffe.extended_ast import LastNodeError
from griffe.extensions import Extensions
from griffe.extensions.base import _BaseVisitor  # noqa: WPS450


def visit(
    module_name: str,
    filepath: Path,
    code: str,
    extensions: Extensions | None = None,
    parent: Module | None = None,
) -> Module:
    """Parse and visit a module file.

    Parameters:
        module_name: The module name (as when importing [from] it).
        filepath: The module file path.
        code: The module contents.
        extensions: The extensions to use when visiting the AST.
        parent: The optional parent of this module.

    Returns:
        The module, with its members populated.
    """
    return _MainVisitor(module_name, filepath, code, extensions or Extensions(), parent).get_module()


# ==========================================================
# docstrings
def _get_docstring(node):
    if isinstance(node, NodeExpr):
        doc = node.value
    elif node.body and isinstance(node.body[0], NodeExpr):
        doc = node.body[0].value
    else:
        return None
    if isinstance(doc, NodeConstant) and isinstance(doc.value, str):
        return Docstring(doc.value, doc.lineno, doc.end_lineno)
    if isinstance(doc, NodeStr):
        return Docstring(doc.s, doc.lineno, doc.end_lineno)
    return None


# ==========================================================
# base classes
def _get_base_class_name(node):
    if isinstance(node, NodeName):
        return node.id
    if isinstance(node, NodeAttribute):
        return f"{_get_base_class_name(node.value)}.{node.attr}"
    # TODO: resolve subscript
    if isinstance(node, NodeSubscript):
        return f"{_get_base_class_name(node.value)}[{_get_base_class_name(node.slice)}]"


# ==========================================================
# annotations
def _get_name_annotation(node):
    return node.id


def _get_constant_annotation(node):
    return repr(node.value)


def _get_attribute_annotation(node):
    return f"{_get_annotation(node.value)}.{node.attr}"


def _get_binop_annotation(node):
    if isinstance(node.op, NodeBitOr):
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
    NodeName: _get_name_annotation,
    NodeConstant: _get_constant_annotation,
    NodeAttribute: _get_attribute_annotation,
    NodeBinOp: _get_binop_annotation,
    NodeSubscript: _get_subscript_annotation,
    NodeIndex: _get_index_annotation,
    NodeTuple: _get_tuple_annotation,
    NodeList: _get_list_annotation,
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
    return f"{_get_value(node.left)} {_get_value(node.op)} {_get_value(node.right)}"


def _get_bitor_value(node):
    return "|"


def _get_mult_value(node):
    return "*"


def _get_unaryop_value(node):
    if isinstance(node.op, NodeUSub):
        return f"-{_get_value(node.operand)}"
    if isinstance(node.op, NodeUAdd):
        return f"+{_get_value(node.operand)}"
    if isinstance(node.op, NodeNot):
        return f"not {_get_value(node.operand)}"


def _get_slice_value(node):
    value = f"{_get_value(node.lower) if node.lower else ''}:{_get_value(node.upper) if node.upper else ''}"
    if node.step:
        value = f"{value}:{_get_value(node.step)}"
    return value


def _get_subscript_value(node):
    return f"{_get_value(node.value)}[{_get_value(node.slice).strip('()')}]"


def _get_index_value(node):
    return _get_value(node.value)


def _get_lambda_value(node):
    return f"lambda {_get_value(node.args)}: {_get_value(node.body)}"


def _get_list_value(node):
    return "[" + ", ".join(_get_value(el) for el in node.elts) + "]"


def _get_tuple_value(node):
    return "(" + ", ".join(_get_value(el) for el in node.elts) + ")"


def _get_keyword_value(node):
    return f"{node.arg}={_get_value(node.value)}"


def _get_dict_value(node):
    pairs = zip(node.keys, node.values)
    return "{" + ", ".join(f"{_get_value(key)}: {_get_value(value)}" for key, value in pairs) + "}"


def _get_set_value(node):
    return "{" + ", ".join(_get_value(el) for el in node.elts) + "}"


def _get_ellipsis_value(node):
    return "..."


def _get_starred_value(node):
    return _get_value(node.value)


def _get_formatted_value(node):
    return f"{{{_get_value(node.value)}}}"


def _get_joinedstr_value(node):
    return "".join(_get_value(value) for value in node.values)


def _get_boolop_value(node):
    if isinstance(node.op, NodeOr):
        return " or ".join(_get_value(value) for value in node.values)
    if isinstance(node.op, NodeAnd):
        return " and ".join(_get_value(value) for value in node.values)


def _get_compare_value(node):
    left = _get_value(node.left)
    ops = [_get_value(op) for op in node.ops]
    comparators = [_get_value(comparator) for comparator in node.comparators]
    return f"{left} " + " ".join(f"{op} {comp}" for op, comp in zip(ops, comparators))


def _get_noteq_value(node):
    return "!="


def _get_generatorexp_value(node):
    element = _get_value(node.elt)
    generators = [_get_value(gen) for gen in node.generators]
    return f"{element} " + " ".join(generators)


def _get_listcomp_value(node):
    element = _get_value(node.elt)
    generators = [_get_value(gen) for gen in node.generators]
    return f"[{element} " + " ".join(generators) + "]"


def _get_dictcomp_value(node):
    key = _get_value(node.key)
    value = _get_value(node.value)
    generators = [_get_value(gen) for gen in node.generators]
    return f"{{{key}: {value} " + " ".join(generators) + "}"


def _get_comprehension_value(node):
    target = _get_value(node.target)
    iterable = _get_value(node.iter)
    conditions = [_get_value(condition) for condition in node.ifs]
    value = f"for {target} in {iterable}"
    if conditions:
        value = f"{value} if " + " if ".join(conditions)
    if node.is_async:
        value = f"async {value}"
    return value


def _get_ifexp_value(node):
    return f"{_get_value(node.body)} if {_get_value(node.test)} else {_get_value(node.orelse)}"


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
    NodeName: _get_name_value,
    NodeConstant: _get_constant_value,
    NodeAttribute: _get_attribute_value,
    NodeBinOp: _get_binop_value,
    NodeUnaryOp: _get_unaryop_value,
    NodeSubscript: _get_subscript_value,
    NodeIndex: _get_index_value,
    NodeList: _get_list_value,
    NodeTuple: _get_tuple_value,
    NodeKeyword: _get_keyword_value,
    NodeDict: _get_dict_value,
    NodeSet: _get_set_value,
    NodeFormattedValue: _get_formatted_value,
    NodeJoinedStr: _get_joinedstr_value,
    NodeCall: _get_call_value,
    NodeSlice: _get_slice_value,
    NodeBoolOp: _get_boolop_value,
    NodeGeneratorExp: _get_generatorexp_value,
    NodeComprehension: _get_comprehension_value,
    NodeCompare: _get_compare_value,
    NodeNotEq: _get_noteq_value,
    NodeBitOr: _get_bitor_value,
    NodeMult: _get_mult_value,
    NodeListComp: _get_listcomp_value,
    NodeLambda: _get_lambda_value,
    NodeDictComp: _get_dictcomp_value,
    NodeStarred: _get_starred_value,
    NodeIfExp: _get_ifexp_value,
}


def _get_value(node):
    return _node_value_map.get(type(node), lambda _: None)(node)


# ==========================================================
# names
def _get_attribute_name(node):
    return f"{_get_names(node.value)}.{node.attr}"


def _get_name_name(node):
    return node.id


def _get_assign_names(node):
    return [name for name in [_get_names(target) for target in node.targets] if name]


def _get_annassign_names(node):
    return [name for name in _get_names(node.target) if name]


_node_names_map = {
    NodeAssign: _get_assign_names,
    NodeAnnAssign: _get_annassign_names,
    NodeName: _get_name_name,
    NodeAttribute: _get_attribute_name,
}


def _get_names(node):
    return _node_names_map.get(type(node), lambda _: None)(node)


def _get_instance_names(node):
    return [name.split(".", 1)[1] for name in _get_names(node) if name.startswith("self.")]


# ==========================================================
# parameters
def _get_parameter_default(node, filepath):
    if node is None:
        return None
    if isinstance(node, NodeConstant):
        return repr(node.value)
    if isinstance(node, NodeName):
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
        parent: Module | None = None,
    ) -> None:
        super().__init__()
        self.module_name: str = module_name
        self.filepath: Path = filepath
        self.code: str = code
        self.extensions: Extensions = extensions.instantiate(self)
        # self.scope = defaultdict(dict)
        self.root: Node | None = None
        self.parent: Module | None = parent
        self.current: Module | Class | Function = None  # type: ignore
        self.in_decorator: bool = False

    def _visit(self, node: Node, parent: Node | None = None) -> None:
        node.parent = parent  # type: ignore
        self._run_specific_or_generic(node)

    def get_module(self) -> Module:
        # optimisation: equivalent to ast.parse, but with optimize=1 to remove assert statements
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
        self.current = Module(name=self.module_name, filepath=self.filepath, docstring=_get_docstring(node))
        if self.parent is not None:
            self.current.parent = self.parent
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

        # handle parameters
        parameters = Parameters()
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
            default = _get_parameter_default(default, self.filepath)
            parameters.add(Parameter(arg.arg, annotation=annotation, kind=kind, default=default))

        if node.args.vararg:
            annotation = _get_annotation(node.args.vararg.annotation)
            parameters.add(
                Parameter(
                    f"*{node.args.vararg.arg}",
                    annotation=annotation,
                    kind=inspect.Parameter.VAR_POSITIONAL,
                    default="()",
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
            default = _get_parameter_default(default, self.filepath)
            parameters.add(
                Parameter(kwarg.arg, annotation=annotation, kind=inspect.Parameter.KEYWORD_ONLY, default=default)
            )

        if node.args.kwarg:
            annotation = _get_annotation(node.args.kwarg.annotation)
            parameters.add(
                Parameter(
                    f"**{node.args.kwarg.arg}",
                    annotation=annotation,
                    kind=inspect.Parameter.VAR_KEYWORD,
                    default="{}",
                )
            )

        function = Function(
            name=node.name,
            lineno=lineno,
            endlineno=node.end_lineno,
            parameters=parameters,
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

    def visit_Assign(self, node) -> None:
        self.handle_data(node)

    def visit_AnnAssign(self, node) -> None:
        self.handle_data(node, _get_annotation(node))
