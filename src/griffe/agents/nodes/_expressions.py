"""This module contains utilities for building information from nodes."""

from __future__ import annotations

import ast
import sys
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Sequence

from griffe.expressions import Expression, Name
from griffe.logger import LogLevel, get_logger

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


def _build_add(node: ast.Add, parent: Module | Class, **kwargs: Any) -> str:
    return "+"


def _build_and(node: ast.And, parent: Module | Class, **kwargs: Any) -> str:
    return "and"


def _build_arguments(node: ast.arguments, parent: Module | Class, **kwargs: Any) -> str:
    return ", ".join(arg.arg for arg in node.args)


def _build_attribute(node: ast.Attribute, parent: Module | Class, **kwargs: Any) -> Expression:
    left = _build(node.value, parent, **kwargs)

    if isinstance(left, str):
        resolver = f"str.{node.attr}"
    else:

        def resolver() -> str:  # type: ignore[misc]
            return f"{left.full}.{node.attr}"

    right = Name(node.attr, resolver, first_attr_name=False)
    return Expression(left, ".", right)


def _build_binop(node: ast.BinOp, parent: Module | Class, **kwargs: Any) -> Expression:
    left = _build(node.left, parent, **kwargs)
    right = _build(node.right, parent, **kwargs)
    return Expression(left, " ", _build(node.op, parent, **kwargs), " ", right)


def _build_bitand(node: ast.BitAnd, parent: Module | Class, **kwargs: Any) -> str:
    return "&"


def _build_bitor(node: ast.BitOr, parent: Module | Class, **kwargs: Any) -> str:
    return "|"


def _build_bitxor(node: ast.BitXor, parent: Module | Class, **kwargs: Any) -> str:
    return "^"


