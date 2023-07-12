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
from ast import arguments as NodeArguments
from ast import comprehension as NodeComprehension
from ast import keyword as NodeKeyword
from typing import TYPE_CHECKING, Any, Callable

from griffe.logger import get_logger

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):
    from ast import ExtSlice as NodeExtSlice
    from ast import Index as NodeIndex

if TYPE_CHECKING:
    from pathlib import Path


logger = get_logger(__name__)


def _extract_add(node: NodeAdd, **kwargs: Any) -> str:
    return "+"


def _extract_and(node: NodeAnd, **kwargs: Any) -> str:
    return "and"


def _extract_arguments(node: NodeArguments, **kwargs: Any) -> str:
    return ", ".join(arg.arg for arg in node.args)


def _extract_attribute(node: NodeAttribute, **kwargs: Any) -> str:
    return f"{_extract(node.value, **kwargs)}.{node.attr}"


def _extract_binop(node: NodeBinOp, **kwargs: Any) -> str:
    return f"{_extract(node.left, **kwargs)} {_extract(node.op, **kwargs)} {_extract(node.right, **kwargs)}"


def _extract_bitor(node: NodeBitOr, **kwargs: Any) -> str:
    return "|"


def _extract_bitand(node: NodeBitAnd, **kwargs: Any) -> str:
    return "&"


def _extract_bitxor(node: NodeBitXor, **kwargs: Any) -> str:
    return "^"


def _extract_boolop(node: NodeBoolOp, **kwargs: Any) -> str:
    return f" {_extract(node.op, **kwargs)} ".join(_extract(value, **kwargs) for value in node.values)


def _extract_call(node: NodeCall, **kwargs: Any) -> str:
    positional_args = ", ".join(_extract(arg, **kwargs) for arg in node.args)
    keyword_args = ", ".join(_extract(kwarg, **kwargs) for kwarg in node.keywords)
    if positional_args and keyword_args:
        args = f"{positional_args}, {keyword_args}"
    elif positional_args:
        args = positional_args
    elif keyword_args:
        args = keyword_args
    else:
        args = ""
    return f"{_extract(node.func, **kwargs)}({args})"


def _extract_compare(node: NodeCompare, **kwargs: Any) -> str:
    left = _extract(node.left, **kwargs)
    ops = [_extract(op, **kwargs) for op in node.ops]
    comparators = [_extract(comparator, **kwargs) for comparator in node.comparators]
    return f"{left} " + " ".join(f"{op} {comp}" for op, comp in zip(ops, comparators))


def _extract_comprehension(node: NodeComprehension, **kwargs: Any) -> str:
    target = _extract(node.target, **kwargs)
    iterable = _extract(node.iter, **kwargs)
    conditions = [_extract(condition, **kwargs) for condition in node.ifs]
    value = f"for {target} in {iterable}"
    if conditions:
        value = f"{value} if " + " if ".join(conditions)
    if node.is_async:
        return f"async {value}"
    return value


def _extract_constant(
    node: NodeConstant,
    *,
    in_formatted_str: bool = False,
    in_joined_str: bool = False,
    **kwargs: Any,
) -> str:
    if in_joined_str and not in_formatted_str and isinstance(node.value, str):
        return node.value
    return {type(...): lambda _: "..."}.get(type(node.value), repr)(node.value)


def _extract_dict(node: NodeDict, **kwargs: Any) -> str:
    pairs = zip(node.keys, node.values)
    gen = (f"{'None' if key is None else _extract(key, **kwargs)}: {_extract(value, **kwargs)}" for key, value in pairs)
    return "{" + ", ".join(gen) + "}"


def _extract_dictcomp(node: NodeDictComp, **kwargs: Any) -> str:
    key = _extract(node.key, **kwargs)
    value = _extract(node.value, **kwargs)
    generators = [_extract(gen, **kwargs) for gen in node.generators]
    return f"{{{key}: {value} " + " ".join(generators) + "}"


def _extract_div(node: NodeDiv, **kwargs: Any) -> str:
    return "/"


def _extract_ellipsis(node: NodeEllipsis, **kwargs: Any) -> str:
    return "..."


def _extract_eq(node: NodeEq, **kwargs: Any) -> str:
    return "=="


def _extract_floordiv(node: NodeFloorDiv, **kwargs: Any) -> str:
    return "//"


def _extract_formatted(node: NodeFormattedValue, **kwargs: Any) -> str:
    return f"{{{_extract(node.value, in_formatted_str=True, **kwargs)}}}"


def _extract_generatorexp(node: NodeGeneratorExp, **kwargs: Any) -> str:
    element = _extract(node.elt, **kwargs)
    generators = [_extract(gen, **kwargs) for gen in node.generators]
    return f"{element} " + " ".join(generators)


def _extract_gte(node: NodeNotEq, **kwargs: Any) -> str:
    return ">="


def _extract_gt(node: NodeNotEq, **kwargs: Any) -> str:
    return ">"


def _extract_ifexp(node: NodeIfExp, **kwargs: Any) -> str:
    return f"{_extract(node.body, **kwargs)} if {_extract(node.test, **kwargs)} else {_extract(node.orelse, **kwargs)}"


def _extract_invert(node: NodeInvert, **kwargs: Any) -> str:
    return "~"


