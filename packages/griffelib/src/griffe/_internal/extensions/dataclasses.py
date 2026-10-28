# SPDX-License-Identifier: ISC
#
# Copyright (c) 2021, Timothée Mazzucotelli and contributors
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Built-in extension adding support for dataclasses.
#
# This extension re-creates `__init__` methods of dataclasses
# during static analysis.

from __future__ import annotations

import ast
from contextlib import suppress
from functools import cache
from typing import Any, cast

from griffe._internal.enumerations import ParameterKind
from griffe._internal.expressions import (
    Expr,
    ExprAttribute,
    ExprCall,
    ExprDict,
)
from griffe._internal.extensions.base import Extension
from griffe._internal.logger import logger
from griffe._internal.models import Attribute, Class, Decorator, Function, Module, Parameter, Parameters


def _dataclass_decorator(decorators: list[Decorator]) -> Expr | None:
    for decorator in decorators:
        if isinstance(decorator.value, Expr) and decorator.value.canonical_path == "dataclasses.dataclass":
            return decorator.value
    return None


def _expr_args(expr: Expr) -> dict[str, str | Expr]:
    args = {}
    if isinstance(expr, ExprCall):
        for argument in expr.arguments:
            try:
                args[argument.name] = argument.value  # ty:ignore[unresolved-attribute]
            except AttributeError:
                # Argument is a unpacked variable.
                with suppress(Exception):
                    collection = expr.function.parent.modules_collection  # ty:ignore[unresolved-attribute]
                    var = collection[argument.value.canonical_path]  # ty:ignore[unresolved-attribute]
                    args.update(_expr_args(var.value))
    elif isinstance(expr, ExprDict):
        args.update({ast.literal_eval(str(key)): value for key, value in zip(expr.keys, expr.values, strict=False)})
    return args


def _dataclass_arguments(decorators: list[Decorator]) -> dict[str, Any]:
    if (expr := _dataclass_decorator(decorators)) and isinstance(expr, ExprCall):
        return _expr_args(expr)
    return {}


def _field_arguments(attribute: Attribute) -> dict[str, Any]:
    if attribute.value:
        value = attribute.value
        if isinstance(value, ExprAttribute):
            value = value.last
        if isinstance(value, ExprCall) and value.canonical_path == "dataclasses.field":
            return _expr_args(value)
    return {}


@cache
def _dataclass_parameters(class_: Class) -> dict[str, Parameter]:
    # Fetch `@dataclass` arguments if any.
    dec_args = _dataclass_arguments(class_.decorators)

    # Parameters not added to `__init__`, return empty dict.
    if dec_args.get("init") == "False":
        return {}

    # All parameters marked as keyword-only.
    kw_only = dec_args.get("kw_only") == "True"

    # Iterate on current attributes to find parameters.
    parameters: dict[str, Parameter] = {}
    for member in class_.members.values():
        if member.is_attribute:
            member = cast("Attribute", member)

            # All dataclass parameters have annotations.
            if member.annotation is None:
                continue

            # Attributes that have labels for these characteristics are
            # not class parameters:
            # - @property
            # - @cached_property
            # - ClassVar annotation
            if "property" in member.labels or (
                # TODO: It is better to explicitly check for `ClassVar`, but
                # `Visitor.handle_attribute` unwraps it from the annotation.
                # Maybe create `internal_labels` and store "classvar" in there.
                "class-attribute" in member.labels and "instance-attribute" not in member.labels
            ):
                continue

            # Start of keyword-only parameters.
            if isinstance(member.annotation, Expr) and member.annotation.canonical_path == "dataclasses.KW_ONLY":
                kw_only = True
                continue

            # Fetch `field` arguments if any.
            field_args = _field_arguments(member)

            # Parameter not added to `__init__`, skip it.
            if field_args.get("init") == "False":
                continue

            # Determine parameter kind. An explicit `field(kw_only=...)` takes
            # precedence over `@dataclass(kw_only=...)` and the `KW_ONLY` sentinel.
            field_kw_only = field_args.get("kw_only")
            kind = (
                ParameterKind.keyword_only
                if field_kw_only == "True" or (kw_only and field_kw_only != "False")
                else ParameterKind.positional_or_keyword
            )

            # Determine parameter default.
            if "default_factory" in field_args:
                default: str | Expr | None = ExprCall(function=field_args["default_factory"], arguments=[])
            else:
                default = field_args.get("default", None if field_args else member.value)

            # Add parameter to the dict.
            parameters[member.name] = Parameter(
                member.name,
                annotation=member.annotation,
                kind=kind,
                default=default,
                docstring=member.docstring,
            )

    return parameters


