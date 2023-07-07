"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

import sys
from ast import AST, PyCF_ONLY_AST
from ast import Attribute as NodeAttribute
from ast import BinOp as NodeBinOp
from ast import BitAnd as NodeBitAnd
from ast import BitOr as NodeBitOr
from ast import Call as NodeCall
from ast import Constant as NodeConstant
from ast import Ellipsis as NodeEllipsis
from ast import IfExp as NodeIfExp
from ast import Invert as NodeInvert
from ast import List as NodeList
from ast import Name as NodeName
from ast import Subscript as NodeSubscript
from ast import Tuple as NodeTuple
from ast import UAdd as NodeUAdd
from ast import UnaryOp as NodeUnaryOp
from ast import USub as NodeUSub
from ast import keyword as NodeKeyword  # noqa: N812
from contextlib import contextmanager
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Iterator, Sequence

from griffe.expressions import Expression, Name
from griffe.logger import LogLevel, get_logger

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):
    from ast import Index as NodeIndex

if TYPE_CHECKING:
    from pathlib import Path

    from griffe.dataclasses import Class, Module


logger = get_logger(__name__)


def _join(sequence: Sequence, item: str) -> list:
    if not sequence:
        return []
    new_sequence = [sequence[0]]
    for element in sequence[1:]:
        new_sequence.append(item)
        new_sequence.append(element)
    return new_sequence


class _ExpressionBuilder:
    __slots__ = ("parent", "_node_map", "_literal_strings")

    def __init__(self, parent: Module | Class) -> None:
        self.parent = parent
        self._literal_strings = False
        self._node_map: dict[type, Callable[[Any], str | Name | Expression]] = {
            NodeAttribute: self._build_attribute,
            NodeBinOp: self._build_binop,
            NodeBitAnd: self._build_bitand,
            NodeBitOr: self._build_bitor,
            NodeCall: self._build_call,
            NodeConstant: self._build_constant,
            NodeEllipsis: self._build_ellipsis,
            NodeIfExp: self._build_ifexp,
            NodeInvert: self._build_invert,
            NodeKeyword: self._build_keyword,
            NodeList: self._build_list,
            NodeName: self._build_name,
            NodeSubscript: self._build_subscript,
            NodeTuple: self._build_tuple,
            NodeUnaryOp: self._build_unaryop,
            NodeUAdd: self._build_uadd,
            NodeUSub: self._build_usub,
        }

        # TODO: remove once Python 3.8 support is dropped
        if sys.version_info < (3, 9):
            self._node_map[NodeIndex] = self._build_index

    @contextmanager
    def literal_strings(self) -> Iterator[None]:
        self._literal_strings = True
        try:
            yield
        finally:
            self._literal_strings = False

    def _build_attribute(self, node: NodeAttribute) -> Expression:
        left = self._build(node.value)

        def resolver() -> str:
            return f"{left.full}.{node.attr}"  # type: ignore[union-attr]

        right = Name(node.attr, resolver, first_attr_name=False)
        return Expression(left, ".", right)

    def _build_binop(self, node: NodeBinOp) -> Expression:
        left = self._build(node.left)
        right = self._build(node.right)
        return Expression(left, self._build(node.op), right)

    def _build_bitand(self, node: NodeBitAnd) -> str:  # noqa: ARG002
        return " & "

    def _build_bitor(self, node: NodeBitOr) -> str:  # noqa: ARG002
        return " | "

    def _build_call(self, node: NodeCall) -> Expression:
        posargs = Expression(*_join([self._build(arg) for arg in node.args], ", "))
        kwargs = Expression(*_join([self._build(kwarg) for kwarg in node.keywords], ", "))
        args: Expression | str
        if posargs and kwargs:
            args = Expression(posargs, ", ", kwargs)
        elif posargs:
            args = posargs
        elif kwargs:
            args = kwargs
        else:
            args = ""
        return Expression(self._build(node.func), "(", args, ")")

    def _build_constant(self, node: NodeConstant) -> str | Name | Expression:
        if isinstance(node.value, str) and not self._literal_strings:
            # A string in an annotation is a stringified annotation: we parse and build it again.
            # If we fail to parse it (syntax errors), we consider it's a literal string and log a message.
            # Literal strings must be wrapped in Literal[...] to be picked up as such.
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
                return self._build(parsed.body)  # type: ignore[attr-defined]
        return self._build_literal(node)

    def _build_literal(self, node: NodeConstant) -> str:
        return {type(...): lambda _: "..."}.get(type(node.value), repr)(node.value)

    def _build_ellipsis(self, node: NodeEllipsis) -> str:  # noqa: ARG002
        return "..."

    def _build_ifexp(self, node: NodeIfExp) -> Expression:
        return Expression(
            self._build(node.body),
            " if ",
            self._build(node.test),
            " else ",
            self._build(node.orelse),
        )

    def _build_invert(self, node: NodeInvert) -> str:  # noqa: ARG002
        return "~"

    def _build_keyword(self, node: NodeKeyword) -> Expression:
        return Expression(f"{node.arg}=", self._build(node.value))

    def _build_list(self, node: NodeList) -> Expression:
        return Expression("[", *_join([self._build(el) for el in node.elts], ", "), "]")

    def _build_name(self, node: NodeName) -> Name:
        return Name(node.id, partial(self.parent.resolve, node.id))

    def _build_subscript(self, node: NodeSubscript) -> Expression:
        left = self._build(node.value)
        if left.full in {"typing.Literal", "typing_extensions.Literal"}:  # type: ignore[union-attr]
            with self.literal_strings():
                subscript = self._build(node.slice)
        else:
            subscript = self._build(node.slice)
        return Expression(left, "[", subscript, "]")

    def _build_tuple(self, node: NodeTuple) -> Expression:
        return Expression(*_join([self._build(el) for el in node.elts], ", "))

    def _build_unaryop(self, node: NodeUnaryOp) -> Expression:
        return Expression(self._build(node.op), self._build(node.operand))

    def _build_uadd(self, node: NodeUAdd) -> str:  # noqa: ARG002
        return "+"

    def _build_usub(self, node: NodeUSub) -> str:  # noqa: ARG002
        return "-"

    # TODO: remove once Python 3.8 support is dropped
    if sys.version_info < (3, 9):

        def _build_index(self, node: NodeIndex) -> str | Name | Expression:
            return self._build(node.value)

    def _build(self, node: AST) -> str | Name | Expression:
        return self._node_map[type(node)](node)


