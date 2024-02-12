"""This module contains utilities for extracting information from nodes."""

from __future__ import annotations

from itertools import zip_longest
from typing import TYPE_CHECKING, Any, Iterable

from griffe.enumerations import ParameterKind
from griffe.logger import get_logger

if TYPE_CHECKING:
    import ast

    from griffe.dataclasses import Class, Module


logger = get_logger(__name__)


def get_parameters(node: ast.arguments) -> list[tuple[str, ast.AST, ParameterKind, str | ast.AST]]:
    parameters = []

    # TODO: probably some optimizations to do here
    args_kinds_defaults: Iterable = reversed(
        (
            *zip_longest(
                reversed(
                    (
                        *zip_longest(
                            node.posonlyargs,
                            [],
                            fillvalue=ParameterKind.positional_only,
                        ),
                        *zip_longest(node.args, [], fillvalue=ParameterKind.positional_or_keyword),
                    ),
                ),
                reversed(node.defaults),
                fillvalue=None,
            ),
        ),
    )
    arg: ast.arg
    kind: ParameterKind
    arg_default: ast.AST | None
    for (arg, kind), arg_default in args_kinds_defaults:
        parameters.append((arg.arg, arg.annotation, kind, arg_default))

    if node.vararg:
        parameters.append(
            (
                node.vararg.arg,
                node.vararg.annotation,
                ParameterKind.var_positional,
                "()",
            ),
        )

    # TODO: probably some optimizations to do here
    kwargs_defaults: Iterable = reversed(
        (
            *zip_longest(
                reversed(node.kwonlyargs),
                reversed(node.kw_defaults),
                fillvalue=None,
            ),
        ),
    )
    kwarg: ast.arg
    kwarg_default: ast.AST | None
    for kwarg, kwarg_default in kwargs_defaults:
        parameters.append(
            (kwarg.arg, kwarg.annotation, ParameterKind.keyword_only, kwarg_default),
        )

    if node.kwarg:
        parameters.append(
            (
                node.kwarg.arg,
                node.kwarg.annotation,
                ParameterKind.var_keyword,
                "{}",
            ),
        )

    return parameters


def get_call_keyword_arguments(node: ast.Call, parent: Module | Class) -> dict[str, Any]:
    """Get the list of keyword argument names and values from a Call node.

    Parameters:
        node: The node to extract the keyword arguments from.

    Returns:
        The keyword argument names and values.
    """
    return {kw.arg: safe_get_expression(kw.value, parent) for kw in node.keywords if kw.arg}


__all__ = ["get_call_keyword_arguments"]
