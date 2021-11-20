"""This module contains utilities for extracting information from AST nodes."""

from __future__ import annotations

from ast import AST as Node
from ast import And as NodeAnd
from ast import AnnAssign as NodeAnnAssign
from ast import Assign as NodeAssign
from ast import Attribute as NodeAttribute
from ast import BinOp as NodeBinOp
from ast import BitAnd as NodeBitAnd
from ast import BitOr as NodeBitOr
from ast import BoolOp as NodeBoolOp
from ast import Call as NodeCall
from ast import Compare as NodeCompare
from ast import Constant as NodeConstant
from ast import Dict as NodeDict
from ast import DictComp as NodeDictComp
from ast import Ellipsis as NodeEllipsis
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
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

from griffe.collections import LinesCollection
from griffe.expressions import Expression, Name

if TYPE_CHECKING:
    from griffe.dataclasses import Class, Module


def _join(sequence, item):
    if not sequence:
        return []
    new_sequence = [sequence[0]]
    for element in sequence[1:]:
        new_sequence.extend((item, element))
    return new_sequence


# ==========================================================
# base classes
def _get_baseclass_name(node: NodeName, parent: Module | Class) -> Name:
    return Name(node.id, partial(parent.resolve, node.id))


def _get_baseclass_attribute(node: NodeAttribute, parent: Module | Class) -> Expression:
    left = get_baseclass(node.value, parent)

    def resolver():  # noqa: WPS430
        return f"{left.full}.{node.attr}"

    right = Name(node.attr, resolver)
    return Expression(left, ".", right)


def _get_baseclass_subscript(node: NodeSubscript, parent: Module | Class) -> Expression:
    left = get_baseclass(node.value, parent)
    subscript = get_baseclass(node.slice, parent)
    return Expression(left, "[", subscript, "]")


_node_baseclass_map = {
    NodeName: _get_baseclass_name,
    NodeAttribute: _get_baseclass_attribute,
    NodeSubscript: _get_baseclass_subscript,
}


def get_baseclass(node: Node, parent: Class | Module) -> Name | Expression:
    """Extract a resolvable name for a given base class.

    Parameters:
        node: The base class node.
        parent: The parent used to resolve the name.

    Returns:
        A resovable name or expression.
    """
    return _node_baseclass_map.get(type(node), lambda node, parent: None)(node, parent)  # type: ignore


# ==========================================================
# annotations
def _get_name_annotation(node: NodeName, parent: Class | Module) -> Name:
    return Name(node.id, partial(parent.resolve, node.id))


def _get_constant_annotation(node: NodeConstant, parent: Class | Module) -> str:
    return repr(node.value)


def _get_attribute_annotation(node: NodeAttribute, parent: Class | Module) -> Expression:
    left = get_annotation(node.value, parent)

    def resolver():  # noqa: WPS430
        return f"{left.full}.{node.attr}"

    right = Name(node.attr, resolver)
    return Expression(left, ".", right)


def _get_binop_annotation(node: NodeBinOp, parent: Class | Module) -> Expression:
    left = get_annotation(node.left, parent)
    right = get_annotation(node.right, parent)
    return Expression(left, get_annotation(node.op, parent), right)


def _get_bitor_annotation(node: NodeBitOr, parent: Class | Module) -> str:
    return " | "


def _get_bitand_annotation(node: NodeBitOr, parent: Class | Module) -> str:
    return " & "


def _get_subscript_annotation(node: NodeSubscript, parent: Class | Module) -> Expression:
    left = get_annotation(node.value, parent)
    subscript = get_annotation(node.slice, parent)
    return Expression(left, "[", subscript, "]")


def _get_index_annotation(node: NodeIndex, parent: Class | Module) -> str | Name | Expression:
    return get_annotation(node.value, parent)  # type: ignore


def _get_tuple_annotation(node: NodeTuple, parent: Class | Module) -> Expression:
    return Expression(*_join([get_annotation(el, parent) for el in node.elts], ", "))


def _get_list_annotation(node: NodeList, parent: Class | Module) -> Expression:
    return Expression("[", *_join([get_annotation(el, parent) for el in node.elts], ", "), "]")


