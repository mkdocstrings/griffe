"""Tests for the `diff` module."""

from __future__ import annotations

import sys

import pytest

from griffe.diff import Breakage, BreakageKind, find_breaking_changes
from griffe.loader import GriffeLoader
from tests.helpers import temporary_pypackage, temporary_visited_module


@pytest.mark.skipif(sys.version_info < (3, 8), reason="no positional-only parameters on Python 3.7")
@pytest.mark.parametrize(
    ("old_code", "new_code", "expected_breakages"),
    [
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
    with temporary_visited_module(old_code) as old_module, temporary_visited_module(new_code) as new_module:
        breaking = list(find_breaking_changes(old_module, new_module))
    assert len(breaking) == len(expected_breakages)
    for breakage, expected_kind in zip(breaking, expected_breakages):
        assert breakage.kind is expected_kind


@pytest.mark.skipif(sys.version_info < (3, 8), reason="no positional-only parameters on Python 3.7")
@pytest.mark.parametrize(
    ("old_code", "new_code", "old_import_code", "new_import_code", "expected_breakages"),
    [
        # ),
        (
            "a = True",
            "a = False",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.ATTRIBUTE_CHANGED_VALUE],
        ),
        (
            "class A(int, str): ...",
            "class A(int): ...",
            "from ._mod_a import A",
            "from ._mod_a import A",
            [BreakageKind.CLASS_REMOVED_BASE],
        ),
        (
            "A = 0",
            "class A: ...",
            "from ._mod_a import A",
            "from ._mod_a import A",
            [BreakageKind.OBJECT_CHANGED_KIND],
        ),
        (
            "a = True",
            "",
            "from ._mod_a import a",
            "",
            [BreakageKind.OBJECT_REMOVED],
        ),
        (
            "def a(): ...",
            "def a(x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_ADDED_REQUIRED],
        ),
        (
            "def a(x=0): ...",
            "def a(x=1): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_CHANGED_DEFAULT],
        ),
        (
            # positional-only to keyword-only
            "def a(x, /): ...",
            "def a(*, x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # keyword-only to positional-only
            "def a(*, x): ...",
            "def a(x, /): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # positional or keyword to positional-only
            "def a(x): ...",
            "def a(x, /): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # positional or keyword to keyword-only
            "def a(x): ...",
            "def a(*, x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        # to variadic positional
        (
            # positional-only to variadic positional
            "def a(x, /): ...",
            "def a(*x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [],
        ),
        (
            # positional or keyword to variadic positional
            "def a(x): ...",
            "def a(*x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # keyword-only to variadic positional
            "def a(*, x): ...",
            "def a(*x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # variadic keyword to variadic positional
            "def a(**x): ...",
            "def a(*x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # positional or keyword to variadic positional, with variadic keyword
            "def a(x): ...",
            "def a(*x, **y): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [],
        ),
        (
            # keyword-only to variadic positional, with variadic keyword
            "def a(*, x): ...",
            "def a(*x, **y): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [],
        ),
        # to variadic keyword
        (
            # positional-only to variadic keyword
            "def a(x, /): ...",
            "def a(**x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # positional or keyword to variadic keyword
            "def a(x): ...",
            "def a(**x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # keyword-only to variadic keyword
            "def a(*, x): ...",
            "def a(**x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [],
        ),
        (
            # variadic positional to variadic keyword
            "def a(*x): ...",
            "def a(**x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_CHANGED_KIND],
        ),
        (
            # positional-only to variadic keyword, with variadic positional
            "def a(x, /): ...",
            "def a(*y, **x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [],
        ),
        (
            # positional or keyword to variadic keyword, with variadic positional
            "def a(x): ...",
            "def a(*y, **x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [],
        ),
        (
            "def a(x=1): ...",
            "def a(x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_CHANGED_REQUIRED],
        ),
        (
            "def a(x, y): ...",
            "def a(y, x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_MOVED, BreakageKind.PARAMETER_MOVED],
        ),
        (
            "def a(x, y): ...",
            "def a(x): ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [BreakageKind.PARAMETER_REMOVED],
        ),
        (
            "def a() -> int: ...",
            "def a() -> str: ...",
            "from ._mod_a import a",
            "from ._mod_a import a",
            [],  # not supported yet: BreakageKind.RETURN_CHANGED_TYPE
        ),
    ],
)
def test_diff_griffe_with_alias(
        old_code: str,
        new_code: str,
        old_import_code: str,
        new_import_code: str,
        expected_breakages: list[Breakage],
) -> None:
    """Test the different incompatibility finders, but with alias that is imported from private module.

    Parameters:
        old_code: Parametrized code of the old module version.
        new_code: Parametrized code of the new module version.
        old_import_code: Parametrized code of the old __init__ module.
        new_import_code: Parametrized code of the new __init__ module.
        expected_breakages: A list of breakage kinds to expect.
    """
    with temporary_pypackage("package_old", ["__init__.py", "_mod_a.py"]) as tmp_package_old, \
            temporary_pypackage("package_new", ["__init__.py", "_mod_a.py"]) as tmp_package_new:
        old_init = tmp_package_old.path / "__init__.py"
        old_mod_a = tmp_package_old.path / "_mod_a.py"
        new_init = tmp_package_new.path / "__init__.py"
        new_mod_a = tmp_package_new.path / "_mod_a.py"

        old_init.write_text(old_import_code)
        new_init.write_text(new_import_code)

        old_mod_a.write_text(old_code)
        new_mod_a.write_text(new_code)

        loader = GriffeLoader(search_paths=[tmp_package_old.tmpdir, tmp_package_new.tmpdir])
        old_package = loader.load_module(tmp_package_old.name)
        new_package = loader.load_module(tmp_package_new.name)

        breaking = list(find_breaking_changes(old_package.module, new_package.module))

    assert len(breaking) == len(expected_breakages)
    for breakage, expected_kind in zip(breaking, expected_breakages):
        assert breakage.kind is expected_kind
