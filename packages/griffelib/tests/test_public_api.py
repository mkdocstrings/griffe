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

# Tests for public API handling.

import pytest

from griffe import temporary_visited_module
from griffe._internal.helpers import temporary_visited_package


def test_not_detecting_imported_objects_as_public() -> None:
    """Imported objects not listed in `__all__` must not be considered public."""
    with temporary_visited_module("from abc import ABC\ndef func(): ...") as module:
        assert not module["ABC"].is_public
        assert module["func"].is_public  # Control case.


def test_detecting_dunder_attributes_as_public() -> None:
    """Dunder attributes (methods, etc.) must be considered public."""
    with temporary_visited_module(
        """
        def __getattr__(name): ...
        class A:
            def __init__(self): ...
        """,
    ) as module:
        assert module["__getattr__"].is_public
        assert module["A.__init__"].is_public


def test_propagating_public_attribute_to_inherited_members() -> None:
    """Inherited members must inherit the original `public` value."""
    with temporary_visited_package(
        "pkg",
        {
            "foo.py": """
            class A:
                def method(self): ...
            class B(A): ...
            def func(): ...
            """,
            "bar.py": "from pkg.foo import func\n__all__ = []",
        },
    ) as pkg:
        # Baseline: `method` should be public in both classes.
        class_a = pkg["foo.A"]
        class_b = pkg["foo.B"]
        assert class_b["method"].public is None
        assert class_a["method"].is_public
        assert class_b["method"].is_public

        # Overriding `method.public` should be reflected in both classes.
        class_a["method"].public = False
        assert not class_b["method"].public
        assert not class_a["method"].is_public
        assert not class_b["method"].is_public

        # Setting `public` on an inherited member is forbidden.
        with pytest.raises(TypeError):
            class_b["method"].public = True

        # Baseline: only the original function is public.
        func = pkg["foo.func"]
        func_alias = pkg["bar.func"]
        assert func.public is None
        assert func.is_public
        assert func_alias.public is None
        assert not func_alias.is_public

        # Setting public on the original object doesn't impact aliases.
        func.public = True
        assert func_alias.public is None
        assert not func_alias.is_public

        # We can set the `public` attribute of non-inherited aliases.
        func_alias.public = True
        assert func_alias.is_public
