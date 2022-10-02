"""Tests for the `diff` module."""

import sys

import pytest

from griffe.diff import BreakageKind, find_breaking_changes
from tests.helpers import temporary_visited_module


@pytest.mark.skipif(sys.version_info < (3, 8), reason="no positional-only parameters on Python 3.7")
@pytest.mark.parametrize(
    ("old_code", "new_code", "expected_breakages"),
    [
        # (
        #     "var: int",
        #     "var: str",
        #     [BreakageKind.ATTRIBUTE_CHANGED_TYPE],
        # ),
        (
            "a = True",
            "a = False",
            [BreakageKind.ATTRIBUTE_CHANGED_VALUE],
        ),
        (
            "class A(int, str): ...",
            "class A(int): ...",
            [BreakageKind.CLASS_REMOVED_BASE],
        ),
        (
            "A = 0",
            "class A: ...",
            [BreakageKind.OBJECT_CHANGED_KIND],
        ),
        (
            "a = True",
            "",
            [BreakageKind.OBJECT_REMOVED],
        ),
        (
            "def a(): ...",
            "def a(x): ...",
            [BreakageKind.PARAMETER_ADDED_REQUIRED],
        ),
        (
            "def a(x=0): ...",
            "def a(x=1): ...",
            [BreakageKind.PARAMETER_CHANGED_DEFAULT],
        ),
        (
            # positional-only to keyword-only
            "def a(x, /): ...",
            "def a(*, x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # keyword-only to positional-only
            "def a(*, x): ...",
            "def a(x, /): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # positional or keyword to positional-only
            "def a(x): ...",
            "def a(x, /): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # positional or keyword to keyword-only
            "def a(x): ...",
            "def a(*, x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        # to variadic positional
        (
            # positional-only to variadic positional
            "def a(x, /): ...",
            "def a(*x): ...",
            [],
        ),
        (
            # positional or keyword to variadic positional
            "def a(x): ...",
            "def a(*x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # keyword-only to variadic positional
            "def a(*, x): ...",
            "def a(*x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # variadic keyword to variadic positional
            "def a(**x): ...",
            "def a(*x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # positional or keyword to variadic positional, with variadic keyword
            "def a(x): ...",
            "def a(*x, **y): ...",
            [],
        ),
        (
            # keyword-only to variadic positional, with variadic keyword
            "def a(*, x): ...",
            "def a(*x, **y): ...",
            [],
        ),
        # to variadic keyword
        (
            # positional-only to variadic keyword
            "def a(x, /): ...",
            "def a(**x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # positional or keyword to variadic keyword
            "def a(x): ...",
            "def a(**x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # keyword-only to variadic keyword
            "def a(*, x): ...",
            "def a(**x): ...",
            [],
        ),
        (
            # variadic positional to variadic keyword
            "def a(*x): ...",
            "def a(**x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # positional-only to variadic keyword, with variadic positional
            "def a(x, /): ...",
            "def a(*y, **x): ...",
            [],
        ),
        (
            # positional or keyword to variadic keyword, with variadic positional
            "def a(x): ...",
            "def a(*y, **x): ...",
            [],
        ),
        (
            "def a(x=1): ...",
            "def a(x): ...",
            [BreakageKind.PARAMETER_CHANGED_REQUIRED],
        ),
        (
            "def a(x, y): ...",
            "def a(y, x): ...",
            [BreakageKind.PARAMETER_MOVED],
        ),
        (
            "def a(x, y): ...",
            "def a(x): ...",
            [BreakageKind.PARAMETER_REMOVED],
        ),
        (
            "def a() -> int: ...",
            "def a() -> str: ...",
            [BreakageKind.RETURN_CHANGED_TYPE],
        ),
    ],
)
def test_diff_griffe(old_code, new_code, expected_breakages):
    """Test the different incompatibility finders.

    Parameters:
        old_code: Parametrized code of the old module version.
        new_code: Parametrized code of the new module version.
        expected_breakages: A list of breakage kinds to expect.
    """
    with temporary_visited_module(old_code) as old_module:
        with temporary_visited_module(new_code) as new_module:
            breaking = list(find_breaking_changes(old_module, new_module))
    if not expected_breakages:
        assert not breaking
    for breakage, expected_kind in zip(breaking, expected_breakages):
        assert breakage.kind is expected_kind
