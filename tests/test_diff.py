"""Tests for the `diff` module."""

from __future__ import annotations

import pytest

from griffe.diff import Breakage, BreakageKind, find_breaking_changes
from griffe.tests import temporary_visited_module, temporary_visited_package


@pytest.mark.parametrize(
    ("old_code", "new_code", "expected_breakages"),
    [
        (
            "a = True",
            "a = False",
            [BreakageKind.ATTRIBUTE_CHANGED_VALUE],
        ),
        (
            "class a(int, str): ...",
            "class a(int): ...",
            [BreakageKind.CLASS_REMOVED_BASE],
        ),
        (
            "a = 0",
            "class a: ...",
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
            [BreakageKind.PARAMETER_MOVED, BreakageKind.PARAMETER_MOVED],
        ),
        (
            "def a(x, y): ...",
            "def a(x): ...",
            [BreakageKind.PARAMETER_REMOVED],
        ),
        (
            "class a:\n\tb: int | None = None",
            "class a:\n\tb: int",
            [BreakageKind.ATTRIBUTE_CHANGED_VALUE],
        ),
        (
            "def a() -> int: ...",
            "def a() -> str: ...",
            [],  # not supported yet: BreakageKind.RETURN_CHANGED_TYPE
        ),
    ],
)
def test_diff_griffe(old_code: str, new_code: str, expected_breakages: list[Breakage]) -> None:
    """Test the different incompatibility finders.

    Parameters:
        old_code: Parametrized code of the old module version.
        new_code: Parametrized code of the new module version.
        expected_breakages: A list of breakage kinds to expect.
    """
    # check without any alias
    with temporary_visited_module(old_code) as old_package, temporary_visited_module(new_code) as new_package:
        breaking = list(find_breaking_changes(old_package, new_package))
    assert len(breaking) == len(expected_breakages)
    for breakage, expected_kind in zip(breaking, expected_breakages):
        assert breakage.kind is expected_kind
    # check with aliases
    import_a = "from ._mod_a import a"
    old_modules = {"__init__.py": import_a, "_mod_a.py": old_code}
    new_modules = {"__init__.py": new_code and import_a, "_mod_a.py": new_code}
    with temporary_visited_package("package_old", old_modules) as old_package:  # noqa: SIM117
        with temporary_visited_package("package_new", new_modules) as new_package:
            breaking = list(find_breaking_changes(old_package, new_package))
    assert len(breaking) == len(expected_breakages)
    for breakage, expected_kind in zip(breaking, expected_breakages):
        assert breakage.kind is expected_kind


def test_moving_members_in_parent_classes() -> None:
    """Test that moving an object from a base class to a parent class doesn't trigger a breakage."""
    old_code = """
        class Parent:
            ...

        class Base(Parent):
            def method(self):
                ...
    """
    new_code = """
        class Parent:
            def method(self):
                ...

        class Base(Parent):
            ...
    """
    with temporary_visited_module(old_code) as old_package, temporary_visited_module(new_code) as new_package:
        assert not list(find_breaking_changes(old_package, new_package))
