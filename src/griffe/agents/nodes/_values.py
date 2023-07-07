"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

import sys
from ast import AST
from ast import Add as NodeAdd
from ast import And as NodeAnd
from ast import Attribute as NodeAttribute
from ast import BinOp as NodeBinOp
from ast import BitAnd as NodeBitAnd
from ast import BitOr as NodeBitOr
from ast import BitXor as NodeBitXor
from ast import BoolOp as NodeBoolOp
from ast import Call as NodeCall
from ast import Compare as NodeCompare
from ast import Constant as NodeConstant
from ast import Dict as NodeDict
from ast import DictComp as NodeDictComp
from ast import Div as NodeDiv
from ast import Ellipsis as NodeEllipsis
from ast import Eq as NodeEq
from ast import FloorDiv as NodeFloorDiv
from ast import FormattedValue as NodeFormattedValue
from ast import GeneratorExp as NodeGeneratorExp
from ast import Gt as NodeGt
from ast import GtE as NodeGtE
from ast import IfExp as NodeIfExp
from ast import In as NodeIn
from ast import Invert as NodeInvert
from ast import Is as NodeIs
from ast import IsNot as NodeIsNot
from ast import JoinedStr as NodeJoinedStr
from ast import Lambda as NodeLambda
from ast import List as NodeList
from ast import ListComp as NodeListComp
from ast import LShift as NodeLShift
from ast import Lt as NodeLt
from ast import LtE as NodeLtE
from ast import MatMult as NodeMatMult
from ast import Mod as NodeMod
from ast import Mult as NodeMult
from ast import Name as NodeName
from ast import NamedExpr as NodeNamedExpr
from ast import Not as NodeNot
from ast import NotEq as NodeNotEq
from ast import NotIn as NodeNotIn
from ast import Or as NodeOr
from ast import Pow as NodePow
from ast import RShift as NodeRShift
from ast import Set as NodeSet
from ast import SetComp as NodeSetComp
from ast import Slice as NodeSlice
from ast import Starred as NodeStarred
from ast import Sub as NodeSub
from ast import Subscript as NodeSubscript
from ast import Tuple as NodeTuple
from ast import UAdd as NodeUAdd
from ast import UnaryOp as NodeUnaryOp
from ast import USub as NodeUSub
from ast import Yield as NodeYield
from ast import arguments as NodeArguments  # noqa: N812
from ast import comprehension as NodeComprehension  # noqa: N812
from ast import keyword as NodeKeyword  # noqa: N812
from typing import TYPE_CHECKING, Any, Callable

from griffe.logger import get_logger

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):
    from ast import ExtSlice as NodeExtSlice
    from ast import Index as NodeIndex

if TYPE_CHECKING:
    from pathlib import Path


logger = get_logger(__name__)


def _extract_add(node: NodeAdd) -> str:  # noqa: ARG001
    return "+"


def _extract_and(node: NodeAnd) -> str:  # noqa: ARG001
    return " and "


def _extract_arguments(node: NodeArguments) -> str:
    return ", ".join(arg.arg for arg in node.args)


def _extract_attribute(node: NodeAttribute) -> str:
    return f"{_extract(node.value)}.{node.attr}"


def _extract_binop(node: NodeBinOp) -> str:
    return f"{_extract(node.left)} {_extract(node.op)} {_extract(node.right)}"


def _extract_bitor(node: NodeBitOr) -> str:  # noqa: ARG001
    return "|"


def _extract_bitand(node: NodeBitAnd) -> str:  # noqa: ARG001
    return "&"


def _extract_bitxor(node: NodeBitXor) -> str:  # noqa: ARG001
    return "^"


def _extract_boolop(node: NodeBoolOp) -> str:
    return _extract(node.op).join(_extract(value) for value in node.values)


def _extract_call(node: NodeCall) -> str:
    posargs = ", ".join(_extract(arg) for arg in node.args)
    kwargs = ", ".join(_extract(kwarg) for kwarg in node.keywords)
    if posargs and kwargs:
        args = f"{posargs}, {kwargs}"
    elif posargs:
        args = posargs
    elif kwargs:
        args = kwargs
    else:
        args = ""
    return f"{_extract(node.func)}({args})"


def _extract_compare(node: NodeCompare) -> str:
    left = _extract(node.left)
    ops = [_extract(op) for op in node.ops]
    comparators = [_extract(comparator) for comparator in node.comparators]
    return f"{left} " + " ".join(f"{op} {comp}" for op, comp in zip(ops, comparators))


def _extract_comprehension(node: NodeComprehension) -> str:
    target = _extract(node.target)
    iterable = _extract(node.iter)
    conditions = [_extract(condition) for condition in node.ifs]
    value = f"for {target} in {iterable}"
    if conditions:
        value = f"{value} if " + " if ".join(conditions)
    if node.is_async:
        return f"async {value}"
    return value


