"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

import ast
import sys
from typing import TYPE_CHECKING, Any, Callable

from griffe.logger import get_logger

if TYPE_CHECKING:
    from pathlib import Path


logger = get_logger(__name__)


def _extract_add(node: ast.Add, **kwargs: Any) -> str:
    return "+"


def _extract_and(node: ast.And, **kwargs: Any) -> str:
    return "and"


def _extract_arguments(node: ast.arguments, **kwargs: Any) -> str:
    return ", ".join(arg.arg for arg in node.args)


def _extract_attribute(node: ast.Attribute, **kwargs: Any) -> str:
    return f"{_extract(node.value, **kwargs)}.{node.attr}"


def _extract_binop(node: ast.BinOp, **kwargs: Any) -> str:
    return f"{_extract(node.left, **kwargs)} {_extract(node.op, **kwargs)} {_extract(node.right, **kwargs)}"


def _extract_bitor(node: ast.BitOr, **kwargs: Any) -> str:
    return "|"


def _extract_bitand(node: ast.BitAnd, **kwargs: Any) -> str:
    return "&"


def _extract_bitxor(node: ast.BitXor, **kwargs: Any) -> str:
    return "^"


def _extract_boolop(node: ast.BoolOp, **kwargs: Any) -> str:
    return f" {_extract(node.op, **kwargs)} ".join(_extract(value, **kwargs) for value in node.values)


def _extract_call(node: ast.Call, **kwargs: Any) -> str:
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


def _extract_compare(node: ast.Compare, **kwargs: Any) -> str:
    left = _extract(node.left, **kwargs)
    ops = [_extract(op, **kwargs) for op in node.ops]
    comparators = [_extract(comparator, **kwargs) for comparator in node.comparators]
    return f"{left} " + " ".join(f"{op} {comp}" for op, comp in zip(ops, comparators))


def _extract_comprehension(node: ast.comprehension, **kwargs: Any) -> str:
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
    node: ast.Constant,
    *,
    in_formatted_str: bool = False,
    in_joined_str: bool = False,
    **kwargs: Any,
) -> str:
    if in_joined_str and not in_formatted_str and isinstance(node.value, str):
        return node.value
    return {type(...): lambda _: "..."}.get(type(node.value), repr)(node.value)


def _extract_dict(node: ast.Dict, **kwargs: Any) -> str:
    pairs = zip(node.keys, node.values)
    gen = (f"{'None' if key is None else _extract(key, **kwargs)}: {_extract(value, **kwargs)}" for key, value in pairs)
    return "{" + ", ".join(gen) + "}"


def _extract_dictcomp(node: ast.DictComp, **kwargs: Any) -> str:
    key = _extract(node.key, **kwargs)
    value = _extract(node.value, **kwargs)
    generators = [_extract(gen, **kwargs) for gen in node.generators]
    return f"{{{key}: {value} " + " ".join(generators) + "}"


def _extract_div(node: ast.Div, **kwargs: Any) -> str:
    return "/"


def _extract_eq(node: ast.Eq, **kwargs: Any) -> str:
    return "=="


def _extract_floordiv(node: ast.FloorDiv, **kwargs: Any) -> str:
    return "//"


def _extract_formatted(node: ast.FormattedValue, **kwargs: Any) -> str:
    return f"{{{_extract(node.value, in_formatted_str=True, **kwargs)}}}"


def _extract_generatorexp(node: ast.GeneratorExp, **kwargs: Any) -> str:
    element = _extract(node.elt, **kwargs)
    generators = [_extract(gen, **kwargs) for gen in node.generators]
    return f"{element} " + " ".join(generators)


def _extract_gte(node: ast.NotEq, **kwargs: Any) -> str:
    return ">="


def _extract_gt(node: ast.NotEq, **kwargs: Any) -> str:
    return ">"


def _extract_ifexp(node: ast.IfExp, **kwargs: Any) -> str:
    return f"{_extract(node.body, **kwargs)} if {_extract(node.test, **kwargs)} else {_extract(node.orelse, **kwargs)}"


def _extract_invert(node: ast.Invert, **kwargs: Any) -> str:
    return "~"