def _build_boolop(node: ast.BoolOp, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression(
        *_join([_build(value, parent, **kwargs) for value in node.values], f" {_build(node.op, parent, **kwargs)} "),
    )


def _build_call(node: ast.Call, parent: Module | Class, **kwargs: Any) -> Expression:
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


def _build_compare(node: ast.Compare, parent: Module | Class, **kwargs: Any) -> Expression:
    left = _build(node.left, parent, **kwargs)
    ops = [_build(op, parent, **kwargs) for op in node.ops]
    comparators = [_build(comparator, parent, **kwargs) for comparator in node.comparators]
    return Expression(left, " ", *_join([Expression(op, " ", comp) for op, comp in zip(ops, comparators)], " "))


def _build_comprehension(node: ast.comprehension, parent: Module | Class, **kwargs: Any) -> Expression:
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
    node: ast.Constant,
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
                    flags=ast.PyCF_ONLY_AST,
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


def _build_dict(node: ast.Dict, parent: Module | Class, **kwargs: Any) -> Expression:
    pairs = zip(node.keys, node.values)
    body = [
        Expression("None" if key is None else _build(key, parent, **kwargs), ": ", _build(value, parent, **kwargs))
        for key, value in pairs
    ]
    return Expression("{", Expression(*_join(body, ", ")), "}")


def _build_dictcomp(node: ast.DictComp, parent: Module | Class, **kwargs: Any) -> Expression:
    key = _build(node.key, parent, **kwargs)
    value = _build(node.value, parent, **kwargs)
    generators = [_build(gen, parent, **kwargs) for gen in node.generators]
    return Expression("{", key, ": ", value, Expression(*_join(generators, " ")), "}")


def _build_div(node: ast.Div, parent: Module | Class, **kwargs: Any) -> str:
    return "/"


def _build_eq(node: ast.Eq, parent: Module | Class, **kwargs: Any) -> str:
    return "=="


def _build_floordiv(node: ast.FloorDiv, parent: Module | Class, **kwargs: Any) -> str:
    return "//"


def _build_formatted(node: ast.FormattedValue, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("{", _build(node.value, parent, in_formatted_str=True, **kwargs), "}")


def _build_generatorexp(node: ast.GeneratorExp, parent: Module | Class, **kwargs: Any) -> Expression:
    element = _build(node.elt, parent, **kwargs)
    generators = [_build(gen, parent, **kwargs) for gen in node.generators]
    return Expression(element, " ", Expression(*_join(generators, " ")))


def _build_gte(node: ast.GtE, parent: Module | Class, **kwargs: Any) -> str:
    return ">="


def _build_gt(node: ast.Gt, parent: Module | Class, **kwargs: Any) -> str:
    return ">"


def _build_ifexp(node: ast.IfExp, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression(
        _build(node.body, parent, **kwargs),
        " if ",
        _build(node.test, parent, **kwargs),
        " else ",
        _build(node.orelse, parent, **kwargs),
    )


def _build_invert(node: ast.Invert, parent: Module | Class, **kwargs: Any) -> str:
    return "~"


def _build_in(node: ast.In, parent: Module | Class, **kwargs: Any) -> str:
    return "in"


def _build_is(node: ast.Is, parent: Module | Class, **kwargs: Any) -> str:
    return "is"


def _build_isnot(node: ast.IsNot, parent: Module | Class, **kwargs: Any) -> str:
    return "is not"


def _build_joinedstr(node: ast.JoinedStr, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("f'", *[_build(value, parent, in_joined_str=True) for value in node.values], "'")


def _build_keyword(node: ast.keyword, parent: Module | Class, **kwargs: Any) -> Expression:
    if node.arg is None:
        return Expression("**", _build(node.value, parent, **kwargs))
    return Expression(node.arg, "=", _build(node.value, parent, **kwargs))


def _build_lambda(node: ast.Lambda, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("lambda ", _build(node.args, parent, **kwargs), ": ", _build(node.body, parent, **kwargs))


def _build_list(node: ast.List, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("[", *_join([_build(el, parent, **kwargs) for el in node.elts], ", "), "]")


def _build_listcomp(node: ast.ListComp, parent: Module | Class, **kwargs: Any) -> Expression:
    element = _build(node.elt, parent, **kwargs)
    generators = [_build(gen, parent, **kwargs) for gen in node.generators]
    return Expression("[", element, *_join(generators, " "), "]")


def _build_lshift(node: ast.LShift, parent: Module | Class, **kwargs: Any) -> str:
    return "<<"


def _build_lte(node: ast.LtE, parent: Module | Class, **kwargs: Any) -> str:
    return "<="


def _build_lt(node: ast.Lt, parent: Module | Class, **kwargs: Any) -> str:
    return "<"


def _build_matmult(node: ast.MatMult, parent: Module | Class, **kwargs: Any) -> str:
    return "@"


def _build_mod(node: ast.Mod, parent: Module | Class, **kwargs: Any) -> str:
    return "%"


def _build_mult(node: ast.Mult, parent: Module | Class, **kwargs: Any) -> str:
    return "*"


def _build_name(node: ast.Name, parent: Module | Class, **kwargs: Any) -> Name:
    return Name(node.id, partial(parent.resolve, node.id))


def _build_named_expr(node: ast.NamedExpr, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("(", _build(node.target, parent, **kwargs), " := ", _build(node.value, parent, **kwargs), ")")


def _build_not(node: ast.Not, parent: Module | Class, **kwargs: Any) -> str:
    return "not "


def _build_noteq(node: ast.NotEq, parent: Module | Class, **kwargs: Any) -> str:
    return "!="


def _build_notin(node: ast.NotIn, parent: Module | Class, **kwargs: Any) -> str:
    return "not in"


def _build_or(node: ast.Or, parent: Module | Class, **kwargs: Any) -> str:
    return "or"


def _build_pow(node: ast.Pow, parent: Module | Class, **kwargs: Any) -> str:
    return "**"


def _build_rshift(node: ast.RShift, parent: Module | Class, **kwargs: Any) -> str:
    return ">>"


def _build_set(node: ast.Set, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("{", *_join([_build(el, parent, **kwargs) for el in node.elts], ", "), "}")


def _build_setcomp(node: ast.SetComp, parent: Module | Class, **kwargs: Any) -> Expression:
    element = _build(node.elt, parent, **kwargs)
    generators = [_build(gen, parent, **kwargs) for gen in node.generators]
    return Expression("{", element, " ", *_join(generators, " "), "}")


def _build_slice(node: ast.Slice, parent: Module | Class, **kwargs: Any) -> Expression:
    lower = _build(node.lower, parent, **kwargs) if node.lower else ""
    upper = _build(node.upper, parent, **kwargs) if node.upper else ""
    value = Expression(lower, ":", upper)
    if node.step:
        value.extend((":", _build(node.step, parent, **kwargs)))
    return value


def _build_starred(node: ast.Starred, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression("*", _build(node.value, parent, **kwargs))


def _build_sub(node: ast.Sub, parent: Module | Class, **kwargs: Any) -> str:
    return "-"


def _build_subscript(
    node: ast.Subscript,
    parent: Module | Class,
    *,
    parse_strings: bool = False,
    literal_strings: bool = False,
    in_subscript: bool = False,
    **kwargs: Any,
) -> Expression:
    left = _build(node.value, parent, **kwargs)
    if parse_strings:
        if left.full in {"typing.Literal", "typing_extensions.Literal"}:  # type: ignore[union-attr]
            literal_strings = True
        subscript = _build(
            node.slice,
            parent,
            parse_strings=True,
            literal_strings=literal_strings,
            in_subscript=True,
            **kwargs,
        )
    else:
        subscript = _build(node.slice, parent, in_subscript=True, **kwargs)
    return Expression(left, "[", subscript, "]")


def _build_tuple(
    node: ast.Tuple,
    parent: Module | Class,
    *,
    in_subscript: bool = False,
    **kwargs: Any,
) -> Expression:
    values = _join([_build(el, parent, **kwargs) for el in node.elts], ", ")
    if in_subscript:
        return Expression(*values)
    return Expression("(", *values, ")")


def _build_uadd(node: ast.UAdd, parent: Module | Class, **kwargs: Any) -> str:
    return "+"


def _build_unaryop(node: ast.UnaryOp, parent: Module | Class, **kwargs: Any) -> Expression:
    return Expression(_build(node.op, parent, **kwargs), _build(node.operand, parent, **kwargs))


def _build_usub(node: ast.USub, parent: Module | Class, **kwargs: Any) -> str:
    return "-"


def _build_yield(node: ast.Yield, parent: Module | Class, **kwargs: Any) -> str | Name | Expression:
    if node.value is None:
        return repr(None)
    return _build(node.value, parent, **kwargs)


_node_map: dict[type, Callable[[Any, Module | Class], str | Name | Expression]] = {
    ast.Add: _build_add,
    ast.And: _build_and,
    ast.arguments: _build_arguments,
    ast.Attribute: _build_attribute,
    ast.BinOp: _build_binop,
    ast.BitAnd: _build_bitand,
    ast.BitOr: _build_bitor,
    ast.BitXor: _build_bitxor,
    ast.BoolOp: _build_boolop,
    ast.Call: _build_call,
    ast.Compare: _build_compare,
    ast.comprehension: _build_comprehension,
    ast.Constant: _build_constant,
    ast.Dict: _build_dict,
    ast.DictComp: _build_dictcomp,
    ast.Div: _build_div,
    ast.Eq: _build_eq,
    ast.FloorDiv: _build_floordiv,
    ast.FormattedValue: _build_formatted,
    ast.GeneratorExp: _build_generatorexp,
    ast.Gt: _build_gt,
    ast.GtE: _build_gte,
    ast.IfExp: _build_ifexp,
    ast.In: _build_in,
    ast.Invert: _build_invert,
    ast.Is: _build_is,
    ast.IsNot: _build_isnot,
    ast.JoinedStr: _build_joinedstr,
    ast.keyword: _build_keyword,
    ast.Lambda: _build_lambda,
    ast.List: _build_list,
    ast.ListComp: _build_listcomp,
    ast.LShift: _build_lshift,
    ast.Lt: _build_lt,
    ast.LtE: _build_lte,
    ast.MatMult: _build_matmult,
    ast.Mod: _build_mod,
    ast.Mult: _build_mult,
    ast.Name: _build_name,
    ast.NamedExpr: _build_named_expr,
    ast.Not: _build_not,
    ast.NotEq: _build_noteq,
    ast.NotIn: _build_notin,
    ast.Or: _build_or,
    ast.Pow: _build_pow,
    ast.RShift: _build_rshift,
    ast.Set: _build_set,
    ast.SetComp: _build_setcomp,
    ast.Slice: _build_slice,
    ast.Starred: _build_starred,
    ast.Sub: _build_sub,
    ast.Subscript: _build_subscript,
    ast.Tuple: _build_tuple,
    ast.UAdd: _build_uadd,
    ast.UnaryOp: _build_unaryop,
    ast.USub: _build_usub,
    ast.Yield: _build_yield,
}

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):

    def _build_extslice(node: ast.ExtSlice, parent: Module | Class, **kwargs: Any) -> Expression:
        return Expression(*_join([_build(dim, parent, **kwargs) for dim in node.dims], ","))

    def _build_index(node: ast.Index, parent: Module | Class, **kwargs: Any) -> str | Name | Expression:
        return _build(node.value, parent, **kwargs)

    _node_map[ast.ExtSlice] = _build_extslice
    _node_map[ast.Index] = _build_index


def _build(node: ast.AST, parent: Module | Class, **kwargs: Any) -> str | Name | Expression:
    return _node_map[type(node)](node, parent, **kwargs)


def get_expression(
    node: ast.AST | None,
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
    node: ast.AST | None,
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
