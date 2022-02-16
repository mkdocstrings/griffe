"""Tests for the `dataclasses` module."""


from griffe.dataclasses import Module


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
