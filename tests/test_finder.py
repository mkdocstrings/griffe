"""Tests for the `finder` module."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from griffe.finder import ModuleFinder, NamespacePackage, _handle_editable_module, _handle_pth_file
from griffe.tests import temporary_pypackage


@pytest.mark.parametrize(
    ("pypackage", "module", "add_to_search_path", "expected_top_name", "expected_top_path"),
    [
        (("a", ["b.py"]), "a/b.py", True, "a", "a/__init__.py"),
        (("a", ["b.py"]), "a/b.py", False, "a", "a/__init__.py"),
        (("a/b", ["c.py"]), "a/b/c.py", True, "a", "a"),
        (("a/b", ["c.py"]), "a/b/c.py", False, "b", "a/b/__init__.py"),
    ],
)
def test_find_module_with_path(
    pypackage: tuple[str, list[str]],
    module: str,
    add_to_search_path: bool,
    expected_top_name: str,
    expected_top_path: str,
) -> None:
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
        if isinstance(package, NamespacePackage):
            assert package.path == [tmp_package.tmpdir / expected_top_path]
        else:
            assert package.path == tmp_package.tmpdir / expected_top_path


@pytest.mark.parametrize(
    "statement",
    [
        "__import__('pkg_resources').declare_namespace(__name__)",
        "__path__ = __import__('pkgutil').extend_path(__path__, __name__)",
    ],
)
def test_find_pkg_style_namespace_packages(statement: str) -> None:
    """Check that the finder can find pkg-style namespace packages.

    Parameters:
        statement: The statement in the `__init__` module allowing to mark the package as namespace.
    """
    with temporary_pypackage("namespace/package1") as tmp_package1, temporary_pypackage(
        "namespace/package2",
    ) as tmp_package2:
        tmp_package1.path.parent.joinpath("__init__.py").write_text(statement)
        tmp_package2.path.parent.joinpath("__init__.py").write_text(statement)
        finder = ModuleFinder(search_paths=[tmp_package1.tmpdir, tmp_package2.tmpdir])
        _, package = finder.find_spec("namespace")
        assert package.name == "namespace"
        assert isinstance(package, NamespacePackage)
        assert package.path == [tmp_package1.path.parent, tmp_package2.path.parent]


def test_pth_file_handling(tmp_path: Path) -> None:
    """Assert .pth files are correctly handled.

    Parameters:
        tmp_path: Pytest fixture.
    """
    pth_file = tmp_path / "hello.pth"
    pth_file.write_text(
        dedent(
            """
            # comment

            import thing
            import\tthing
            /doesnotexist
            tests
            """,
        ),
    )
    directories = _handle_pth_file(pth_file)
    assert directories == [Path("tests")]


def test_pth_file_handling_with_semi_colon(tmp_path: Path) -> None:
    """Assert .pth files are correctly handled.

    Parameters:
        tmp_path: Pytest fixture.
    """
    pth_file = tmp_path / "hello.pth"
    pth_file.write_text(
        dedent(
            """
            # comment
            import thing; import\tthing; /doesnotexist; tests
            """,
        ),
    )
    directories = _handle_pth_file(pth_file)
    assert directories == [Path("tests")]


@pytest.mark.parametrize("editable_file_name", ["__editables_whatever.py", "_editable_impl_whatever.py"])
def test_editables_file_handling(tmp_path: Path, editable_file_name: str) -> None:
    """Assert editable modules by `editables` are handled.

    Parameters:
        tmp_path: Pytest fixture.
    """
    pth_file = tmp_path / editable_file_name
    pth_file.write_text("hello\nF.map_module('griffe', 'src/griffe/__init__.py')")
    assert _handle_editable_module(pth_file) == [Path("src")]


def test_setuptools_file_handling(tmp_path: Path) -> None:
    """Assert editable modules by `setuptools` are handled.

    Parameters:
        tmp_path: Pytest fixture.
    """
    pth_file = tmp_path / "__editable__whatever.py"
    pth_file.write_text("hello\nMAPPING = {'griffe': 'src/griffe'}")
    assert _handle_editable_module(pth_file) == [Path("src")]


def test_setuptools_file_handling_multiple_paths(tmp_path: Path) -> None:
    """Assert editable modules by `setuptools` are handled when multiple packages are installed in the same editable.

    Parameters:
        tmp_path: Pytest fixture.
    """
    pth_file = tmp_path / "__editable__whatever.py"
    pth_file.write_text(
        "hello=1\nMAPPING = {\n'griffe':\n 'src1/griffe', 'briffe':'src2/briffe'}\ndef printer():\n  print(hello)",
    )
    assert _handle_editable_module(pth_file) == [Path("src1"), Path("src2")]


def test_scikit_build_core_file_handling(tmp_path: Path) -> None:
    """Assert editable modules by `scikit-build-core` are handled.

    Parameters:
        tmp_path: Pytest fixture.
    """
    pth_file = tmp_path / "_whatever_editable.py"
    pth_file.write_text(
        "hello=1\ninstall({'whatever': '/path/to/whatever'}, {'whatever.else': '/else'}, None, False, True)",
    )
    # the second dict is not handled: scikit-build-core puts these files
    # in a location that Griffe won't be able to discover anyway
    # (they don't respect standard package or namespace package layouts,
    # and rely on dynamic meta path finder stuff)
    assert _handle_editable_module(pth_file) == [Path("/path/to/whatever")]