def _build_attribute(node: NodeAttribute, parent: Module | Class) -> Expression:
    left = _build(node.value, parent)

    def resolver() -> str:
        return f"{left.full}.{node.attr}"  # type: ignore[union-attr]

    right = Name(node.attr, resolver, first_attr_name=False)
    return Expression(left, ".", right)


def _build_binop(node: NodeBinOp, parent: Module | Class) -> Expression:
    left = _build(node.left, parent)
    right = _build(node.right, parent)
    return Expression(left, _build(node.op, parent), right)


def _build_bitand(node: NodeBitAnd, parent: Module | Class) -> str:  # noqa: ARG001
    return " & "


def _build_bitor(node: NodeBitOr, parent: Module | Class) -> str:  # noqa: ARG001
    return " | "


def _build_call(node: NodeCall, parent: Module | Class) -> Expression:
    posargs = Expression(*_join([_build(arg, parent) for arg in node.args], ", "))
    kwargs = Expression(*_join([_build(kwarg, parent) for kwarg in node.keywords], ", "))
    args: Expression | str
    if posargs and kwargs:
        args = Expression(posargs, ", ", kwargs)
    elif posargs:
        args = posargs
    elif kwargs:
        args = kwargs
    else:
        args = ""
    return Expression(_build(node.func, parent), "(", args, ")")


def _build_constant(node: NodeConstant, parent: Module | Class) -> str | Name | Expression:
    return _build_literal(node, parent)


def _build_literal(node: NodeConstant, parent: Module | Class) -> str:  # noqa: ARG001
    return {type(...): lambda _: "..."}.get(type(node.value), repr)(node.value)


def _build_ellipsis(node: NodeEllipsis, parent: Module | Class) -> str:  # noqa: ARG001
    return "..."


def _build_ifexp(node: NodeIfExp, parent: Module | Class) -> Expression:
    return Expression(
        _build(node.body, parent),
        " if ",
        _build(node.test, parent),
        " else ",
        _build(node.orelse, parent),
    )


def _build_invert(node: NodeInvert, parent: Module | Class) -> str:  # noqa: ARG001
    return "~"


def _build_keyword(node: NodeKeyword, parent: Module | Class) -> Expression:
    return Expression(f"{node.arg}=", _build(node.value, parent))


def _build_list(node: NodeList, parent: Module | Class) -> Expression:
    return Expression("[", *_join([_build(el, parent) for el in node.elts], ", "), "]")


def _build_name(node: NodeName, parent: Module | Class) -> Name:
    return Name(node.id, partial(parent.resolve, node.id))


def _build_subscript(node: NodeSubscript, parent: Module | Class) -> Expression:
    left = _build(node.value, parent)
    if left.full in {"typing.Literal", "typing_extensions.Literal"}:  # type: ignore[union-attr]
        subscript = _build(node.slice, parent)
    else:
        subscript = _build(node.slice, parent)
    return Expression(left, "[", subscript, "]")


def _build_tuple(node: NodeTuple, parent: Module | Class) -> Expression:
    return Expression(*_join([_build(el, parent) for el in node.elts], ", "))


def _build_unaryop(node: NodeUnaryOp, parent: Module | Class) -> Expression:
    return Expression(_build(node.op, parent), _build(node.operand, parent))


def _build_uadd(node: NodeUAdd, parent: Module | Class) -> str:  # noqa: ARG001
    return "+"


def _build_usub(node: NodeUSub, parent: Module | Class) -> str:  # noqa: ARG001
    return "-"


_node_map: dict[type, Callable[[Any, Module | Class], str | Name | Expression]] = {
    NodeAttribute: _build_attribute,
    NodeBinOp: _build_binop,
    NodeBitAnd: _build_bitand,
    NodeBitOr: _build_bitor,
    NodeCall: _build_call,
    NodeConstant: _build_constant,
    NodeEllipsis: _build_ellipsis,
    NodeIfExp: _build_ifexp,
    NodeInvert: _build_invert,
    NodeKeyword: _build_keyword,
    NodeList: _build_list,
    NodeName: _build_name,
    NodeSubscript: _build_subscript,
    NodeTuple: _build_tuple,
    NodeUnaryOp: _build_unaryop,
    NodeUAdd: _build_uadd,
    NodeUSub: _build_usub,
}

# TODO: remove once Python 3.8 support is dropped
if sys.version_info < (3, 9):

    def _build_index(node: NodeIndex, parent: Module | Class) -> str | Name | Expression:
        return _build(node.value, parent)

    _node_map[NodeIndex] = _build_index


def _build(node: AST, parent: Module | Class) -> str | Name | Expression:
    return _node_map[type(node)](node, parent)


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
    if parse_strings:
        builder = _ExpressionBuilder(parent)
        return builder._build(node)
    return _build(node, parent)


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
