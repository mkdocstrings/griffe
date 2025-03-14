"""Test names and expressions methods."""

from __future__ import annotations

import ast
import sys

import pytest

from griffe import Module, Parser, get_expression, temporary_visited_module
from tests.test_nodes import syntax_examples


@pytest.mark.parametrize(
    ("annotation", "items"),
    [
        ("tuple[int, float] | None", 2),
        ("None | tuple[int, float]", 2),
        ("Optional[tuple[int, float]]", 2),
        ("typing.Optional[tuple[int, float]]", 2),
    ],
)
def test_explode_return_annotations(annotation: str, items: int) -> None:
    """Check that we correctly split items from return annotations.

    Parameters:
        annotation: The return annotation.
        items: The number of items to write in the docstring returns section.
    """
    newline = "\n            "
    returns = newline.join(f"x{_}: Some value." for _ in range(items))
    code = f"""
    import typing
    from typing import Optional

    def function() -> {annotation}:
        '''This function returns either two ints or None

        Returns:
            {returns}
        '''
    """
    with temporary_visited_module(code) as module:
        sections = module["function"].docstring.parse(Parser.google)
        assert sections[1].value


@pytest.mark.parametrize(
    "annotation",
    [
        "int",
        "tuple[int]",
        "dict[str, str]",
        "Optional[tuple[int, float]]",
    ],
)
def test_full_expressions(annotation: str) -> None:
    """Assert we can transform expressions to their full form without errors."""
    code = f"x: {annotation}"
    with temporary_visited_module(code) as module:
        assert str(module["x"].annotation) == annotation


def test_resolving_full_names() -> None:
    """Assert expressions are correctly transformed to their fully-resolved form."""
    with temporary_visited_module(
        """
        from package import module
        attribute1: module.Class

        from package import module as mod
        attribute2: mod.Class
        """,
    ) as module:
        assert module["attribute1"].annotation.canonical_path == "package.module.Class"
        assert module["attribute2"].annotation.canonical_path == "package.module.Class"


# YORE: EOL 3.11: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python less than 3.12 does not have PEP 695 generics")
def test_resolving_type_parameters() -> None:
    """Assert type parameters correctly transformed to their fully-resolved form."""
    with temporary_visited_module(
        """
        class C[T]:
            class D[T]:
                def func[Y](self, arg1: T, arg2: Y): pass
                attr: T

            def func[Z](arg1: T, arg2: Y): pass
        """,
    ) as module:
        assert module["C.D.func"].parameters["arg1"].annotation.canonical_path == "module.C.D:T"
        assert module["C.D.func"].parameters["arg2"].annotation.canonical_path == "module.C.D.func:Y"

        assert module["C.D.attr"].annotation.canonical_path == "module.C.D:T"

        assert module["C.func"].parameters["arg1"].annotation.canonical_path == "module.C:T"
        assert module["C.func"].parameters["arg2"].annotation.canonical_path == "Y"


@pytest.mark.parametrize("code", syntax_examples)
def test_expressions(code: str) -> None:
    """Test building annotations from AST nodes.

    Parameters:
        code: An expression (parametrized).
    """
    top_node = compile(code, filename="<>", mode="exec", flags=ast.PyCF_ONLY_AST, optimize=2)
    expression = get_expression(top_node.body[0].value, parent=Module("module"))  # type: ignore[attr-defined]
    assert str(expression) == code


def test_length_one_tuple_as_string() -> None:
    """Length-1 tuples must have a trailing comma."""
    code = "x = ('a',)"
    with temporary_visited_module(code) as module:
        assert str(module["x"].value) == "('a',)"


def test_resolving_init_parameter() -> None:
    """Instance attribute values should resolve to matching parameters.

    They must not resolve to the member of the same name in the same class,
    or to objects with the same name in higher scopes.
    """
    with temporary_visited_module(
        """
        x = 1

        class Class:
            def __init__(self, x: int):
                self.x: int = x
        """,
    ) as module:
        assert module["Class.x"].value.canonical_path == "module.Class(x)"
