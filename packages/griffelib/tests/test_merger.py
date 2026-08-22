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

# Tests for the `merger` module.

from __future__ import annotations

import pytest

from griffe import temporary_visited_package


def test_dont_trigger_alias_resolution_when_merging_stubs() -> None:
    """Assert that we don't trigger alias resolution when merging stubs."""
    with temporary_visited_package(
        "package",
        {
            "mod.py": "import pathlib\n\ndef f() -> pathlib.Path:\n    return pathlib.Path()",
            "mod.pyi": "import pathlib\n\ndef f() -> pathlib.Path: ...",
        },
    ) as pkg:
        assert not pkg["mod.pathlib"].resolved


def test_merge_stubs_on_wildcard_imported_objects() -> None:
    """Assert that stubs can be merged on wildcard imported objects."""
    with temporary_visited_package(
        "package",
        {
            "mod.py": "class A:\n    def hello(value: int | str) -> int | str:\n        return value",
            "__init__.py": "from .mod import *",
            "__init__.pyi": """
                from typing import overload
                class A:
                    @overload
                    def hello(value: int) -> int: ...
                    @overload
                    def hello(value: str) -> str: ...
                """,
        },
    ) as pkg:
        assert pkg["A.hello"].overloads


def test_merge_imports() -> None:
    """Assert that imports are merged correctly."""
    with temporary_visited_package(
        "package",
        {
            "mod.py": "import abc",
            "mod.pyi": "import collections",
        },
    ) as pkg:
        assert set(pkg["mod"].imports) == {"abc", "collections"}


def test_override_exports() -> None:
    """Assert that exports are overridden too (like imports are merged)."""
    with temporary_visited_package(
        "package",
        {
            "__init__.py": "import dynamic_all\n__all__ = dynamic_all()",
            "__init__.pyi": "from ._hello import hello\n__all__ = ['hello']",
            "_hello.py": "def hello() -> None:\n    '''Say hello.'''",
        },
    ) as pkg:
        assert pkg.exports == ["hello"]


def test_merge_attribute_values() -> None:
    """Assert that attribute values are merged correctly."""
    with temporary_visited_package(
        "package",
        {
            "__init__.py": "import dynamic_all\n__all__ = dynamic_all()",
            "__init__.pyi": "from ._hello import hello\n__all__ = ['hello']",
            "_hello.py": "def hello() -> None:\n    '''Say hello.'''",
        },
    ) as pkg:
        assert str(pkg["__all__"].value) == "['hello']"


def test_merge_overload_annotations() -> None:
    """Assert that overload annotations are merged correctly."""
    with temporary_visited_package(
        "package",
        {
            "mod.py": "def func(x): ...",
            "mod.pyi": """
                from typing import overload

                @overload
                def func(x: int) -> int: ...

                @overload
                def func(x: float) -> float: ...
                """,
        },
    ) as pkg:
        func = pkg["mod.func"]
        assert str(func.parameters["x"].annotation) == "int | float"
        assert str(func.returns) == "int | float"


@pytest.mark.parametrize(
    ("psd", "expected"),
    [(True, "Stubs"), (False, "Source")],
)
def test_prefer_stubs_docstrings(psd: bool, expected: str) -> None:
    """The "prefer stubs docstrings" option is respected."""
    with temporary_visited_package(
        "package",
        {
            "mod.py": "def func():\n    '''Source'''",
            "mod.pyi": "def func():\n    '''Stubs'''",
        },
        prefer_stubs_docs=psd,
    ) as pkg:
        func = pkg["mod.func"]
        assert func.docstring.value == expected
