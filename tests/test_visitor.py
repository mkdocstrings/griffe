"""Test visit mechanisms."""

import pytest

from tests.helpers import temporary_visited_module

# import sys
# import hypothesmith as hs
# import libcst
# from hypothesis import given, settings
# @given(hs.from_node(node=libcst.Module))
# @pytest.mark.skipif(sys.version_info >= (3, 11, 0), reason="Too slow on Python 3.11?")
# def test_visit_arbitrary_code(code: str):
#     with temporary_visited_module(code):
#         ...


# TODO: move this in test_nodes once hypothesmith is ready
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
    ],
)
def test_building_value_from_nodes(expression):
    """Test building value from AST nodes.

    Parameters:
        expression: An expression (parametrized).
    """
    with temporary_visited_module(f"a = {expression}") as module:
        assert "a" in module.members
        assert module["a"].value == expression
