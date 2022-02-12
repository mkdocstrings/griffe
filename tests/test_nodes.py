"""Test nodes utilities."""

from ast import PyCF_ONLY_AST

import pytest

from griffe.agents.nodes import relative_to_absolute
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