def _extract_in(node: NodeIn, **kwargs: Any) -> str:
    return "in"


def _extract_is(node: NodeIs, **kwargs: Any) -> str:
    return "is"


def _extract_isnot(node: NodeIsNot, **kwargs: Any) -> str:
    return "is not"


def _extract_joinedstr(node: NodeJoinedStr, **kwargs: Any) -> str:
    return "f" + repr("".join(_extract(value, in_joined_str=True, **kwargs) for value in node.values))


def _extract_keyword(node: NodeKeyword, **kwargs: Any) -> str:
    if node.arg is None:
        return f"**{_extract(node.value, **kwargs)}"
    return f"{node.arg}={_extract(node.value, **kwargs)}"


def _extract_lambda(node: NodeLambda, **kwargs: Any) -> str:
    return f"lambda {_extract(node.args, **kwargs)}: {_extract(node.body, **kwargs)}"


def _extract_list(node: NodeList, **kwargs: Any) -> str:
    return "[" + ", ".join(_extract(el, **kwargs) for el in node.elts) + "]"


def _extract_listcomp(node: NodeListComp, **kwargs: Any) -> str:
    element = _extract(node.elt, **kwargs)
    generators = [_extract(gen, **kwargs) for gen in node.generators]
    return f"[{element} " + " ".join(generators) + "]"


def _extract_lshift(node: NodeLShift, **kwargs: Any) -> str:
    return "<<"


def _extract_lte(node: NodeNotEq, **kwargs: Any) -> str:
    return "<="


def _extract_lt(node: NodeNotEq, **kwargs: Any) -> str:
    return "<"


def _extract_matmult(node: NodeMatMult, **kwargs: Any) -> str:
    return "@"


def _extract_mod(node: NodeMod, **kwargs: Any) -> str:
    return "%"


def _extract_mult(node: NodeMult, **kwargs: Any) -> str:
    return "*"


def _extract_name(node: NodeName, **kwargs: Any) -> str:
    return node.id


def _extract_named_expr(node: NodeNamedExpr, **kwargs: Any) -> str:
    return f"({_extract(node.target, **kwargs)} := {_extract(node.value, **kwargs)})"


def _extract_not(node: NodeNot, **kwargs: Any) -> str:
    return "not "


def _extract_noteq(node: NodeNotEq, **kwargs: Any) -> str:
    return "!="


def _extract_notin(node: NodeNotIn, **kwargs: Any) -> str:
    return "not in"


def _extract_or(node: NodeOr, **kwargs: Any) -> str:
    return "or"


def _extract_pow(node: NodePow, **kwargs: Any) -> str:
    return "**"


def _extract_rshift(node: NodeRShift, **kwargs: Any) -> str:
    return ">>"


def _extract_set(node: NodeSet, **kwargs: Any) -> str:
    return "{" + ", ".join(_extract(el, **kwargs) for el in node.elts) + "}"


def _extract_setcomp(node: NodeSetComp, **kwargs: Any) -> str:
    element = _extract(node.elt, **kwargs)
    generators = [_extract(gen, **kwargs) for gen in node.generators]
    return f"{{{element} " + " ".join(generators) + "}"


def _extract_slice(node: NodeSlice, **kwargs: Any) -> str:
    lower = _extract(node.lower, **kwargs) if node.lower else ""
    upper = _extract(node.upper, **kwargs) if node.upper else ""
    value = f"{lower}:{upper}"
    if node.step:
        return f"{value}:{_extract(node.step, **kwargs)}"
    return value


def _extract_starred(node: NodeStarred, **kwargs: Any) -> str:
    return f"*{_extract(node.value, **kwargs)}"


def _extract_sub(node: NodeSub, **kwargs: Any) -> str:
    return "-"


def _extract_subscript(node: NodeSubscript, **kwargs: Any) -> str:
    subscript = _extract(node.slice, **kwargs)
    if isinstance(subscript, str) and subscript.startswith("(") and subscript.endswith(")"):
        subscript = subscript[1:-1]
    return f"{_extract(node.value, **kwargs)}[{subscript}]"


def _extract_tuple(node: NodeTuple, **kwargs: Any) -> str:
    return "(" + ", ".join(_extract(el, **kwargs) for el in node.elts) + ")"


def _extract_uadd(node: NodeUAdd, **kwargs: Any) -> str:
    return "+"


def _extract_unaryop(node: NodeUnaryOp, **kwargs: Any) -> str:
    return f"{_extract(node.op, **kwargs)}{_extract(node.operand, **kwargs)}"


def _extract_usub(node: NodeUSub, **kwargs: Any) -> str:
    return "-"


def _extract_yield(node: NodeYield, **kwargs: Any) -> str:
    if node.value is None:
        return repr(None)
    return _extract(node.value, **kwargs)


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

    def _extract_extslice(node: NodeExtSlice, **kwargs: Any) -> str:
        return ",".join(_extract(dim, **kwargs) for dim in node.dims)

    def _extract_index(node: NodeIndex, **kwargs: Any) -> str:
        return _extract(node.value, **kwargs)

    _node_map[NodeExtSlice] = _extract_extslice
    _node_map[NodeIndex] = _extract_index


def _extract(node: AST, **kwargs: Any) -> str:
    return _node_map[type(node)](node, **kwargs)


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


__all__ = ["get_value", "safe_get_value"]
