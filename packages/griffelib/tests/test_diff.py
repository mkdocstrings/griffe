# SPDX-License-Identifier: ISC

# Copyright (c) 2021, Timothée Mazzucotelli and contributors

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

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

from griffe import (
    BreakageKind,
    ChangeFlag,
    ChangeKind,
    find_breaking_changes,
    find_changes,
    temporary_visited_module,
    temporary_visited_package,
)


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
            "class a:\n\tb: int | None = None",
            "class a:\n\tb: int",
            [BreakageKind.ATTRIBUTE_CHANGED_VALUE],
        ),
        (
            "def a() -> int: ...",
            "def a() -> str: ...",
            [],  # Not supported yet: `BreakageKind.RETURN_CHANGED_TYPE`.
        ),
    ],
)
def test_diff_griffe(old_code: str, new_code: str, expected_breakages: list[BreakageKind]) -> None:
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


@pytest.mark.parametrize(
    ("old_code", "new_code", "expected_changes"),
    [
        (
            "",
            "a = 1",
            [(ChangeKind.OBJECT_ADDED, frozenset())],
        ),
        (
            "a = 1",
            "",
            [(ChangeKind.OBJECT_REMOVED, frozenset({ChangeFlag.BREAKING}))],
        ),
        (
            "a = 1",
            "class a: ...",
            [(ChangeKind.OBJECT_CHANGED_KIND, frozenset({ChangeFlag.BREAKING}))],
        ),
        (
            "class a: ...",
            "class a(int): ...",
            [(ChangeKind.CLASS_BASE_ADDED, frozenset({ChangeFlag.WARNING}))],
        ),
        (
            "class a(int): ...",
            "class a: ...",
            [(ChangeKind.CLASS_BASE_REMOVED, frozenset({ChangeFlag.BREAKING}))],
        ),
        (
            "def a(): ...",
            "def a(x): ...",
            [(ChangeKind.PARAMETER_ADDED, frozenset({ChangeFlag.BREAKING}))],
        ),
        (
            "def a(): ...",
            "def a(x=1): ...",
            [(ChangeKind.PARAMETER_ADDED, frozenset())],
        ),
        (
            "def a(): ...",
            "def a(*args, **kwargs): ...",
            [
                (ChangeKind.PARAMETER_ADDED, frozenset()),
                (ChangeKind.PARAMETER_ADDED, frozenset()),
            ],
        ),
        (
            "def a(x): ...",
            "def a(): ...",
            [(ChangeKind.PARAMETER_REMOVED, frozenset({ChangeFlag.BREAKING}))],
        ),
        (
            "def a(x, /): ...",
            "def a(*args): ...",
            [
                (ChangeKind.PARAMETER_REMOVED, frozenset({ChangeFlag.WARNING})),
                (ChangeKind.PARAMETER_ADDED, frozenset()),
            ],
        ),
        (
            "def a(x, y): ...",
            "def a(y, x): ...",
            [
                (ChangeKind.PARAMETER_MOVED, frozenset({ChangeFlag.BREAKING})),
                (ChangeKind.PARAMETER_MOVED, frozenset({ChangeFlag.BREAKING})),
            ],
        ),
        (
            "def a(*, x): ...",
            "def a(**x): ...",
            [(ChangeKind.PARAMETER_CHANGED_KIND, frozenset({ChangeFlag.WARNING}))],
        ),
        (
            "def a(x=1): ...",
            "def a(x): ...",
            [(ChangeKind.PARAMETER_CHANGED_DEFAULT, frozenset({ChangeFlag.BREAKING}))],
        ),
        (
            "def a(x): ...",
            "def a(x=1): ...",
            [(ChangeKind.PARAMETER_CHANGED_DEFAULT, frozenset())],
        ),
        (
            "def a(x: int) -> int: ...",
            "def a(x: str) -> str: ...",
            [
                (ChangeKind.PARAMETER_CHANGED_TYPE, frozenset({ChangeFlag.WARNING})),
                (ChangeKind.RETURN_CHANGED_TYPE, frozenset({ChangeFlag.WARNING})),
            ],
        ),
        (
            "def a() -> int: ...",
            "def a(): ...",
            [(ChangeKind.RETURN_CHANGED_TYPE, frozenset({ChangeFlag.BREAKING}))],
        ),
        (
            "a: int = 1",
            "a: str = 2",
            [
                (ChangeKind.ATTRIBUTE_CHANGED_TYPE, frozenset({ChangeFlag.WARNING})),
                (ChangeKind.ATTRIBUTE_CHANGED_VALUE, frozenset({ChangeFlag.BREAKING})),
            ],
        ),
    ],
)
def test_find_changes(
    old_code: str,
    new_code: str,
    expected_changes: list[tuple[ChangeKind, frozenset[ChangeFlag]]],
) -> None:
    """Test finding both breaking and non-breaking API changes."""
    with temporary_visited_module(old_code) as old_package, temporary_visited_module(new_code) as new_package:
        changes = list(find_changes(old_package, new_package))

    assert [(change.kind, change.flags) for change in changes] == expected_changes


