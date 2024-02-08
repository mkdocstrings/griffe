"""Tests for the `dataclasses` module."""

from __future__ import annotations

from copy import deepcopy

import griffe
from griffe.dataclasses import Docstring, Module
from griffe.loader import GriffeLoader
from griffe.tests import module_vtree, temporary_pypackage, temporary_visited_module


def test_submodule_exports() -> None:
    """Check that a module is exported depending on whether it was also imported."""
    root = Module("root")
    sub = Module("sub")
    root["sub"] = sub

    assert not root.member_is_exported(sub, explicitely=True)
    assert not root.member_is_exported(sub, explicitely=False)

    root.imports["sub"] = "root.sub"
    assert not root.member_is_exported(sub, explicitely=True)
    assert root.member_is_exported(sub, explicitely=False)

    root.exports = {"sub"}
    assert root.member_is_exported(sub, explicitely=True)
    assert root.member_is_exported(sub, explicitely=False)


def test_has_docstrings() -> None:
    """Assert the `.has_docstrings` method is recursive."""
    module = module_vtree("a.b.c.d")
    module["b.c.d"].docstring = Docstring("Hello.")
    assert module.has_docstrings


def test_handle_aliases_chain_in_has_docstrings() -> None:
    """Assert the `.has_docstrings` method can handle aliases chains in members."""
    with temporary_pypackage("package", ["mod_a.py", "mod_b.py"]) as tmp_package:
        mod_a = tmp_package.path / "mod_a.py"
        mod_b = tmp_package.path / "mod_b.py"
        mod_a.write_text("from .mod_b import someobj")
        mod_b.write_text("from somelib import someobj")

        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load(tmp_package.name)
        assert not package.has_docstrings
        loader.resolve_aliases(implicit=True)
        assert not package.has_docstrings


def test_has_docstrings_does_not_trigger_alias_resolution() -> None:
    """Assert the `.has_docstrings` method does not trigger alias resolution."""
    with temporary_pypackage("package", ["mod_a.py", "mod_b.py"]) as tmp_package:
        mod_a = tmp_package.path / "mod_a.py"
        mod_b = tmp_package.path / "mod_b.py"
        mod_a.write_text("from .mod_b import someobj")
        mod_b.write_text("from somelib import someobj")

        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load(tmp_package.name)
        assert not package.has_docstrings
        assert not package["mod_a.someobj"].resolved


def test_deepcopy() -> None:
    """Assert we can deep-copy object trees."""
    loader = GriffeLoader()
    mod = loader.load("griffe")

    deepcopy(mod)
    deepcopy(mod.as_dict())


def test_alias_proxies() -> None:
    """Assert that the Alias class has all the necessary methods and properties."""
    api = griffe.load("griffe")
    alias_members = set(api["dataclasses.Alias"].all_members.keys())
    for cls in (
        api["dataclasses.Module"],
        api["dataclasses.Class"],
        api["dataclasses.Function"],
        api["dataclasses.Attribute"],
    ):
        for name in cls.all_members:
            if not name.startswith("_") or name.startswith("__"):
                assert name in alias_members


def test_dataclass_parameters() -> None:
    """Don't return properties as parameters of dataclasses."""
    with temporary_visited_module(
        """
        from dataclasses import dataclass
        from functools import cached_property

        @dataclass
        class Point:
            x: float
            y: float

            @property
            def a(self):
                return 0

            @cached_property
            def b(self):
                return 0
        """,
    ) as module:
        params = module["Point"].parameters
        assert "a" not in params
        assert "b" not in params