_node_annotation_map = {
    NodeName: _get_name_annotation,
    NodeConstant: _get_constant_annotation,
    NodeAttribute: _get_attribute_annotation,
    NodeBinOp: _get_binop_annotation,
    NodeBitOr: _get_bitor_annotation,
    NodeBitAnd: _get_bitand_annotation,
    NodeSubscript: _get_subscript_annotation,
    NodeIndex: _get_index_annotation,
    NodeTuple: _get_tuple_annotation,
    NodeList: _get_list_annotation,
}


def get_annotation(node: Node, parent: Class | Module) -> str | Name | Expression:
    """Extract a resolvable annotation.

    Parameters:
        node: The annotation node.
        parent: The parent used to resolve the name.

    Returns:
        A string or resovable name or expression.
    """
    return _node_annotation_map.get(type(node), lambda node, parent: None)(node, parent)  # type: ignore


# ==========================================================
# docstrings
def get_docstring(
    node: Node,
    strict: bool = False,
) -> tuple[str | None, int | None, int | None]:
    """Extract a docstring.

    Parameters:
        node: The node to extract the docstring from.
        strict: Whether to skip searching the body (functions).

    Returns:
        A tuple with the value and line numbers of the docstring.
    """
    # TODO: possible optimization using a type map
    if isinstance(node, NodeExpr):
        doc = node.value
    elif node.body and isinstance(node.body[0], NodeExpr) and not strict:  # type: ignore
        doc = node.body[0].value  # type: ignore
    else:
        return None, None, None
    if isinstance(doc, NodeConstant) and isinstance(doc.value, str):
        return doc.value, doc.lineno, doc.end_lineno
    if isinstance(doc, NodeStr):
        return doc.s, doc.lineno, doc.end_lineno
    return None, None, None


# ==========================================================
# values
def _get_name_value(node: NodeName):
    return node.id


def _get_constant_value(node: NodeConstant):
    return repr(node.value)


def _get_attribute_value(node: NodeAttribute):
    return f"{get_value(node.value)}.{node.attr}"


def _get_binop_value(node: NodeBinOp):
    return f"{get_value(node.left)} {get_value(node.op)} {get_value(node.right)}"


def _get_bitor_value(node: NodeBitOr):
    return "|"


def _get_mult_value(node: NodeMult):
    return "*"


def _get_unaryop_value(node: NodeUnaryOp):
    if isinstance(node.op, NodeUSub):
        return f"-{get_value(node.operand)}"
    if isinstance(node.op, NodeUAdd):
        return f"+{get_value(node.operand)}"
    if isinstance(node.op, NodeNot):
        return f"not {get_value(node.operand)}"


def _get_slice_value(node: NodeSlice):
    value = f"{get_value(node.lower) if node.lower else ''}:{get_value(node.upper) if node.upper else ''}"
    if node.step:
        value = f"{value}:{get_value(node.step)}"
    return value


def _get_subscript_value(node: NodeSubscript):
    return f"{get_value(node.value)}[{get_value(node.slice).strip('()')}]"


def _get_index_value(node: NodeIndex):
    return get_value(node.value)  # type: ignore


def _get_lambda_value(node: NodeLambda):
    return f"lambda {get_value(node.args)}: {get_value(node.body)}"


def _get_list_value(node: NodeList):
    return "[" + ", ".join(get_value(el) for el in node.elts) + "]"


def _get_tuple_value(node: NodeTuple):
    return "(" + ", ".join(get_value(el) for el in node.elts) + ")"


def _get_keyword_value(node: NodeKeyword):
    return f"{node.arg}={get_value(node.value)}"


def _get_dict_value(node: NodeDict):
    pairs = zip(node.keys, node.values)
    return "{" + ", ".join(f"{get_value(key)}: {get_value(value)}" for key, value in pairs) + "}"  # type: ignore


def _get_set_value(node: NodeSet):
    return "{" + ", ".join(get_value(el) for el in node.elts) + "}"


def _get_ellipsis_value(node: NodeEllipsis):
    return "..."


def _get_starred_value(node: NodeStarred):
    return get_value(node.value)


def _get_formatted_value(node: NodeFormattedValue):
    return f"{{{get_value(node.value)}}}"


def _get_joinedstr_value(node: NodeJoinedStr):
    return "".join(get_value(value) for value in node.values)


def _get_boolop_value(node: NodeBoolOp):
    if isinstance(node.op, NodeOr):
        return " or ".join(get_value(value) for value in node.values)
    if isinstance(node.op, NodeAnd):
        return " and ".join(get_value(value) for value in node.values)