def _extract_constant(node: NodeConstant) -> str:
    return repr(node.value)


def _extract_constant_no_string_repr(node: NodeConstant) -> str:
    if isinstance(node.value, str):
        return node.value
    return repr(node.value)


def _extract_dict(node: NodeDict) -> str:
    pairs = zip(node.keys, node.values)
    gen = (f"{'None' if key is None else _extract(key)}: {_extract(value)}" for key, value in pairs)
    return "{" + ", ".join(gen) + "}"


def _extract_dictcomp(node: NodeDictComp) -> str:
    key = _extract(node.key)
    value = _extract(node.value)
    generators = [_extract(gen) for gen in node.generators]
    return f"{{{key}: {value} " + " ".join(generators) + "}"


def _extract_div(node: NodeDiv) -> str:  # noqa: ARG001
    return "/"


def _extract_ellipsis(node: NodeEllipsis) -> str:  # noqa: ARG001
    return "..."


def _extract_eq(node: NodeEq) -> str:  # noqa: ARG001
    return "=="


def _extract_floordiv(node: NodeFloorDiv) -> str:  # noqa: ARG001
    return "//"


def _extract_formatted(node: NodeFormattedValue) -> str:
    return f"{{{_extract(node.value)}}}"


def _extract_generatorexp(node: NodeGeneratorExp) -> str:
    element = _extract(node.elt)
    generators = [_extract(gen) for gen in node.generators]
    return f"{element} " + " ".join(generators)


def _extract_gte(node: NodeNotEq) -> str:  # noqa: ARG001
    return ">="


def _extract_gt(node: NodeNotEq) -> str:  # noqa: ARG001
    return ">"


def _extract_ifexp(node: NodeIfExp) -> str:
    return f"{_extract(node.body)} if {_extract(node.test)} else {_extract(node.orelse)}"


def _extract_invert(node: NodeInvert) -> str:  # noqa: ARG001
    return "~"


def _extract_in(node: NodeIn) -> str:  # noqa: ARG001
    return "in"


def _extract_is(node: NodeIs) -> str:  # noqa: ARG001
    return "is"


def _extract_isnot(node: NodeIsNot) -> str:  # noqa: ARG001
    return "is not"


def _extract_joinedstr(node: NodeJoinedStr) -> str:
    _node_map[NodeConstant] = _extract_constant_no_string_repr
    try:
        return "f" + repr("".join(_extract(value) for value in node.values))
    finally:
        _node_map[NodeConstant] = _extract_constant


def _extract_keyword(node: NodeKeyword) -> str:
    return f"{node.arg}={_extract(node.value)}"


def _extract_lambda(node: NodeLambda) -> str:
    return f"lambda {_extract(node.args)}: {_extract(node.body)}"


def _extract_list(node: NodeList) -> str:
    return "[" + ", ".join(_extract(el) for el in node.elts) + "]"


def _extract_listcomp(node: NodeListComp) -> str:
    element = _extract(node.elt)
    generators = [_extract(gen) for gen in node.generators]
    return f"[{element} " + " ".join(generators) + "]"


def _extract_lshift(node: NodeLShift) -> str:  # noqa: ARG001
    return "<<"


def _extract_lte(node: NodeNotEq) -> str:  # noqa: ARG001
    return "<="


def _extract_lt(node: NodeNotEq) -> str:  # noqa: ARG001
    return "<"


def _extract_matmult(node: NodeMatMult) -> str:  # noqa: ARG001
    return "@"


def _extract_mod(node: NodeMod) -> str:  # noqa: ARG001
    return "%"


def _extract_mult(node: NodeMult) -> str:  # noqa: ARG001
    return "*"


def _extract_name(node: NodeName) -> str:
    return node.id


def _extract_not(node: NodeNot) -> str:  # noqa: ARG001
    return "not "


def _extract_noteq(node: NodeNotEq) -> str:  # noqa: ARG001
    return "!="


def _extract_notin(node: NodeNotIn) -> str:  # noqa: ARG001
    return "not in"


def _extract_or(node: NodeOr) -> str:  # noqa: ARG001
    return " or "


def _extract_pow(node: NodePow) -> str:  # noqa: ARG001
    return "**"


def _extract_rshift(node: NodeRShift) -> str:  # noqa: ARG001
    return ">>"


def _extract_set(node: NodeSet) -> str:
    return "{" + ", ".join(_extract(el) for el in node.elts) + "}"


def _extract_setcomp(node: NodeSetComp) -> str:
    element = _extract(node.elt)
    generators = [_extract(gen) for gen in node.generators]
    return f"{{{element} " + " ".join(generators) + "}"


def _extract_slice(node: NodeSlice) -> str:
    value = f"{_extract(node.lower) if node.lower else ''}:{_extract(node.upper) if node.upper else ''}"
    if node.step:
        return f"{value}:{_extract(node.step)}"
    return value


def _extract_starred(node: NodeStarred) -> str:
    return _extract(node.value)


