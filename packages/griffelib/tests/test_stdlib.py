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

# Fuzzing on the standard library.

from __future__ import annotations

import sys
from contextlib import suppress
from typing import TYPE_CHECKING

import pytest

from griffe import GriffeLoader, LoadingError

if TYPE_CHECKING:
    from collections.abc import Iterator

    from griffe import Alias, Object


def _access_inherited_members(obj: Object | Alias) -> None:
    try:
        is_class = obj.is_class
    except Exception:  # noqa: BLE001
        return
    if is_class:
        assert obj.inherited_members is not None
    else:
        for cls in obj.classes.values():
            _access_inherited_members(cls)


@pytest.fixture(name="stdlib_loader", scope="session")
def fixture_stdlib_loader() -> Iterator[GriffeLoader]:
    """Yield a GriffeLoader instance.

    During teardown, resolve aliases and access inherited members
    to make sure that no exception is raised when computing MRO.
    """
    loader = GriffeLoader(allow_inspection=False, store_source=False)
    yield loader
    loader.resolve_aliases(implicit=True, external=None)
    for module in loader.modules_collection.members.values():
        _access_inherited_members(module)
    loader.stats()


@pytest.mark.parametrize("mod", sorted([m for m in getattr(sys, "stdlib_module_names", ()) if not m.startswith("_")]))
def test_fuzzing_on_stdlib(stdlib_loader: GriffeLoader, mod: str) -> None:
    """Run Griffe on the standard library."""
    with suppress(ImportError, LoadingError):
        stdlib_loader.load(mod)
