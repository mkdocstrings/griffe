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

# Test functions loading.

from __future__ import annotations

import pytest

from griffe import ParameterKind, temporary_visited_module


def test_visit_simple_function() -> None:
    """Test functions parameters loading."""
    with temporary_visited_module("def f(foo='<>'): ...") as module:
        function = module["f"]
        assert len(function.parameters) == 1
        param = function.parameters[0]
        assert param is function.parameters["foo"]
        assert param.name == "foo"
        assert param.kind is ParameterKind.positional_or_keyword
        assert param.default == "'<>'"


def test_visit_function_positional_only_param() -> None:
    """Test functions parameters loading."""
    with temporary_visited_module("def f(posonly, /): ...") as module:
        function = module["f"]
        assert len(function.parameters) == 1
        param = function.parameters[0]
        assert param is function.parameters["posonly"]
        assert param.name == "posonly"
        assert param.kind is ParameterKind.positional_only
        assert param.default is None


def test_visit_function_positional_only_param_with_default() -> None:
    """Test functions parameters loading."""
    with temporary_visited_module("def f(posonly=0, /): ...") as module:
        function = module["f"]
        assert len(function.parameters) == 1
        param = function.parameters[0]
        assert param is function.parameters["posonly"]
        assert param.name == "posonly"
        assert param.kind is ParameterKind.positional_only
        assert param.default == "0"


def test_visit_function_positional_or_keyword_param() -> None:
    """Test functions parameters loading."""
    with temporary_visited_module("def f(posonly, /, poskw): ...") as module:
        function = module["f"]
        assert len(function.parameters) == 2
        param = function.parameters[1]
        assert param is function.parameters["poskw"]
        assert param.name == "poskw"
        assert param.kind is ParameterKind.positional_or_keyword
        assert param.default is None


def test_visit_function_positional_or_keyword_param_with_default() -> None:
    """Test functions parameters loading."""
    with temporary_visited_module("def f(posonly, /, poskw=0): ...") as module:
        function = module["f"]
        assert len(function.parameters) == 2
        param = function.parameters[1]
        assert param is function.parameters["poskw"]
        assert param.name == "poskw"
        assert param.kind is ParameterKind.positional_or_keyword
        assert param.default == "0"


def test_visit_function_keyword_only_param() -> None:
    """Test functions parameters loading."""
    with temporary_visited_module("def f(*, kwonly): ...") as module:
        function = module["f"]
        assert len(function.parameters) == 1
        param = function.parameters[0]
        assert param is function.parameters["kwonly"]
        assert param.name == "kwonly"
        assert param.kind is ParameterKind.keyword_only
        assert param.default is None


def test_visit_function_keyword_only_param_with_default() -> None:
    """Test functions parameters loading."""
    with temporary_visited_module("def f(*, kwonly=0): ...") as module:
        function = module["f"]
        assert len(function.parameters) == 1
        param = function.parameters[0]
        assert param is function.parameters["kwonly"]
        assert param.name == "kwonly"
        assert param.kind is ParameterKind.keyword_only
        assert param.default == "0"


def test_visit_function_syntax_error() -> None:
    """Test functions parameters loading."""
    with pytest.raises(SyntaxError), temporary_visited_module("def f(/, poskw=0): ..."):
        ...


def test_visit_function_variadic_params() -> None:
    """Test functions variadic parameters visit."""
    with temporary_visited_module("def f(*args: str, kw=1, **kwargs: int): ...") as module:
        function = module["f"]
        assert len(function.parameters) == 3
        param = function.parameters[0]
        assert param.name == "args"
        assert param.annotation.name == "str"
        assert param.annotation.canonical_path == "str"
        param = function.parameters[1]
        assert param.annotation is None
        param = function.parameters[2]
        assert param.name == "kwargs"
        assert param.annotation.name == "int"
        assert param.annotation.canonical_path == "int"


def test_visit_function_params_annotations() -> None:
    """Test functions parameters loading."""
    with temporary_visited_module(
        """
        import typing
        from typing import Any
        def f_annorations(
            a: str,
            b: Any,
            c: typing.Optional[typing.List[int]],
            d: float | None):
            ...
        """,
    ) as module:
        function = module["f_annorations"]
        assert len(function.parameters) == 4
        param = function.parameters[0]
        assert param.annotation.name == "str"
        assert param.annotation.canonical_path == "str"
        param = function.parameters[1]
        assert param.annotation.name == "Any"
        assert param.annotation.canonical_path == "typing.Any"
        param = function.parameters[2]
        assert str(param.annotation) == "typing.Optional[typing.List[int]]"
        param = function.parameters[3]
        assert str(param.annotation) == "float | None"