def _get_compare_value(node: NodeCompare):
    left = get_value(node.left)
    ops = [get_value(op) for op in node.ops]
    comparators = [get_value(comparator) for comparator in node.comparators]
    return f"{left} " + " ".join(f"{op} {comp}" for op, comp in zip(ops, comparators))


def _get_noteq_value(node: NodeNotEq):
    return "!="


def _get_generatorexp_value(node: NodeGeneratorExp):
    element = get_value(node.elt)
    generators = [get_value(gen) for gen in node.generators]
    return f"{element} " + " ".join(generators)


def _get_listcomp_value(node: NodeListComp):
    element = get_value(node.elt)
    generators = [get_value(gen) for gen in node.generators]
    return f"[{element} " + " ".join(generators) + "]"


def _get_dictcomp_value(node: NodeDictComp):
    key = get_value(node.key)
    value = get_value(node.value)
    generators = [get_value(gen) for gen in node.generators]
    return f"{{{key}: {value} " + " ".join(generators) + "}"


def _get_comprehension_value(node: NodeComprehension):
    target = get_value(node.target)
    iterable = get_value(node.iter)
    conditions = [get_value(condition) for condition in node.ifs]
    value = f"for {target} in {iterable}"
    if conditions:
        value = f"{value} if " + " if ".join(conditions)
    if node.is_async:
        value = f"async {value}"
    return value


def _get_ifexp_value(node: NodeIfExp):
    return f"{get_value(node.body)} if {get_value(node.test)} else {get_value(node.orelse)}"


def _get_call_value(node: NodeCall):
    posargs = ", ".join(get_value(arg) for arg in node.args)
    kwargs = ", ".join(get_value(kwarg) for kwarg in node.keywords)
    if posargs and kwargs:
        args = f"{posargs}, {kwargs}"
    elif posargs:
        args = posargs
    elif kwargs:
        args = kwargs
    else:
        args = ""
    return f"{get_value(node.func)}({args})"


_node_value_map = {
    type(None): lambda _: repr(None),
    NodeName: _get_name_value,
    NodeConstant: _get_constant_value,
    NodeAttribute: _get_attribute_value,
    NodeBinOp: _get_binop_value,
    NodeUnaryOp: _get_unaryop_value,
    NodeEllipsis: _get_ellipsis_value,
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


def get_value(node: Node) -> str:
    """Extract a complex value as a string.

    Parameters:
        node: The node to extract the value from.

    Returns:
        The unparsed code of the node.
    """
    return _node_value_map.get(type(node), lambda _: None)(node)  # type: ignore


# ==========================================================
# names
def _get_attribute_name(node: NodeAttribute):
    return f"{get_names(node.value)}.{node.attr}"


def _get_name_name(node: NodeName):
    return node.id


def _get_assign_names(node: NodeAssign):
    names = (get_names(target) for target in node.targets)
    return [name for name in names if name]


def _get_annassign_names(node: NodeAnnAssign):
    name = get_names(node.target)
    return [name] if name else []


_node_names_map = {
    NodeAssign: _get_assign_names,
    NodeAnnAssign: _get_annassign_names,
    NodeName: _get_name_name,
    NodeAttribute: _get_attribute_name,
}


def get_names(node: Node) -> list[str]:
    """Extract names from an assignment node.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return _node_names_map.get(type(node), lambda _: None)(node)  # type: ignore


def get_instance_names(node: Node) -> list[str]:
    """Extract names from an assignment node, only for instance attributes.

    Parameters:
        node: The node to extract names from.

    Returns:
        A list of names.
    """
    return [name.split(".", 1)[1] for name in get_names(node) if name.startswith("self.")]


# ==========================================================
# parameters
def get_parameter_default(node: Node, filepath: Path, lines_collection: LinesCollection) -> str | None:
    """Extract the default value of a function parameter.

    Parameters:
        node: The node to extract the default value from.
        filepath: The filepath in which the parameter is written.
            It allows to retrieve the actual code directly from the lines collection.
        lines_collection: A collection of source code lines.

    Returns:
        The default value as a string.
    """
    if node is None:
        return None
    if isinstance(node, NodeConstant):
        return repr(node.value)
    if isinstance(node, NodeName):
        return node.id
    if node.lineno == node.end_lineno:
        return lines_collection[filepath][node.lineno - 1][node.col_offset : node.end_col_offset]
    # TODO: handle multiple line defaults
    return None
