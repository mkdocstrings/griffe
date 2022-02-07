"""Tests for the `loader` module."""

from griffe.loader import GriffeLoader
from tests.helpers import temporary_pyfile


def test_has_docstrings_does_not_try_to_resolve_alias():
    """Assert that checkins presence of docstrings does not trigger alias resolution."""
    with temporary_pyfile("""from abc import abstractmethod""") as (module_name, path):
        loader = GriffeLoader(search_paths=[path.parent])
        module = loader.load_module(module_name)
        loader.resolve_aliases()
        assert "abstractmethod" in module.members
        assert not module.has_docstrings
