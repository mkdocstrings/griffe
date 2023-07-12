"""This module contains utilities for building information from nodes."""

from __future__ import annotations

import sys
from ast import AST, PyCF_ONLY_AST
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
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Sequence

from griffe.expressions import Expression, Name
from griffe.logger import LogLevel, get_logger

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):
    from ast import ExtSlice as NodeExtSlice
    from ast import Index as NodeIndex

if TYPE_CHECKING:
    from pathlib import Path

    from griffe.dataclasses import Class, Module


logger = get_logger(__name__)


def _join(sequence: Sequence, item: str | Name | Expression) -> list:
    if not sequence:
        return []
    new_sequence = [sequence[0]]
    for element in sequence[1:]:
        new_sequence.append(item)
        new_sequence.append(element)
    return new_sequence


def _build_add(node: NodeAdd, parent: Module | Class, **kwargs: Any) -> str:
    return "+"


def _build_and(node: NodeAnd, parent: Module | Class, **kwargs: Any) -> str:
    return "and"


def _build_arguments(node: NodeArguments, parent: Module | Class, **kwargs: Any) -> str:
    return ", ".join(arg.arg for arg in node.args)


def _build_attribute(node: NodeAttribute, parent: Module | Class, **kwargs: Any) -> Expression:
    left = _build(node.value, parent, **kwargs)

    if isinstance(left, str):
        resolver = f"str.{node.attr}"
    else:

        def resolver() -> str:  # type: ignore[misc]
            return f"{left.full}.{node.attr}"

    right = Name(node.attr, resolver, first_attr_name=False)
    return Expression(left, ".", right)


def _build_binop(node: NodeBinOp, parent: Module | Class, **kwargs: Any) -> Expression:
    left = _build(node.left, parent, **kwargs)
    right = _build(node.right, parent, **kwargs)
    return Expression(left, " ", _build(node.op, parent, **kwargs), " ", right)


def _build_bitand(node: NodeBitAnd, parent: Module | Class, **kwargs: Any) -> str:
    return "&"


def _build_bitor(node: NodeBitOr, parent: Module | Class, **kwargs: Any) -> str:
    return "|"


def _build_bitxor(node: NodeBitXor, parent: Module | Class, **kwargs: Any) -> str:
    return "^"


