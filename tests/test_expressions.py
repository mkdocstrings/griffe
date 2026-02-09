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


@pytest.mark.parametrize("code", syntax_examples)
def test_expressions(code: str) -> None:
    """Test building annotations from AST nodes.

    Parameters:
        code: An expression (parametrized).
    """
    top_node = compile(code, filename="<>", mode="exec", flags=ast.PyCF_ONLY_AST, optimize=2)
    expression = get_expression(top_node.body[0].value, parent=Module("module"))  # ty:ignore[unresolved-attribute]
    assert str(expression) == code


def test_length_one_tuple_as_string() -> None:
    """Length-1 tuples must have a trailing comma."""
    code = "x = ('a',)"
    with temporary_visited_module(code) as module:
        assert str(module["x"].value) == "('a',)"


@pytest.mark.parametrize(
    ("annotation", "modernized"),
    [
        ("Union[str, int, float]", "str | int | float"),
        ("typing.Union[str, int, float]", "str | int | float"),
        ("Union[Tuple[str, ...], Dict[str, int]]", "tuple[str, ...] | dict[str, int]"),
        ("typing.Union[typing.Tuple[str, ...], typing.Dict[str, int]]", "tuple[str, ...] | dict[str, int]"),
        ("Tuple[List[Dict[str, Set[str]]]]", "tuple[list[dict[str, set[str]]]]"),
        ("typing.Tuple[typing.List[typing.Dict[str, typing.Set[str]]]]", "tuple[list[dict[str, set[str]]]]"),
        ("Optional[Tuple[List[bool]]]", "tuple[list[bool]] | None"),
        ("typing.Optional[typing.Tuple[typing.List[bool]]]", "tuple[list[bool]] | None"),
    ],
)
def test_modernizing_specific_expressions(annotation: str, modernized: str) -> None:
    """Modernize expressions correctly.

    Parameters:
        annotation: Original annotation (parametrized).
        modernized: Expected modernized annotation (parametrized).
    """
    with temporary_visited_module(
        f"""
        import typing
        from typing import Union, Optional, Tuple, Dict, List, Set, Literal
        a: {annotation}
        """,
    ) as module:
        expression = module["a"].annotation
        assert str(expression.modernize()) == modernized


@pytest.mark.parametrize(
    "annotation",
    [
        "typing.Literal['s']",
        "Literal['s']",
    ],
)
def test_handling_modernization_without_crashing(annotation: str) -> None:
    """Modernizing expressions never crashes.

    Parameters:
        annotation: Original annotation (parametrized).
    """
    with temporary_visited_module(
        f"""
        import typing
        from typing import Union, Optional, Tuple, Dict, List, Set, Literal
        a: {annotation}
        """,
    ) as module:
        module["a"].annotation.modernize()


@pytest.mark.parametrize("code", syntax_examples)
def test_modernizing_idempotence(code: str) -> None:
    """Modernize expressions that can't be modernized.

    Parameters:
        code: An expression (parametrized).
    """
    top_node = compile(code, filename="<>", mode="exec", flags=ast.PyCF_ONLY_AST, optimize=2)
    expression = get_expression(top_node.body[0].value, parent=Module("module"))  # ty:ignore[unresolved-attribute]
    modernized = expression.modernize()  # ty:ignore[possibly-missing-attribute]
    assert expression == modernized
    assert str(expression) == str(modernized)


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


@pytest.mark.parametrize(
    "code",
    [
        # Core.
        "a * (b + c)",  # Lower precedence as a sub-expression of one that has higher precedence.
        "(a and b) == c",
        "((a | b) + c).d",
        "a - (b - c)",  # Left-association.
        "(a ** b) ** c",  # Right-association.
        # Unary operator and edge cases:
        # > The power operator `**` binds less tightly than an arithmetic
        # > or bitwise unary operator on its right, that is, `2**-1` is `0.5`.
        "a ** -b",
        "-a ** b",
        "(-a) ** b",
        # Misc: conditionals, lambdas, comprehensions and generators.
        "(lambda: 0).a",
        "(lambda x: a + x if b else c)(d).e",
        "a if (b if c else d) else e",  # Right-association.
        "(a if b else c) if d else e",  # Forced left-association.
        "(a for a in b).c",
    ],
)
def test_parentheses_preserved(code: str) -> None:
    """Parentheses used to enforce an order of operations should not be removed."""
    with temporary_visited_module(f"val = {code}") as module:
        value_expr = module["val"].value
        assert str(value_expr) == code


# YORE: EOL 3.11: Remove line.
@pytest.mark.skipif(sys.version_info < (3, 12), reason="Python less than 3.12 does not have PEP 695 generics")
def test_resolving_type_parameters() -> None:
    """Assert type parameters are correctly transformed to their fully-resolved form."""
    with temporary_visited_module(
        """
        class C[T]:
            class D[T]:
                def func[Y](self, arg1: T, arg2: Y): pass
                attr: T
            def func[Z](arg1: T, arg2: Y): pass
        """,
    ) as module:
        assert module["C.D.func"].parameters["arg1"].annotation.canonical_path == "module.C.D[T]"
        assert module["C.D.func"].parameters["arg2"].annotation.canonical_path == "module.C.D.func[Y]"

        assert module["C.D.attr"].annotation.canonical_path == "module.C.D[T]"

        assert module["C.func"].parameters["arg1"].annotation.canonical_path == "module.C[T]"
        assert module["C.func"].parameters["arg2"].annotation.canonical_path == "Y"


def test_render_dict_comprehension() -> None:
    """Assert dict comprehensions are rendered correctly."""
    with temporary_visited_module(
        """
        d = {k: v for k, v in items if k}
        """,
    ) as module:
        assert str(module["d"].value) == "{k: v for k, v in items if k}"
