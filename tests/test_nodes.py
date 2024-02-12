"""Test nodes utilities."""

from __future__ import annotations

import logging
from ast import PyCF_ONLY_AST

import pytest

from griffe.agents.nodes import relative_to_absolute
from griffe.expressions import Expr, ExprName
from griffe.tests import module_vtree, temporary_visited_module

syntax_examples = [
    # operations
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
    # unary operations
    "+b",
    "-b",
    "~b",
    # comparisons
    "b == c",
    "b >= c",
    "b > c",
    "b <= c",
    "b < c",
    "b != c",
    # boolean logic
    "b and c",
    "b or c",
    "not b",
    # identify
    "b is c",
    "b is not c",
    # membership
    "b in c",
    "b not in c",
    # calls
    "call()",
    "call(something)",
    "call(something=something)",
    # strings
    "f'a {round(key, 2)} {z}'",
    # slices
    "o[x]",
    "o[x, y]",
    "o[x:y]",
    "o[x:y, z]",
    "o[x, y(z)]",
    # walrus operator
    "a if (a := b) else c",
    # starred
    "a(*b, **c)",
    # structs
    "(a, b, c)",
    "{a, b, c}",
    "{a: b, c: d}",
    "[a, b, c]",
    # yields
    "yield",
    "yield a",
    "yield from a",
    # lambdas
    "lambda a: a",
    "lambda a, b: a",
    "lambda *a, **b: a",
    "lambda a, b=0: a",
    "lambda a, /, b, c: a",
    "lambda a, *, b, c: a",
    "lambda a, /, b, *, c: a",
]


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
    node = compile(code, mode="exec", filename="<>", flags=PyCF_ONLY_AST).body[0]  # type: ignore[attr-defined]
    module = module_vtree(path, leaf_package=is_package, return_leaf=True)
    for name in node.names:
        assert relative_to_absolute(node, name, module) == expected


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

        # make space after comma non-significant
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
        params = module.members["f"].parameters  # type: ignore[union-attr]
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
    with caplog.at_level(logging.ERROR), temporary_visited_module(
        """
            from collections import namedtuple
            class Thing(namedtuple('Thing', 'attr1 attr2')):
                ...
            """,
    ):
        pass
    assert not caplog.records
