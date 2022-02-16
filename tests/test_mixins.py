"""Tests for the `mixins` module."""

from tests.helpers import module_vtree


def test_access_members_using_string_and_tuples():
    """Assert wa can access the same members with both strings and tuples."""
    module = module_vtree("a.b.c.d")
    assert module["b"] is module[("b",)]
    assert module["b.c"] is module[("b", "c")]
    assert module["b.c.d"] is module[("b", "c", "d")]
