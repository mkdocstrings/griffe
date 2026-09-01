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

# Test nodes utilities.

from __future__ import annotations

import logging
import sys
import weakref
from ast import AST, Add, Name, PyCF_ONLY_AST

import pytest

from griffe import (
    Expr,
    ExprName,
    ast_children,
    module_vtree,
    relative_to_absolute,
    temporary_visited_module,
)
from griffe._internal.agents import visitor as visitor_module

syntax_examples = [
    # Operations.
    "b + c",
    "b - c",
    "b * c",
    "b / c",
    "b // c",
    "b ** c",
    "b ^ c",
    "b & c",
    "b | c",
    "b @ c",
    "b % c",
    "b >> c",
    "b << c",
    # Unary operations.
    "+b",
    "-b",
    "~b",
    # Comparisons.
    "b == c",
    "b >= c",
    "b > c",
    "b <= c",
    "b < c",
    "b != c",
    # Boolean logic.
    "b and c",
    "b or c",
    "not b",
    # Identify.
    "b is c",
    "b is not c",
    # Membership.
    "b in c",
    "b not in c",
    # Calls.
    "call()",
    "call(something)",
    "call(something=something)",
    # Strings.
    "f'a {round(key, 2)} {z}'",
    'f"it\'s {x}"',  # ' only -> " delimiter
    "f\"don't {x} won't {y}\"",  # multiple ' -> " delimiter
    "f'say \"hello\" to {x}'",  # " only -> ' delimiter
    'f\'"quoted" and "re-quoted" {x}\'',  # multiple " -> ' delimiter
    "f'''it's \"complicated\" {x}'''",  # both -> triple-' delimiter
    "f'''she said \"it's fine\" to {x}'''",  # both, different parts -> triple-'
    # YORE: EOL 3.13: Regex-replace `\*\(\[(.+)\].+\),` with `\1,` within line.
    *(["t'a {round(key, 2)} {z}'"] if sys.version_info >= (3, 14) else []),
    # YORE: EOL 3.13: Regex-replace `\*\(\[(.+)\].+\),` with `\1,` within line.
    *(['t"it\'s {x}"'] if sys.version_info >= (3, 14) else []),
    # YORE: EOL 3.13: Regex-replace `\*\(\[(.+)\].+\),` with `\1,` within line.
    *(["t'say \"hello\" to {x}'"] if sys.version_info >= (3, 14) else []),
    # YORE: EOL 3.13: Regex-replace `\*\(\[(.+)\].+\),` with `\1,` within line.
    *(["t'''it's \"complicated\" {x}'''"] if sys.version_info >= (3, 14) else []),
    # Formatted values: conversions and format specifiers.
    "f'{x!r}'",
    "f'{x!s}'",
    "f'{x!a}'",
    "f'{x:>10}'",
    "f'{x:{width}}'",
    "f'{x!r:>{width}}'",
    "f'a {x:%Y-%m-%d} b'",
    "f'{(x := 1)}'",
    "f'{ {1: 2}}'",
    # YORE: EOL 3.13: Regex-replace `\*\(\[(.+)\].+\),` with `\1,` within line.
    *(["t'{x!r}'"] if sys.version_info >= (3, 14) else []),
    # YORE: EOL 3.13: Regex-replace `\*\(\[(.+)\].+\),` with `\1,` within line.
    *(["t'{x!s:>{width}}'"] if sys.version_info >= (3, 14) else []),
    # Slices.
    "o[x]",
    "o[x, y]",
    "o[x:y]",
    "o[x:y, z]",
    "o[x, y(z)]",
    "o[(a, b):y]",
    "o[a + b:]",
    # Walrus operator.
    "a if (a := b) else c",
    "{(a := 1): 2}",
    "{1: (a := 2)}",
    "[a for a in b if (c := a)]",
    # Starred.
    "a(*b, **c)",
    "a(*b | c)",
    # Structs.
    "(a, b, c)",
    "{a, b, c}",
    "{a: b, c: d}",
    "{a + b: c + d for a, b in e}",
    "[a, b, c]",
    "[a + b for a in c]",
    # Generator expressions.
    "(a + b for a in c)",
    "a(b for b in c)",
    "sum((a for a in b), c)",
    "[(a for a in b), c]",
    "{1: (a for a in b)}",
    "(a for a in b if (c := a))",
    # Yields.
    "yield",
    "yield a",
    "yield a + b",
    "yield from a",
    # Lambdas.
    "lambda a: a",
    "lambda a, b: a",
    "lambda *a, **b: a",
    "lambda a, b=0: a",
    "lambda a=b + c: a",
    "lambda a, /, b, c: a",
    "lambda a, *, b, c: a",
    "lambda a, /, b, *, c: a",
    "lambda a, /: a",
    "lambda a, b, /: a",
    "lambda a, /, *args: args",
    "lambda a, /, **kwargs: kwargs",
    "lambda a, /, *, b: b",
    "lambda a, /, b=0, *args, c=1, **kwargs: a",
    "lambda *args, b: b",
    "lambda *args, b=0: b",
    # Calls with expression-level arguments.
    "call(a=b + c)",
    # Attribute access on integer literals.
    "(1).bit_length()",
]


