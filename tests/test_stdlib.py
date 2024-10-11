"""Fuzzing on the standard library."""

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


@pytest.mark.skipif(sys.version_info < (3, 10), reason="Python less than 3.10 does not have sys.stdlib_module_names")
@pytest.mark.parametrize("mod", sorted([m for m in getattr(sys, "stdlib_module_names", ()) if not m.startswith("_")]))
def test_fuzzing_on_stdlib(stdlib_loader: GriffeLoader, mod: str) -> None:
    """Run Griffe on the standard library."""
    with suppress(ImportError, LoadingError):
        stdlib_loader.load(mod)
