"""Fuzzing on the standard library."""

from __future__ import annotations

import sys
from contextlib import suppress
from typing import TYPE_CHECKING

import pytest

from griffe.loader import GriffeLoader

if TYPE_CHECKING:
    from griffe.dataclasses import Alias, Object


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


@pytest.mark.skipif(sys.version_info < (3, 10), reason="Python less than 3.10 does not have sys.stdlib_module_names")
def test_fuzzing_on_stdlib() -> None:
    """Run Griffe on the standard library."""
    stblib_packages = sorted([m for m in sys.stdlib_module_names if not m.startswith("_")])  # type: ignore[attr-defined,unused-ignore]

    loader = GriffeLoader()
    for package in stblib_packages:
        with suppress(ImportError):
            loader.load(package)

    loader.resolve_aliases(implicit=True, external=True)
    for module in loader.modules_collection.members.values():
        _access_inherited_members(module)

    loader.stats()
