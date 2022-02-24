"""Tests for the `loader` module."""

from griffe.expressions import Name
from griffe.loader import GriffeLoader
from tests.helpers import temporary_pyfile, temporary_pypackage


def test_has_docstrings_does_not_try_to_resolve_alias():
    """Assert that checkins presence of docstrings does not trigger alias resolution."""
    with temporary_pyfile("""from abc import abstractmethod""") as (module_name, path):
        loader = GriffeLoader(search_paths=[path.parent])
        module = loader.load_module(module_name)
        loader.resolve_aliases()
        assert "abstractmethod" in module.members
        assert not module.has_docstrings


def test_recursive_wildcard_expansion():
    """Assert that wildcards are expanded recursively."""
    with temporary_pypackage("package", ["mod_a/mod_b/mod_c.py"]) as tmp_package:
        mod_a_dir = tmp_package.path / "mod_a"
        mod_b_dir = mod_a_dir / "mod_b"
        mod_a = mod_a_dir / "__init__.py"
        mod_b = mod_b_dir / "__init__.py"
        mod_c = mod_b_dir / "mod_c.py"
        mod_c.write_text("CONST_X = 'X'\nCONST_Y = 'Y'")
        mod_b.write_text("from .mod_c import *")
        mod_a.write_text("from .mod_b import *")

        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load_module(tmp_package.name)

        assert "CONST_X" in package["mod_a.mod_b.mod_c"].members
        assert "CONST_Y" in package["mod_a.mod_b.mod_c"].members

        assert "CONST_X" not in package.members
        assert "CONST_Y" not in package.members

        loader.expand_wildcards(package)

        assert "CONST_X" in package["mod_a"].members
        assert "CONST_Y" in package["mod_a"].members
        assert "CONST_X" in package["mod_a.mod_b"].members
        assert "CONST_Y" in package["mod_a.mod_b"].members


def test_dont_shortcut_alias_chain_after_expanding_wildcards():
    """Assert public aliases paths are not resolved to canonical paths when expanding wildcards."""
    with temporary_pypackage("package", ["mod_a.py", "mod_b.py", "mod_c.py"]) as tmp_package:
        mod_a = tmp_package.path / "mod_a.py"
        mod_b = tmp_package.path / "mod_b.py"
        mod_c = tmp_package.path / "mod_c.py"

        mod_a.write_text("from package.mod_b import *\nclass Child(Base): ...\n")
        mod_b.write_text("from package.mod_c import Base\n__all__ = ['Base']\n")
        mod_c.write_text("class Base: ...\n")

        loader = GriffeLoader(search_paths=[tmp_package.tmpdir])
        package = loader.load_module(tmp_package.name)
        loader.resolve_aliases(package)
        child = package["mod_a.Child"]
        assert child.bases
        base = child.bases[0]
        assert isinstance(base, Name)
        assert base.source == "Base"
        assert base.full == "package.mod_b.Base"