def test_shared_ast_nodes_do_not_retain_parent_trees() -> None:
    """Shared AST operator/context instances must not keep parsed trees alive."""
    expression = compile("left + right", filename="<test>", mode="eval", flags=PyCF_ONLY_AST).body  # ty:ignore[unresolved-attribute]
    children = list(ast_children(expression))

    assert any(isinstance(child, Name) and child.parent is expression for child in children)  # ty:ignore[unresolved-attribute]
    assert any(isinstance(child, Add) and not hasattr(child, "parent") for child in children)
    assert all(isinstance(child, AST) for child in children)


def test_visitor_releases_ast_without_cyclic_gc(monkeypatch: pytest.MonkeyPatch) -> None:
    """A completed static analysis must not leave parent cycles behind."""
    references: list[weakref.ReferenceType[AST]] = []
    builtin_compile = compile

    def capture_ast(*args: object, **kwargs: object) -> AST:
        node = builtin_compile(*args, **kwargs)  # ty:ignore[no-matching-overload]
        references.append(weakref.ref(node))
        return node

    monkeypatch.setattr(visitor_module, "compile", capture_ast, raising=False)
    with temporary_visited_module("value = left + right"):
        pass

    assert references
    assert all(reference() is None for reference in references)


@pytest.mark.parametrize(
    ("code", "path", "is_package", "expected"),
    [
        ("from . import b", "a", False, "a.b"),
        ("from . import b", "a", True, "a.b"),
        ("from . import c", "a.b", False, "a.c"),
        ("from . import c", "a.b", True, "a.b.c"),
        ("from . import d", "a.b.c", False, "a.b.d"),
        ("from .c import d", "a", False, "a.c.d"),
        ("from .c import d", "a.b", False, "a.c.d"),
        ("from .b import c", "a.b", True, "a.b.b.c"),
        ("from .. import e", "a.c.d.i", False, "a.c.e"),
        ("from ..d import e", "a.c.d.i", False, "a.c.d.e"),
        ("from ... import f", "a.c.d.i", False, "a.f"),
        ("from ...b import f", "a.c.d.i", False, "a.b.f"),
        ("from ...c.d import e", "a.c.d.i", False, "a.c.d.e"),
        ("from .c import *", "a", False, "a.c.*"),
        ("from .c import *", "a.b", False, "a.c.*"),
        ("from .b import *", "a.b", True, "a.b.b.*"),
        ("from .. import *", "a.c.d.i", False, "a.c.*"),
        ("from ..d import *", "a.c.d.i", False, "a.c.d.*"),
        ("from ... import *", "a.c.d.i", False, "a.*"),
        ("from ...b import *", "a.c.d.i", False, "a.b.*"),
        ("from ...c.d import *", "a.c.d.i", False, "a.c.d.*"),
    ],
)
def test_relative_to_absolute_imports(code: str, path: str, is_package: bool, expected: str) -> None:
    """Check if relative imports are correctly converted to absolute ones.

    Parameters:
        code: The parametrized module code.
        path: The parametrized module path.
        is_package: Whether the module is a package (or subpackage) (parametrized).
        expected: The parametrized expected absolute path.
    """
    node = compile(code, mode="exec", filename="<>", flags=PyCF_ONLY_AST).body[0]  # ty:ignore[unresolved-attribute]
    module = module_vtree(path, leaf_package=is_package, return_leaf=True)
    for name in node.names:
        assert relative_to_absolute(node, name, module) == expected


def test_multipart_imports() -> None:
    """Assert that a multipart path like `a.b.c` imported as `x` points to the right target."""
    with temporary_visited_module(
        """
        import pkg.b.c
        import pkg.b.c as alias
        """,
    ) as module:
        pkg = module["pkg"]
        alias = module["alias"]
    assert pkg.target_path == "pkg"
    assert alias.target_path == "pkg.b.c"


