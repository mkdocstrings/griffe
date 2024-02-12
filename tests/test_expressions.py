"""Test names and expressions methods."""

from __future__ import annotations

import ast

import pytest

from griffe.dataclasses import Module
from griffe.docstrings.parsers import Parser
from griffe.expressions import get_expression
from griffe.tests import temporary_visited_module
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


@pytest.mark.parametrize("code", syntax_examples)
def test_expressions(code: str) -> None:
    """Test building annotations from AST nodes.

    Parameters:
        code: An expression (parametrized).
    """
    top_node = compile(code, filename="<>", mode="exec", flags=ast.PyCF_ONLY_AST, optimize=2)
    expression = get_expression(top_node.body[0].value, parent=Module("module"))  # type: ignore[attr-defined]
    assert str(expression) == code
