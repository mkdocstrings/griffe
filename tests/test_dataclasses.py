"""Tests for the `dataclasses` module."""

from copy import deepcopy

from griffe.dataclasses import Docstring, Module
from griffe.loader import GriffeLoader
from tests.helpers import module_vtree, temporary_pypackage


def test_submodule_exports():
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


def test_has_docstrings():
    """Assert the `.has_docstrings` method is recursive."""
    module = module_vtree("a.b.c.d")
    module["b.c.d"].docstring = Docstring("Hello.")
    assert module.has_docstrings


def test_handle_aliases_chain_in_has_docstrings():
    """Assert the `.has_docstrings` method can handle aliases chains in members."""
    with temporary_pypackage("package", ["mod_a.py", "mod_b.py"]) as tmp_package:
        mod_a = tmp_package.path / "mod_a.py"
        mod_b = tmp_package.path / "mod_b.py"
        mod_a.write_text("from .mod_b import someobj")
        mod_b.write_text("from somelib import someobj")

        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load_module(tmp_package.name)
        assert not package.has_docstrings
        loader.resolve_aliases(only_exported=False)
        assert not package.has_docstrings


def test_has_docstrings_does_not_trigger_alias_resolution():
    """Assert the `.has_docstrings` method does not trigger alias resolution."""
    with temporary_pypackage("package", ["mod_a.py", "mod_b.py"]) as tmp_package:
        mod_a = tmp_package.path / "mod_a.py"
        mod_b = tmp_package.path / "mod_b.py"
        mod_a.write_text("from .mod_b import someobj")
        mod_b.write_text("from somelib import someobj")

        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load_module(tmp_package.name)
        assert not package.has_docstrings
        assert not package["mod_a.someobj"].resolved


def test_deepcopy():
    """Assert we can deep-copy object trees."""
    loader = GriffeLoader()
    mod = loader.load_module("griffe")

    deepcopy(mod)
    deepcopy(mod.as_dict())
