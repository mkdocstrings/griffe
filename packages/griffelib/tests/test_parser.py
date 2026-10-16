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
import inspect
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest

from griffe import Extension, Extensions
from griffe._internal.agents import parser as parser_module
from griffe._internal.agents.visitor import Visitor, visit


class _NodeExtension(Extension):
    def on_function_node(self, **kwargs: Any) -> None:
        pass


class _PostLoadExtension(Extension):
    def on_function(self, **kwargs: Any) -> None:
        pass


def test_all_node_aware_hooks_are_registered() -> None:
    """Keep native routing synchronized with visit-time extension API additions."""
    node_aware_hooks = {
        name
        for name, callback in vars(Extension).items()
        if name.startswith("on_") and "node" in inspect.signature(callback).parameters
    }

    assert set(parser_module._NODE_AWARE_HOOKS) == node_aware_hooks


def test_native_parser_is_used_without_node_aware_hooks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Use Ruff when installed extensions do not require the concrete source AST."""
    calls = 0

    def prune(code: str) -> str:
        nonlocal calls
        calls += 1
        return code

    monkeypatch.setattr(parser_module, "prune_source", prune)
    parser_module._compile_module("def f(): pass", filename="module.py", extensions=Extensions(_PostLoadExtension()))

    assert calls == 1


def test_native_parser_is_skipped_without_functions(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid paying for a second parse when no implementation suite can be removed."""
    calls = 0

    def prune(code: str) -> str:
        nonlocal calls
        calls += 1
        return code

    monkeypatch.setattr(parser_module, "prune_source", prune)
    parser_module._compile_module("value = 1", filename="module.py", extensions=Extensions())

    assert calls == 0


def test_native_parser_is_skipped_for_stub_files(monkeypatch: pytest.MonkeyPatch) -> None:
    """Avoid pruning stub files, whose function bodies contain no implementations."""
    calls = 0

    def prune(code: str) -> str:
        nonlocal calls
        calls += 1
        return code

    monkeypatch.setattr(parser_module, "prune_source", prune)
    parser_module._compile_module("def f(): ...", filename="module.pyi", extensions=Extensions())

    assert calls == 0


def test_node_aware_hooks_force_cpython_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep complete CPython nodes available to visit-time extension callbacks."""
    calls = 0

    def prune(code: str) -> str:
        nonlocal calls
        calls += 1
        return code

    monkeypatch.setattr(parser_module, "prune_source", prune)
    parser_module._compile_module("def f(): pass", filename="module.py", extensions=Extensions(_NodeExtension()))

    assert calls == 0


def test_custom_visitors_can_disable_native_pruning(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the complete tree available to Visitor subclasses with custom traversal."""
    calls = 0

    def prune(code: str) -> str:
        nonlocal calls
        calls += 1
        return code

    monkeypatch.setattr(parser_module, "prune_source", prune)

    class CustomVisitor(Visitor):
        pass

    CustomVisitor("module", Path("module.py"), "def f(): pass", Extensions()).get_module()

    assert calls == 0


def test_cpython_retries_an_invalid_native_result(monkeypatch: pytest.MonkeyPatch) -> None:
    """Never expose a diagnostic caused by native source pruning."""
    monkeypatch.setattr(parser_module, "prune_source", lambda code: "def invalid(: pass")

    node = parser_module._compile_module("def valid(): pass", filename="module.py", extensions=Extensions())

    assert isinstance(node.body[0], ast.FunctionDef)


def test_cpython_compiles_untouched_source_when_native_declines(monkeypatch: pytest.MonkeyPatch) -> None:
    """Use the normal source when Ruff cannot prune it."""
    monkeypatch.setattr(parser_module, "prune_source", lambda code: None)

    node = parser_module._compile_module("def valid(): pass", filename="module.py", extensions=Extensions())

    assert isinstance(node.body[0], ast.FunctionDef)


@pytest.mark.skipif(parser_module.prune_source is None, reason="prune-source is not installed")
def test_native_and_cpython_visitors_are_equivalent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Produce the same public model from the native and compatibility parser paths."""
    source = dedent(
        '''
        """Module docs."""

        from typing import TYPE_CHECKING, overload

        CONSTANT: int = 1
        """Constant docs."""

        if TYPE_CHECKING:
            import platform

        @overload
        def convert(value: int) -> str: ...

        def convert(value: object) -> str:
            temporary = repr(value)
            return temporary

        class Example:
            """Class docs."""

            field: int

            def __init__(self, field: int = 0) -> None:
                self.field = field
                """Field docs."""

            @property
            def doubled(self) -> int:
                intermediate = self.field * 2
                return intermediate
        ''',
    )
    native_prune_source = parser_module.prune_source
    native = visit("module", Path("module.py"), source, extensions=Extensions())

    monkeypatch.setattr(parser_module, "prune_source", None)
    cpython = visit("module", Path("module.py"), source, extensions=Extensions())
    monkeypatch.setattr(parser_module, "prune_source", native_prune_source)

    assert native.as_json(full=True, sort_keys=True) == cpython.as_json(full=True, sort_keys=True)