def test_find_changes_detects_public_visibility_changes() -> None:
    """Test that changing public visibility is modeled as an addition or removal."""
    old_code = "__all__ = ['a']\na = 1\nb = 2"
    new_code = "__all__ = ['b']\na = 1\nb = 2"
    with temporary_visited_module(old_code) as old_package, temporary_visited_module(new_code) as new_package:
        changes = list(find_changes(old_package, new_package))

    assert [change.kind for change in changes] == [ChangeKind.OBJECT_REMOVED, ChangeKind.OBJECT_ADDED]
    assert changes[0].is_breaking
    assert not changes[1].is_breaking


@pytest.mark.parametrize(
    ("old_deprecation", "new_deprecation", "expected_kind", "expected_flags"),
    [
        (None, "Use b instead", ChangeKind.OBJECT_DEPRECATED, frozenset({ChangeFlag.DEPRECATION})),
        ("Use b instead", None, ChangeKind.OBJECT_UNDEPRECATED, frozenset()),
        (
            "Use b instead",
            "Use c instead",
            ChangeKind.OBJECT_CHANGED_DEPRECATION,
            frozenset({ChangeFlag.DEPRECATION}),
        ),
    ],
)
def test_find_changes_detects_deprecations(
    old_deprecation: str | None,
    new_deprecation: str | None,
    expected_kind: ChangeKind,
    expected_flags: frozenset[ChangeFlag],
) -> None:
    """Test that deprecation metadata changes are reported."""
    with temporary_visited_module("def a(): ...") as old_package:  # noqa: SIM117
        with temporary_visited_module("def a(): ...") as new_package:
            old_package["a"].deprecated = old_deprecation
            new_package["a"].deprecated = new_deprecation
            changes = list(find_changes(old_package, new_package))

    assert len(changes) == 1
    assert changes[0].kind is expected_kind
    assert changes[0].flags == expected_flags
    assert changes[0].as_dict() == {
        "kind": expected_kind,
        "object_path": "module.a",
        "old_value": old_deprecation,
        "new_value": new_deprecation,
        "flags": sorted(expected_flags, key=lambda flag: flag.value),
    }


def test_find_breaking_changes_filters_changes() -> None:
    """Test that the legacy API adapts only breaking-tagged changes."""
    old_code = "a = 1\ndef f(x=1): ..."
    new_code = "b = 2\ndef f(x): ..."
    with temporary_visited_module(old_code) as old_package, temporary_visited_module(new_code) as new_package:
        changes = list(find_changes(old_package, new_package))
        breakages = list(find_breaking_changes(old_package, new_package))

    assert [change.kind for change in changes] == [
        ChangeKind.OBJECT_REMOVED,
        ChangeKind.PARAMETER_CHANGED_DEFAULT,
        ChangeKind.OBJECT_ADDED,
    ]
    assert len(breakages) == sum(change.is_breaking for change in changes)
    assert [breakage.kind for breakage in breakages] == [
        BreakageKind.OBJECT_REMOVED,
        BreakageKind.PARAMETER_CHANGED_REQUIRED,
    ]


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
