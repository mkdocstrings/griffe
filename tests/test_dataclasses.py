"""Tests for the `dataclasses` module."""

from griffe.dataclasses import Docstring, Module


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

