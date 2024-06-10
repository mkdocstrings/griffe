"""Tests for our own API."""

from __future__ import annotations

from itertools import chain
from typing import Iterator

import griffe


def test_alias_proxies() -> None:
    """Assert that the Alias class has all the necessary methods and properties."""
    internal_api = griffe.load("_griffe")
    alias_members = set(internal_api["dataclasses.Alias"].all_members.keys())
    for cls in (
        internal_api["dataclasses.Module"],
        internal_api["dataclasses.Class"],
        internal_api["dataclasses.Function"],
        internal_api["dataclasses.Attribute"],
    ):
        for name in cls.all_members:
            if not name.startswith("_") or name.startswith("__"):
                assert name in alias_members


def _yield_public_objects(module: griffe.Module) -> Iterator[tuple[str, str]]:
    for submodule in module.modules.values():
        if not submodule.is_alias:
            yield from _yield_public_objects(submodule)
    for member in chain(
        module.attributes.values(),
        module.functions.values(),
        module.classes.values(),
    ):
        if member.is_public:
            yield member.name, member.path


def test_public_api() -> None:
    """Assert that all public objects are exposed under `griffe`."""
    internal_api: griffe.Module = griffe.load("_griffe")  # type: ignore[assignment]
    not_exposed = []
    for name, path in _yield_public_objects(internal_api):
        if name not in griffe.__all__ or not hasattr(griffe, name):
            not_exposed.append(path)
    assert not not_exposed, "Objects not exposed:\n" + "\n".join(sorted(not_exposed))