def _build_boolop(node: NodeBoolOp, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression(
        *_join([_build(value, parent, **kwargs) for value in node.values], f" {_build(node.op, parent, **kwargs)} "),
    )


def _build_call(node: NodeCall, parent: Module | Class, **kwargs: Any) -> Expression:
    positional_args = Expression(*_join([_build(arg, parent, **kwargs) for arg in node.args], ", "))
    keyword_args = Expression(*_join([_build(kwarg, parent, **kwargs) for kwarg in node.keywords], ", "))
    args: Expression | str
    if positional_args and keyword_args:
        args = Expression(positional_args, ", ", keyword_args)
    elif positional_args:
        args = positional_args
    elif keyword_args:
        args = keyword_args
    else:
        args = ""
    return Expression(_build(node.func, parent, **kwargs), "(", args, ")")


def _build_compare(node: NodeCompare, parent: Module | Class, **kwargs: Any) -> Expression:
    left = _build(node.left, parent, **kwargs)
    ops = [_build(op, parent, **kwargs) for op in node.ops]
    comparators = [_build(comparator, parent, **kwargs) for comparator in node.comparators]
    return Expression(left, " ", *_join([Expression(op, " ", comp) for op, comp in zip(ops, comparators)], " "))


def _build_comprehension(node: NodeComprehension, parent: Module | Class, **kwargs: Any) -> Expression:
    target = _build(node.target, parent, **kwargs)
    iterable = _build(node.iter, parent, **kwargs)
    conditions = [_build(condition, parent, **kwargs) for condition in node.ifs]
    value = Expression("for ", target, " in ", iterable)
    if conditions:
        value.extend((" if ", *_join(conditions, " if ")))
    if node.is_async:
        value.insert(0, "async ")
    return value


def _build_constant(
    node: NodeConstant,
    parent: Module | Class,
    *,
    in_formatted_str: bool = False,
    in_joined_str: bool = False,
    parse_strings: bool = False,
    literal_strings: bool = False,
    **kwargs: Any,
) -> str | Name | Expression:
    if isinstance(node.value, str):
        if in_joined_str and not in_formatted_str:
            # We're in a f-string, not in a formatted value, don't keep quotes.
            return node.value
        if parse_strings and not literal_strings:
            # We're in a place where a string could be a type annotation
            # (and not in a Literal[...] type annotation).
            # We parse the string and build from the resulting nodes again.
            # If we fail to parse it (syntax errors), we consider it's a literal string and log a message.
            try:
                parsed = compile(
                    node.value,
                    mode="eval",
                    filename="<string-annotation>",
                    flags=PyCF_ONLY_AST,
                    optimize=1,
                )
            except SyntaxError:
                logger.debug(
                    f"Tried and failed to parse {node.value!r} as Python code, "
                    "falling back to using it as a string literal "
                    "(postponed annotations might help: https://peps.python.org/pep-0563/)",
                )
            else:
                return _build(parsed.body, parent, **kwargs)  # type: ignore[attr-defined]
    return {type(...): lambda _: "..."}.get(type(node.value), repr)(node.value)


def _build_dict(node: NodeDict, parent: Module | Class, **kwargs: Any) -> Expression:
    pairs = zip(node.keys, node.values)
    body = [
        Expression("None" if key is None else _build(key, parent, **kwargs), ": ", _build(value, parent, **kwargs))
        for key, value in pairs
    ]
    return Expression("{", Expression(*_join(body, ", ")), "}")


def _build_dictcomp(node: NodeDictComp, parent: Module | Class, **kwargs: Any) -> Expression:
    key = _build(node.key, parent, **kwargs)
    value = _build(node.value, parent, **kwargs)
    generators = [_build(gen, parent, **kwargs) for gen in node.generators]
    return Expression("{", key, ": ", value, Expression(*_join(generators, " ")), "}")


def _build_div(node: NodeDiv, parent: Module | Class, **kwargs: Any) -> str:
    return "/"


def _build_ellipsis(node: NodeEllipsis, parent: Module | Class, **kwargs: Any) -> str:
    return "..."


def _build_eq(node: NodeEq, parent: Module | Class, **kwargs: Any) -> str:
    return "=="


def _build_floordiv(node: NodeFloorDiv, parent: Module | Class, **kwargs: Any) -> str:
    return "//"


def _build_formatted(node: NodeFormattedValue, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("{", _build(node.value, parent, in_formatted_str=True, **kwargs), "}")


def _build_generatorexp(node: NodeGeneratorExp, parent: Module | Class, **kwargs: Any) -> Expression:
    element = _build(node.elt, parent, **kwargs)
    generators = [_build(gen, parent, **kwargs) for gen in node.generators]
    return Expression(element, " ", Expression(*_join(generators, " ")))


def _build_gte(node: NodeGtE, parent: Module | Class, **kwargs: Any) -> str:
    return ">="


def _build_gt(node: NodeGt, parent: Module | Class, **kwargs: Any) -> str:
    return ">"


def _build_ifexp(node: NodeIfExp, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression(
        _build(node.body, parent, **kwargs),
        " if ",
        _build(node.test, parent, **kwargs),
        " else ",
        _build(node.orelse, parent, **kwargs),
    )


def _build_invert(node: NodeInvert, parent: Module | Class, **kwargs: Any) -> str:
    return "~"


def _build_in(node: NodeIn, parent: Module | Class, **kwargs: Any) -> str:
    return "in"


def _build_is(node: NodeIs, parent: Module | Class, **kwargs: Any) -> str:
    return "is"


def _build_isnot(node: NodeIsNot, parent: Module | Class, **kwargs: Any) -> str:
    return "is not"


def _build_joinedstr(node: NodeJoinedStr, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("f'", *[_build(value, parent, in_joined_str=True) for value in node.values], "'")


def _build_keyword(node: NodeKeyword, parent: Module | Class, **kwargs: Any) -> Expression:
    if node.arg is None:
        return Expression("**", _build(node.value, parent, **kwargs))
    return Expression(node.arg, "=", _build(node.value, parent, **kwargs))


def _build_lambda(node: NodeLambda, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("lambda ", _build(node.args, parent, **kwargs), ": ", _build(node.body, parent, **kwargs))


def _build_list(node: NodeList, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("[", *_join([_build(el, parent, **kwargs) for el in node.elts], ", "), "]")


def _build_listcomp(node: NodeListComp, parent: Module | Class, **kwargs: Any) -> Expression:
    element = _build(node.elt, parent, **kwargs)
    generators = [_build(gen, parent, **kwargs) for gen in node.generators]
    return Expression("[", element, *_join(generators, " "), "]")


def _build_lshift(node: NodeLShift, parent: Module | Class, **kwargs: Any) -> str:
    return "<<"


def _build_lte(node: NodeLtE, parent: Module | Class, **kwargs: Any) -> str:
    return "<="


def _build_lt(node: NodeLt, parent: Module | Class, **kwargs: Any) -> str:
    return "<"


def _build_matmult(node: NodeMatMult, parent: Module | Class, **kwargs: Any) -> str:
    return "@"


def _build_mod(node: NodeMod, parent: Module | Class, **kwargs: Any) -> str:
    return "%"


def _build_mult(node: NodeMult, parent: Module | Class, **kwargs: Any) -> str:
    return "*"


def _build_name(node: NodeName, parent: Module | Class, **kwargs: Any) -> Name:
    return Name(node.id, partial(parent.resolve, node.id))


def _build_named_expr(node: NodeNamedExpr, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("(", _build(node.target, parent, **kwargs), " := ", _build(node.value, parent, **kwargs), ")")


def _build_not(node: NodeNot, parent: Module | Class, **kwargs: Any) -> str:
    return "not "


def _build_noteq(node: NodeNotEq, parent: Module | Class, **kwargs: Any) -> str:
    return "!="


def _build_notin(node: NodeNotIn, parent: Module | Class, **kwargs: Any) -> str:
    return "not in"


def _build_or(node: NodeOr, parent: Module | Class, **kwargs: Any) -> str:
    return "or"


def _build_pow(node: NodePow, parent: Module | Class, **kwargs: Any) -> str:
    return "**"


def _build_rshift(node: NodeRShift, parent: Module | Class, **kwargs: Any) -> str:
    return ">>"


def _build_set(node: NodeSet, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("{", *_join([_build(el, parent, **kwargs) for el in node.elts], ", "), "}")


def _build_setcomp(node: NodeSetComp, parent: Module | Class, **kwargs: Any) -> Expression:
    element = _build(node.elt, parent, **kwargs)
    generators = [_build(gen, parent, **kwargs) for gen in node.generators]
    return Expression("{", element, " ", *_join(generators, " "), "}")


def _build_slice(node: NodeSlice, parent: Module | Class, **kwargs: Any) -> Expression:
    lower = _build(node.lower, parent, **kwargs) if node.lower else ""
    upper = _build(node.upper, parent, **kwargs) if node.upper else ""
    value = Expression(lower, ":", upper)
    if node.step:
        value.extend((":", _build(node.step, parent, **kwargs)))
    return value


def _build_starred(node: NodeStarred, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("*", _build(node.value, parent, **kwargs))


def _build_sub(node: NodeSub, parent: Module | Class, **kwargs: Any) -> str:
    return "-"


def _build_subscript(
    node: NodeSubscript,
    parent: Module | Class,
    *,
    parse_strings: bool = False,
    **kwargs: Any,
) -> Expression:
    left = _build(node.value, parent, **kwargs)
    if parse_strings:
        literal_strings = left.full in {"typing.Literal", "typing_extensions.Literal"}  # type: ignore[union-attr]
        subscript = _build(node.slice, parent, parse_strings=True, **{**kwargs, "literal_strings": literal_strings})
    else:
        subscript = _build(node.slice, parent, **kwargs)
    return Expression(left, "[", subscript, "]")


def _build_tuple(node: NodeTuple, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression(*_join([_build(el, parent, **kwargs) for el in node.elts], ", "))


def _build_uadd(node: NodeUAdd, parent: Module | Class, **kwargs: Any) -> str:
    return "+"


def _build_unaryop(node: NodeUnaryOp, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression(_build(node.op, parent, **kwargs), _build(node.operand, parent, **kwargs))


def _build_usub(node: NodeUSub, parent: Module | Class, **kwargs: Any) -> str:
    return "-"


def _build_yield(node: NodeYield, parent: Module | Class, **kwargs: Any) -> str | Name | Expression:
    if node.value is None:
        return repr(None)
    return _build(node.value, parent, **kwargs)


_node_map: dict[type, Callable[[Any, Module | Class], str | Name | Expression]] = {
    NodeAdd: _build_add,
    NodeAnd: _build_and,
    NodeArguments: _build_arguments,
    NodeAttribute: _build_attribute,
    NodeBinOp: _build_binop,
    NodeBitAnd: _build_bitand,
    NodeBitOr: _build_bitor,
    NodeBitXor: _build_bitxor,
    NodeBoolOp: _build_boolop,
    NodeCall: _build_call,
    NodeCompare: _build_compare,
    NodeComprehension: _build_comprehension,
    NodeConstant: _build_constant,
    NodeDict: _build_dict,
    NodeDictComp: _build_dictcomp,
    NodeDiv: _build_div,
    NodeEllipsis: _build_ellipsis,
    NodeEq: _build_eq,
    NodeFloorDiv: _build_floordiv,
    NodeFormattedValue: _build_formatted,
    NodeGeneratorExp: _build_generatorexp,
    NodeGt: _build_gt,
    NodeGtE: _build_gte,
    NodeIfExp: _build_ifexp,
    NodeIn: _build_in,
    NodeInvert: _build_invert,
    NodeIs: _build_is,
    NodeIsNot: _build_isnot,
    NodeJoinedStr: _build_joinedstr,
    NodeKeyword: _build_keyword,
    NodeLambda: _build_lambda,
    NodeList: _build_list,
    NodeListComp: _build_listcomp,
    NodeLShift: _build_lshift,
    NodeLt: _build_lt,
    NodeLtE: _build_lte,
    NodeMatMult: _build_matmult,
    NodeMod: _build_mod,
    NodeMult: _build_mult,
    NodeName: _build_name,
    NodeNamedExpr: _build_named_expr,
    NodeNot: _build_not,
    NodeNotEq: _build_noteq,
    NodeNotIn: _build_notin,
    NodeOr: _build_or,
    NodePow: _build_pow,
    NodeRShift: _build_rshift,
    NodeSet: _build_set,
    NodeSetComp: _build_setcomp,
    NodeSlice: _build_slice,
    NodeStarred: _build_starred,
    NodeSub: _build_sub,
    NodeSubscript: _build_subscript,
    NodeTuple: _build_tuple,
    NodeUAdd: _build_uadd,
    NodeUnaryOp: _build_unaryop,
    NodeUSub: _build_usub,
    NodeYield: _build_yield,
}

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):

    def _build_extslice(node: NodeExtSlice, parent: Module | Class, **kwargs: Any) -> Expression:
        return Expression(*_join([_build(dim, parent, **kwargs) for dim in node.dims], ","))

    def _build_index(node: NodeIndex, parent: Module | Class, **kwargs: Any) -> str | Name | Expression:
        return _build(node.value, parent, **kwargs)

    _node_map[NodeExtSlice] = _build_extslice
    _node_map[NodeIndex] = _build_index


def _build(node: AST, parent: Module | Class, **kwargs: Any) -> str | Name | Expression:
    return _node_map[type(node)](node, parent, **kwargs)


def get_expression(
    node: AST | None,
    parent: Module | Class,
    *,
    parse_strings: bool | None = None,
) -> str | Name | Expression | None:
    """Build an expression from an AST.

    Parameters:
        node: The annotation node.
        parent: The parent used to resolve the name.
        parse_strings: Whether to try and parse strings as type annotations.

    Returns:
        A string or resovable name or expression.
    """
    if node is None:
        return None
    if parse_strings is None:
        try:
            module = parent.module
        except ValueError:
            parse_strings = False
        else:
            parse_strings = not module.imports_future_annotations
    return _build(node, parent, parse_strings=parse_strings)


def safe_get_expression(
    node: AST | None,
    parent: Module | Class,
    *,
    parse_strings: bool | None = None,
    log_level: LogLevel | None = LogLevel.error,
    msg_format: str = "{path}:{lineno}: Failed to get expression from {node_class}: {error}",
) -> str | Name | Expression | None:
    """Safely (no exception) build a resolvable annotation.

    Parameters:
        node: The annotation node.
        parent: The parent used to resolve the name.
        parse_strings: Whether to try and parse strings as type annotations.
        log_level: Log level to use to log a message. None to disable logging.
        msg_format: A format string for the log message. Available placeholders:
            path, lineno, node, error.

    Returns:
        A string or resovable name or expression.
    """
    try:
        return get_expression(node, parent, parse_strings=parse_strings)
    except Exception as error:  # noqa: BLE001
        if log_level is None:
            return None
        node_class = node.__class__.__name__
        try:
            path: Path | str = parent.relative_filepath
        except ValueError:
            path = "<in-memory>"
        lineno = node.lineno  # type: ignore[union-attr]
        message = msg_format.format(path=path, lineno=lineno, node_class=node_class, error=error)
        getattr(logger, log_level.value)(message)
    return None


_msg_format = "{path}:{lineno}: Failed to get %s expression from {node_class}: {error}"
get_annotation = partial(get_expression, parse_strings=None)
safe_get_annotation = partial(
    safe_get_expression,
    parse_strings=None,
    msg_format=_msg_format % "annotation",
)
get_base_class = partial(get_expression, parse_strings=False)
safe_get_base_class = partial(
    safe_get_expression,
    parse_strings=False,
    msg_format=_msg_format % "base class",
)
get_condition = partial(get_expression, parse_strings=False)
safe_get_condition = partial(
    safe_get_expression,
    parse_strings=False,
    msg_format=_msg_format % "condition",
)


__all__ = [
    "get_annotation",
    "get_base_class",
    "get_condition",
    "get_expression",
    "safe_get_annotation",
    "safe_get_base_class",
    "safe_get_condition",
    "safe_get_expression",
]
