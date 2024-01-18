"""Tests for the `finder` module."""

from __future__ import annotations

import os
from pathlib import Path
from textwrap import dedent

import pytest

from griffe.dataclasses import Module
from griffe.finder import ModuleFinder, NamespacePackage, Package, _handle_editable_module, _handle_pth_file
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
    paths = [sp.path for sp in _handle_pth_file(pth_file)]
    assert paths == [Path("tests")]


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
    paths = [sp.path for sp in _handle_pth_file(pth_file)]
    assert paths == [Path("tests")]


@pytest.mark.parametrize("editable_file_name", ["__editables_whatever.py", "_editable_impl_whatever.py"])
def test_editables_file_handling(tmp_path: Path, editable_file_name: str) -> None:
    """Assert editable modules by `editables` are handled.

    Parameters:
        tmp_path: Pytest fixture.
    """
    pth_file = tmp_path / editable_file_name
    pth_file.write_text("hello\nF.map_module('griffe', 'src/griffe/__init__.py')")
    paths = [sp.path for sp in _handle_editable_module(pth_file)]
    assert paths == [Path("src")]


def test_setuptools_file_handling(tmp_path: Path) -> None:
    """Assert editable modules by `setuptools` are handled.

    Parameters:
        tmp_path: Pytest fixture.
    """
    pth_file = tmp_path / "__editable__whatever.py"
    pth_file.write_text("hello\nMAPPING = {'griffe': 'src/griffe'}")
    paths = [sp.path for sp in _handle_editable_module(pth_file)]
    assert paths == [Path("src")]


def test_setuptools_file_handling_multiple_paths(tmp_path: Path) -> None:
    """Assert editable modules by `setuptools` are handled when multiple packages are installed in the same editable.

    Parameters:
        tmp_path: Pytest fixture.
    """
    pth_file = tmp_path / "__editable__whatever.py"
    pth_file.write_text(
        "hello=1\nMAPPING = {\n'griffe':\n 'src1/griffe', 'briffe':'src2/briffe'}\ndef printer():\n  print(hello)",
    )
    paths = [sp.path for sp in _handle_editable_module(pth_file)]
    assert paths == [Path("src1"), Path("src2")]


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
    paths = [sp.path for sp in _handle_editable_module(pth_file)]
    assert paths == [Path("/path/to/whatever")]


def test_meson_python_file_handling(tmp_path: Path) -> None:
    """Assert editable modules by `meson-python` are handled.

    Parameters:
        tmp_path: Pytest fixture.
    """
    pth_file = tmp_path / "_whatever_editable_loader.py"
    pth_file.write_text(
        # the path in argument 2 suffixed with src must exist, so we pass '.'
        "hello=1\ninstall({'griffe', 'hello'}, '.', ['/tmp/ninja'], False)",
    )
    search_paths = _handle_editable_module(pth_file)
    assert all(sp.always_scan_for == "griffe" for sp in search_paths)
    paths = [sp.path for sp in search_paths]
    assert paths == [Path("src")]


@pytest.mark.parametrize(
    ("first", "second", "find_stubs", "expect"),
    [
        ("package", "stubs", True, "both"),
        ("stubs", "package", True, "both"),
        ("package", None, True, "package"),
        (None, "package", True, "package"),
        ("stubs", None, True, "stubs"),
        (None, "stubs", True, "stubs"),
        (None, None, True, "none"),
        ("package", "stubs", False, "package"),
        ("stubs", "package", False, "package"),
        ("package", None, False, "package"),
        (None, "package", False, "package"),
        ("stubs", None, False, "none"),
        (None, "stubs", False, "none"),
        (None, None, False, "none"),
    ],
)
def test_finding_stubs_packages(
    tmp_path: Path,
    first: str | None,
    second: str | None,
    find_stubs: bool,
    expect: str,
) -> None:
    """Find stubs-only packages.

    Parameters:
        tmp_path: Pytest fixture.
    """
    search_path1 = tmp_path / "sp1"
    search_path2 = tmp_path / "sp2"
    search_path1.mkdir()
    search_path2.mkdir()

    if first == "package":
        package = search_path1 / "package"
        package.mkdir()
        package.joinpath("__init__.py").touch()
    elif first == "stubs":
        stubs = search_path1 / "package-stubs"
        stubs.mkdir()
        stubs.joinpath("__init__.pyi").touch()

    if second == "package":
        package = search_path2 / "package"
        package.mkdir()
        package.joinpath("__init__.py").touch()
    elif second == "stubs":
        stubs = search_path2 / "package-stubs"
        stubs.mkdir()
        stubs.joinpath("__init__.pyi").touch()

    finder = ModuleFinder([search_path1, search_path2])

    if expect == "none":
        with pytest.raises(ModuleNotFoundError):
            finder.find_spec("package", try_relative_path=False, find_stubs_package=find_stubs)
        return

    name, result = finder.find_spec("package", try_relative_path=False, find_stubs_package=find_stubs)
    assert name == "package"

    if expect == "both":
        assert isinstance(result, Package)
        assert result.path.suffix == ".py"
        assert not result.path.parent.name.endswith("-stubs")
        assert result.stubs
        assert result.stubs.suffix == ".pyi"
        assert result.stubs.parent.name.endswith("-stubs")
    elif expect == "package":
        assert isinstance(result, Package)
        assert result.path.suffix == ".py"
        assert not result.path.parent.name.endswith("-stubs")
        assert result.stubs is None
    elif expect == "stubs":
        assert isinstance(result, Package)
        assert result.path.suffix == ".pyi"
        assert result.path.parent.name.endswith("-stubs")
        assert result.stubs is None


@pytest.mark.parametrize("namespace_package", [False, True])
def test_scanning_package_and_module_with_same_names(namespace_package: bool) -> None:
    """The finder correctly scans package and module having same the name.

    Parameters:
        namespace_package: Whether the temporary package is a namespace one.
    """
    init = not namespace_package
    with temporary_pypackage("pkg", ["pkg/mod.py", "mod/mod.py"], init=init, inits=init) as tmp_package:
        # Here we must make sure that all paths are relative
        # to correctly assert the finder's behavior,
        # so we pass `.` and actually enter the temporary directory.
        path = Path(tmp_package.name)
        filepath: Path | list[Path] = [path] if namespace_package else path
        old = os.getcwd()
        os.chdir(tmp_package.path.parent)
        try:
            finder = ModuleFinder(search_paths=[])
            found = [path for _, path in finder.submodules(Module("pkg", filepath=filepath))]
        finally:
            os.chdir(old)
        check = (
            path / "pkg/mod.py",
            path / "mod/mod.py",
        )
        for mod in check:
            assert mod in found


def test_not_finding_namespace_package_twice() -> None:
    """Deduplicate paths when finding namespace packages."""
    with temporary_pypackage("pkg", ["pkg/mod.py", "mod/mod.py"], init=False, inits=False) as tmp_package:
        old = os.getcwd()
        os.chdir(tmp_package.tmpdir)
        try:
            finder = ModuleFinder(search_paths=[Path("."), tmp_package.tmpdir])
            found = finder.find_package("pkg")
        finally:
            os.chdir(old)
        assert isinstance(found, NamespacePackage)
        assert len(found.path) == 1
