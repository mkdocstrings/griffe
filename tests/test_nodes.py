"""Test nodes utilities."""

from __future__ import annotations

from ast import PyCF_ONLY_AST

import pytest

from griffe.agents.nodes import get_value, relative_to_absolute
from griffe.expressions import Expression, Name
from tests.helpers import module_vtree, temporary_visited_module


@pytest.mark.parametrize(
    ("code", "path", "is_package", "expected"),
    [
        ("from . import b", "a", False, "a.b"),
        ("from . import c", "a.b", False, "a.c"),
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
def test_relative_to_absolute_imports(code, path, is_package, expected):
    """Check if relative imports are correctly converted to absolute ones.

    Parameters:
        code: The parametrized module code.
        path: The parametrized module path.
        is_package: Whether the module is a package (or subpackage) (parametrized).
        expected: The parametrized expected absolute path.
    """
    node = compile(code, mode="exec", filename="<>", flags=PyCF_ONLY_AST).body[0]
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
    ],
)
def test_building_annotations_from_nodes(expression):
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


def _flat(expression: str | Name | Expression) -> list[str | Name]:
    if not isinstance(expression, Expression):
        return [expression]
    items = []
    for item in expression:
        if isinstance(item, Expression):
            items.extend(_flat(item))
        else:
            items.append(item)
    return items


@pytest.mark.parametrize(
    ("code", "has_name"),
    [
        ("import typing\nclass A: ...\na: typing.Literal['A']", False),
        ("from typing import Literal\nclass A: ...\na: Literal['A']", False),
        ("from mod import A\na: 'A'", True),
        ("from mod import A\na: list['A']", True),
    ],
)
def test_forward_references(code, has_name):
    """Check that we support forward references (type names as strings).

    Parameters:
        code: Parametrized code.
        has_name: Whether the annotation should contain a Name rather than a string.
    """
    with temporary_visited_module(code) as module:
        flat = _flat(module["a"].annotation)
        if has_name:
            assert any(isinstance(item, Name) and item.source == "A" for item in flat)
            assert all(not (isinstance(item, str) and item == "A") for item in flat)
        else:
            assert any(isinstance(item, str) and item == "'A'" for item in flat)
            assert all(not (isinstance(item, Name) and item.source == "A") for item in flat)


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
def test_default_value_from_nodes(default):
    """Test getting default value from AST nodes.

    Parameters:
        default: A default value (parametrized).
    """
    module_defs = f"def f(x={default}):\n    return x"
    with temporary_visited_module(module_defs) as module:
        assert "f" in module.members
        params = module.members["f"].parameters
        assert len(params) == 1
        assert params[0].default == default


@pytest.mark.parametrize(
    "expression",
    [
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
        "f'{round(key, 2)}'",
        # slices
        "o[x]",
        "o[x,y]",
        "o[x:y]",
        "o[x:y,z]",
        "o[x, y(z)]",
    ],
)
def test_building_value_from_nodes(expression):
    """Test building value from AST nodes.

    Parameters:
        expression: An expression (parametrized).
    """
    node = compile(expression, mode="exec", filename="<>", flags=PyCF_ONLY_AST).body[0].value
    value = get_value(node)

    # make space after comma non-significant
    value = value.replace(", ", ",")
    expression = expression.replace(", ", ",")

    assert value == expression