def _extract_in(node: ast.In, **kwargs: Any) -> str:
    return "in"


def _extract_is(node: ast.Is, **kwargs: Any) -> str:
    return "is"


def _extract_isnot(node: ast.IsNot, **kwargs: Any) -> str:
    return "is not"


def _extract_joinedstr(node: ast.JoinedStr, **kwargs: Any) -> str:
    return "f" + repr("".join(_extract(value, in_joined_str=True, **kwargs) for value in node.values))


def _extract_keyword(node: ast.keyword, **kwargs: Any) -> str:
    if node.arg is None:
        return f"**{_extract(node.value, **kwargs)}"
    return f"{node.arg}={_extract(node.value, **kwargs)}"


def _extract_lambda(node: ast.Lambda, **kwargs: Any) -> str:
    return f"lambda {_extract(node.args, **kwargs)}: {_extract(node.body, **kwargs)}"


def _extract_list(node: ast.List, **kwargs: Any) -> str:
    return "[" + ", ".join(_extract(el, **kwargs) for el in node.elts) + "]"


def _extract_listcomp(node: ast.ListComp, **kwargs: Any) -> str:
    element = _extract(node.elt, **kwargs)
    generators = [_extract(gen, **kwargs) for gen in node.generators]
    return f"[{element} " + " ".join(generators) + "]"


def _extract_lshift(node: ast.LShift, **kwargs: Any) -> str:
    return "<<"


def _extract_lte(node: ast.NotEq, **kwargs: Any) -> str:
    return "<="


def _extract_lt(node: ast.NotEq, **kwargs: Any) -> str:
    return "<"


def _extract_matmult(node: ast.MatMult, **kwargs: Any) -> str:
    return "@"


def _extract_mod(node: ast.Mod, **kwargs: Any) -> str:
    return "%"


def _extract_mult(node: ast.Mult, **kwargs: Any) -> str:
    return "*"


def _extract_name(node: ast.Name, **kwargs: Any) -> str:
    return node.id


def _extract_named_expr(node: ast.NamedExpr, **kwargs: Any) -> str:
    return f"({_extract(node.target, **kwargs)} := {_extract(node.value, **kwargs)})"


def _extract_not(node: ast.Not, **kwargs: Any) -> str:
    return "not "


def _extract_noteq(node: ast.NotEq, **kwargs: Any) -> str:
    return "!="


def _extract_notin(node: ast.NotIn, **kwargs: Any) -> str:
    return "not in"


def _extract_or(node: ast.Or, **kwargs: Any) -> str:
    return "or"


def _extract_pow(node: ast.Pow, **kwargs: Any) -> str:
    return "**"


def _extract_rshift(node: ast.RShift, **kwargs: Any) -> str:
    return ">>"


def _extract_set(node: ast.Set, **kwargs: Any) -> str:
    return "{" + ", ".join(_extract(el, **kwargs) for el in node.elts) + "}"


def _extract_setcomp(node: ast.SetComp, **kwargs: Any) -> str:
    element = _extract(node.elt, **kwargs)
    generators = [_extract(gen, **kwargs) for gen in node.generators]
    return f"{{{element} " + " ".join(generators) + "}"


def _extract_slice(node: ast.Slice, **kwargs: Any) -> str:
    lower = _extract(node.lower, **kwargs) if node.lower else ""
    upper = _extract(node.upper, **kwargs) if node.upper else ""
    value = f"{lower}:{upper}"
    if node.step:
        return f"{value}:{_extract(node.step, **kwargs)}"
    return value


def _extract_starred(node: ast.Starred, **kwargs: Any) -> str:
    return f"*{_extract(node.value, **kwargs)}"


def _extract_sub(node: ast.Sub, **kwargs: Any) -> str:
    return "-"


def _extract_subscript(node: ast.Subscript, **kwargs: Any) -> str:
    subscript = _extract(node.slice, **kwargs)
    if isinstance(subscript, str) and subscript.startswith("(") and subscript.endswith(")"):
        subscript = subscript[1:-1]
    return f"{_extract(node.value, **kwargs)}[{subscript}]"