def _mro(class_: Class) -> list[Class]:
    try:
        return class_.mro()
    except ValueError:
        return []


def _dataclass_fields(
    class_: Class,
    collected: dict[Class, dict[str, Parameter]],
) -> dict[str, Parameter]:
    # The fields that `class_.__dataclass_fields__` holds at runtime, collected like Python does.
    # A dataclass gets the fields of each base, own and inherited, from the end of the MRO
    # to its start, then its own fields. A redeclared field replaces the previous one
    # but keeps its position. Any other class inherits the fields of the first dataclass
    # in its MRO, if any. `collected` holds the fields of classes already visited
    # while handling the current package; it is not a global cache because bases
    # can only be resolved once their packages are loaded.
    if class_ not in collected:
        fields: dict[str, Parameter] = {}
        if _dataclass_decorator(class_.decorators):
            for base in reversed(_mro(class_)):
                fields.update(_dataclass_fields(base, collected))
            fields.update(_dataclass_parameters(class_))
        else:
            for parent in _mro(class_):
                if _dataclass_decorator(parent.decorators):
                    fields.update(_dataclass_fields(parent, collected))
                    break
        collected[class_] = fields
    return collected[class_]


def _reorder_parameters(parameters: list[Parameter]) -> list[Parameter]:
    # Re-order, putting positional-only in front and keyword-only at the end.
    pos_only = []
    pos_kw = []
    kw_only = []
    for param in parameters:
        if param.kind is ParameterKind.positional_only:
            pos_only.append(param)
        elif param.kind is ParameterKind.keyword_only:
            kw_only.append(param)
        else:
            pos_kw.append(param)
    return pos_only + pos_kw + kw_only


def _set_dataclass_init(class_: Class, collected: dict[Class, dict[str, Parameter]]) -> None:
    # At least one parent dataclass makes the current class a dataclass:
    # that's how `dataclasses.is_dataclass` works.
    if any(_dataclass_decorator(parent.decorators) for parent in _mro(class_)):
        class_.labels.add("dataclass")

    # If the class is not decorated with `@dataclass`, skip it.
    if not _dataclass_decorator(class_.decorators):
        return

    logger.debug("Handling dataclass: %s", class_.path)

    # Collect all fields.
    init_parameters = list(_dataclass_fields(class_, collected).values())

    # Create `__init__` method with re-ordered parameters.
    init = Function(
        "__init__",
        lineno=0,
        endlineno=0,
        parent=class_,
        parameters=Parameters(
            Parameter(name="self", annotation=None, kind=ParameterKind.positional_or_keyword, default=None),
            *_reorder_parameters(init_parameters),
        ),
        returns="None",
    )
    class_.set_member("__init__", init)


def _del_members_annotated_as_initvar(class_: Class) -> None:
    # Definitions annotated as InitVar are not class members.
    attributes = [member for member in class_.members.values() if isinstance(member, Attribute)]
    for attribute in attributes:
        if isinstance(attribute.annotation, Expr) and attribute.annotation.canonical_path == "dataclasses.InitVar":
            class_.del_member(attribute.name)


def _apply_recursively(
    mod_cls: Module | Class,
    processed: set[str],
    collected: dict[Class, dict[str, Parameter]],
) -> None:
    if mod_cls.canonical_path in processed:
        return
    processed.add(mod_cls.canonical_path)
    if isinstance(mod_cls, Class):
        if "__init__" not in mod_cls.members:
            _set_dataclass_init(mod_cls, collected)
            _del_members_annotated_as_initvar(mod_cls)
        for member in mod_cls.members.values():
            if not member.is_alias and member.is_class:
                _apply_recursively(member, processed, collected)  # ty:ignore[invalid-argument-type]
    elif isinstance(mod_cls, Module):
        for member in mod_cls.members.values():
            if not member.is_alias and (member.is_module or member.is_class):
                _apply_recursively(member, processed, collected)  # ty:ignore[invalid-argument-type]


class DataclassesExtension(Extension):
    """Built-in extension adding support for dataclasses.

    This extension creates `__init__` methods of dataclasses
    if they don't already exist.
    """

    def on_package(self, *, pkg: Module, **kwargs: Any) -> None:  # noqa: ARG002
        """Hook for loaded packages.

        Parameters:
            pkg: The loaded package.
        """
        _apply_recursively(pkg, set(), {})
