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

# Tests for the `diff` module.

from __future__ import annotations

import pytest

from griffe import Breakage, BreakageKind, find_breaking_changes, temporary_visited_module, temporary_visited_package


@pytest.mark.parametrize(
    ("old_code", "new_code", "expected_breakages"),
    [
        (
            "class a(int, str): ...",
            "class a(int): ...",
            [BreakageKind.CLASS_REMOVED_BASE],
        ),
        (
            # Replacing a base keeps the count unchanged but removes an inherited type.
            "class a(ValueError): ...",
            "class a(RuntimeError): ...",
            [BreakageKind.CLASS_REMOVED_BASE],
        ),
        (
            # Adding more bases must not hide the removal of an existing base.
            "class a(ValueError): ...",
            "class a(RuntimeError, TypeError): ...",
            [BreakageKind.CLASS_REMOVED_BASE],
        ),
        (
            # Each removed base produces its own breakage.
            "class a(ValueError, TypeError): ...",
            "class a: ...",
            [BreakageKind.CLASS_REMOVED_BASE, BreakageKind.CLASS_REMOVED_BASE],
        ),
        (
            "class a(ValueError): ...",
            "class a(ValueError): ...",
            [],
        ),
        (
            "class a(ValueError): ...",
            "class a(ValueError, TypeError): ...",
            [],
        ),
        (
            # Reordering bases does not remove an inherited type.
            "class a(ValueError, TypeError): ...",
            "class a(TypeError, ValueError): ...",
            [],
        ),
        (
            # An unchanged alias name can refer to a different base class.
            "from builtins import ValueError as Error\nclass a(Error): ...",
            "from builtins import RuntimeError as Error\nclass a(Error): ...",
            [BreakageKind.CLASS_REMOVED_BASE],
        ),
        (
            # Renaming an alias preserves the inherited type.
            "from builtins import ValueError as OldError\nclass a(OldError): ...",
            "from builtins import ValueError as NewError\nclass a(NewError): ...",
            [],
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
            # Positional-only to keyword-only.
            "def a(x, /): ...",
            "def a(*, x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # Keyword-only to positional-only.
            "def a(*, x): ...",
            "def a(x, /): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # Positional or keyword to positional-only.
            "def a(x): ...",
            "def a(x, /): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # Positional or keyword to keyword-only.
            "def a(x): ...",
            "def a(*, x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        # To variadic positional.
        (
            # Positional-only to variadic positional.
            "def a(x, /): ...",
            "def a(*x): ...",
            [],
        ),
        (
            # Positional or keyword to variadic positional.
            "def a(x): ...",
            "def a(*x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # Keyword-only to variadic positional.
            "def a(*, x): ...",
            "def a(*x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # Variadic keyword to variadic positional.
            "def a(**x): ...",
            "def a(*x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # Positional or keyword to variadic positional, with variadic keyword.
            "def a(x): ...",
            "def a(*x, **y): ...",
            [],
        ),
        (
            # Keyword-only to variadic positional, with variadic keyword.
            "def a(*, x): ...",
            "def a(*x, **y): ...",
            [],
        ),
        # To variadic keyword.
        (
            # Positional-only to variadic keyword.
            "def a(x, /): ...",
            "def a(**x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # Positional or keyword to variadic keyword.
            "def a(x): ...",
            "def a(**x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # Keyword-only to variadic keyword.
            "def a(*, x): ...",
            "def a(**x): ...",
            [],
        ),
        (
            # Variadic positional to variadic keyword.
            "def a(*x): ...",
            "def a(**x): ...",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # Positional-only to variadic keyword, with variadic positional.
            "def a(x, /): ...",
            "def a(*y, **x): ...",
            [],
        ),
        (
            # Positional or keyword to variadic keyword, with variadic positional.
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
            "def a() -> int: ...",
            "def a() -> str: ...",
            [],  # Not supported yet: `BreakageKind.RETURN_CHANGED_TYPE`.
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
    # Check without any alias.
    with temporary_visited_module(old_code) as old_package, temporary_visited_module(new_code) as new_package:
        breaking = list(find_breaking_changes(old_package, new_package))
    assert len(breaking) == len(expected_breakages)
    for breakage, expected_kind in zip(breaking, expected_breakages, strict=False):
        assert breakage.kind is expected_kind
    # Check with aliases.
    import_a = "from ._mod_a import a\n__all__ = ['a']"
    old_modules = {"__init__.py": import_a, "_mod_a.py": old_code}
    new_modules = {"__init__.py": new_code and import_a, "_mod_a.py": new_code}
    with temporary_visited_package("package_old", old_modules) as old_package:  # noqa: SIM117
        with temporary_visited_package("package_new", new_modules) as new_package:
            breaking = list(find_breaking_changes(old_package, new_package))
    assert len(breaking) == len(expected_breakages)
    for breakage, expected_kind in zip(breaking, expected_breakages, strict=False):
        assert breakage.kind is expected_kind


def test_removed_bases_reported_individually() -> None:
    """Report each removed base in declaration order, without the retained bases."""
    # Retain one base and replace two others with a new base.
    old_code = "class a(ValueError, TypeError, RuntimeError): ..."
    new_code = "class a(TypeError, LookupError): ..."

    with temporary_visited_module(old_code) as old_package, temporary_visited_module(new_code) as new_package:
        breaking = list(find_breaking_changes(old_package, new_package))

    # Each diagnostic identifies only its removed base.
    assert len(breaking) == 2
    for breakage, removed_base in zip(breaking, ("ValueError", "RuntimeError"), strict=True):
        assert breakage.kind is BreakageKind.CLASS_REMOVED_BASE
        assert [base.canonical_path for base in breakage.old_value] == [removed_base]
        assert breakage.new_value == []
        assert breakage.explain().endswith(f"[{removed_base}] -> []")


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


@pytest.mark.parametrize(
    ("old_code", "new_code", "expected_members"),
    [
        pytest.param(
            """
            class Base:
                def method(self, value): ...

            class Sub(Base):
                pass
            """,
            """
            class Base:
                def method(self, value): ...

            class Sub(Base):
                def method(self): ...
            """,
            {"Sub.method"},
            id="base-first-override-changes",
        ),
        pytest.param(
            """
            class Sub(Base):
                pass

            class Base:
                def method(self, value): ...
            """,
            """
            class Sub(Base):
                def method(self): ...

            class Base:
                def method(self, value): ...
            """,
            {"Sub.method"},
            id="subclass-first-override-changes",
        ),
        pytest.param(
            """
            class Base:
                def method(self, value): ...

            class Sub(Base):
                pass
            """,
            """
            class Base:
                def method(self): ...

            class Sub(Base):
                def method(self): ...
            """,
            {"Base.method", "Sub.method"},
            id="base-first-base-and-override-change",
        ),
        pytest.param(
            """
            class Sub(Base):
                pass

            class Base:
                def method(self, value): ...
            """,
            """
            class Sub(Base):
                def method(self): ...

            class Base:
                def method(self): ...
            """,
            {"Base.method", "Sub.method"},
            id="subclass-first-base-and-override-change",
        ),
    ],
)
def test_new_override_compared_with_inherited_method(old_code: str, new_code: str, expected_members: set[str]) -> None:
    """Compare every old/new member pair regardless of class declaration order."""
    # Visit the source without executing it so either class can be declared first.
    with temporary_visited_module(old_code) as old_package, temporary_visited_module(new_code) as new_package:
        breakages = list(find_breaking_changes(old_package, new_package))

    # Report each affected method exactly once, including both methods when the base also changes.
    expected_paths = {f"{new_package.path}.{member}" for member in expected_members}
    assert {breakage.obj.path for breakage in breakages} == expected_paths
    assert len(breakages) == len(expected_paths)
    assert all(breakage.kind is BreakageKind.PARAMETER_REMOVED for breakage in breakages)
