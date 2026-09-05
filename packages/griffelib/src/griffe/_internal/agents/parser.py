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

from __future__ import annotations

import ast
import sys
from importlib import import_module
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable

    from griffe._internal.extensions.base import Extensions


# These callbacks all receive a live AST node. The native fast path deliberately removes function
# implementation nodes that Griffe itself never visits, so extensions must see the original tree.
_NODE_AWARE_HOOKS: Final = (
    "on_node",
    "on_instance",
    "on_members",
    "on_module_node",
    "on_module_instance",
    "on_module_members",
    "on_class_node",
    "on_class_instance",
    "on_class_members",
    "on_function_node",
    "on_function_instance",
    "on_attribute_node",
    "on_attribute_instance",
    "on_type_alias_node",
    "on_type_alias_instance",
    "on_alias_instance",
)

try:
    from prune_source import prune_source
except (ImportError, KeyError):
    prune_source = None


def _compile_module(
    code: str,
    *,
    filename: str,
    extensions: Extensions,
    compiler: Callable[..., ast.Module] = compile,
    allow_native: bool = True,
) -> ast.Module:
    """Compile a module AST, pruning irrelevant function bodies with Ruff when possible."""
    source = code
    used_native = False
    if (
        allow_native
        and prune_source is not None
        and not filename.endswith(".pyi")
        and "def" in code
        and not extensions.has_hooks(*_NODE_AWARE_HOOKS)
    ):
        pruned = prune_source(code)
        if pruned is not None:
            source = pruned
            used_native = True

    try:
        # Preserve the visitor's existing AST compilation flags and optimization level.
        return compiler(source, mode="exec", filename=filename, flags=ast.PyCF_ONLY_AST, optimize=1)
    except SyntaxError:
        # Ruff and CPython occasionally differ in semantic validation. Recompile the untouched
        # source so callers always receive CPython's original result and diagnostic.
        if used_native:
            return compiler(code, mode="exec", filename=filename, flags=ast.PyCF_ONLY_AST, optimize=1)
        raise