def _extract_tuple(node: ast.Tuple, **kwargs: Any) -> str:
    return "(" + ", ".join(_extract(el, **kwargs) for el in node.elts) + ")"


def _extract_uadd(node: ast.UAdd, **kwargs: Any) -> str:
    return "+"


def _extract_unaryop(node: ast.UnaryOp, **kwargs: Any) -> str:
    return f"{_extract(node.op, **kwargs)}{_extract(node.operand, **kwargs)}"


def _extract_usub(node: ast.USub, **kwargs: Any) -> str:
    return "-"


def _extract_yield(node: ast.Yield, **kwargs: Any) -> str:
    if node.value is None:
        return repr(None)
    return _extract(node.value, **kwargs)


_node_map: dict[type, Callable[[Any], str]] = {
    ast.Add: _extract_add,
    ast.And: _extract_and,
    ast.arguments: _extract_arguments,
    ast.Attribute: _extract_attribute,
    ast.BinOp: _extract_binop,
    ast.BitAnd: _extract_bitand,
    ast.BitOr: _extract_bitor,
    ast.BitXor: _extract_bitxor,
    ast.BoolOp: _extract_boolop,
    ast.Call: _extract_call,
    ast.Compare: _extract_compare,
    ast.comprehension: _extract_comprehension,
    ast.Constant: _extract_constant,
    ast.DictComp: _extract_dictcomp,
    ast.Dict: _extract_dict,
    ast.Div: _extract_div,
    ast.Eq: _extract_eq,
    ast.FloorDiv: _extract_floordiv,
    ast.FormattedValue: _extract_formatted,
    ast.GeneratorExp: _extract_generatorexp,
    ast.GtE: _extract_gte,
    ast.Gt: _extract_gt,
    ast.IfExp: _extract_ifexp,
    ast.In: _extract_in,
    ast.Invert: _extract_invert,
    ast.Is: _extract_is,
    ast.IsNot: _extract_isnot,
    ast.JoinedStr: _extract_joinedstr,
    ast.keyword: _extract_keyword,
    ast.Lambda: _extract_lambda,
    ast.ListComp: _extract_listcomp,
    ast.List: _extract_list,
    ast.LShift: _extract_lshift,
    ast.LtE: _extract_lte,
    ast.Lt: _extract_lt,
    ast.MatMult: _extract_matmult,
    ast.Mod: _extract_mod,
    ast.Mult: _extract_mult,
    ast.Name: _extract_name,
    ast.NamedExpr: _extract_named_expr,
    ast.NotEq: _extract_noteq,
    ast.Not: _extract_not,
    ast.NotIn: _extract_notin,
    ast.Or: _extract_or,
    ast.Pow: _extract_pow,
    ast.RShift: _extract_rshift,
    ast.SetComp: _extract_setcomp,
    ast.Set: _extract_set,
    ast.Slice: _extract_slice,
    ast.Starred: _extract_starred,
    ast.Sub: _extract_sub,
    ast.Subscript: _extract_subscript,
    ast.Tuple: _extract_tuple,
    ast.UAdd: _extract_uadd,
    ast.UnaryOp: _extract_unaryop,
    ast.USub: _extract_usub,
    ast.Yield: _extract_yield,
}

# TODO: remove once Python 3.8 support is
if sys.version_info < (3, 9):

    def _extract_extslice(node: ast.ExtSlice, **kwargs: Any) -> str:
        return ",".join(_extract(dim, **kwargs) for dim in node.dims)

    def _extract_index(node: ast.Index, **kwargs: Any) -> str:
        return _extract(node.value, **kwargs)

    _node_map[ast.ExtSlice] = _extract_extslice
    _node_map[ast.Index] = _extract_index


def _extract(node: ast.AST, **kwargs: Any) -> str:
    return _node_map[type(node)](node, **kwargs)


def get_value(node: ast.AST | None) -> str | None:
    """Get the string representation of a node.

    Parameters:
        node: The node to represent.

    Returns:
        The representing code for the node.
    """
    if node is None:
        return None
    return _extract(node)


def safe_get_value(node: ast.AST | None, filepath: str | Path | None = None) -> str | None:
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
