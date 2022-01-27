"""Tests for the `finder` module."""

import pytest

from griffe.finder import ModuleFinder
from tests.helpers import temporary_pypackage


@pytest.mark.parametrize(
    ("pypackage", "module", "add_to_search_path", "expected_top_name", "expected_top_path"),
    [
        (("a", ["b.py"]), "a/b.py", True, "a", "a/__init__.py"),
        (("a", ["b.py"]), "a/b.py", False, "a", "a/__init__.py"),
        (("a/b", ["c.py"]), "a/b/c.py", True, "a", "a"),
        (("a/b", ["c.py"]), "a/b/c.py", False, "b", "a/b/__init__.py"),
    ],
)
def test_find_module_with_path(pypackage, module, add_to_search_path, expected_top_name, expected_top_path):
    """Check that the finder can find modules using strings and Paths.

    Parameters:
        pypackage: A temporary package (metadata) on the file system (parametrized).
        module: The module path to load (parametrized).
        add_to_search_path: Whether to add the temporary package parent path to the finder search paths (parametrized).
        expected_top_name: Expected top module name (parametrized).
        expected_top_path: Expected top module path (parametrized).
    """
    with temporary_pypackage(*pypackage) as tmp_package:
        finder = ModuleFinder(search_paths=[tmp_package.tmpdir] if add_to_search_path else None)
        _, package = finder.find_spec(tmp_package.tmpdir / module)
        assert package.name == expected_top_name
        if package.is_namespace:
            assert package.path == [tmp_package.tmpdir / expected_top_path]
        else:
            assert package.path == tmp_package.tmpdir / expected_top_path