@pytest.mark.parametrize(
    "expression",
    [
        "A",
        "A.B",
        "A[B]",
        "A.B[C.D]",
        "~A",
        "A | B",
        "A[[B, C], D]",
        "A(b=c, d=1)",
        "A[-1, +2.3]",
        "A[B, C.D(e='syntax error')]",
    ],
)
def test_building_annotations_from_nodes(expression: str) -> None:
    """Test building annotations from AST nodes.

    Parameters:
        expression: An expression (parametrized).
    """
    class_defs = "\n\n".join(f"class {letter}: ..." for letter in "ABCD")
    with temporary_visited_module(f"{class_defs}\n\nx: {expression}\ny: {expression} = 0") as module:
        assert "x" in module.members
        assert "y" in module.members
        assert str(module["x"].annotation) == expression
        assert str(module["y"].annotation) == expression


@pytest.mark.parametrize("code", syntax_examples)
def test_building_expressions_from_nodes(code: str) -> None:
    """Test building annotations from AST nodes.

    Parameters:
        code: An expression (parametrized).
    """
    with temporary_visited_module(f"__z__ = {code}") as module:
        assert "__z__" in module.members

        # Make space after comma non-significant.
        value = str(module["__z__"].value).replace(", ", ",")
        assert value == code.replace(", ", ",")


@pytest.mark.parametrize(
    ("code", "has_name"),
    [
        ("import typing\nclass A: ...\na: typing.Literal['A']", False),
        ("from typing import Literal\nclass A: ...\na: Literal['A']", False),
        ("import typing_extensions\nclass A: ...\na: typing.Literal['A']", False),
        ("from typing_extensions import Literal\nclass A: ...\na: Literal['A']", False),
        ("from mod import A\na: 'A'", True),
        ("from mod import A\na: list['A']", True),
    ],
)
def test_forward_references(code: str, has_name: bool) -> None:
    """Check that we support forward references (type names as strings).

    Parameters:
        code: Parametrized code.
        has_name: Whether the annotation should contain a Name rather than a string.
    """
    with temporary_visited_module(code) as module:
        annotation = list(module["a"].annotation.iterate(flat=True))
        if has_name:
            assert any(isinstance(item, ExprName) and item.name == "A" for item in annotation)
            assert all(not (isinstance(item, str) and item == "A") for item in annotation)
        else:
            assert "'A'" in annotation
            assert all(not (isinstance(item, ExprName) and item.name == "A") for item in annotation)


@pytest.mark.parametrize(
    "default",
    [
        "1",
        "'test_string'",
        "dict(key=1)",
        "{'key': 1}",
        "DEFAULT_VALUE",
        "None",
    ],
)
def test_default_value_from_nodes(default: str) -> None:
    """Test getting default value from AST nodes.

    Parameters:
        default: A default value (parametrized).
    """
    module_defs = f"def f(x={default}):\n    return x"
    with temporary_visited_module(module_defs) as module:
        assert "f" in module.members
        params = module.members["f"].parameters  # ty:ignore[unresolved-attribute]
        assert len(params) == 1
        assert str(params[0].default) == default


# https://github.com/mkdocstrings/griffe/issues/159
def test_parsing_complex_string_annotations() -> None:
    """Test parsing of complex, stringified annotations."""
    with temporary_visited_module(
        """
        class ArgsKwargs:
            def __init__(self, args: 'tuple[Any, ...]', kwargs: 'dict[str, Any] | None' = None) -> None:
                ...

            @property
            def args(self) -> 'tuple[Any, ...]':
                ...

            @property
            def kwargs(self) -> 'dict[str, Any] | None':
                ...
        """,
    ) as module:
        init_args_annotation = module["ArgsKwargs.__init__"].parameters["args"].annotation
        assert isinstance(init_args_annotation, Expr)
        assert init_args_annotation.is_tuple
        kwargs_return_annotation = module["ArgsKwargs.kwargs"].annotation
        assert isinstance(kwargs_return_annotation, Expr)


def test_parsing_dynamic_base_classes(caplog: pytest.LogCaptureFixture) -> None:
    """Assert parsing dynamic base classes does not trigger errors.

    Parameters:
        caplog: Pytest fixture to capture logs.
    """
    with (
        caplog.at_level(logging.ERROR),
        temporary_visited_module(
            """
            from collections import namedtuple
            class Thing(namedtuple('Thing', 'attr1 attr2')):
                ...
            """,
        ),
    ):
        pass
    assert not caplog.records