def _extract_sub(node: NodeSub) -> str:  # noqa: ARG001
    return "-"


def _extract_subscript(node: NodeSubscript) -> str:
    subscript = _extract(node.slice)
    if isinstance(subscript, str) and subscript.startswith("(") and subscript.endswith(")"):
        subscript = subscript[1:-1]
    return f"{_extract(node.value)}[{subscript}]"


def _extract_tuple(node: NodeTuple) -> str:
    return "(" + ", ".join(_extract(el) for el in node.elts) + ")"


def _extract_uadd(node: NodeUAdd) -> str:  # noqa: ARG001
    return "+"


def _extract_unaryop(node: NodeUnaryOp) -> str:
    return f"{_extract(node.op)}{_extract(node.operand)}"


def _extract_usub(node: NodeUSub) -> str:  # noqa: ARG001
    return "-"


def _extract_yield(node: NodeYield) -> str:
    if node.value is None:
        return repr(None)
    return _extract(node.value)


def _extract_named_expr(node: NodeNamedExpr) -> str:
    return f"({_extract(node.target)} := {_extract(node.value)})"


_node_map: dict[type, Callable[[Any], str]] = {
    NodeAdd: _extract_add,
    NodeAnd: _extract_and,
    NodeArguments: _extract_arguments,
    NodeAttribute: _extract_attribute,
    NodeBinOp: _extract_binop,
    NodeBitAnd: _extract_bitand,
    NodeBitOr: _extract_bitor,
    NodeBitXor: _extract_bitxor,
    NodeBoolOp: _extract_boolop,
    NodeCall: _extract_call,
    NodeCompare: _extract_compare,
    NodeComprehension: _extract_comprehension,
    NodeConstant: _extract_constant,
    NodeDictComp: _extract_dictcomp,
    NodeDict: _extract_dict,
    NodeDiv: _extract_div,
    NodeEllipsis: _extract_ellipsis,
    NodeEq: _extract_eq,
    NodeFloorDiv: _extract_floordiv,
    NodeFormattedValue: _extract_formatted,
    NodeGeneratorExp: _extract_generatorexp,
    NodeGtE: _extract_gte,
    NodeGt: _extract_gt,
    NodeIfExp: _extract_ifexp,
    NodeIn: _extract_in,
    NodeInvert: _extract_invert,
    NodeIs: _extract_is,
    NodeIsNot: _extract_isnot,
    NodeJoinedStr: _extract_joinedstr,
    NodeKeyword: _extract_keyword,
    NodeLambda: _extract_lambda,
    NodeListComp: _extract_listcomp,
    NodeList: _extract_list,
    NodeLShift: _extract_lshift,
    NodeLtE: _extract_lte,
    NodeLt: _extract_lt,
    NodeMatMult: _extract_matmult,
    NodeMod: _extract_mod,
    NodeMult: _extract_mult,
    NodeName: _extract_name,
    NodeNamedExpr: _extract_named_expr,
    NodeNotEq: _extract_noteq,
    NodeNot: _extract_not,
    NodeNotIn: _extract_notin,
    NodeOr: _extract_or,
    NodePow: _extract_pow,
    NodeRShift: _extract_rshift,
    NodeSetComp: _extract_setcomp,
    NodeSet: _extract_set,
    NodeSlice: _extract_slice,
    NodeStarred: _extract_starred,
    NodeSub: _extract_sub,
    NodeSubscript: _extract_subscript,
    NodeTuple: _extract_tuple,
    NodeUAdd: _extract_uadd,
    NodeUnaryOp: _extract_unaryop,
    NodeUSub: _extract_usub,
    NodeYield: _extract_yield,
}

# TODO: remove once Python 3.8 support is
if sys.version_info < (3, 9):

    def _extract_extslice(node: NodeExtSlice) -> str:
        return ",".join(_extract(dim) for dim in node.dims)

    def _extract_index(node: NodeIndex) -> str:
        return _extract(node.value)

    _node_map[NodeExtSlice] = _extract_extslice
    _node_map[NodeIndex] = _extract_index


def _extract(node: AST) -> str:
    return _node_map[type(node)](node)


def get_value(node: AST | None) -> str | None:
    """Get the string representation of a node.

    Parameters:
        node: The node to represent.

    Returns:
        The representing code for the node.
    """
    if node is None:
        return None
    return _extract(node)


def safe_get_value(node: AST | None, filepath: str | Path | None = None) -> str | None:
    """Safely (no exception) get the string representation of a node.

    Parameters:
        node: The node to represent.
        filepath: An optional filepath from where the node comes.

    Returns:
        The representing code for the node.
    """
    try:
        return get_value(node)
    except Exception as error:
        message = f"Failed to represent node {node}"
        if filepath:
            message += f" at {filepath}:{node.lineno}"  # type: ignore[union-attr]
        message += f": {error}"
        logger.exception(message)
        return None
